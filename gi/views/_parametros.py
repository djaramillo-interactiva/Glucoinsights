import json

from django.db.models import Value, IntegerField
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.text import slugify

from gi.models import (
    GrupoEtareo,
    Indicador,
    Tarea,
    ServicioTarea,
    GrupoPacientes,
    Medicacion,
)
from ._base import DataView
from ..utils import load_indicadores

parametros_title = "Parámetros de la plataforma"


class GruposEtareosView(DataView):
    def get(self, request):
        dt = GrupoEtareo.objects.values("id", "nombre", "edad_inicio", "edad_fin")
        return render(
            request,
            "gi/views/parametros/grupos-etareos.html",
            {"data": list(dt), "title": parametros_title},
        )

    def post(self, request):
        grupos = self.data
        created = []
        updated = []
        deleted = []

        for grupo in grupos:
            if grupo.get("id"):
                g = GrupoEtareo.objects.get(id=grupo["id"])
                g.nombre = grupo["nombre"]
                g.edad_inicio = grupo["edad_inicio"]
                g.edad_fin = grupo["edad_fin"]
                g.save()
                updated.append(g.id)
            else:
                g = GrupoEtareo(**grupo)
                g.save()
                created.append(g.id)

        for grupo in GrupoEtareo.objects.exclude(id__in=created + updated):
            deleted.append(grupo.id)
            grupo.delete()

        dt = GrupoEtareo.objects.values("id", "nombre", "edad_inicio", "edad_fin")
        return JsonResponse({"data": list(dt)}, status=200)


class IndicadoresView(DataView):
    def get(self, request):
        # data = load_json('parametros.json')['indicadores']
        tipo_indicadores = Indicador.tipos_choices
        data = []

        for tipo_ind, tipo_label in tipo_indicadores:
            title_i, data_i = load_indicadores(tipo=tipo_ind)
            indicador_data = {"title": tipo_label, "indicadores": []}

            for data_class in data_i:
                indicador_obj, c = Indicador.objects.get_or_create(
                    tipo=tipo_ind,
                    slug=data_class.slug,
                    defaults={
                        "meta": 0,
                        "descripcion": data_class.description,
                        "nombre": data_class.name,
                    },
                )
                indicador_data["indicadores"].append(indicador_obj.to_dict)
            data.append(indicador_data)

        return render(
            request,
            "gi/views/parametros/indicadores.html",
            {"data": data, "title": parametros_title},
        )

    def post(self, request):
        if self.data.get("id"):
            return JsonResponse({}, status=400)
        i = Indicador(**self.data)
        i.save()
        return JsonResponse({"id": i.id})

    def put(self, request):
        for item in self.data:
            i = Indicador.objects.get(id=item.get("id"))
            i.tipo = item.get("tipo")
            i.nombre = item.get("nombre")
            i.descripcion = item.get("descripcion")
            i.meta = item.get("meta")
            i.save()
        return JsonResponse({})


class TareasView(DataView):
    def get(self, request):
        # Tarea.objects.get_or_create(nombre='Servicio / Intervención', order=99)

        data = self._get_data()
        return render(
            request,
            "gi/views/parametros/tareas.html",
            {
                "title": parametros_title,
                "data": data,
                "service_options": list(
                    map(
                        lambda x: {"value": x[0], "label": x[1]},
                        ServicioTarea.service_choices,
                    )
                ),
            },
        )

    def _get_data(self):
        return [x.to_dict for x in Tarea.objects.all()]

    def _save_services(self, t_json: dict, t: Tarea):
        services = t_json.get("data", [])
        visited = []

        for i, service in enumerate(services):
            if service.get("id"):
                s = ServicioTarea.objects.get(id=service.get("id"), fk_tarea=t)
                s.nombre = service.get("nombre")
                s.cantidad = service.get("cantidad")
            else:
                s = ServicioTarea(**service)
                s.order = i
                s.fk_tarea = t
            s.order = i
            s.save()
            visited.append(s.id)
        t.serviciotarea_set.exclude(id__in=visited).delete()

    def post(self, request):
        visited = []
        for index, t_json in enumerate(self.data):
            if t_json.get("id"):
                t = Tarea.objects.get(id=t_json["id"])
                t.nombre = t_json.get("nombre")
            else:
                t = Tarea(
                    nombre=t_json.get("nombre"), order=int(t_json.get("order", "0"))
                )
            t.save()
            visited.append(t.id)
            self._save_services(t_json, t)
        Tarea.objects.exclude(id__in=visited).delete()

        return JsonResponse({"data": self._get_data()})

    def put(self, request):
        try:
            t = Tarea.objects.get(id=self.data.get("id"))
            t.nombre = self.data.get("nombre")
            t.order = self.data.get("order")

            self._save_services(self.data, t)

            return JsonResponse({"id": t.id})
        except Tarea.DoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request):
        try:
            t = Tarea.objects.get(id=self.data.get("id"))
            t.delete()
            return JsonResponse({"id": t.id})
        except Tarea.DoesNotExist:
            return JsonResponse({}, status=404)


