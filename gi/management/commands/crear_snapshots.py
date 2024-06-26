from itertools import chain

from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from django.utils.timezone import now

from gi.models import Indicador, IndicadorSnapshot, GrupoGestion

from gi.indicadores.hta import get_hta_dict
from gi.indicadores.dm import get_dm_dict
from gi.indicadores.erc import get_erc_dict
from gi.indicadores.otros import get_otros_dict
from gi.utils import get_pacientes_grupo_gestion

func_map = {
    Indicador.TIPO_INDICADOR_HTA: get_hta_dict,
    Indicador.TIPO_INDICADOR_ERC: get_erc_dict,
    Indicador.TIPO_INDICADOR_DM: get_dm_dict,
    Indicador.TIPO_INDICADOR_OTROS: get_otros_dict,
}


class Command(BaseCommand):
    help = "Agrega los indicadores iniciales a la base de datos"

    @atomic
    def handle(self, *args, **options):
        indicadores = Indicador.objects.all()
        grupos_gestion = chain([None], GrupoGestion.objects.all())
        today = now()
        for g in grupos_gestion:
            p = get_pacientes_grupo_gestion(g)
            for tipo, indicadores_data_func in func_map.items():
                dict_data = indicadores_data_func(None, p)
                for indicador in indicadores.filter(tipo=tipo):
                    snapshot, c = IndicadorSnapshot.objects.get_or_create(
                        fk_indicador=indicador,
                        fk_grupo_gestion=g,
                        month=today.month,
                        year=today.year,
                        defaults={"value": 0},
                    )
                    snapshot.value = dict_data[indicador.slug][0]
                    snapshot.save()
