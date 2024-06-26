from datetime import timedelta
from typing import Tuple

from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from django.db.models import F, Value, CharField, Count, BooleanField
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.vary import vary_on_headers

from gi.models import (
    Paciente,
    Complicacion,
    MetaPaciente,
    ControlPaciente,
    GrupoPacientes,
    Medicacion,
    ExamenPaciente,
    MedicacionPaciente,
    Ciudad,
    HospitalizacionPaciente,
    Tratamiento,
    VariablesClinicas,
)
from gi.utils import (
    parse_date,
    get_pacientes_usuario,
    get_patients_filters,
    apply_patient_filters,
    get_m2m_checkboxes,
)
from gi.constants import (
    METRICA_PESO,
    METRICA_TENSION_ARTERIAL,
    METRICA_HEMOGLOBINA_GLICOSILADA,
    METRICA_MICROALBUMINURIA,
)
from ._base import DataView, AuthenticatedView


def get_pacientes(request, group: GrupoPacientes = None, pacientes_qs=None):
    current = int(request.GET.get("page", "1"))
    page_size = int(request.GET.get("size", "25"))

    queryset = (
        pacientes_qs
        if pacientes_qs is not None
        else get_pacientes_usuario(request.user)
    )
    if group:
        queryset = group.pacientes.all()
    queryset = apply_patient_filters(request, queryset)

    qs_pacientes = queryset.annotate(
        paciente=Concat("nombres", Value(" "), "apellidos", output_field=CharField()),
        ciudad=F("ciudad_asignacion__nombre"),
        riesgo_rcv=F("nivel_riesgo_rcv"),
        riesgo_tfg=F("estadio"),
        metas=Count("metapaciente"),
    )

    if request.GET.get("order_by"):
        order_by_slug = request.GET["order_by"]
        ord_dir = request.GET.get("order_dir")
        qs_pacientes = qs_pacientes.order_by(
            f"{'-' if ord_dir == 'd' else ''}{order_by_slug}"
        )
    else:
        qs_pacientes = qs_pacientes.order_by("-id")

    paginator = Paginator(qs_pacientes, page_size)
    items = []

    estadio_code = {
        '1':'20',
        '2':'21',
        '3a':'22',
        '3b':'23',
        '4':'24',
        '5':'25',
        '0':'26',
    }

    estadio_label = {
        '1':'Estadio 1',
        '2':'Estadio 2',
        '3a':'Estadio 3a',
        '3b':'Estadio 3b',
        '4':'Estadio 4',
        '5':'Estadio 5',
        '0':'Sin Calcular',
    }
    
    for item in paginator.page(current).object_list:
        vc: VariablesClinicas = (
            VariablesClinicas.objects.filter(fk_paciente_id=item.id)
            .order_by("-fecha_cargue")
            .first()
        )
        
        if ( str(item.estadio_erc) in estadio_code):
            code = estadio_code[item.estadio_erc]
        else:
            code = '26'


        if ( str(item.estadio_erc) in estadio_label):
            label = estadio_label[item.estadio_erc]
        else:
            label = 'Sin Calcular'

        items.append(
            {
                "slug": item.id,
                "id": item.id,
                "paciente": item.paciente,
                "diagnostico": item.tipo_diabetes,
                "ciudad": item.ciudad,
                "riesgo_rcv": {
                    "label": item.riesgo_rcv,
                    "code": item.codigo_estado_nivel_riesgo_rcv,
                },
                "riesgo_tfg": {
                    "label": label,
                    "code": code,
                },
                "metas": item.metas,
                "ultimo_seguimiento": item.codigo_ultimo_seguimiento,
                "telefono": item.telefono,
                "actions": [
                    {
                        "icon": "chevron_right",
                        "route": reverse(
                            "gi:datos-paciente", kwargs={"id_paciente": item.id}
                        ),
                    }
                ],
            }
        )
    return items, paginator.count, paginator.num_pages


class SeguimientoPacientesView(DataView):
    def get(self, request):
        grupos = GrupoPacientes.objects.values(
            "id", label=F("nombre"), value=Value(False, output_field=BooleanField())
        )
        items, total, num_pages = get_pacientes(request)

        return render(
            request,
            "gi/views/seguimiento/pacientes.html",
            {
                "title": "Seguimiento de Pacientes",
                "aside": "seguimiento",
                "grupos": list(grupos),
                "pages": num_pages,
                "total": total,
                "data": items,
                **get_patients_filters(),
            },
        )

    def post(self, request):
        paciente_ids = self.data.get("pacientes")
        grupo_ids = self.data.get("grupos")
        pacientes = get_pacientes_usuario(request.user).filter(id__in=paciente_ids)

        for grupo_id in grupo_ids:
            g = GrupoPacientes.objects.get(id=grupo_id)
            g.pacientes.add(*pacientes)

        return JsonResponse({})


