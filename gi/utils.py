import datetime
import json
import math
import os
from io import BytesIO
from typing import Union

import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F, Subquery, OuterRef, Case, Value, When, Q
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import get_current_timezone, now
from pandas import DataFrame

from gi.constants import DEFAULT_DATE_FORMAT, MONTHS
from gi.models import (
    Paciente,
    GrupoGestion,
    GrupoEtareo,
    Usuario,
    ExamenPaciente,
    Ciudad,
    VariablesClinicas,
)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


def parse_date(date: str):
    parsed = datetime.datetime.strptime(date, DEFAULT_DATE_FORMAT)
    return pytz.timezone(str(get_current_timezone())).localize(parsed)


def load_json(file) -> dict:
    data = json.load(
        open(os.path.join(SITE_ROOT, "static/gi/json", file), encoding="utf-8")
    )
    return data


def get_months_filter():
    return {
        "label": "Mes",
        "slug": "mes",
        "options": [
            {"label": month, "value": index} for index, month in enumerate(MONTHS, 1)
        ],
    }


def get_indicadores_filtros(year: int = None) -> list:
    meses = dict(enumerate(MONTHS, 1))

    ge = GrupoEtareo.objects.values(label=F("nombre"), value=F("id"))
    grupos_etareos = {
        "label": "Grupo etáreo",
        "slug": "grupo-etareo",
        "options": list(ge),
    }
    tiempo_afiliacion = {
        "label": "Tiempo de afiliación",
        "slug": "tiempo-afiliacion",
        "options": [
            {"label": "Menos de 1 año", "value": "menos-1-año"},
            {"label": "Entre 1 año y 2 años", "value": "1-y-2-años"},
            {"label": "Entre 2 año y 3 años", "value": "2-y-3-años"},
            {"label": "Entre 3 año y 5 años", "value": "3-y-5-años"},
            {"label": "mas de 5 años", "value": "mas-5-años"},
        ],
    }
    regiones = {"label": "Region", "slug": "region", "options": []}
    current_year = datetime.datetime.now().year

    fechas_cargues = VariablesClinicas.objects.dates("fecha_cargue", "year").reverse()

    return [
        {
            "label": "Año",
            "slug": "year",
            "options": [
                {
                    "meses": [
                        {"label": meses[mes.month], "value": mes.month}
                        for mes in VariablesClinicas.objects.filter(
                            fecha_cargue__year=date.year
                        ).dates("fecha_cargue", "month")
                    ],
                    "label": f"{date.year}",
                    "value": f"{date.year}",
                }
                for date in fechas_cargues[:5]
            ],
        },
        {"label": "Mes", "slug": "mes", "options": []},
    ]


def add_years(date: Union[datetime.datetime, datetime.date], years: int):
    try:
        return date.replace(year=date.year + years)
    except ValueError:
        # 29 de febrero
        return date.replace(year=date.year + years, month=2, day=28)


