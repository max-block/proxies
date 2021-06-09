from mb_base1.jinja import Templates
from mb_base1.server import AppRouter, Server

from app.app import App
from app.jinja import custom_jinja
from app.routers import group_router, proxy_router, ui_router
from app.telegram import Telegram

app = App()
templates = Templates(app, custom_jinja)
routers = [
    AppRouter(group_router.init(app), prefix="/api/groups", tag="group"),
    AppRouter(proxy_router.init(app), prefix="/api/proxies", tag="proxy"),
    AppRouter(ui_router.init(app, templates), tag="ui"),
]
server = Server(app, Telegram(app), routers, templates).get_server()