class SeguimientoPacientesApiView(AuthenticatedView):
    def get(self, request):
        items, total, num_pages = get_pacientes(request)
        return JsonResponse({"data": items, "pages": num_pages, "total": total})


class BasePacienteView(DataView):
    paciente = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.paciente = get_pacientes_usuario(request.user).get(
                id=kwargs.get("id_paciente", "0")
            )
        except Paciente.DoesNotExist:
            self.paciente = Paciente()
        return super().dispatch(request, *args, **kwargs)

    def save_data(self):
        """
        Aca se debe poner la lógica para guardar el paciente de acuerdo a lo recibido en el request.

        Tener en cuenta:

        'self.data' = dict de los datos recibidos en 'request'
        'self.paciente' = paciente que se va a modificar o a crear
        """
        pass

    def post(self, request, id_paciente: int = None):
        self.save_data()
        self.paciente.save()
        return JsonResponse({"id": self.paciente.id})

    def put(self, request, id_paciente: int):
        try:
            self.save_data()
            self.paciente.save()
            return JsonResponse({"id": self.paciente.id})
        except Paciente.DoesNotExist:
            return JsonResponse({}, status=404)

    def delete(self, request, id_paciente: int = None):
        # override
        return JsonResponse({}, status=405)


class DatosPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int = None):
        if self.paciente:
            datos_paciente = {
                "id": self.paciente.id if self.paciente.id else "",
                "nombres": self.paciente.nombres,
                "apellidos": self.paciente.apellidos,
                "tipo_documento": self.paciente.tipo_documento,
                "numero_documento": self.paciente.numero_documento,
                "fecha_nacimiento": self.paciente.fecha_nacimiento.strftime("%Y-%m-%d"),
                "genero": self.paciente.genero,
                "grupo_etnico": self.paciente.grupo_etnico,
                "estado_civil": self.paciente.estado_civil,
                "nivel_estudios": self.paciente.nivel_estudios,
                "estrato": self.paciente.estrato,
                "departamento_contacto": self.paciente.ciudad_contacto.departamento
                if self.paciente.ciudad_contacto
                else "",
                "ciudad_contacto_id": self.paciente.ciudad_contacto_id
                if self.paciente.ciudad_contacto
                else 0,
                "direccion": self.paciente.direccion,
                "barrio": self.paciente.barrio,
                "telefono": "Sin información" if self.paciente.telefono == str(0) else self.paciente.telefono,
                "telefono_emergencia": self.paciente.telefono_emergencia,
                "eps_id": self.paciente.eps_id if self.paciente.eps else 0,
                "grupo_gestion_id": self.paciente.grupo_gestion_id
                if self.paciente.grupo_gestion
                else 0,
                "ciudad_asignacion_id": self.paciente.ciudad_asignacion_id
                if self.paciente.ciudad_asignacion
                else 0,
                "fecha_afiliacion": self.paciente.fecha_afiliacion.strftime("%Y-%m-%d"),
            }
        else:
            datos_paciente = {}
        return render(
            request,
            "gi/views/paciente/datos.html",
            {
                "active": "datos-paciente",
                "title": "Datos del paciente",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "datos_paciente": datos_paciente,
                "backlink": reverse("gi:seguimiento-pacientes"),
                "parametros": {
                    "tipos_documento": Paciente.get_tipos_documento(),
                    "generos": Paciente.get_generos(),
                    "estados_civiles": Paciente.get_estados_civiles(),
                    "grupos_etnicos": Paciente.get_grupos_etnicos(),
                    "niveles_estudio": Paciente.get_niveles_estudio(),
                    "estratos": Paciente.get_estratos(),
                    "ciudades": Paciente.get_ciudades(),
                    "departamentos": Paciente.get_departamentos_ciudades(),
                    "eps": Paciente.get_eps_list(),
                    "grupos_gestion": Paciente.get_grupos_gestion_list(request.user),
                },
            },
        )

    def save_data(self):
        p = self.paciente
        p.nombres = self.data.get("nombres")
        p.apellidos = self.data.get("apellidos")
        p.tipo_documento = self.data.get("tipo_documento")
        p.numero_documento = self.data.get("numero_documento")
        p.fecha_nacimiento = parse_date(self.data.get("fecha_nacimiento"))
        p.genero = self.data.get("genero")
        p.grupo_etnico = self.data.get("grupo_etnico")
        p.estado_civil = self.data.get("estado_civil")
        p.nivel_estudios = self.data.get("nivel_estudios")
        p.estrato = self.data.get("estrato")

        if self.data.get("ciudad_contacto_id", "0") != "0":
            p.ciudad_contacto_id = self.data.get("ciudad_contacto_id")

        p.direccion = self.data.get("direccion")
        p.barrio = self.data.get("barrio")
        p.telefono = self.data.get("telefono")
        p.telefono_emergencia = self.data.get("telefono_emergencia")

        if self.data.get("eps_id", "0") != "0":
            p.eps_id = self.data.get("eps_id")

        if self.data.get("grupo_gestion_id", "0") != "0":
            p.grupo_gestion_id = self.data.get("grupo_gestion_id")

        if self.data.get("ciudad_asignacion_id", "0") != "0":
            p.ciudad_asignacion_id = self.data.get("ciudad_asignacion_id")

        p.fecha_afiliacion = parse_date(self.data.get("fecha_afiliacion"))

        p.actualizar_riesgocardiovascular(save=False)
        p.actualizar_riesgo_tfg(save=False)


class PerfilamientoPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int = None):
        if not self.paciente.id:
            return redirect("gi:crear-datos-paciente")
        qs_grupos = GrupoPacientes.objects.all()
        qs_grupos_paciente = self.paciente.grupopacientes_set.all()
        grupos = get_m2m_checkboxes(qs_grupos, qs_grupos_paciente)

        qs_complicaciones = Complicacion.objects.all()
        qs_complicaciones_paciente = self.paciente.complicaciones_diagnostico.all()
        complicaciones = get_m2m_checkboxes(
            qs_complicaciones, qs_complicaciones_paciente
        )

        qs_tratamientos = Tratamiento.objects.all()
        qs_tratamientos_cliente = self.paciente.tratamientos.all()
        tratamientos = get_m2m_checkboxes(qs_tratamientos, qs_tratamientos_cliente)

        return render(
            request,
            "gi/views/paciente/perfilamiento.html",
            {
                "active": "perfilamiento",
                "title": "Perfilamiento del paciente",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "backlink": reverse("gi:seguimiento-pacientes"),
                "complicaciones": complicaciones,
                "tratamientos": tratamientos,
                "grupos": grupos,
                "tipos_diabetes": Paciente.get_tipos_diabetes(),
                "diagnosticos": Paciente.get_diagnosticos(),
                "estadios_erc": Paciente.get_estadios_erc(),
                "diagnosticos_adicionales": self.paciente.diagnosticos_adicionales,
                "diagnostico_paciente": {
                    "peso":  "Sin información" if self.paciente.peso == 0 else self.paciente.peso,
                    "estatura": "Sin información" if self.paciente.estatura == 0 else self.paciente.estatura,
                    "tipoDiabetes": self.paciente.tipo_diabetes,
                    "diagnostico": self.paciente.diagnostico,
                    "estadio_erc": self.paciente.estadio_erc,
                    "anio_diagnostico": self.paciente.fecha_diagnostico.strftime("%Y"),
                    "mes_diagnostico": self.paciente.fecha_diagnostico.strftime("%m"),
                    "riesgo_tfg": {
                        "riesgo": self.paciente.tfg,
                        "nivel": self.paciente.estadio,
                        "codigoEstado": self.paciente.codigo_estado_estadio,
                        "creatinina": self.paciente.ultima_creatinina,
                    },
                    "riesgo_rcv": {
                        "riesgo": self.paciente.riesgo_cardiovascular,
                        "colesterolTotal": "Sin información" if self.paciente.colesterol_total == 0 else self.paciente.colesterol_total,
                        "hdl": "Sin información" if self.paciente.hdl == 0 else self.paciente.hdl,
                        "tas": "Sin información" if self.paciente.tas == 0 else self.paciente.tas,
                        "tad": "Sin información" if self.paciente.tad == 0 else self.paciente.tad,
                        "fumador": self.paciente.es_fumador,
                        "nivel": self.paciente.nivel_riesgo_rcv,
                        "codigoEstado": self.paciente.codigo_estado_nivel_riesgo_rcv,
                    },
                    "programa_nefroproteccion": {
                        "activo": self.paciente.programa_nefroproteccion != "",
                        "nombre": self.paciente.programa_nefroproteccion,
                    },
                },
            },
        )

    def save_data(self):
        p = self.paciente
        p.tipo_diabetes = self.data.get("tipoDiabetes")
        riesgo_rcv = self.data.get("riesgo_rcv", {})

        if riesgo_rcv.get("colesterolTotal") == "Sin información":
            p.colesterol_total = 0
        else:
            p.colesterol_total = riesgo_rcv.get("colesterolTotal")

        if riesgo_rcv.get("hdl") == "Sin información":
             p.hdl = 0
        else:
            p.hdl = riesgo_rcv.get("hdl")
        
        if riesgo_rcv.get("tas") == "Sin información":
            p.tas = 0
        else:
            p.tas = riesgo_rcv.get("tas")
        
        if riesgo_rcv.get("tad") == "Sin información":
            p.tad = 0
        else:
            p.tad = riesgo_rcv.get("tad")
        
        p.es_fumador = riesgo_rcv.get("fumador")

        if self.data.get("estatura") == "Sin información":
            p.estatura = 0
        else:
            p.estatura = self.data.get("estatura")
        
        if self.data.get("peso") == "Sin información":
            p.peso = 0
        else:
            p.peso = self.data.get("peso")

        p.actualizar_riesgocardiovascular(save=False)
        p.actualizar_riesgo_tfg(save=False)

        for complicacion in self.data.get("complicaciones", []):
            _complicacion = Complicacion.objects.filter(
                id=complicacion.get("slug")
            ).first()
            if _complicacion:
                complicacion_seleccionada = complicacion.get("value", False)
                existe_paciente_complicacion = p.complicaciones_diagnostico.filter(
                    id=_complicacion.id
                ).exists()

                if existe_paciente_complicacion:
                    if not complicacion_seleccionada:
                        p.complicaciones_diagnostico.remove(_complicacion)
                else:
                    if complicacion_seleccionada:
                        p.complicaciones_diagnostico.add(_complicacion)

        for tratamiento in self.data.get("tratamientos", []):
            _tratamiento = Tratamiento.objects.filter(
                id=tratamiento.get("slug")
            ).first()
            if _tratamiento:
                selected = tratamiento.get("value", False)
                if not selected:
                    p.tratamientos.remove(_tratamiento)
                if selected:
                    p.tratamientos.add(_tratamiento)

        for grupo in self.data.get("grupos", []):
            _grupo: GrupoPacientes = GrupoPacientes.objects.filter(
                id=grupo.get("slug")
            ).first()
            if _grupo:
                existe_paciente_grupo = _grupo.pacientes.filter(id=p.id).exists()
                grupo_seleccionado = grupo.get("value", False)

                if existe_paciente_grupo:
                    if not grupo_seleccionado:
                        _grupo.pacientes.remove(p)
                else:
                    if grupo_seleccionado:
                        _grupo.pacientes.add(p)

        anio_diagnostico = self.data.get("anio_diagnostico")
        mes_diagnostico = self.data.get("mes_diagnostico")
        p.fecha_diagnostico = parse_date(f"{anio_diagnostico}-{mes_diagnostico}-01")

        p.diagnostico = self.data.get("diagnostico", "")
        p.estadio_erc = self.data.get("estadio_erc", "")
        for diagnostico_adicional in self.data.get("diagnosticosAdicionales", []):
            slug = diagnostico_adicional.get("slug", "")
            value = diagnostico_adicional.get("value", False)
            if slug == "hta":
                p.diagnostico_hta = value
            elif slug == "erc":
                p.diagnostico_erc = value
            elif slug == "epoc":
                p.diagnostico_epoc = value
            elif slug == "falla_cardiaca":
                p.diagnostico_falla_cardiaca = value
            elif slug == "hipoglicemia":
                p.diagnostico_hipoglicemia = value

        p.programa_nefroproteccion = self.data.get("programa_nefroproteccion", {}).get(
            "nombre", ""
        )