def calcular_riesgo_cardiovascular(
    genero: str, edad: int, colesterol: float, tas: float, diabetes: bool, fumador: bool
):
    print(fumador)
    if(genero == "No se cargo género" or colesterol == 0 or tas == 0):
        return 0
    else :
        try:
            hdl = 45

            factores_edad = {
                Paciente.GENERO_MASCULINO: 3.06117,
                Paciente.GENERO_FEMENINO: 2.32888,
            }
            factores_colesterol = {
                Paciente.GENERO_MASCULINO: 1.1237,
                Paciente.GENERO_FEMENINO: 1.20904,
            }
            factores_hdl = {
                Paciente.GENERO_MASCULINO: -0.93263,
                Paciente.GENERO_FEMENINO: -0.70833,
            }
            factores_tas = {
                Paciente.GENERO_MASCULINO: 1.93303,
                Paciente.GENERO_FEMENINO: 2.76157,
            }
            factores_tabaquismo = {
                Paciente.GENERO_MASCULINO: 0.65451,
                Paciente.GENERO_FEMENINO: 0.52873,
            }
            factores_diabetes = {
                Paciente.GENERO_MASCULINO: 0.57367,
                Paciente.GENERO_FEMENINO: 0.69154,
            }

            bool_mapper = {True: 1, False: 0}

            factor1 = {
                Paciente.GENERO_MASCULINO: 23.9802,
                Paciente.GENERO_FEMENINO: 26.1931,
            }

            factor2 = {
                Paciente.GENERO_MASCULINO: 0.88936,
                Paciente.GENERO_FEMENINO: 0.95012,
            }

            factor_colombia = 0.75

            valor_edad = math.log(edad) * factores_edad[genero]
            valor_colesterol = math.log(colesterol) * factores_colesterol[genero]
            valor_hdl = math.log(hdl) * factores_hdl[genero]
            valor_tas = math.log(tas) * factores_tas[genero]
            valor_tabaquismo = factores_tabaquismo[genero] * bool_mapper[fumador]
            valor_diabetes = factores_diabetes[genero] * bool_mapper[diabetes]

            sum_valores = (
                valor_edad
                + valor_colesterol
                + valor_hdl
                + valor_tas
                + valor_tabaquismo
                + valor_diabetes
            )

            parcial = math.exp(sum_valores - factor1[genero])
            response = 1 - pow(factor2[genero], parcial)

            return response * factor_colombia
        
        except:
            return 0


def calcular_tfg(genero: str, edad: int, peso: float, creatinina: float):
    try:
        factor_genero = {Paciente.GENERO_MASCULINO: 1, Paciente.GENERO_FEMENINO: 0.85}
        numerador = (140 - edad) * peso
        denominador = 72 * creatinina
        return round(factor_genero[genero] * (numerador / denominador))
    except:
        return 0


def get_pacientes_usuario(user: User, base_qs=None):
    if user.is_authenticated:
        app_user: Usuario = Usuario.objects.filter(fk_user_django=user).first()
        if app_user:
            if base_qs is None:
                base_qs = Paciente.objects.all()
            if app_user.todos_grupos_gestion:
                return base_qs
            else:
                ids_grupos_gestion = app_user.grupos_gestion.values_list(
                    "id", flat=True
                )
                return base_qs.filter(
                    grupo_gestion_id__in=ids_grupos_gestion
                ).distinct()

    return Paciente.objects.none()


def get_pacientes_grupo_gestion(g: GrupoGestion):
    if g:
        return Paciente.objects.filter(grupo_gestion=g)
    else:
        return Paciente.objects.all()


def get_grupos_gestion_usuario(user: User):
    app_user: Usuario = Usuario.objects.filter(fk_user_django=user).first()
    if app_user:
        if app_user.todos_grupos_gestion:
            return GrupoGestion.objects.all()
        else:
            return app_user.grupos_gestion.all()

    return GrupoGestion.objects.none()


