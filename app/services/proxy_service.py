from mb_std import ParallelTasks, hrequest, md, utc_delta, utc_now
from wrapt import synchronized

from app.models import ProxyStatus
from app.services.base import AppService, AppServiceParams


class ProxyService(AppService):
    def __init__(self, base_params: AppServiceParams):
        super().__init__(base_params)

    def check_proxy(self, pk):
        proxy = self.db.proxy.get(pk)
        res = hrequest("https://httpbin.org/ip", proxy=proxy.url, timeout=5)
        status = ProxyStatus.OK if res.json.get("origin") == proxy.host else ProxyStatus.DOWN
        updated = {"status": status, "checked_at": utc_now()}
        if status == ProxyStatus.OK:
            updated["last_ok_at"] = utc_now()

        proxy = self.db.proxy.find_by_id_and_update(pk, {"$set": updated})
        if proxy.delete_me():
            self.db.proxy.delete_by_id(pk)
        return updated

    @synchronized
    def check_next_proxies(self):
        proxies = self.db.proxy.find(
            {"$or": [{"checked_at": None}, {"checked_at": {"$lt": utc_delta(minutes=-5)}}]},
            "checked_at",
            limit=15,
        )

        if proxies:
            tasks = ParallelTasks(max_workers=15)
            for p in proxies:
                tasks.add_task(f"check_proxy_{p.id}", self.check_proxy, args=(p.id,))
            tasks.execute()

    def stats(self):
        statuses = {}
        for status in ProxyStatus:
            statuses[status] = self.db.proxy.count({"status": status})

        last_checked = self.db.proxy.find_one({"checked_at": None})
        if not last_checked:
            last_checked = self.db.proxy.find_one({}, "checked_at")

        return md(statuses, last_checked)
