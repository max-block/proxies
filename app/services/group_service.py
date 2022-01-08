import re

from mb_std import hrequest, utc_delta, utc_now
from pymongo.errors import BulkWriteError
from wrapt import synchronized

from app.models import Proxy
from app.services.base import AppService, AppServiceParams


class GroupService(AppService):
    def __init__(self, base_params: AppServiceParams):
        super().__init__(base_params)

    def check(self, pk):
        self.logger.debug(f"group_service.check called, pk={pk}")
        group = self.db.group.get(pk)

        res = hrequest(group.link)
        if res.is_error():
            return {"error": res.error}

        hosts = self.parse_ip_addresses(res.body)
        if hosts:
            proxies = [Proxy.from_group(group, host) for host in hosts]
            try:
                self.db.proxy.insert_many(proxies, ordered=False)
            except BulkWriteError:
                pass

        self.db.group.update_by_id(pk, {"$set": {"checked_at": utc_now()}})
        return {"hosts": hosts}

    def delete(self, pk: str):
        self.db.proxy.delete_many({"group": pk})
        return self.db.group.delete_by_id(pk)

    @synchronized
    def check_next_group(self):
        group = self.db.group.find_one(
            {"$or": [{"checked_at": None}, {"checked_at": {"$lt": utc_delta(hours=-1)}}]},
            "-checked_at",
        )
        if group:
            self.check(group.id)

    @staticmethod
    def parse_ip_addresses(data: str) -> set[str]:
        hosts = set()
        for line in data.split("\n"):
            line = line.lower().strip()
            m = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", line)
            if m:
                hosts.add(line)
        return hosts
