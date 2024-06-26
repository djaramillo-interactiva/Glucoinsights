import datetime

from gi.models import Paciente, VariablesClinicas
import pandas as pd


def incidencia_hta(mes: int, year: int):
    # fk_paciente__diagnostico_hta = True
    df_hta = pd.DataFrame(
        VariablesClinicas.objects.filter(
            fecha_cargue__month=mes,
            fecha_cargue__year=year,
            fecha_hta__lt=datetime.datetime(
                year=year if mes < 12 else year + 1,
                month=mes + 1 if mes < 12 else 1,
                day=1,
            ),
            fecha_hta__isnull=False,
        ).values()
    )
