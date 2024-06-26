from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.vary import vary_on_headers

from gi.utils import (
    get_pacientes_usuario,
    get_patients_filters,
    apply_patient_filters,
    get_months_filter,
)
from gi.models import GrupoPacientes, VariablesClinicas
from gi_dashboards import get_all_dashboards, get_dashboard_by_slug

from ._base import AuthenticatedView
from ._seguimiento import get_pacientes

import pandas as pd


class VariablasClinicasView(AuthenticatedView):
    @vary_on_headers("Content-Type")
    def get(self, request, slug_grupo=None):
        today = now()
        mes = int(request.GET.get("mes", "0")) or today.month
        anio = today.year
        g = None
        if slug_grupo:
            g = GrupoPacientes.objects.get(slug=slug_grupo)
            pacientes_grupo = g.pacientes.all()
            base_qs = get_pacientes_usuario(request.user, pacientes_grupo)
        else:
            base_qs = get_pacientes_usuario(request.user)
        base_qs = apply_patient_filters(request, queryset=base_qs)

        df = VariablesClinicas.objects.filter(
            fk_paciente_id__in=base_qs.values_list("id", flat=True),
            fecha_cargue__month=mes,
            fecha_cargue__year=anio,
        )

        base_qs_df = pd.DataFrame(df.values())
        data = get_all_dashboards(base_qs_df)
        # data = get_segmentacion_data(df) if df.count() > 0 else []

        filters = get_patients_filters()
        filters["filters"].insert(0, get_months_filter())

        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"data": data})

        return render(
            request,
            "gi/views/segmentacion/variables-clinicas.html",
            {
                "aside": "segmentacion",
                "title": "Segmentación"
                if not g
                else f"Grupo {g.nombre} - Segmentación",
                "grupo": g,
                "backlink": reverse("gi:segmentacion-grupos") if g else None,
                "data": data,
                **filters,
            },
        )


class SegmentacionGruposView(AuthenticatedView):
    def get(self, request):
        data = list(
            GrupoPacientes.objects.annotate(count=Count("pacientes")).values(
                "slug", "count", name=F("nombre")
            )
        )
        for d in data:
            d["route"] = reverse(
                "gi:dashboard-segmentacion-grupo", kwargs={"slug_grupo": d["slug"]}
            )

        return render(
            request,
            "gi/views/segmentacion/grupos.html",
            {
                "title": "Segmentación grupos de pacientes",
                "aside": "segmentacion",
                "data": data,
            },
        )


class DetallesVariable(AuthenticatedView):
    @vary_on_headers("Content-Type")
    def get(self, request, slug_grupo=None, slug=None):
        today = now()
        mes = int(request.GET.get("mes", "0")) or today.month
        anio = today.year

        # Condicional para filtrar pacientes segun un grupo usando el slug del grupo
        if slug_grupo:
            g = GrupoPacientes.objects.get(slug_grupo=slug_grupo)
            pacientes_grupo = g.pacientes.all()
            patients = get_pacientes_usuario(request.user, pacientes_grupo)

        # En el caso de que el request no tenga slug de grupo se arma la query para todos los pacientes a los que tiene acceso el usuario
        else:
            patients = get_pacientes_usuario(request.user)

        patients = apply_patient_filters(
            request, queryset=patients
        )  # Se aplican los filtos que se especifican en el request, como por ejemplo string en apellido nombre o numero de documento, ciudad entre otros

        base_qs = pd.DataFrame(
            VariablesClinicas.objects.filter(
                fk_paciente_id__in=patients.values_list("id", flat=True),
                fecha_cargue__month=mes,
                fecha_cargue__year=anio,
            ).values()
        )
        segment = get_dashboard_by_slug(slug, base_qs)
        segment_filters = [
            {"label": x, "value": i} for i, x in enumerate(segment.labels)
        ]

        chart_data = segment.get_chart_data
        segment_filter = (
            int(request.GET.get("segmento", segment_filters[0]["value"])) or 0
        )
        del chart_data["href"]

        p_qs = patients.filter(id__in=segment.get_patients(segment_filter))

        filters = get_patients_filters()
        filters["filters"].insert(0, get_months_filter())

        items, total, num_pages = get_pacientes(request, pacientes_qs=p_qs)

        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse(
                {
                    "data": items,
                    "pages": num_pages,
                    "total": total,
                    "chart_data": chart_data,
                }
            )

        return render(
            request,
            "gi/views/segmentacion/detalles-variable.html",
            {
                "backlink": reverse("gi:variables-clinicas"),
                "title": "Segmentación",
                "aside": "segmentacion",
                "chart_data": chart_data,
                "data": items,
                "pages": num_pages,
                "total": total,
                **filters,
                "segment_filters": segment_filters,
            },
        )