class MetasPacienteView(BasePacienteView):
    def post(self, request, id_paciente: int = None):
        p = self.paciente

        id_meta_paciente = self.data.get("id", None)
        if not id_meta_paciente:
            meta_paciente: MetaPaciente = MetaPaciente(fk_paciente=p)
        else:
            meta_paciente: MetaPaciente = p.metapaciente_set.filter(
                id=id_meta_paciente
            ).first()

        if meta_paciente:
            meta_paciente.tipo = self.data.get("concepto", "")
            meta_paciente.meta = self.data.get("meta", 0)
            meta_paciente.fecha_inicio = parse_date(self.data.get("fecha_inicio"))
            meta_paciente.fecha_fin = parse_date(self.data.get("fecha_limite"))

            meta_paciente.save()

        return JsonResponse(meta_paciente.to_dict())


class TareasPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int):
        medicamentos_paciente = []
        qs_medicamentos_paciente = self.paciente.medicacionpaciente_set.all()
        for medicamento in qs_medicamentos_paciente:
            medicamentos_paciente.append(
                {
                    "medicamento": medicamento.fk_medicacion_id,
                    "dosis": medicamento.dosis_mg,
                    "fecha_formulacion": medicamento.fecha_formulacion.strftime(
                        "%Y-%m-%d"
                    ),
                    "tiempo_formulacion": medicamento.tiempo_formulacion_meses,
                }
            )

        grupos = []
        qs_grupos_paciente = self.paciente.grupopacientes_set.all()
        for grupo in qs_grupos_paciente:
            qs_servicios_tareas = grupo.servicios_tarea.all().annotate(
                nombre_tarea=F("fk_tarea__nombre")
            )

            hash_tareas = {}
            for servicio_tarea in qs_servicios_tareas:
                if servicio_tarea.fk_tarea_id not in hash_tareas:
                    hash_tareas[servicio_tarea.fk_tarea_id] = {
                        "id": servicio_tarea.fk_tarea_id,
                        "nombre": servicio_tarea.nombre_tarea,
                        "data": [],
                    }

                today = now()
                realizados = ControlPaciente.objects.filter(
                    fk_paciente=self.paciente,
                    tipo=servicio_tarea.nombre,
                    fecha__lte=today + relativedelta(years=1),
                ).count()
                if realizados < servicio_tarea.cantidad:
                    estado = {"label": "Incompleto", "code": 2}
                else:
                    estado = {"label": "Completo", "code": 1}

                hash_tareas[servicio_tarea.fk_tarea_id]["data"].append(
                    {
                        "concepto": servicio_tarea.nombre,
                        "id": servicio_tarea.id,
                        "realizados": realizados,
                        "recomendados": servicio_tarea.cantidad,
                        "estado": estado,
                    }
                )

            grupos.append(
                {
                    "id": grupo.id,
                    "nombre": grupo.nombre,
                    "tareas": [hash_tareas[id_tarea] for id_tarea in hash_tareas],
                }
            )

        medicamentos_qs = Medicacion.objects.all()
        medicamentos = [
            {
                "name": category["label"],
                "options": list(
                    medicamentos_qs.filter(categoria=category["value"])
                    .annotate(label=F("nombre"), slug=F("id"))
                    .values("label", "slug")
                ),
            }
            for category in Medicacion.get_categorias(include_empty=True)
        ]
        return render(
            request,
            "gi/views/paciente/tareas.html",
            {
                "active": "tareas",
                "title": "Tareas",
                "aside": "seguimiento",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "grupos": grupos,
                "medicamentos": medicamentos,
                "medicamentos_paciente": medicamentos_paciente,
            },
        )

    def save_data(self):
        p = self.paciente
        ids_medicacion_paciente = []
        for medicamento in self.data:
            medicacion_id = medicamento.get("medicamento", 0)
            if medicacion_id:
                medicacion: Medicacion = Medicacion.objects.filter(
                    id=medicacion_id
                ).first()
                if medicacion:
                    dosis_mg = medicamento.get("dosis", 0)
                    tiempo_formulacion_meses = medicamento.get("tiempo_formulacion", 0)
                    try:
                        fecha_formulacion = parse_date(
                            medicamento.get("fecha_formulacion")
                        )
                    except:
                        fecha_formulacion = now()

                    medicacion_paciente: MedicacionPaciente = (
                        p.medicacionpaciente_set.filter(
                            fk_medicacion=medicacion
                        ).first()
                    )
                    if not medicacion_paciente:
                        medicacion_paciente = MedicacionPaciente(
                            fk_paciente=p, fk_medicacion=medicacion
                        )

                    medicacion_paciente.dosis_mg = dosis_mg
                    medicacion_paciente.fecha_formulacion = fecha_formulacion
                    medicacion_paciente.tiempo_formulacion_meses = (
                        tiempo_formulacion_meses
                    )
                    medicacion_paciente.save()

                    ids_medicacion_paciente.append(medicacion_paciente.id)

        p.medicacionpaciente_set.exclude(id__in=ids_medicacion_paciente).delete()


class ControlesPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int):
        return render(
            request,
            "gi/views/paciente/controles.html",
            {
                "active": "controles",
                "aside": "seguimiento",
                "title": "Controles del paciente",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "backlink": reverse("gi:seguimiento-pacientes"),
                "tipos_control": ControlPaciente.get_tipos_p(),
                "data": [
                    control.to_dict()
                    for control in self.paciente.controlpaciente_set.all()
                ],
            },
        )

    def post(self, request, id_paciente: int = None):
        paciente: Paciente = (
            get_pacientes_usuario(request.user).filter(id=id_paciente).first()
        )
        if paciente:
            id_control = self.data.get("id", None)
            if not id_control:
                control: ControlPaciente = ControlPaciente(fk_paciente=paciente)
            else:
                control: ControlPaciente = paciente.controlpaciente_set.filter(
                    id=id_control
                ).first()

            if control:
                control.fecha = parse_date(self.data.get("fecha"))
                control.observaciones = self.data.get("observaciones", "")
                control.tiene_soporte = self.data.get("soporte", False)
                control.tipo = self.data.get("tipo", "")
                control.glucometria = self.data.get("glucometria", None)

                control.tas = self.data.get("tas", None)
                control.tad = self.data.get("tad", None)
                control.peso = self.data.get("peso", None)
                control.numero_eventos_hipoglicemia = self.data.get(
                    "numero_eventos_hipoglicemia", 0
                )

                control.save()

            paciente.actualizar_ultimo_seguimiento(save=True)

            return JsonResponse(control.to_dict())
        else:
            return JsonResponse({}, status=404)


class HospitalizacionesPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int):
        return render(
            request,
            "gi/views/paciente/hospitalizaciones.html",
            {
                "active": "hospitalizaciones",
                "aside": "seguimiento",
                "title": "Hospitalizaciones del paciente",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "backlink": reverse("gi:seguimiento-pacientes"),
                "tipos_hospitalizaciones": HospitalizacionPaciente.get_tipos(),
                "diagnosticos": HospitalizacionPaciente.get_diagnosticos(),
                "data": [
                    hospitalizacion.to_dict()
                    for hospitalizacion in self.paciente.hospitalizacionpaciente_set.all()
                ],
            },
        )

    def post(self, request, id_paciente: int = None):
        paciente: Paciente = (
            get_pacientes_usuario(request.user).filter(id=id_paciente).first()
        )
        if paciente:
            id_hospitalizacion = self.data.get("id", None)
            if not id_hospitalizacion:
                hospitalizacion: HospitalizacionPaciente = HospitalizacionPaciente(
                    fk_paciente=paciente
                )
            else:
                hospitalizacion: HospitalizacionPaciente = (
                    paciente.hospitalizacionpaciente_set.filter(
                        id=id_hospitalizacion
                    ).first()
                )

            if hospitalizacion:
                hospitalizacion.fecha = parse_date(self.data.get("fecha"))
                hospitalizacion.observaciones = self.data.get("observaciones", "")
                hospitalizacion.tiene_soporte = self.data.get("soporte", False)
                hospitalizacion.era_evitable = self.data.get("era_evitable", False)
                hospitalizacion.relacionado_con_diabetes = self.data.get(
                    "relacionado_con_diabetes", False
                )
                hospitalizacion.tipo = self.data.get("tipo", "")

                hospitalizacion.save()

            paciente.actualizar_ultimo_seguimiento(save=True)

            return JsonResponse(hospitalizacion.to_dict())
        else:
            return JsonResponse({}, status=404)


class ExamenesPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int):
        return render(
            request,
            "gi/views/paciente/examenes.html",
            {
                "active": "examenes",
                "aside": "seguimiento",
                "title": "Examenes del paciente",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "backlink": reverse("gi:seguimiento-pacientes"),
                "data": [
                    examen.to_dict()
                    for examen in self.paciente.examenpaciente_set.all()
                ],
            },
        )

    def post(self, request, id_paciente: int = None):
        paciente: Paciente = (
            get_pacientes_usuario(request.user).filter(id=id_paciente).first()
        )
        if paciente:
            id_examen = self.data.get("id", None)
            if not id_examen:
                examen: ExamenPaciente = ExamenPaciente(fk_paciente=paciente)
            else:
                examen: ExamenPaciente = paciente.examenpaciente_set.filter(
                    id=id_examen
                ).first()

            if examen:
                examen.fecha = parse_date(self.data.get("fecha"))
                examen.tsh = self.data.get("tsh", 0)
                examen.alat = self.data.get("alat", 0)
                examen.glicemia_basal = self.data.get("glicemia", 0)
                examen.asat = self.data.get("asat", 0)
                examen.microalbuminuria = self.data.get("micro", 0)
                examen.creatinina = self.data.get("creatinina", 0)
                examen.hdl = self.data.get("hdl", 0)
                examen.ldl = self.data.get("ldl", 0)
                examen.ct = self.data.get("ct", 0)
                examen.hemoglobina_glicosilada = self.data.get(
                    "hemoglobina_glicosilada", 0
                )

                examen.save()

            paciente.actualizar_hba1c(save=True)
            paciente.actualizar_riesgo_tfg(save=False)
            paciente.actualizar_ultimo_seguimiento(save=True)

            return JsonResponse(examen.to_dict())
        else:
            return JsonResponse({}, status=404)


