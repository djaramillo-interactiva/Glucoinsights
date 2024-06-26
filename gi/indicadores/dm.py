from typing import Optional

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet, Q
from django.utils.timezone import now

from gi.constants import DM_CIE_10
from gi.indicadores.utils import get_tamizaje_qs, div_by_zero_catch
from gi.models import Paciente, Indicador
from gi.utils import (
    get_pacientes_usuario,
    annotate_last_hba1c,
    annotate_last_ldl,
    annotate_imc,
)

# TOTAL NUEVA EPS
total = 7000000


def get_dm_dict(user, base_qs=None):
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)
    return {
        "control-hta-dm": control_hta(base_qs, user),
        "cobertura-hba1c": cobertura_hba1c(base_qs, user),
        "control-hba1c": control_hba1c(base_qs, user),
        "tamizaje-ldl": tamizaje_ldl(base_qs, user),
        "meta-ldl": meta_ldl(base_qs, user),
        "imc-normal": imc_normal(base_qs, user),
        "indidencia-dm": incidencia(base_qs, user),
        "prevalencia-dm": prevalencia(base_qs, user),
        "cobertura-programa-dm": cobertura(base_qs, user),
        "control-dm-programa": control(base_qs, user),
        "hospitalizacion-dm": hospitalizacion(base_qs, user),
        "proporcion-dm-con-hba1c-mayor-9": proporcion_hba1c(base_qs, user),
        "cobertura-hba1c-dm": cobertura_hba1c(base_qs, user),
        "tamizaje-erc-dm": tamizaje_erc_cr(base_qs, user),
        "tamizaje-erc-rac-dm": tamizaje_erc_cr_rac(base_qs, user),
        "tasa-incidencia-amputacion-mi": incidencia_amputacion(base_qs, user),
        "prevalencia-amputacion-mi": prevalencia_amputacion(base_qs, user),
        "tamizaje-dilipidemia": tamizaje_dislipidemia(base_qs, user),
        "captacion-dm": captacion_dm(base_qs, user),
    }


def _get_pacientes_dm(
    base_qs: Optional[QuerySet[Paciente]], user
) -> QuerySet[Paciente]:
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)
    birth_date_limit = now() - relativedelta(years=18)
    return base_qs.exclude(
        tipo_diabetes=Paciente.TIPO_DIABETES_SIN_CLASIFICACION
    ).filter(fecha_nacimiento__lte=birth_date_limit)