def get_users(request):
    current = int(request.GET.get("page", "1"))
    page_size = int(request.GET.get("size", "25"))

    app_user: Usuario = Usuario.objects.filter(fk_user_django=request.user).first()
    if app_user:
        if app_user.todos_grupos_gestion:
            users = Usuario.objects.all()
        else:
            grupos_gestion_usuario = get_grupos_gestion_usuario(request.user)
            users = Usuario.objects.filter(
                grupos_gestion__in=grupos_gestion_usuario.values_list("id", flat=True)
            )

        if request.GET.get("term"):
            users = users.filter(
                fk_user_django__username__icontains=request.GET.get("term")
            )
        if request.GET.get("grupos_gestion"):
            users = users.filter(grupos_gestion__in=[request.GET.get("grupos_gestion")])
        if request.GET.get("ciudad"):
            users = users.filter(
                grupos_gestion__ciudades__id=int(request.GET.get("ciudad"))
            )
        if request.GET.get("todos_grupos_gestion"):
            users = users.filter(
                todos_grupos_gestion=request.GET.get("todos_grupos_gestion") == "True"
            )
        if request.GET.get("order_by"):
            order_by_slug = request.GET.get("order_by")
            order_by = None
            if order_by_slug == "grupos_gestion":
                order_by = "grupos_gestion"
            if order_by_slug == "mail":
                order_by = "fk_user_django__email"
            if order_by_slug == "name":
                order_by = "fk_user_django__username"
            if order_by:
                ord_dir = request.GET.get("order_dir")
                users = users.order_by(f"{'-' if ord_dir == 'd' else ''}{order_by}")

        users = users.annotate(
            slug=F("id"),
            name=F("fk_user_django__username"),
            mail=F("fk_user_django__email"),
        )
        paginator = Paginator(users, page_size)
        items = []
        pages = paginator.num_pages
        total = paginator.count
        for item in paginator.page(current).object_list:
            if item.todos_grupos_gestion:
                grupos_gestion = []
            else:
                grupos_gestion = list(
                    item.grupos_gestion.all()
                    .annotate(slug=F("id"), label=F("nombre"))
                    .values("slug", "label")
                )
            items.append(
                {
                    "id": item.id,
                    "slug": item.slug,
                    "name": item.name,
                    "todos_grupos_gestion": "Sí" if item.todos_grupos_gestion else "No",
                    "grupos_gestion": grupos_gestion
                    or [{"slug": "N/A", "label": "N/A"}],
                    "mail": item.mail or "N/A",
                    "actions": [{"icon": "chevron_right", "slug": "edit"}],
                }
            )
        return items, pages, total
    else:
        return [], 0, 0


