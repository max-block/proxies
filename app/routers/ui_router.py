import pydash
from fastapi import APIRouter
from mb_base1.jinja import Templates, form_choices
from mb_base1.utils import depends_form
from mb_std import md
from starlette.requests import Request
from starlette.responses import HTMLResponse
from wtforms import Form, IntegerField, SelectField, StringField
from wtforms import validators as fv

from app.app import App
from app.models import Group, ProxyType


class CreateGroupForm(Form):
    name = StringField(validators=[fv.input_required()])
    link = StringField(validators=[fv.input_required()])
    username = StringField()
    password = StringField()
    port = IntegerField(validators=[fv.input_required()])
    type = SelectField(choices=form_choices(ProxyType))


def init(app: App, templates: Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def index_page(req: Request):
        return templates.render(req, "index.j2")

    @router.get("/groups", response_class=HTMLResponse)
    def groups_page(req: Request):
        groups = app.db.group.find({}, "name")
        form = CreateGroupForm()
        return templates.render(req, "groups.j2", md(groups, form))

    @router.get("/proxies", response_class=HTMLResponse)
    def proxies_page(req: Request):
        proxies = app.db.proxy.find({}, "host")
        return templates.render(req, "proxies.j2", md(proxies))

    @router.post("/groups")
    def create_group(form_data=depends_form):
        form = CreateGroupForm(form_data)
        if form.validate():
            group = Group(**pydash.rename_keys(form.data, {"name": "_id"}))
            return app.db.group.insert_one(group)
        return {"errors": form.errors}

    return router
