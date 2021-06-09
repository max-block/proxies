from fastapi import APIRouter
from mb_base1.jinja import Templates
from mb_commons import md
from starlette.responses import HTMLResponse

from app.app import App


def init(app: App, templates: Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def index_page():
        return templates.render("index.j2")

    @router.get("/groups", response_class=HTMLResponse)
    def groups_page():
        groups = app.db.group.find({}, "name")
        return templates.render("groups.j2", md(groups))

    @router.get("/proxies", response_class=HTMLResponse)
    def proxies_page():
        proxies = app.db.proxy.find({}, "host")
        return templates.render("proxies.j2", md(proxies))

    return router
