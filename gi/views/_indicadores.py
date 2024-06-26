import logging
from datetime import datetime
from typing import Tuple

import numpy as np
from dateutil.relativedelta import relativedelta
from django.db.models import F, QuerySet
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.vary import vary_on_headers
from pandas import DataFrame

from gi.indicadores.dm import get_dm_dict
from gi.indicadores.erc import get_erc_dict
from gi.indicadores.hta import get_hta_dict
from gi.indicadores.otros import get_otros_dict
from gi.models import Indicador, Paciente, GrupoEtareo, Ciudad, VariablesClinicas
from gi.utils import (
    get_indicadores_filtros,
    add_years,
    get_pacientes_usuario,
    load_indicadores,
    get_indicador,
    load_custom_indicadores,
    last_day_of_month,
)
from gi_indicadores.indicador import AbstractIndicador
from ._base import AuthenticatedView
from ._seguimiento import get_pacientes

logger = logging.getLogger(__name__)


def _filter_patients(request):
    pacientes = get_pacientes_usuario(request.user)

    if request.GET.get("grupo-etareo"):
        pacientes = GrupoEtareo.objects.get(
            id=request.GET["grupo-etareo"]
        ).get_pacientes(request.user)
    if request.GET.get("tiempo-afiliacion"):
        current_time = datetime.now()
        if request.GET["tiempo-afiliacion"] == "menos-1-año":
            pacientes = pacientes.filter(
                fecha_afiliacion__gte=add_years(current_time, -1)
            )
        elif request.GET["tiempo-afiliacion"] == "1-y-2-años":
            pacientes = pacientes.filter(
                fecha_afiliacion__gte=add_years(current_time, -2)
            )
        elif request.GET["tiempo-afiliacion"] == "2-y-3-años":
            pacientes = pacientes.filter(
                fecha_afiliacion__gte=add_years(current_time, -3)
            )
        elif request.GET["tiempo-afiliacion"] == "3-y-5-años":
            pacientes = pacientes.filter(
                fecha_afiliacion__gte=add_years(current_time, -5)
            )
        elif request.GET["tiempo-afiliacion"] == "mas-5-años":
            pacientes = pacientes.filter(
                fecha_afiliacion__lte=add_years(current_time, -5)
            )

    if request.GET.get("mes"):
        # TODO qué se debería filtrar por mes.
        pass
    return pacientes


def parse_patients(patients) -> DataFrame:
    data = list(
        patients.annotate(
            nombres=F("fk_paciente__nombres"),
            apellidos=F("fk_paciente__apellidos"),
            tipo_documento=F("fk_paciente__tipo_documento"),
            numero_documento=F("fk_paciente__numero_documento"),
            genero=F("fk_paciente__genero"),
            es_fumador=F("fk_paciente__es_fumador"),
            albuminuria=F("microalbuminuria"),
            Fecha=F("fecha_cargue"),
        ).values(
            "nombres",
            "apellidos",
            "tipo_documento",
            "numero_documento",
            "genero",
            "colesterol_total",
            "hdl",
            "tas",
            "tad",
            "es_fumador",
            "estatura",
            "peso",
            "hba1c",
            "ldl",
            "albuminuria",
            "creatinina",
            "tfg",
            "Fecha",
        )
    )
    df = DataFrame(data)
    if not df.empty:
        df = df.astype(
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
                "hba1c": float,
                "ldl": float,
                "albuminuria": float,
                "creatinina": float,
                "Fecha": "datetime64[ns]",
                "tfg": float,
            }
        )
        numeric_columns = [
            "colesterol_total",
            "hdl",
            "tas",
            "tad",
            "estatura",
            "peso",
            "hba1c",
            "ldl",
            "albuminuria",
            "creatinina",
            "tfg",
        ]
        for col in numeric_columns:
            df[col].fillna(0, inplace=True)
        df["IMC"] = np.where(
            (df["estatura"] > 0) & (df["peso"] > 0), df["peso"] / df["estatura"] ** 2, 0
        )
    return df


