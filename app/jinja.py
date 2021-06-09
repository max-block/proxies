from markupsafe import Markup
from mb_base1.jinja import CustomJinja

from app.app import App


def header_info(_app: App):
    info = ""
    return Markup(info)


def footer_info(_app: App):
    info = ""
    return Markup(info)


custom_jinja = CustomJinja(header_info=header_info, footer_info=footer_info)
