from mb_base1.config import BaseAppConfig
from mb_base1.services.dconfig_service import DC
from mb_base1.services.dvalue_service import DV

from app import __version__


class AppConfig(BaseAppConfig):
    app_version: str = __version__
    tags: list[str] = ["group", "proxy"]  # type annotation is requred
    main_menu: dict[str, str] = {"/groups": "groups", "/proxies": "proxies"}  # type annotation is requred
    telegram_bot_help = ""


class DConfigSettings(dict):
    config1 = DC("", "telegram bot token")


class DValueSettings(dict):
    last_checked_at = DV(None, "bla bla about last_checked_at", False)
