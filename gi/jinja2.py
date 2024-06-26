from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {"static": static, "url": reverse, "get_messages": _get_messages}
    )
    return env


def _get_messages(request):
    system_messages = messages.get_messages(request)
    response = []
    for message in system_messages:
        response.append(
            {"tags": message.tags, "text": message.message, "level": message.level}
        )
    return response
