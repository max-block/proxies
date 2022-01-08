from fastapi import APIRouter, Query
from mb_std import utc_delta
from mb_std.mongo import make_query

from app.app import App
from app.models import ProxyStatus, ProxyType


def init(app: App) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_proxies(
        status: ProxyStatus | None = None,
        group: str | None = None,
        type_: ProxyType | None = Query(None, alias="type"),
        host: str | None = None,
        limit: int = 100,
    ):
        query = make_query(status=status, group=group, type=type_, host=host)
        return app.db.proxy.find(query, "-checked_at", limit)

    @router.delete("")
    def delete_all_proxies():
        app.db.proxy.delete_many({})

    @router.post("/{pk}/check")
    def check_proxy(pk):
        return app.proxy_service.check_proxy(pk)

    @router.get("/live")
    def get_live_proxies():
        proxies = app.db.proxy.find({"status": ProxyStatus.OK, "last_ok_at": {"$gt": utc_delta(minutes=-5)}})
        return {"proxies": [p.url for p in proxies]}

    @router.get("/stats")
    def get_stats():
        return app.proxy_service.stats()

    @router.get("/{pk}")
    def get_proxy(pk):
        return app.db.proxy.get_or_none(pk)

    return router