class TendenciasPacienteView(BasePacienteView):
    def get(self, request, id_paciente: int):
        meta_global, metas_individuales = self.paciente.get_metas()

        return render(
            request,
            "gi/views/paciente/tendencias.html",
            {
                "active": "tendencias",
                "aside": "seguimiento",
                "title": "Tendencias del paciente",
                "id_paciente": id_paciente,
                "paciente": self.paciente,
                "backlink": reverse("gi:seguimiento-pacientes"),
                "metas_config": {
                    "tipos": MetaPaciente.get_tipos(),
                    "global": "{0:.1%}".format(meta_global),
                    "registros": metas_individuales,
                },
                "tipos_indicador": [
                    {"label": "Peso", "value": METRICA_PESO},
                    {
                        "label": "Hemoglobina glicosilada",
                        "value": METRICA_HEMOGLOBINA_GLICOSILADA,
                    },
                    {"label": "Microalbuminuria", "value": METRICA_MICROALBUMINURIA},
                    {"label": "Presión arterial", "value": METRICA_TENSION_ARTERIAL},
                ],
            },
        )


class IndicadoresPacienteView(BasePacienteView):
    def _get_registros_controles(self, tipo_indicador):
        response = []

        variables_clinicas = self.paciente.variablesclinicas_set.all()
        metas_paciente = self.paciente.metapaciente_set.all()
        today = now()

        meta_valor = None
        meta_valor_2 = None
        if tipo_indicador == METRICA_PESO:
            qs_meta_peso: MetaPaciente = (
                metas_paciente.filter(tipo=MetaPaciente.TIPO_META_PESO)
                .order_by("-fecha_fin")
                .first()
            )
            meta_valor = qs_meta_peso.meta if qs_meta_peso else 0
        elif tipo_indicador == METRICA_MICROALBUMINURIA:
            qs_meta_peso: MetaPaciente = (
                metas_paciente.filter(tipo=MetaPaciente.TIPO_META_MICROALBUMINURIA)
                .order_by("-fecha_fin")
                .first()
            )
            meta_valor = qs_meta_peso.meta if qs_meta_peso else 0
        elif tipo_indicador == METRICA_HEMOGLOBINA_GLICOSILADA:
            qs_meta_peso: MetaPaciente = (
                metas_paciente.filter(
                    tipo=MetaPaciente.TIPO_META_HEMOGLOBINA_GLICOSILADA
                )
                .order_by("-fecha_fin")
                .first()
            )
            meta_valor = qs_meta_peso.meta if qs_meta_peso else 0
        elif tipo_indicador == METRICA_TENSION_ARTERIAL:
            qs_meta_tas: MetaPaciente = (
                metas_paciente.filter(tipo=MetaPaciente.TIPO_META_TAS)
                .order_by("-fecha_fin")
                .first()
            )
            qs_meta_tad: MetaPaciente = (
                metas_paciente.filter(tipo=MetaPaciente.TIPO_META_TAD)
                .order_by("-fecha_fin")
                .first()
            )
            meta_valor = qs_meta_tas.meta if qs_meta_tas else 0
            meta_valor_2 = qs_meta_tad.meta if qs_meta_tad else 0

        for meta in metas_paciente:
            valor = None
            valor_2 = None

            variables_clinicas.filter(
                fecha_cargue__gte=today, fecha_cargue__lte=today + timedelta(days=30)
            )

            if meta_valor is not None:
                response.append(
                    {
                        "id": meta.id,
                        "metrica": tipo_indicador,
                        "valor": valor,
                        "valor2": valor_2,
                        "recomendados": {
                            "valor": meta_valor,
                            "valor2": meta_valor_2,
                        },
                        "fecha": meta.fecha_fin.strftime("%Y-%m-%d"),
                    }
                )

        return response

    def _get_registros_examenes(self, tipo_indicador):
        response = []

        examenes = self.paciente.examenpaciente_set.all()
        metas_paciente = self.paciente.metapaciente_set.all()

        if tipo_indicador == METRICA_HEMOGLOBINA_GLICOSILADA:
            qs_meta_hemoglobina_glicosilada: MetaPaciente = (
                metas_paciente.filter(
                    tipo=MetaPaciente.TIPO_META_HEMOGLOBINA_GLICOSILADA
                )
                .order_by("-fecha_fin")
                .first()
            )

            meta_valor = (
                qs_meta_hemoglobina_glicosilada.meta
                if qs_meta_hemoglobina_glicosilada
                else 0
            )
        elif tipo_indicador == METRICA_MICROALBUMINURIA:
            qs_meta_microalbuminuria: MetaPaciente = (
                metas_paciente.filter(tipo=MetaPaciente.TIPO_META_MICROALBUMINURIA)
                .order_by("-fecha_fin")
                .first()
            )
            meta_valor = (
                qs_meta_microalbuminuria.meta if qs_meta_microalbuminuria else 0
            )
        else:
            meta_valor = None

        for examen in examenes:
            if tipo_indicador == METRICA_HEMOGLOBINA_GLICOSILADA:
                valor = examen.hemoglobina_glicosilada
            elif tipo_indicador == METRICA_MICROALBUMINURIA:
                valor = examen.microalbuminuria
            else:
                valor = None

            if valor is not None:
                response.append(
                    {
                        "id": examen.id,
                        "metrica": tipo_indicador,
                        "valor": valor,
                        "valor2": None,
                        "recomendados": {
                            "valor": meta_valor,
                            "valor2": None,
                        },
                        "fecha": examen.fecha.strftime("%Y-%m-%d"),
                    }
                )

        return response

    def get(self, request, id_paciente: int):
        tipo_indicador = request.GET.get("indicador")
        registros = []
        if tipo_indicador == METRICA_PESO or tipo_indicador == METRICA_TENSION_ARTERIAL:
            registros = self._get_registros_controles(tipo_indicador=tipo_indicador)
        elif (
            tipo_indicador == METRICA_MICROALBUMINURIA
            or tipo_indicador == METRICA_HEMOGLOBINA_GLICOSILADA
        ):
            registros = self._get_registros_examenes(tipo_indicador=tipo_indicador)

        return JsonResponse({"registros": registros})


