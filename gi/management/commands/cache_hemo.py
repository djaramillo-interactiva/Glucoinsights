from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.transaction import atomic

from gi.models import Paciente
from gi.utils import annotate_last_hba1c


class Command(BaseCommand):
    help = "Agrega los indicadores iniciales a la base de datos"

    @atomic
    def handle(self, *args, **options):
        for p in Paciente.objects.exclude(
            Q(examenpaciente__hemoglobina_glicosilada__isnull=True)
            | Q(examenpaciente__hemoglobina_glicosilada=0)
        ).annotate(**annotate_last_hba1c):
            p.hba1c = p.last_register_hba1c
            p.save()