class GruposPacientesView(DataView):
    def get(self, request):
        tareas = [x.to_dict for x in Tarea.objects.all()]
        grupos = []

        for t in tareas:
            grupos.append(
                {
                    "label": t["nombre"],
                    "children": [
                        {"label": x["nombre"], "id": x["id"], "value": False}
                        for x in t["data"]
                    ],
                    "value": False,
                }
            )

        data = self._get_grupos_data()
        return render(
            request,
            "gi/views/parametros/grupos-pacientes.html",
            {"title": parametros_title, "data": data, "groups": json.dumps(grupos)},
        )

    def _get_grupos_data(self):
        data = list(
            GrupoPacientes.objects.annotate(
                total=Value(20, output_field=IntegerField())
            ).values("id", "nombre", "slug", "total")
        )
        for index, d in enumerate(data):
            st = (
                ServicioTarea.objects.filter(grupopacientes__id=d["id"])
                .distinct()
                .values_list("id", flat=True)
            )
            d["order"] = index
            d["servicios"] = list(st)
        return data

    def _save_related(self, g: GrupoPacientes):
        servicios_tarea = self.data.get("servicios", [])
        for servicio_tarea in servicios_tarea:
            g.servicios_tarea.add(ServicioTarea.objects.get(id=servicio_tarea))

    def post(self, request):
        g = GrupoPacientes(
            nombre=self.data.get("nombre"),
            order=int(self.data.get("order", "0")),
            slug=slugify(self.data.get("nombre")),
        )
        g.save()
        self._save_related(g)
        return JsonResponse({"data": self._get_grupos_data()})

    def put(self, request):
        try:
            g = GrupoPacientes.objects.get(id=self.data.get("id"))
            g.nombre = self.data.get("nombre")
            g.order = self.data.get("order")
            g.slug = slugify(g.nombre)
            g.servicios_tarea.clear()
            g.save()
            self._save_related(g)
            return JsonResponse({"data": self._get_grupos_data()})
        except GrupoPacientes.DoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request):
        try:
            g = GrupoPacientes.objects.get(id=self.data.get("id"))
            g.delete()
            return JsonResponse({"data": self._get_grupos_data()})
        except GrupoPacientes.DoesNotExist:
            return JsonResponse({}, status=404)


class MedicacionView(DataView):
    def get(self, request):
        data = Medicacion.objects.values("id", "nombre", "categoria")
        return render(
            request,
            "gi/views/parametros/medicacion.html",
            {
                "data": list(data),
                "categories": Medicacion.get_categorias(include_empty=False),
                "title": parametros_title,
            },
        )

    def post(self, request):
        visited = []
        for index, med in enumerate(self.data):
            if med.get("id"):
                m = Medicacion.objects.filter(id=med["id"]).first()
                m.order = index
                for field in med.keys():
                    if field != "id":
                        setattr(m, field, med[field])
                m.save()
            else:
                m = Medicacion(**med)
                m.order = index
                m.save()
            visited.append(m.id)
        Medicacion.objects.exclude(id__in=visited).delete()
        data = Medicacion.objects.values("id", "nombre")

        return JsonResponse({"data": list(data)})

    def put(self, request):
        try:
            m = Medicacion.objects.get(id=self.data.get("id"))
            m.nombre = self.data.get("nombre")
            m.dosis = self.data.get("dosis")
            m.order = self.data.get("order")
            m.save()
            return JsonResponse({"id": m.id})
        except Medicacion.DoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request):
        try:
            m = Medicacion.objects.get(id=self.data.get("id"))
            m.delete()
            return JsonResponse({"id": self.data.get("id")})
        except Medicacion.DoesNotExist:
            return JsonResponse({}, status=404)
