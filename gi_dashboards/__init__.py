import logging
from typing import Optional

from django.conf import settings
from .dashboards import *

from gi_dashboards.dashboards.base import BaseSegment


def get_dashboard_by_slug(slug, df) -> Optional[BaseSegment]:
    import importlib

    import_module = importlib.import_module(settings.SEGMENTOS_MODULE)
    for name in settings.SEGMENTOS:
        cls = getattr(import_module, name)
        instance: BaseSegment = cls(df)
        if instance.slug == slug:
            return instance
    return None


def get_all_dashboards(df):
    import importlib

    import_module = importlib.import_module(settings.SEGMENTOS_MODULE)
    dashboard = []
    for name in settings.SEGMENTOS:
        cls = getattr(import_module, name)
        instance: BaseSegment = cls(df)
        dashboard.append(instance.get_chart_data)
    return dashboard
