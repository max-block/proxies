from mb_base1.app import BaseApp

from app.config import AppConfig, DConfigSettings, DValueSettings
from app.db import DB
from app.services.base import AppServiceParams
from app.services.group_service import GroupService
from app.services.proxy_service import ProxyService


class App(BaseApp):
    def __init__(self):
        super().__init__(AppConfig(), DConfigSettings(), DValueSettings())
        self.db = DB(self.database)
        self.group_service = GroupService(self.base_params)
        self.proxy_service = ProxyService(self.base_params)

        self.scheduler.add_job(self.proxy_service.check_next_proxies, 5)
        self.scheduler.add_job(self.group_service.check_next_group, 60)

    @property
    def base_params(self):
        return AppServiceParams(super().base_params, self.db)
