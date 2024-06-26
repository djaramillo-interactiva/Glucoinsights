from typing import Tuple, List

from django.utils.text import slugify
from pandas import DataFrame

import gi.models


class AbstractIndicador:
    name = ""
    description = ""
    slug = ""
    label = ""
    tipo = ""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.description = kwargs.get("description", "")
        self.slug = kwargs.get("slug", "")
        self.label = kwargs.get("label", "")
        self.tipo = kwargs.get("tipo", "")

    def calc_value(self, **kwargs):
        raise NotImplementedError(
            "subclasses of Indicador must provide a get_value() method"
        )

    def get_summary(self, **kwargs):
        data = None
        if kwargs.get("calc", True):
            data = self.calc_value(**kwargs)
        return {
            "nombre": self.name,
            "slug": self.slug,
            "descripcion": self.description,
            "tipo": {"name": self.tipo, "slug": slugify(self.tipo)},
            "metric": {
                "label": self.label,
                "value": data.get("value", 0) if data else None,
                "target": self.get_target(),
                "trend": data.get("trend", False) if data else None,
            },
        }

    @property
    def slug_tipo(self):
        return slugify(self.tipo)

    def get_data(self, **kwargs):
        data = self.calc_value(**kwargs)

        return [
            {
                "nombre": self.name,
                "slug": self.slug,
                "descripcion": self.description,
                "slug_tipo": self.slug_tipo,
                "metric": {
                    "label": self.label,
                    "value": round(data.get("value", 0), 2),
                    "target": self.get_target(),
                },
            }
        ]

    def get_historic(self, **kwargs) -> Tuple[List[str], List[float]]:
        return [], []

    def get_column_filter(self, **kwargs):
        raise NotImplementedError(
            "subclasses of Indicador must provide a get_column_filter() method"
        )

    def get_pacientes_interes(self, **kwargs):
        raise NotImplementedError(
            "subclasses of Indicador must provide a get_pacientes_interes() method"
        )

    def get_target(self):
        try:
            from gi.models import Indicador

            indicador = Indicador.objects.filter(slug=self.slug, tipo=self.tipo).first()
            target = indicador.meta if indicador else 0
        except:
            target = 0
        return target
