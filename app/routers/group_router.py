from fastapi import APIRouter
from mb_base1.utils import j

from app.app import App
from app.models import Group, GroupCreate


def init(app: App) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_groups():
        return app.db.group.find({}, "-created_at")

    @router.post("")
    def create_group(params: GroupCreate):
        return str(app.db.group.insert_one(Group(**params.dict())).inserted_id)

    @router.get("/{pk}")
    def get_group(pk):
        return app.db.group.get(pk)

    @router.delete("/{pk}")
    def delete_group(pk):
        return j(app.db.group.delete_by_id(pk))

    @router.post("/{pk}/check")
    def check_group(pk):
        return app.group_service.check(pk)

    return router
