from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from gi.models import Tarea, ServicioTarea


class Command(BaseCommand):
    help = "Carga las tareas iniciales"

    @atomic
    def handle(self, *args, **options):
        t, c = Tarea.objects.get_or_create(
            nombre="Servicio / Intervención", defaults={"order": 0}
        )

        lista_servicio = [
            "Odontológica",
            "Psicológica",
            "Médico general",
            "Endocrinólogo y Medicina general",
            "Oftalmolófico",
            "Podólogo",
            "Nutricional",
        ]

        for index, item in enumerate(lista_servicio):
            ServicioTarea.objects.get_or_create(
                nombre=item, fk_tarea=t, defaults={"order": index, "cantidad": 0}
            )
        self.stdout.write("DONE")
