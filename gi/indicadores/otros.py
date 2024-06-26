from dateutil.relativedelta import relativedelta
from django.db.models import (
    Count,
    Q,
    QuerySet,
    Case,
    When,
    Value,
    F,
    Subquery,
    OuterRef,
)
from django.utils.timezone import now

from gi.indicadores.dm import annotate_last_hba1c
from gi.indicadores.utils import div_by_zero_catch
from gi.models import Paciente, ControlPaciente
from gi.utils import get_pacientes_usuario


def get_otros_dict(user, base_qs=None):
    if base_qs is None:
        base_qs = get_pacientes_usuario(user)
    return {
        "control-hta-diagnosticados": control_hta(base_qs),
        "control-dm-diagnosticados": control_dm(base_qs),
        "control-obesidad": control_obesidad(base_qs),
        "control-hipoglicemia": control_hipoglicemia(base_qs),
    }


@div_by_zero_catch
def control_hta(base_qs):
    today = now()
    control_date_limit = today - relativedelta(months=7)
    age_limit = today - relativedelta(years=60)

    p_qs = base_qs.filter(diagnostico_hta=True)

    grupo_1: QuerySet[Paciente] = p_qs.annotate(
        count_registers=Count(
            "controlpaciente",
            filter=Q(
                controlpaciente__tas__lte=140,
                controlpaciente__tad__lte=80,
                controlpaciente__fecha__gte=control_date_limit,
            ),
        )
    ).filter(count_registers__gte=2, fecha_nacimiento__gte=age_limit)

    grupo_2: QuerySet[Paciente] = p_qs.annotate(
        count_registers=Count(
            "controlpaciente",
            filter=Q(
                controlpaciente__tas__lte=140,
                controlpaciente__tad__lte=80,
                controlpaciente__fecha__gte=control_date_limit,
            ),
        )
    ).filter(count_registers__gte=2, fecha_nacimiento__lt=age_limit)

    return (grupo_1.count() + grupo_2.count()) * 100 / p_qs.count(), (grupo_1 | grupo_2)


@div_by_zero_catch
def control_dm(base_qs):
    p_qs = base_qs.exclude(diagnostico="")
    control_date_limit = now() - relativedelta(months=6)
    # TODO se asume que la meta es 7
    controlados = p_qs.annotate(**annotate_last_hba1c).filter(
        last_register_hba1c__lte=7, examenpaciente__fecha__gte=control_date_limit
    )
    return controlados.count() * 100 / p_qs.count(), controlados


@div_by_zero_catch
def control_obesidad(base_qs):
    p_qs = (
        base_qs.annotate(
            fix_estatura=Case(
                When(estatura__lte=0, then=Value(1)), default=F("estatura")
            )
        )
        .annotate(mts=F("fix_estatura") / Value(100))
        .annotate(imc=F("peso") / (F("mts") * F("mts")))
        .filter(imc__gte=25)
    )

    return p_qs.count() * 100 / base_qs.count(), p_qs


@div_by_zero_catch
def control_hipoglicemia(base_qs):
    p_qs = base_qs.annotate(
        ultimo_control_hipoglicemia=Subquery(
            ControlPaciente.objects.filter(
                fk_paciente_id=OuterRef("id"),
            )
            .order_by("-fecha")
            .values("numero_eventos_hipoglicemia")[:1]
        )
    ).filter(ultimo_control_hipoglicemia__gte=0)

    return p_qs.count() * 100 / base_qs.count(), p_qs