@div_by_zero_catch
def control_hta(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    hta = p_qs.filter(tas__lte=140, tad__lte=90)
    return hta.count() / p_qs.count(), hta


@div_by_zero_catch
def cobertura_hba1c(base_qs, user):
    date_limit = now() - relativedelta(years=10)
    p_qs = (
        _get_pacientes_dm(base_qs, user)
        .filter(fecha_diagnostico__gte=date_limit)
        .annotate(**annotate_last_hba1c)
    )
    tamizaje_qs = p_qs.exclude(
        Q(last_register_hba1c__isnull=True) | Q(last_register_hba1c=0)
    ).distinct()
    return tamizaje_qs.count() / total, tamizaje_qs


@div_by_zero_catch
def control_hba1c(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    control_qs = p_qs.annotate(**annotate_last_hba1c).filter(last_register_hba1c__lte=7)
    return control_qs.count() / p_qs.count(), control_qs


@div_by_zero_catch
def tamizaje_ldl(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user).exclude(
        Q(examenpaciente__ldl__isnull=True) | Q(examenpaciente__ldl=0)
    )
    return p_qs.count() / total, p_qs


@div_by_zero_catch
def meta_ldl(base_qs, user):
    p_qs = (
        _get_pacientes_dm(base_qs, user)
        .annotate(**annotate_last_ldl)
        .filter(last_register_ldl__lte=100)
        .exclude(Q(examenpaciente__ldl__isnull=True) | Q(examenpaciente__ldl=0))
        .distinct()
    )
    return p_qs.count() / total, p_qs


@div_by_zero_catch
def imc_normal(base_qs, user):
    p_qs = annotate_imc(_get_pacientes_dm(base_qs, user))
    normal_pqs = p_qs.filter(imc__gte=20, imc__lte=25)
    return normal_pqs.count() / p_qs.count(), normal_pqs


@div_by_zero_catch
def incidencia(base_qs, user):
    date_limit = now() - relativedelta(years=10)
    p_qs = _get_pacientes_dm(base_qs, user).filter(fecha_diagnostico__gte=date_limit)
    # total = _get_pacientes_dm(base_qs, user).count()
    return p_qs.count() * 100 / total, p_qs


@div_by_zero_catch
def prevalencia(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user).filter()
    # total = _get_pacientes_dm(base_qs, user).count()
    return p_qs.count() * 100 / total, p_qs


@div_by_zero_catch
def cobertura(base_qs, user):
    date_limit = now() - relativedelta(months=6)
    p_qs = _get_pacientes_dm(base_qs, user)
    reciente_dm = p_qs.filter(ultimo_seguimiento__gte=date_limit)
    return reciente_dm.count() * 100 / p_qs.count(), reciente_dm


@div_by_zero_catch
def captacion_dm(base_qs, user):
    prev, qs = prevalencia(base_qs, user)
    meta = Indicador.objects.get(slug="prevalencia-dm").meta
    return min((prev / meta) * 100, 100), qs


@div_by_zero_catch
def control(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user).annotate(**annotate_last_hba1c).distinct()
    birth_date_limit = now() - relativedelta(years=16)
    control_date_limit = now() - relativedelta(months=6)

    grupo_1 = p_qs.filter(
        examenpaciente__fecha__gte=control_date_limit,
        last_register_hba1c__lt=7.5,
        fecha_nacimiento__gte=birth_date_limit,
        diagnostico_erc=False,
    )
    grupo_2 = p_qs.filter(
        examenpaciente__fecha__gte=control_date_limit,
        last_register_hba1c__lt=7,
        fecha_nacimiento__lte=birth_date_limit,
        diagnostico_erc=False,
    )
    grupo_3 = p_qs.filter(
        examenpaciente__fecha__gte=control_date_limit,
        last_register_hba1c__lt=7.5,
        fecha_nacimiento__lte=birth_date_limit,
        diagnostico_erc=True,
    )
    return (grupo_1.count() + grupo_2.count() + grupo_3.count()) * 100 / p_qs.count(), (
        grupo_1 | grupo_2 | grupo_3
    )


@div_by_zero_catch
def hospitalizacion(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    hosp_qs = p_qs.filter(
        hospitalizacionpaciente__diagnostico_cie__in=map(lambda x: x[0], DM_CIE_10)
    )
    return hosp_qs.count() / p_qs.count(), hosp_qs


@div_by_zero_catch
def proporcion_hba1c(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user).annotate(**annotate_last_hba1c).distinct()
    grupo = p_qs.filter(last_register_hba1c__gte=9)
    return grupo.count() * 100 / p_qs.count(), grupo


@div_by_zero_catch
def cobertura_hba1c(base_qs, user):
    register_limit = now() - relativedelta(months=6)
    p_qs = _get_pacientes_dm(base_qs, user)

    # TODO Modificar esto porque la tabla RegistroIndividualPaciente ya no existe
    grupo = p_qs.filter(
        examenpaciente__hemoglobina_glicosilada__isnull=False,
        examenpaciente__fecha__gte=register_limit,
    ).distinct()
    return grupo.count() * 100 / p_qs.count(), grupo


@div_by_zero_catch
def tamizaje_erc_cr(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    t_qs = get_tamizaje_qs(p_qs).filter(examenpaciente__creatinina__gt=0)
    return t_qs.count() * 100 / p_qs.count(), t_qs


@div_by_zero_catch
def tamizaje_erc_cr_rac(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    t_qs = get_tamizaje_qs(p_qs).filter(
        examenpaciente__creatinina__gt=0, examenpaciente__microalbuminuria__gt=0
    )
    return t_qs.count() * 100 / p_qs.count(), t_qs


@div_by_zero_catch
def incidencia_amputacion(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    hosp_qs = p_qs.filter(
        hospitalizacionpaciente__diagnostico_cie__in=map(lambda x: x[0], DM_CIE_10)
    )
    return hosp_qs.count() / p_qs.count(), hosp_qs


@div_by_zero_catch
def prevalencia_amputacion(base_qs, user):
    p_qs = _get_pacientes_dm(base_qs, user)
    hosp_qs = p_qs.filter(
        hospitalizacionpaciente__diagnostico_cie__in=map(lambda x: x[0], DM_CIE_10)
    )
    return hosp_qs.count() / p_qs.count(), hosp_qs


@div_by_zero_catch
def tamizaje_dislipidemia(base_qs, user):
    erc_qs = _get_pacientes_dm(base_qs, user)
    t_qs = get_tamizaje_qs(erc_qs).filter(examenpaciente__hdl__gt=0)
    return t_qs.count() * 100 / erc_qs.count(), t_qs
