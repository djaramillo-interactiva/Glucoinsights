import json
import datetime
import os

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F
from django.http import HttpResponseNotFound, JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone

import pandas as pd
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers

from gi.carga_excel import CargaPacienteDto, dto_mapper
from gi.utils import get_pacientes_usuario, get_excel_response, apply_patient_filters
from ._base import AuthenticatedView
from ..constants import MONTHS
from ..models import CargueBackOffice, VariablesClinicas

from gi.carga_excel._add_error import errores
from gi.carga_excel._pacientes import Logs_cargue

from django.conf import settings



@method_decorator(vary_on_headers("Content-Type"), name="dispatch")
class RegistrosView(AuthenticatedView):
    def get(self, request, slug=None):
        settings.USER_LOGGIN = request.user.id
        print(settings.USER_LOGGIN)
        today = datetime.date.today()
        year = today.year
        if not slug:
            return redirect(reverse("gi:registros", kwargs={"slug": "pacientes"}))

        months = [{"value": i + 1, "label": m} for i, m in enumerate(MONTHS)]
        years = [{"value": year - i, "label": year - i} for i in range(50)]

        descargar_excel_url = reverse('gi:descargar_excel')

        qs = CargueBackOffice.objects.filter(data_type=slug).order_by("-id")
        paginator = Paginator(qs, 20)
        page = request.GET.get("page", "1")
        data = [
            {
                "slug": item.id,
                "id": item.id,
                "month": MONTHS[item.month - 1],
                "date": {"label": item.upload_date.strftime("%Y/%m/%d")},
                "observations": item.observations,
                "user": item.user.username if item.user else " - ",
                "file": [
                    {
                        "icon": "file_download",
                        "iconStyle": "outlined",
                        "route": item.excel_file.url,
                    }
                ],
            }
            for item in paginator.get_page(int(page))
        ]
 
        return render(
            request,
            "gi/views/registros/index.html",
            {
                "title": "Registros de paciente",
                "errores": errores,
                "descargar_excel_url": descargar_excel_url,
                "aside": "registros",
                "months": months,
                "years": years,
                "active": slug,
                "data": data,
                "columns": get_columns(slug),
                "template_url": get_url_plantilla(slug),
                "nav": [
                    {
                        "label": "PACIENTES",
                        "route": reverse("gi:registros", kwargs={"slug": "pacientes"}),
                        "slug": "pacientes",
                    },
                    # {
                    #     "label": "CONTROLES",
                    #     "route": reverse("gi:registros", kwargs={"slug": "controles"}),
                    #     "slug": "controles",
                    # },
                    # {
                    #     "label": "HOSPITALIZACIONES",
                    #     "route": reverse(
                    #         "gi:registros", kwargs={"slug": "hospitalizaciones"}
                    #     ),
                    #     "slug": "hospitalizaciones",
                    # },
                    # {
                    #     "label": "EXÁMENES",
                    #     "route": reverse("gi:registros", kwargs={"slug": "examenes"}),
                    #     "slug": "examenes",
                    # },
                ],
            },
        )

    def post(self, request, slug=None):
        if not slug:
            return JsonResponse({"message": "Solicitud no válida"}, status=400)
        file = request.FILES.get("file")
        cbo = CargueBackOffice(
            data_type=slug,
            excel_file=file,
            month=request.POST.get("month"),
            year=request.POST.get("year"),
            observations=request.POST.get("observations"),
            user=request.user,
        )
        cbo.save()

        return JsonResponse({"message": "Cargado excel correctamente."})

    def delete(self, request, slug):
        if not slug:
            return JsonResponse({"message": "Solicitud no válida"}, status=400)
        body = json.loads(request.body.decode("utf-8"))
        to_delete = CargueBackOffice.objects.filter(id__in=body["data"])
        counter = 0
        for cbo in to_delete:
            cbo.delete_related()
            cbo.delete()
            counter += 1
        msg = (
            "1 registro eliminado"
            if counter == 1
            else f"{counter} registros eliminados"
        )
        return JsonResponse({"message": msg})