class SeguimientoGruposView(AuthenticatedView):
    def get(self, request):
        # data = load_json('grupos.json')
        data = list(
            GrupoPacientes.objects.annotate(count=Count("pacientes")).values(
                "slug", "count", name=F("nombre")
            )
        )
        for d in data:
            d["route"] = reverse("gi:grupo-pacientes", kwargs={"slug_grupo": d["slug"]})

        return render(
            request,
            "gi/views/seguimiento/grupos.html",
            {"title": "Seguimiento de Pacientes", "aside": "seguimiento", "data": data},
        )


class GrupoPacientesView(AuthenticatedView):
    @vary_on_headers("Content-Type")
    def get(self, request, slug_grupo: str):
        g = GrupoPacientes.objects.get(slug=slug_grupo)
        items, total, num_pages = get_pacientes(request, group=g)

        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"data": items, "pages": num_pages, "total": total})

        cities = (
            Ciudad.objects.all()
            .annotate(slug=F("id"), value=F("id"), label=F("nombre"))
            .values("slug", "value", "label")
        )

        return render(
            request,
            "gi/views/seguimiento/detalle-grupo.html",
            {
                "backlink": reverse("gi:seguimiento-grupos"),
                "title": g.nombre,
                "aside": "seguimiento",
                "pages": num_pages,
                "total": total,
                "data": items,
                "cities": list(cities),
                "riesgos_rcv": Paciente.get_niveles_riesgo_rcv(),
                "riesgos_tfg": Paciente.get_estadios_erc_2(),
                "diagnoses": Paciente.get_tipos_diabetes(),
            },
        )


def _get_utimas_metas(view) -> Tuple[float, float, float, float, float]:
    qs_meta_peso: MetaPaciente = (
        view.paciente.metapaciente_set.filter(tipo=MetaPaciente.TIPO_META_PESO)
        .order_by("-fecha_fin")
        .first()
    )
    qs_meta_hemoglobina_glicosilada: MetaPaciente = (
        view.paciente.metapaciente_set.filter(
            tipo=MetaPaciente.TIPO_META_HEMOGLOBINA_GLICOSILADA
        )
        .order_by("-fecha_fin")
        .first()
    )
    qs_meta_microalbuminuria: MetaPaciente = (
        view.paciente.metapaciente_set.filter(
            tipo=MetaPaciente.TIPO_META_MICROALBUMINURIA
        )
        .order_by("-fecha_fin")
        .first()
    )
    qs_meta_tas: MetaPaciente = (
        view.paciente.metapaciente_set.filter(tipo=MetaPaciente.TIPO_META_TAS)
        .order_by("-fecha_fin")
        .first()
    )
    qs_meta_tad: MetaPaciente = (
        view.paciente.metapaciente_set.filter(tipo=MetaPaciente.TIPO_META_TAD)
        .order_by("-fecha_fin")
        .first()
    )

    meta_peso = qs_meta_peso.meta if qs_meta_peso else 0
    meta_hemoglobina_glicosilada = (
        qs_meta_hemoglobina_glicosilada.meta if qs_meta_hemoglobina_glicosilada else 0
    )
    meta_microalbuminuria = (
        qs_meta_microalbuminuria.meta if qs_meta_microalbuminuria else 0
    )
    meta_tas = qs_meta_tas.meta if qs_meta_tas else 0
    meta_tad = qs_meta_tad.meta if qs_meta_tad else 0
    return (
        meta_peso,
        meta_hemoglobina_glicosilada,
        meta_microalbuminuria,
        meta_tas,
        meta_tad,
    )