def get_excel_response(df: DataFrame, filename: str, sheet_name: str):
    vfile = BytesIO()
    xlwriter = pd.ExcelWriter(
        vfile,
        engine="xlsxwriter",
        datetime_format="yyyy-mm-dd",
        date_format="yyyy-mm-dd",
    )
    df.to_excel(xlwriter, sheet_name, index=False)
    xlwriter.save()
    vfile.seek(0)

    response = HttpResponse(
        vfile.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


annotate_last_hba1c = {
    "last_register_hba1c": Subquery(
        ExamenPaciente.objects.filter(
            fk_paciente_id=OuterRef("id"),
        )
        .order_by("-fecha")
        .values("hemoglobina_glicosilada")[:1]
    )
}

annotate_last_ldl = {
    "last_register_ldl": Subquery(
        ExamenPaciente.objects.filter(
            fk_paciente_id=OuterRef("id"),
        )
        .order_by("-fecha")
        .values("ldl")[:1]
    )
}


def get_patients_filters():
    cities = (
        Ciudad.objects.all()
        .annotate(slug=F("id"), value=F("id"), label=F("nombre"))
        .values("slug", "value", "label")
    )

    filters = [
        {
            "slug": "diagnostico",
            "label": "Diagnóstico",
            "options": Paciente.get_tipos_diabetes()
            + [{"label": "Diagnostico diabetes (I, II y otros)", "value": "todos"}],
        },
        {"slug": "ciudad", "label": "Ciudad", "options": list(cities)},
        {
            "slug": "riesgo_rcv",
            "label": "Riesgo RCV",
            "options": Paciente.get_niveles_riesgo_rcv(),
        },
        {
            "slug": "riesgo_tfg",
            "label": "Riesgo TFG",
            "options": Paciente.get_estadios_erc_2(),
        },
        {
            "slug": "imc",
            "label": "IMC",
            "options": [
                {"label": "Normal", "value": "normal"},
                {"label": "Sobrepeso", "value": "sobrepeso"},
                {"label": "Obesidad 1", "value": "obesidad_1"},
                {"label": "Obesidad 2", "value": "obesidad_2"},
                {"label": "Obesidad 3", "value": "obesidad_3"},
            ],
        },
        {
            "slug": "hta",
            "label": "HTA",
            "options": [
                {"label": "Sí", "value": True},
                {"label": "No", "value": False},
            ],
        },
        {
            "slug": "erc",
            "label": "ERC",
            "options": [
                {"label": "Sí", "value": True},
                {"label": "No", "value": False},
            ],
        },
        {
            "slug": "hba1c",
            "label": "Hemoglobina glicosilada",
            "options": [
                {"label": "Sin registro", "value": "no-registro"},
                {"label": "HbA1c < 7", "value": "lt-7"},
                {"label": "HbA1c > 6.5 <= 7", "value": "65-gte-7"},
                {"label": "HbA1c > 7", "value": "gte-7"},
            ],
        },
        {
            "slug": "hipoglicemia",
            "label": "Hipoglicemia",
            "options": [
                {"label": "Si", "value": "true"},
                {"label": "No", "value": "false"},
            ],
        },
    ]

    return {
        "filters": filters,
        "cities": list(cities),
        "riesgos_rcv": Paciente.get_niveles_riesgo_rcv(),
        "riesgos_tfg": Paciente.get_estadios_erc_2(),
        "diagnoses": Paciente.get_tipos_diabetes(),
    }


def annotate_imc(queryset):
    return (
        queryset.annotate(
            fix_estatura=Case(
                When(estatura__lte=0, then=Value(1)), default=F("estatura")
            )
        )
        .annotate(mts=F("fix_estatura") / Value(100))
        .annotate(imc=F("peso") / (F("mts") * F("mts")))
    )


def apply_patient_filters(request, queryset):
    if request.GET.get("term"):
        term = request.GET.get("term")
        queryset = queryset.filter(
            Q(nombres__icontains=term)
            | Q(apellidos__icontains=term)
            | Q(numero_documento__icontains=term)
        )
    if request.GET.get("ciudad"):
        queryset = queryset.filter(ciudad_asignacion_id=request.GET.get("ciudad"))
    if request.GET.get("diagnostico"):
        if request.GET["diagnostico"] == "todos":
            queryset = queryset.exclude(
                Q(tipo_diabetes=Paciente.TIPO_DIABETES_SIN_CLASIFICACION)
                | Q(tipo_diabetes__isnull=True)
            )
        else:
            queryset = queryset.filter(tipo_diabetes=request.GET.get("diagnostico"))
    if request.GET.get("riesgo_rcv"):
        queryset = queryset.filter(nivel_riesgo_rcv=request.GET.get("riesgo_rcv"))
    if request.GET.get("riesgo_tfg"):
        queryset = queryset.filter(estadio_erc=request.GET.get("riesgo_tfg"))
    if request.GET.get("imc"):
        queryset = annotate_imc(queryset)
        filter_value = request.GET.get("imc")
        if filter_value == "desnutricion":
            queryset = queryset.filter(imc__lt=20)
        elif filter_value == "normal":
            queryset = queryset.filter(imc__gte=18.5, imc__lt=25)
        elif filter_value == "sobrepeso":
            queryset = queryset.filter(imc__gte=25, imc__lt=30)
        elif filter_value == "obesidad_1":
            queryset = queryset.filter(imc__gte=30, imc__lt=34.9)
        elif filter_value == "obesidad_2":
            queryset = queryset.filter(imc__gte=35, imc__lt=39.9)
        elif filter_value == "obesidad_3":
            queryset = queryset.filter(imc__gte=40)
    if request.GET.get("hta"):
        queryset = queryset.filter(diagnostico_hta=request.GET.get("hta") == "true")
    if request.GET.get("erc"):
        queryset = queryset.filter(diagnostico_erc=request.GET.get("erc") == "true")
    if request.GET.get("ultima_visita"):
        _now = now()
        one_month = _now - relativedelta(months=1)
        six_months = _now - relativedelta(months=6)
        twelve_months = _now - relativedelta(months=12)
        filter_value = request.GET.get("ultima_visita")

        if filter_value == "menos_1_mes":
            queryset = queryset.filter(ultimo_seguimiento__gt=one_month)
        elif filter_value == "1_6_meses":
            queryset = queryset.filter(
                ultimo_seguimiento__lte=one_month, ultimo_seguimiento__gt=six_months
            )
        elif filter_value == "6_12_meses":
            queryset = queryset.filter(
                ultimo_seguimiento__lte=six_months, ultimo_seguimiento__gt=twelve_months
            )
        elif filter_value == "mas_12_meses":
            queryset = queryset.filter(ultimo_seguimiento__lt=twelve_months)
    if request.GET.get("hba1c"):
        hba1c = request.GET["hba1c"]
        if hba1c == "no-registro":
            queryset = queryset.filter(Q(hba1c=0) | Q(hba1c__isnull=True))
        else:
            queryset = queryset.exclude(Q(hba1c=0) | Q(hba1c__isnull=True))
        if hba1c == "lt-7":
            queryset = queryset.filter(hba1c__lt=7)
        elif hba1c == "65-gte-7":
            queryset = queryset.filter(hba1c__gt=6.5, hba1c__lte=7)
        elif hba1c == "gte-7":
            queryset = queryset.filter(hba1c__gt=7)
    if request.GET.get("hipoglicemia"):
        queryset = queryset.filter(
            diagnostico_hipoglicemia=request.GET["hipoglicemia"] == "true"
        )
    return queryset


def get_m2m_checkboxes(all_qs, patient_qs):
    dict_list = []
    for obj in all_qs:
        dict_list.append(
            {
                "label": obj.nombre,
                "slug": obj.id,
                "value": patient_qs.filter(id=obj.id).exists(),
            }
        )
    return dict_list


def load_indicadores(**kwargs):
    import importlib

    tipo = kwargs.get("tipo")
    ind_module = importlib.import_module(settings.INDICADORES_MODULE)
    indicadores = []
    for name in settings.INDICADORES:
        try:
            cls = getattr(ind_module, name)
            instance = cls()
            if tipo:
                if instance.tipo == tipo:
                    indicadores.append(instance)
            else:
                indicadores.append(instance)
        except AttributeError:
            pass
    return settings.INDICADORES_TITLE, indicadores


def load_custom_indicadores(**kwargs):
    import importlib

    tipo = kwargs.get("tipo")
    ind_module = importlib.import_module(settings.INDICADORES_MODULE)
    indicadores = []
    for name in settings.INDICADORES_CUSTOM:
        try:
            cls = getattr(ind_module, name)
            instance = cls()
            if tipo:
                if instance.tipo == tipo:
                    indicadores.append(instance)
            else:
                indicadores.append(instance)
        except AttributeError:
            pass
    return settings.INDICADORES_CUSTOM_TITLE, indicadores


def get_indicador(**kwargs):
    import importlib

    tipo = kwargs.get("tipo")
    slug = kwargs.get("slug")
    ind_module = importlib.import_module(settings.INDICADORES_MODULE)
    indicador = None
    for name in settings.INDICADORES:
        try:
            cls = getattr(ind_module, name)
            instance = cls()
            if tipo == instance.slug_tipo and slug == instance.slug:
                indicador = instance
                break
        except AttributeError:
            pass
    return indicador


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


def get_dummy_df():
    import os
    from glucoinsights.settings import BASE_DIR

    xlsx_path = os.path.join(BASE_DIR, "gi", "views", "variables-clinicas.xlsx")
    df = pd.read_excel(
        xlsx_path,
        dtype={
            "nombres": str,
            "apellidos": str,
            "tipo_documento": str,
            "numero_documento": str,
            "genero": str,
            "colesterol_total": float,
            "hdl": float,
            "tas": int,
            "tad": int,
            "es_fumador": bool,
            "estatura": float,
            "peso": float,
            "IMC": float,
            "hba1c": float,
            "ldl": float,
            "albuminura": float,
            "creatinina": float,
            "Fecha": "datetime64[ns]",
            "tfg": float,
        },
    )
    dates = list(df.Fecha.unique())
    dates.sort()
    return df[df["Fecha"] == dates[-1]], df
