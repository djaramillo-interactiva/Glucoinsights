from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from gi.models import Tratamiento


class Command(BaseCommand):
    help = "Carga los tratamientos iniciales"

    @atomic
    def handle(self, *args, **options):
        lista_tratamientos = [
            "Insulina glargina 100",
            "Insulina glargina 100 + bolo",
            "Insulina glargina 300",
            "Insulina glargina 300 + bolo",
            "Insulina degludec",
            "Insulina degludec + bolo",
            "Sulfonilureas",
            "DPP4",
            "GLP1",
            "SGLT2",
            "Metformina",
        ]

        for index, item in enumerate(lista_tratamientos):
            Tratamiento.objects.get_or_create(nombre=item, defaults={"order": index})
        self.stdout.write("DONE")
