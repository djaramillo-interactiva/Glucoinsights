from typing import Optional

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet
from django.utils.timezone import now

from gi.constants import ERC_CIE_10
from gi.indicadores.utils import div_by_zero_catch
from gi.models import Paciente, Indicador
from gi.utils import get_pacientes_usuario


def get_erc_dict(user, base_qs=None):
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)
    return {
        "incidencia-erc": incidencia(base_qs, user),
        "prevalencia-erc": prevalencia(base_qs, user),
        "cobertura-programa-erc": cobertura(base_qs, user),
        "captacion-erc": captacion(base_qs, user),
        "hospitalizacion-erc": hospitalizacion(base_qs, user),
        "estadificacion-erc-tfg": estadificacion(base_qs, user),
        "progresion-erc": progresion(base_qs, user),
    }


def _get_pacientes_erc(
    base_qs: Optional[QuerySet[Paciente]], user
) -> QuerySet[Paciente]:
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)
    return base_qs.filter(diagnostico_erc=True)


@div_by_zero_catch
def incidencia(base_qs, user):
    p_qs = _get_pacientes_erc(base_qs, user)
    return p_qs.count() * 100 / base_qs.count(), p_qs


@div_by_zero_catch
def prevalencia(base_qs, user):
    erc_qs = _get_pacientes_erc(base_qs, user)
    limit_date = now().replace(day=1)

    p_qs = erc_qs.filter(fecha_diagnostico__gte=limit_date)
    grupo = p_qs.filter(diagnostico_erc=True)
    return grupo.count() * 100 / p_qs.count(), grupo


@div_by_zero_catch
def cobertura(base_qs, user):
    erc_qs = _get_pacientes_erc(base_qs, user)
    date_limit = now() - relativedelta(months=6)
    grupo = erc_qs.filter(controlpaciente__fecha__gte=date_limit)
    return grupo.count() * 100 / erc_qs.count(), grupo


@div_by_zero_catch
def captacion(base_qs, user):
    prev, qs = prevalencia(base_qs, user)
    meta = Indicador.objects.get(slug="prevalencia-erc").meta
    return min((prev / meta) * 100, 100), qs


@div_by_zero_catch
def hospitalizacion(base_qs, user):
    p_qs = _get_pacientes_erc(base_qs, user)
    hosp_qs = p_qs.filter(
        hospitalizacionpaciente__diagnostico_cie__in=map(lambda x: x[0], ERC_CIE_10)
    )
    total = p_qs.count()
    return (hosp_qs.count() / total) * 100, hosp_qs


@div_by_zero_catch
def estadificacion(base_qs, user):
    p_qs = _get_pacientes_erc(base_qs, user)
    estadio_qs = p_qs.exclude(estadio="")
    return (estadio_qs.count() / p_qs.count()) * 100, Paciente.objects.none()


# Fase 2
def progresion(base_qs, user):
    # TODO registrar grado de la enfermedad renal
    return 40, Paciente.objects.none()
