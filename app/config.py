from mb_base1.config import BaseAppConfig
from mb_base1.services.dvalue_service import DV

from app import __version__


class AppConfig(BaseAppConfig):
    app_version: str = __version__
    tags: list[str] = ["group", "proxy"]
    main_menu: dict[str, str] = {"/groups": "groups", "/proxies": "proxies"}


class DConfigSettings(dict):
    pass


class DValueSettings(dict):
    last_checked_at = DV(None, "bla bla about last_checked_at", False)