class _AbstractIndicadoresView(AuthenticatedView):
    title = ""
    active_tab = ""
    tipo_indicador = ""

    @classmethod
    def get_patients(cls, request, offset: int = 11, historic=True) -> DataFrame:
        patients = VariablesClinicas.objects.all()

        newest_date = get_indicadores_filtros()
        years_options = newest_date[0]["options"][0]
        year = int(years_options["value"])
        month = int(years_options["meses"][0]["value"])

        if request.GET.get("mes") and request.GET.get("year") and not historic:
            year = request.GET.get("year")
            month = request.GET.get("mes")

        base_date = datetime.strptime(f"{year}-{month}", "%Y-%m")
        upper_date = last_day_of_month(base_date)
        lower_date = base_date + relativedelta(months=-1 * offset)
        patients = VariablesClinicas.objects.filter(
            fecha_cargue__gte=lower_date, fecha_cargue__lte=upper_date
        )
        return parse_patients(patients)

    @vary_on_headers("Content-Type")
    def get(self, request):
        # patients = self.get_patients(request=request, historic=False)
        patients = None
        base = load_indicadores(tipo=self.tipo_indicador)
        base_custom = load_custom_indicadores(tipo=self.tipo_indicador)

        def get_group(title, indicators):
            data = []
            for ind in indicators:
                d = ind.get_summary(df=patients, calc=False)
                data.append(d)
                if d.get("tipo", {}).get("slug", None) and d.get("slug"):
                    d["route"] = reverse(
                        "gi:detalle-indicador",
                        kwargs={
                            "tipo_indicador": d.get("tipo", {}).get("slug"),
                            "id_indicador": d.get("slug"),
                        },
                    )
            return {"title": title, "data": data}

        groups = [
            get_group(title=base[0], indicators=base[1]),
            get_group(title=base_custom[0], indicators=base_custom[1]),
        ]

        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse(
                {"filters": get_indicadores_filtros(year=request.GET.get("year"))}
            )
        return render(
            request,
            "gi/views/indicadores/indicadores-category.html",
            {
                "title": self.title,
                "aside": "indicadores",
                "active": self.active_tab,
                "groups": groups,
                "filters": get_indicadores_filtros(year=request.GET.get("year")),
            },
        )


class IndicadoresHtaView(_AbstractIndicadoresView):
    title = "Indicadores HTA"
    active_tab = "indicadores-hta"
    tipo_indicador = Indicador.TIPO_INDICADOR_HTA


class IndicadoresDmView(_AbstractIndicadoresView):
    title = "Indicadores DM"
    active_tab = "indicadores-dm"
    tipo_indicador = Indicador.TIPO_INDICADOR_DM


class IndicadoresErcView(_AbstractIndicadoresView):
    title = "Indicadores ERC"
    active_tab = "indicadores-erc"
    tipo_indicador = Indicador.TIPO_INDICADOR_ERC


class OtrosIndicadoresView(_AbstractIndicadoresView):
    title = "Indicadores Otros"
    active_tab = "indicadores-otros"
    tipo_indicador = Indicador.TIPO_INDICADOR_OTROS


class CalcIndicadorView(_AbstractIndicadoresView):
    def get(self, request, **kwargs):
        tipo_indicador: str = kwargs.get("tipo_indicador")
        id_indicador: str = kwargs.get("id_indicador")
        indicador: AbstractIndicador = get_indicador(
            slug=id_indicador, tipo=tipo_indicador
        )
        if indicador:
            patients = self.get_patients(request, historic=False)
            d = indicador.get_summary(df=patients)
            if d.get("tipo", {}).get("slug", None) and d.get("slug"):
                d["route"] = reverse(
                    "gi:detalle-indicador",
                    kwargs={
                        "tipo_indicador": d.get("tipo", {}).get("slug"),
                        "id_indicador": d.get("slug"),
                    },
                )
            return JsonResponse({"indicador": d}, status=200)
        else:
            return JsonResponse({}, status=404)


