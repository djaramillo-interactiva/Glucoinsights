from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from gi.models import Indicador
from gi.utils import load_json


class Command(BaseCommand):
    help = "Agrega los indicadores iniciales a la base de datos"

    @atomic
    def handle(self, *args, **options):
        indicadores_json = load_json("indicadores.json")
        counter = 0
        for tipo, indicadores_list in indicadores_json.items():
            for item in indicadores_list:
                i = Indicador.objects.filter(tipo=tipo, slug=item["slug"]).first()
                if not i:
                    i = Indicador(tipo=tipo, slug=item["slug"])

                    i.nombre = item["nombre"]
                    i.descripcion = item["descripcion"]
                    i.meta = item["metric"]["target"]
                    i.medida = item["metric"]["label"]
                    i.valor_actual = item["metric"]["value"]
                    i.order = counter

                    i.save()

                    counter += 1
