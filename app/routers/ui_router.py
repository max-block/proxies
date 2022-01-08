from fastapi import APIRouter
from mb_base1.jinja import Templates
from mb_std import md
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.app import App


def init(app: App, templates: Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def index_page(req: Request):
        return templates.render(req, "index.j2")

    @router.get("/groups", response_class=HTMLResponse)
    def groups_page(req: Request):
        groups = app.db.group.find({}, "name")
        return templates.render(req, "groups.j2", md(groups))

    @router.get("/proxies", response_class=HTMLResponse)
    def proxies_page(req: Request):
        proxies = app.db.proxy.find({}, "host")
        return templates.render(req, "proxies.j2", md(proxies))

    return router