class DetalleIndicadorView(AuthenticatedView):
    def filter_patients(
        self, request
    ) -> Tuple[QuerySet[VariablesClinicas], QuerySet[VariablesClinicas]]:
        class_AbstractIndicadoresView = _AbstractIndicadoresView()
        historic = class_AbstractIndicadoresView.get_patients(
            request=request, offset=22, historic=True
        )
        current = class_AbstractIndicadoresView.get_patients(
            request=request, offset=11, historic=False
        )
        return current, historic

    def get(self, request, tipo_indicador: str, id_indicador: str):
        indicador: AbstractIndicador = get_indicador(
            slug=id_indicador, tipo=tipo_indicador
        )
        if not indicador:
            return redirect("gi:indicadores-poblacional")

        """
            df_current, df_total = get_dummy_df()
            data = indicador.get_data(df=df_current)
            labels, values = indicador.get_historic(df=df_total)
        """

        current, historic = self.filter_patients(request)
        data = indicador.get_data(df=current)
        data[0]["route"] = reverse(
            "gi:detalle-indicador",
            kwargs={
                "tipo_indicador": data[0].get("slug_tipo"),
                "id_indicador": data[0].get("slug"),
            },
        )

        labels, values = indicador.get_historic(df=historic)

        # TODO Filtrar los pacientes por las cedulas de pacientes que estan por fuera del indicador, estas cedulas las entrega el calculo del indicador.
        newest_date = get_indicadores_filtros()
        years_options = newest_date[0]["options"][0]
        year = int(years_options["value"])
        month = int(years_options["meses"][0]["value"])

        year = request.GET.get("year", year)
        month = request.GET.get("mes", month)

        list_documents = indicador.get_pacientes_interes(
            df=historic, year=year, month=month
        )

        pacientes_fuera_del_indicador = Paciente.objects.filter(
            numero_documento__in=list_documents
        )

        # pacientes_fuera_del_indicador = Paciente.objects.all()

        patients, total_pacientes, num_pages = get_pacientes(
            request=request, pacientes_qs=pacientes_fuera_del_indicador
        )
        # patients = [0]
        groups = [{"data": data}]
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse(
                {
                    "data": data,
                    "patients": patients,
                    "groups": groups,
                    "pages": num_pages,
                    "total": total_pacientes,
                    "filters": get_indicadores_filtros(year=request.GET.get("year")),
                }
            )
        cities = (
            Ciudad.objects.all()
            .annotate(slug=F("id"), value=F("id"), label=F("nombre"))
            .values("slug", "value", "label")
        )
        return render(
            request,
            "gi/views/indicadores/detalle-indicador.html",
            {
                "backlink": reverse(f"gi:indicadores-{tipo_indicador.lower()}"),
                "title": indicador.name,
                "aside": "indicadores",
                "filters": get_indicadores_filtros(year=request.GET.get("year")),
                "data": data,
                "groups": groups,
                "patients": patients,
                "pages": num_pages,
                "total": total_pacientes,
                "cities": list(cities),
                "riesgos_rcv": Paciente.get_niveles_riesgo_rcv(),
                "riesgos_tfg": Paciente.get_estadios_erc_2(),
                "diagnoses": Paciente.get_tipos_diabetes(),
                "months": labels,
                "historic": values,
            },
        )


def _get_indicadores_type(tipo_indicador, pacientes, user):
    indicador_data = {}
    if tipo_indicador == Indicador.TIPO_INDICADOR_HTA:
        indicador_data = get_hta_dict(user, pacientes)
    elif tipo_indicador == Indicador.TIPO_INDICADOR_DM:
        indicador_data = get_dm_dict(user, pacientes)
    elif tipo_indicador == Indicador.TIPO_INDICADOR_ERC:
        indicador_data = get_erc_dict(user, pacientes)
    elif tipo_indicador == Indicador.TIPO_INDICADOR_OTROS:
        indicador_data = get_otros_dict(user, pacientes)
    return indicador_data
