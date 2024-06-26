from typing import Optional

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet, Count, Q
from django.utils.timezone import now

from gi.indicadores.utils import get_tamizaje_qs, div_by_zero_catch
from gi.models import Paciente, Indicador
from gi.utils import get_pacientes_usuario


def get_hta_dict(user, base_qs=None):
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)

    return {
        "indidencia-hta": incidencia(base_qs, user),
        "prevalencia-hta": prevalencia(base_qs, user),
        "cobertura-programa-hta": cobertura_programa(base_qs, user),
        "control-hta-en-programa": control_programa(base_qs, user),
        "captacion-hta": captacion(base_qs, user),
        "tamizaje-erc-hta": tamizaje_erc(base_qs, user),
        "tamizaje-erc-rac-hta": tamizaje_erc_creatinina(base_qs, user),
        "tamizaje-dislipidemia-hta": tamizaje_dislipidemia(base_qs, user),
    }


def _get_pacientes_hta(
    base_qs: Optional[QuerySet[Paciente]], user
) -> QuerySet[Paciente]:
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)
    birth_date_limit = now() - relativedelta(years=18)
    return base_qs.filter(diagnostico_hta=True, fecha_nacimiento__lte=birth_date_limit)


@div_by_zero_catch
def incidencia(base_qs, user):
    total = base_qs.count()
    pacientes_hta = _get_pacientes_hta(base_qs, user)
    return pacientes_hta.count() / total, pacientes_hta


@div_by_zero_catch
def prevalencia(base_qs, user):
    total = base_qs.count()
    pacientes_hta = _get_pacientes_hta(base_qs, user)
    return pacientes_hta.count() / total, pacientes_hta


@div_by_zero_catch
def cobertura_programa(base_qs, user):
    p_qs = _get_pacientes_hta(base_qs, user)
    total_hta = p_qs.count()
    limit_date = now() - relativedelta(months=6)
    control_hta = p_qs.filter(
        Q(ultimo_seguimiento__gte=limit_date), Q(fecha_diagnostico__gte=limit_date)
    )
    return control_hta.count() * 100 / total_hta, control_hta


@div_by_zero_catch
def control_programa(base_qs, user):
    today = now()
    # control_date_limit = today - relativedelta(months=7)
    age_limit = today - relativedelta(years=60)
    p_qs = _get_pacientes_hta(base_qs, user)
    Paciente.objects.filter(tas__lte=140, tad__lte=80)

    grupo_1 = p_qs.annotate(
        # count_registers=Count('controlpaciente', filter=Q(
        #     controlpaciente__tas__lte=140,
        #     controlpaciente__tad__lte=80,
        #     controlpaciente__fecha__gte=control_date_limit
        # ))
    ).filter(
        # count_registers__gte=2,
        tas__lte=140,
        tad__lte=80,
        fecha_nacimiento__gte=age_limit,
    )

    grupo_2 = p_qs.annotate(
        # count_registers=Count('controlpaciente', filter=Q(
        #     controlpaciente__tas__lte=150,
        #     controlpaciente__tad__lte=90,
        #     controlpaciente__fecha__gte=control_date_limit
        # ))
    ).filter(
        # count_registers__gte=2,
        tas__lte=140,
        tad__lte=80,
        fecha_nacimiento__lt=age_limit,
    )
    return (grupo_1.count() + grupo_2.count()) * 100 / p_qs.count(), (grupo_1 | grupo_2)


@div_by_zero_catch
def captacion(base_qs, user):
    pre = prevalencia(base_qs, user)
    meta = Indicador.objects.get(slug="prevalencia-hta").meta
    return min((pre[0] / meta) * 100, 100), pre[1]


@div_by_zero_catch
def tamizaje_erc_creatinina(base_qs, user):
    hta_qs = _get_pacientes_hta(base_qs, user)
    t_qs = get_tamizaje_qs(hta_qs).filter(examenpaciente__creatinina__gt=0)
    return (t_qs.count() / hta_qs.count()) * 100, t_qs


@div_by_zero_catch
def tamizaje_erc(base_qs, user):
    hta_qs = _get_pacientes_hta(base_qs, user)
    t_qs = get_tamizaje_qs(hta_qs).filter(
        examenpaciente__creatinina__gt=0, examenpaciente__microalbuminuria__gt=0
    )
    return (t_qs.count() / hta_qs.count()) * 100, t_qs


@div_by_zero_catch
def tamizaje_dislipidemia(base_qs, user):
    hta_qs = _get_pacientes_hta(base_qs, user)
    t_qs = get_tamizaje_qs(hta_qs).filter(examenpaciente__hdl__gt=0)
    return (t_qs.count() / hta_qs.count()) * 100, t_qs