class CargarArchivoPacientesView(AuthenticatedView):
    def get(self, request):
        data = CargaPacienteDto.get_fields_dict()

        df = pd.DataFrame(data, index=[0])
        response = get_excel_response(
            df=df, filename="plantilla-pacientes.xlsx", sheet_name="PACIENTES"
        )
        return response

    def post(self, request):
        file = request.FILES.get("archivo-pacientes")
        if file:
            df = pd.read_excel(file)
            carga = CargaPacienteDto(df)
            carga.save_patients()

            messages.add_message(
                request,
                messages.SUCCESS,
                f"El archivo de pacientes se cargó correctamente",
            )
        return redirect("gi:registros")


class DescargarBaseDeDatosView(AuthenticatedView):
    # noinspection DuplicatedCode
    def get(self, request):
        queryset = get_pacientes_usuario(request.user)
        queryset = apply_patient_filters(request, queryset)

        if request.GET.get("filename"):
            filename = request.GET.get("filename")
        else:
            filename = "base-de-datos-pacientes"

        today = timezone.now()
        df = pd.DataFrame(CargaPacienteDto.get_dto_qs(qs=queryset))

        response = get_excel_response(
            df=df,
            filename=f'{filename}-{today.strftime("%Y-%m-%d")}.xlsx',
            sheet_name="PACIENTES",
        )
        return response


class CargaRegistrosView(AuthenticatedView):
    def get(self, request, model: str):
        filename = f"plantilla-{model}.xlsx"
        dto_model = dto_mapper[model]
        if request.GET.get("db"):
            filename = f"base-de-datos-{model}.xlsx"
            df = pd.DataFrame(
                dto_model.model.objects.annotate(
                    paciente=F("fk_paciente__numero_documento")
                ).values(*dto_model.get_fields_dict())
            )
        else:
            df = pd.DataFrame(dto_model.get_fields_dict(), index=[0])
        response = get_excel_response(df=df, filename=filename, sheet_name="REGISTROS")
        return response

    def post(self, request, model: str):
        dto_model = dto_mapper[model]
        file = request.FILES.get("archivo-pacientes")
        if file:
            df = pd.read_excel(file)
            carga = dto_model(df)
            total, errors = carga.save_registros()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Se han guardado {total} registros. Ocurrieron {errors} errores",
            )
        return redirect("gi:registros")


def get_columns(slug: str):
    if slug == "pacientes":
        return [
            {
                "slug": "id",
                "label": "",
                "type": "checkbox",
                "width": "max-content",
                "order": True,
            },
            {
                "slug": "month",
                "label": "Periodo",
                "class": "",
                "type": "text",
                "order": True,
            },
            {
                "slug": "date",
                "label": "Fecha de carga",
                "class": "",
                "type": "tag",
                "order": True,
            },
            {
                "slug": "observations",
                "label": "Observaciones",
                "class": "",
                "type": "text",
                "order": True,
            },
            {
                "slug": "user",
                "label": "Usuario",
                "class": "",
                "type": "text",
                "order": True,
            },
            {
                "slug": "file",
                "label": "Descargar",
                "class": "",
                "type": "actions",
                "order": False,
            },
        ]
    else:
        return [
            {
                "slug": "id",
                "label": "",
                "type": "checkbox",
                "width": "max-content",
                "order": True,
            },
            {
                "slug": "date",
                "label": "Fecha de carga",
                "class": "",
                "type": "tag",
                "order": True,
            },
            {
                "slug": "observations",
                "label": "Observaciones",
                "class": "",
                "type": "text",
                "order": True,
            },
            {
                "slug": "user",
                "label": "Usuario",
                "class": "",
                "type": "text",
                "order": True,
            },
            {
                "slug": "file",
                "label": "Descargar",
                "class": "",
                "type": "actions",
                "order": False,
            },
        ]


def get_url_plantilla(slug):
    print(slug)
    if slug == "pacientes":
        return "plantilla_pacientes_vp1.xlsx"
    if slug == "controles":
        return "plantilla_controles_vp1.xlsx"
    if slug == "hospitalizaciones":
        return "plantilla_hospitalizaciones_vp1.xlsx"
    if slug == "examenes":
        return "plantilla_examenes_vp1.xlsx"
    else:
        return reverse("gi:cargar-registros", kwargs={"model": slug})



class DownloadExcelView(AuthenticatedView):
    def get(self, request):
        # Obtén la ruta absoluta del archivo
        file_path = os.path.join(settings.MEDIA_ROOT, 'cargues', 'reporte.xlsx')
        # Asegúrate de que el archivo exista antes de intentar enviarlo
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/vnd.ms-excel')
        else:
            return HttpResponseNotFound('Archivo no encontrado')