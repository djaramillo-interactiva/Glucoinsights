from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    GrupoEtareo,
    Indicador,
    Tarea,
    ServicioTarea,
    GrupoPacientes,
    Medicacion,
    GrupoGestion,
    Ciudad,
    Usuario,
    Eps,
    Complicacion,
    Paciente,
    MedicacionPaciente,
    ControlPaciente,
    ExamenPaciente,
    MetaPaciente,
    HospitalizacionPaciente,
    Tratamiento,
    VariablesClinicas,
    CargueBackOffice,
)


@admin.register(GrupoEtareo)
class GrupoEtareoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "edad_inicio", "edad_fin")
    list_display_links = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "meta", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    list_filter = ("tipo",)
    search_fields = ("nombre", "tipo", "descripcion")


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    class _ServicioTareaInline(admin.TabularInline):
        model = ServicioTarea
        extra = 0

    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)
    inlines = (_ServicioTareaInline,)


@admin.register(GrupoPacientes)
class GrupoPacientesAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)
    filter_horizontal = ("servicios_tarea", "pacientes")


@admin.register(Medicacion)
class MedicacionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "categoria", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)
    list_filter = ("categoria",)


@admin.register(Eps)
class EpsAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)


@admin.register(GrupoGestion)
class GrupoGestionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)


@admin.register(Complicacion)
class ComplicacionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "order")
    list_display_links = ("id", "nombre")
    list_editable = ("order",)
    search_fields = ("nombre",)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    class _MedicacionInline(admin.TabularInline):
        model = MedicacionPaciente
        extra = 0

    class _ControlInline(admin.TabularInline):
        model = ControlPaciente
        extra = 0

    class _HospitalizacionInline(admin.TabularInline):
        model = HospitalizacionPaciente
        extra = 0

    class _ExamenInline(admin.TabularInline):
        model = ExamenPaciente
        extra = 0

    class _MetaInline(admin.TabularInline):
        model = MetaPaciente
        extra = 0

    list_display = ("id", "tipo_documento", "numero_documento", "nombres", "apellidos")
    list_display_links = ("id", "numero_documento")
    search_fields = ("numero_documento", "nombres", "apellidos")
    filter_horizontal = ("complicaciones_diagnostico",)
    list_filter = (
        "diagnostico_hta",
        "diagnostico_erc",
        "diagnostico_epoc",
        "diagnostico_falla_cardiaca",
    )
    fieldsets = (
        (
            "Información general",
            {
                "fields": (
                    "nombres",
                    "apellidos",
                    ("tipo_documento", "numero_documento"),
                    "fecha_nacimiento",
                    "genero",
                    "grupo_etnico",
                    "estado_civil",
                    "nivel_estudios",
                    "estrato",
                )
            },
        ),
        (
            "Información de contacto",
            {
                "fields": (
                    "ciudad_contacto",
                    "direccion",
                    "barrio",
                    "telefono",
                    "telefono_emergencia",
                )
            },
        ),
        (
            "Asignación",
            {
                "fields": (
                    "eps",
                    "grupo_gestion",
                    "ciudad_asignacion",
                    "fecha_afiliacion",
                )
            },
        ),
        (
            "Perfilamiento",
            {
                "fields": (
                    "tipo_diabetes",
                    "fecha_diagnostico",
                    "diagnostico",
                    ("diagnostico_hta",),
                    (
                        "fecha_erc",
                        "etiologia_erc",
                    ),
                    (
                        "diagnostico_erc",
                        "estadio_erc",
                    ),
                    (
                        "diagnostico_epoc",
                        "diagnostico_falla_cardiaca",
                    ),
                    (
                        "fecha_colesterol",
                        "colesterol_total",
                    ),
                    (
                        "hdl",
                        "tas",
                        "tad",
                    ),
                    (
                        "es_fumador",
                        "nivel_riesgo_rcv",
                    ),
                    (
                        "estatura",
                        "peso",
                    ),
                    "complicaciones_diagnostico",
                    "estadio",
                    "programa_nefroproteccion",
                ),
            },
        ),
        (
            "Métricas",
            {"fields": ("tfg", "riesgo_cardiovascular", "ultimo_seguimiento", "hba1c")},
        ),
    )
    readonly_fields = (
        "estadio",
        "tfg",
        "nivel_riesgo_rcv",
        "riesgo_cardiovascular",
        "ultimo_seguimiento",
        "hba1c",
    )
    inlines = (
        _MedicacionInline,
        _ControlInline,
        _HospitalizacionInline,
        _ExamenInline,
        _MetaInline,
    )


class UsuarioInline(admin.TabularInline):
    model = Usuario
    filter_horizontal = ("grupos_gestion",)
    extra = 0
    max_num = 1


UserAdmin.inlines = (UsuarioInline,)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    filter_horizontal = ("grupos_gestion",)
    list_filter = ("todos_grupos_gestion",)
    list_display = ("fk_user_django", "todos_grupos_gestion")


@admin.register(VariablesClinicas)
class VariablesClinicasAdmin(admin.ModelAdmin):
    list_display = ("fk_paciente", "fecha_cargue")
    readonly_fields = ("estadio",)


@admin.register(CargueBackOffice)
class CargueBackOfficeAdmin(admin.ModelAdmin):
    pass
    # list_display = ('excel_file',)
