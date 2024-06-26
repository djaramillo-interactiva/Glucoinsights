from typing import List, Tuple

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.utils.timezone import now, datetime
import pandas as pd
from gi.constants import (
    DEPARTAMENTOS_COLOMBIA_CHOICES,
    DM_CIE_10,
    HTA_CIE_10,
    ERC_CIE_10,
    OTROS_CIE_10,
    CARGUE_ESTADIO_ERC,
)


class GrupoEtareo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    edad_inicio = models.PositiveIntegerField(default=0, verbose_name="Edad inicio")
    edad_fin = models.PositiveIntegerField(default=0, verbose_name="Edad fin")

    def __str__(self):
        return f"{self.nombre} ({self.edad_inicio} - {self.edad_fin})"

    def get_pacientes(self, user):
        from .utils import add_years, get_pacientes_usuario

        today = now()
        min_limit = add_years(today, -self.edad_inicio)
        max_limit = add_years(today, -self.edad_fin)
        qs_pacientes = get_pacientes_usuario(user=user)
        return qs_pacientes.filter(
            fecha_nacimiento__gte=max_limit, fecha_nacimiento__lte=min_limit
        )

    class Meta:
        ordering = ("edad_inicio", "edad_fin")
        verbose_name = "Parámetros - Grupo etáreo"
        verbose_name_plural = "Parámetros - Grupos etáreos"


class Indicador(models.Model):
    TIPO_INDICADOR_HTA = "HTA"
    TIPO_INDICADOR_DM = "DM"
    TIPO_INDICADOR_ERC = "ERC"
    TIPO_INDICADOR_OTROS = "Otros"
    tipos_choices = (
        (TIPO_INDICADOR_HTA, "HTA"),
        (TIPO_INDICADOR_DM, "DM"),
        (TIPO_INDICADOR_ERC, "ERC"),
        (TIPO_INDICADOR_OTROS, "Otros"),
    )

    tipo = models.CharField(max_length=100, choices=tipos_choices, verbose_name="Tipo")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    slug = models.SlugField(verbose_name="Slug", default="", unique=True)
    medida = models.CharField(max_length=100, verbose_name="Medida", default="")
    tendencia = models.BooleanField(
        verbose_name="Tendencia",
        default=True,
        help_text="Check: Valor es positivo si valor actual > meta. "
        "No check: Valor es positivo si valor actual < meta.",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    meta = models.FloatField(verbose_name="Meta")

    # TODO este valor es calculado
    valor_actual = models.FloatField(verbose_name="Valor actual", default=0)

    def __str__(self):
        return f"{self.tipo} - {self.nombre}"

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "nombre": self.nombre,
            "orden": self.order,
            "descripcion": self.descripcion,
            "meta": self.meta,
        }

    class Meta:
        ordering = ("order", "tipo", "nombre")
        unique_together = ("tipo", "nombre")
        verbose_name = "Parámetros - Indicador"
        verbose_name_plural = "Parámetros - Indicadores"


class Tarea(models.Model):
    _help_text = 'Recuerde que si el nombre de la tarea es "Servicio / Intervención" se considera de sólo lectura'
    nombre = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre", help_text=_help_text
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return self.nombre

    @property
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "data": list(
                ServicioTarea.objects.filter(fk_tarea=self).values(
                    "id", "nombre", "cantidad"
                )
            ),
            "readonly": self.nombre == "Servicio / Intervención",
        }

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Tarea"
        verbose_name_plural = "Parámetros - Tareas"


class ServicioTarea(models.Model):
    service_choices = (("Pruebas", "Pruebas"), ("Placeholder", "Placeholder"))

    fk_tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, verbose_name="Tarea")

    nombre = models.CharField(
        max_length=100, verbose_name="Nombre", choices=service_choices
    )
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return f"{self.fk_tarea} | {self.nombre}"

    class Meta:
        ordering = ("order", "nombre")
        unique_together = ("fk_tarea_id", "nombre")
        verbose_name = "Parámetros - Servicio"
        verbose_name_plural = "Parámetros - Servicios"


class GrupoPacientes(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.CharField(max_length=100, verbose_name="Slug", default="")
    servicios_tarea = models.ManyToManyField(
        ServicioTarea, verbose_name="Servicios", blank=True
    )
    pacientes = models.ManyToManyField("Paciente", verbose_name="Pacientes", blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Grupo de pacientes"
        verbose_name_plural = "Parámetros - Grupos de pacientes"


class Medicacion(models.Model):
    _choices_categoria = (
        ("IECA", "IECA"),
        ("ARA II", "ARA II"),
        ("TIAZIDAS", "TIAZIDAS"),
        ("Otro", "Otro"),
        ("", "Sin categoría"),
    )

    nombre = models.CharField(
        max_length=100, unique=True, choices=_choices_categoria, verbose_name="Nombre"
    )
    categoria = models.CharField(max_length=100, default="", verbose_name="Categoría")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return f"{self.nombre}"

    @classmethod
    def get_categorias(cls, include_empty):
        return [
            {"label": t[1], "value": t[0]}
            for t in cls._choices_categoria
            if t[0] != "" or (include_empty and t[0] == "")
        ]

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Medicación"
        verbose_name_plural = "Parámetros - Medicaciones"


class Eps(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - EPS"
        verbose_name_plural = "Parámetros - EPS"


class Ciudad(models.Model):
    departamento = models.CharField(
        max_length=100,
        choices=DEPARTAMENTOS_COLOMBIA_CHOICES,
        verbose_name="Departamento",
    )
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Ciudad"
        verbose_name_plural = "Parámetros - Ciudades"


class GrupoGestion(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    ciudades = models.ManyToManyField(Ciudad, verbose_name="Ciudades", blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Grupo de gestión"
        verbose_name_plural = "Parámetros - Grupos de gestión"


class Complicacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Complicación"
        verbose_name_plural = "Parámetros - Complicaciones"


class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ("order", "nombre")
        verbose_name = "Parámetros - Tratamiento"
        verbose_name_plural = "Parámetros - Tratamientos"


# Usuarios #
class Usuario(models.Model):
    fk_user_django = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Usuario en el sistema"
    )
    todos_grupos_gestion = models.BooleanField(
        verbose_name="¿Tiene todos los grupos de gestión?", default=False
    )
    grupos_gestion = models.ManyToManyField(
        GrupoGestion, verbose_name="Grupos de gestión", blank=True
    )

    class Meta:
        ordering = ("fk_user_django__username",)
        verbose_name = "Usuario Plataforma"
        verbose_name_plural = "Usuarios Plataforma"

    @property
    def role(self):
        role = self.fk_user_django.groups.values_list("name", flat=True).first()
        return role or ""

    @property
    def to_dict(self):
        if self.todos_grupos_gestion:
            grupos_gestion = []
        else:
            grupos_gestion = list(
                self.grupos_gestion.all()
                .annotate(slug=F("id"), label=F("nombre"))
                .values("slug", "label")
            )

        return {
            "id": self.id,
            "slug": self.id,
            "name": self.fk_user_django.username,
            "role": self.role,
            "todos_grupos_gestion": "Sí" if self.todos_grupos_gestion else "No",
            "grupos_gestion": grupos_gestion,
            "mail": self.fk_user_django.email,
            "actions": [{"icon": "edit", "iconStyle": "outlined", "slug": "edit"}],
        }


# Pacientes
class Paciente(models.Model):
    GENERO_MASCULINO = "Masculino"
    GENERO_FEMENINO = "Femenino"

    TIPO_DIABETES_SIN_CLASIFICACION = "No tiene DM"
    # TIPO_DIABETES_1 = "Diabetes tipo I"
    # TIPO_DIABETES_2 = "Diabetes tipo II"
    # TIPO_DIABETES_2_I = "Diabetes tipo II - insulinorequiriente"

    SIN_DIAGNOSTICO_CIE10 = ""

    NIVEL_RIESGO_RCV_SIN_INFO = "Sin información"
    NIVEL_RIESGO_RCV_BAJO = "Bajo"
    NIVEL_RIESGO_RCV_MODERADO = "Moderado"
    NIVEL_RIESGO_RCV_ALTO = "Alto"
    NIVEL_RIESGO_RCV_MUY_ALTO = "Muy alto"

    ULTIMO_SEGUIMIENTO_MENOS_DE_UN_MES = "Menos de un mes"
    ULTIMO_SEGUIMIENTO_DE_1_A_6_MESES = "De 1 a 6 meses"
    ULTIMO_SEGUIMIENTO_DE_6_A_12_MESES = "De 6 a 12 meses"
    ULTIMO_SEGUIMIENTO_MAS_DE_12_MESES = "Más de 12 meses"

    ESTADIO_SIN_CALCULAR = "Sin calcular"
    ESTADIO_1 = "Estadio 1"
    ESTADIO_2 = "Estadio 2"
    ESTADIO_3a = "Estadio 3a"
    ESTADIO_3b = "Estadio 3b"
    ESTADIO_4 = "Estadio 4"
    ESTADIO_5 = "Estadio 5"
    
    ESTADIO_SIN_CALCULAR_ERC = "0"
    ESTADIO_1_ERC = "1"
    ESTADIO_2_ERC = "2"
    ESTADIO_3a_ERC = "3a"
    ESTADIO_3b_ERC = "3b"
    ESTADIO_4_ERC = "4"
    ESTADIO_5_ERC = "5"

    _tipos_documento_choices = (
        ("RC", "RC"),
        ("TI", "TI"),
        ("CC", "CC"),
        ("CE", "CE"),
        ("PS", "PS"),
        ("MI", "MI."),
        ("AI", "AI"),
        ("CD", "CD"),
        ("SP", "SP"),
        ("PE", "PE"),
        ("PPT", "PPT"),
        ("No se cargo tipo de documento", "No se cargo tipo de documento"),
    )
    _generos_choices = ((GENERO_MASCULINO, "Masculino"), (GENERO_FEMENINO, "Femenino"), ("No se cargo género","No se cargo género"))
    _grupo_etnico_choices = (
        ("Indigena", "Indigena"),
        ("ROM (gitano)", "ROM (gitano)"),
        (
            "Raizal del archipiélago de San Andrés y Providencia",
            "Raizal del archipiélago de San Andrés y Providencia",
        ),
        ("Palenquero de San Basilio", "Palenquero de San Basilio"),
        (
            "Negro(a), mulato(a), afro colombiano(a) o afro descendiente",
            "Negro(a), mulato(a), afro colombiano(a) o afro descendiente",
        ),
        ("Ninguna de las anteriores", "Ninguna de las anteriores"),
        ("No se cargo grupo etnico","No se cargo grupo etnico"),
    )
    _estado_civil_choices = (
        ("Soltero", "Soltero"),
        ("Casado", "Casado"),
        ("Unión libre", "Unión libre"),
        ("Viudo", "Viudo"),
        ("No se cargo estado civil","No se cargo estado civil")
    )
    _nivel_estudio_choices = (
        ("Primaria", "Primaria"),
        ("Bachiller", "Bachiller"),
        ("Técnico/Tecnólogo", "Técnico/Tecnólogo"),
        ("Universitario", "Universitario"),
        ("Posgrado", "Posgrado"),
        ("No se cargo nivel de estudio","No se cargo nivel de estudio")
    )
    _estrato_choices = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
    )
    _tipos_diabetes_choices = (
        ("No tiene DM", "No tiene DM"),
        ("Diabetes tipo I", "Diabetes tipo I"),
        ("Diabetes tipo II", "Diabetes tipo II"),
        (
            "Otros (Posquirúrgica, postrasplante, secundaria a medicamentos, MODY)",
            "Otros (Posquirúrgica, postrasplante, secundaria a medicamentos, MODY)",
        ),
        ("No se cargo el tipo de diabetes","No se cargo el tipo de diabetes"),
    )
    _diagnosticos_choices = DM_CIE_10
    _niveles_riesgo_rcv_choices = (
        (NIVEL_RIESGO_RCV_SIN_INFO, "Sin información"),
        (NIVEL_RIESGO_RCV_BAJO, "Bajo"),
        (NIVEL_RIESGO_RCV_MODERADO, "Moderado"),
        (NIVEL_RIESGO_RCV_ALTO, "Alto"),
        (NIVEL_RIESGO_RCV_MUY_ALTO, "Muy alto"),
    )
    _estadios_choices = (
        (ESTADIO_SIN_CALCULAR, "Sin calcular"),
        (ESTADIO_1, "Estadio 1"),
        (ESTADIO_2, "Estadio 2"),
        (ESTADIO_3a, "Estadio 3a"),
        (ESTADIO_3b, "Estadio 3b"),
        (ESTADIO_4, "Estadio 4"),
        (ESTADIO_5, "Estadio 5"),
    )

    _etiologia_erc = (
        ("Enfermedad poliquística renal", "Enfermedad poliquística renal"),
        ("Otras", "Otras"),
        (
            "Desconocida o paciente en abandono (solo aplica para pacientes con ERC confirmada)",
            "Desconocida o paciente en abandono (solo aplica para pacientes con ERC confirmada)",
        ),
        ("Diabetes.", "Diabetes."),
        (
            "Enfermedad vascular renal (incluye Nefroangioesclerosis por hipertensión arterial).",
            "Enfermedad vascular renal (incluye Nefroangioesclerosis por hipertensión arterial).",
        ),
        (
            "Sospecha de glomerulonefritis sin biopsia renal.",
            "Sospecha de glomerulonefritis sin biopsia renal.",
        ),
        (
            "Glomeruloesclerosis focal y segmentaria.",
            "Glomeruloesclerosis focal y segmentaria.",
        ),
        ("Nefropatía membranosa", "Nefropatía membranosa"),
        ("Nefropatía por IgA", "Nefropatía por IgA"),
        ("Vasculitis", "Vasculitis"),
        ("Lupus eritematoso sistémico.", "Lupus eritematoso sistémico."),
        (
            "Glomerulopatía familiar o genética (incluye Alport).",
            "Glomerulopatía familiar o genética (incluye Alport).",
        ),
        ("Otra glomerulonefritis.", "Otra glomerulonefritis."),
        ("Síndrome hemolítico urémico.", "Síndrome hemolítico urémico."),
        (
            "Nefropatía tóxica (incluye analgésicos).",
            "Nefropatía tóxica (incluye analgésicos).",
        ),
        ("Nefritis intersticial.", "Nefritis intersticial."),
        (
            "Paraproteinemia (incluye mieloma múltiple).",
            "Paraproteinemia (incluye mieloma múltiple).",
        ),
        ("Nefropatía postparto.", "Nefropatía postparto."),
        ("Litiasis.", "Litiasis."),
        (
            "Displasia o hipoplasia renal congénita.",
            "Displasia o hipoplasia renal congénita.",
        ),
        (
            "Perdida de unidad renal por trauma o cirugía.",
            "Perdida de unidad renal por trauma o cirugía.",
        ),
        ("Carcinoma renal.", "Carcinoma renal."),
        (
            "Nefropatía por reflujo vesicoureteral.",
            "Nefropatía por reflujo vesicoureteral.",
        ),
        (
            "Obstrucción de cuello de la vejiga (Incluye HPB, cáncer de próstata, valvas, etc.),",
            "Obstrucción de cuello de la vejiga (Incluye HPB, cáncer de próstata, valvas, etc.),",
        ),
        (
            "Nefropatía obstructiva de causa diferente a 27 (incluye cáncer de cuello uterino, tumores retroperitoneales, etc.)",
            "Nefropatía obstructiva de causa diferente a 27 (incluye cáncer de cuello uterino, tumores retroperitoneales, etc.)",
        ),
        ("No aplica, no tiene ERC", "No aplica, no tiene ERC"),
        (
            "No aplica, paciente reportado por ente territorial por prestación de servicios no incluidos en el plan de beneficios",
            "No aplica, paciente reportado por ente territorial por prestación de servicios no incluidos en el plan de beneficios",
        ),
    )

    _estadio_erc_choices = CARGUE_ESTADIO_ERC
    
    _estadios_choices_erc = (
        (ESTADIO_SIN_CALCULAR_ERC, "0"),
        (ESTADIO_1_ERC, "1"),
        (ESTADIO_2_ERC, "2"),
        (ESTADIO_3a_ERC, "3a"),
        (ESTADIO_3b_ERC, "3b"),
        (ESTADIO_4_ERC, "4"),
        (ESTADIO_5_ERC, "5"),
    )

    # Datos paciente
    nombres = models.CharField(max_length=100, default="", verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, default="", verbose_name="Apellidos")
    tipo_documento = models.CharField(
        max_length=100,
        default="",
        choices=_tipos_documento_choices,
        verbose_name="Tipo de identificación",
    )
    numero_documento = models.CharField(
        max_length=100, default="", verbose_name="Número de documento"
    )
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento", default=now)
    genero = models.CharField(
        max_length=100, default="", choices=_generos_choices, verbose_name="Género"
    )
    grupo_etnico = models.CharField(
        max_length=100,
        default="",
        choices=_grupo_etnico_choices,
        verbose_name="Grupo étnico",
    )
    estado_civil = models.CharField(
        max_length=100,
        default="",
        choices=_estado_civil_choices,
        verbose_name="Estado civil",
    )
    nivel_estudios = models.CharField(
        max_length=100,
        default="",
        choices=_nivel_estudio_choices,
        verbose_name="Nivel de estudios",
    )
    estrato = models.CharField(
        max_length=100, default="", choices=_estrato_choices, verbose_name="Estrato"
    )
    direccion = models.CharField(max_length=300, default="", verbose_name="Dirección")
    barrio = models.CharField(max_length=100, default="", verbose_name="Barrio")
    telefono = models.CharField(max_length=100, default="", verbose_name="Teléfono")
    telefono_emergencia = models.CharField(
        max_length=100, default="", verbose_name="Teléfono contacto de emergencia"
    )
    fecha_afiliacion = models.DateField(verbose_name="Fecha de afiliación", default=now)

    # Diagnóstico

    tipo_diabetes = models.CharField(
        max_length=100, choices=_tipos_diabetes_choices, verbose_name="Tipo de diabetes"
    )
    fecha_diagnostico = models.DateField(default=now, verbose_name="Fecha diagnóstico")
    # Fecha diagnóstico  hipertensión renal -> Nuevo campo V.Piloto
    fecha_diagnostico_hipertension_renal = models.DateField(
        default=now, verbose_name="Fecha diagnóstico hipertensión renal"
    )
    diagnostico_hta = models.BooleanField(
        default=False, verbose_name="Diagnóstico - HTA"
    )

    diagnostico_erc = models.BooleanField(
        default=False, verbose_name="Diagnóstico - ERC"
    )

    # Etiologia de la Erc -> Nuevo campo V.Piloto
    etiologia_erc = models.CharField(
        max_length=200,
        default="",
        verbose_name="Etiologia de la Erc",
        choices=_etiologia_erc,
        blank=True,
    )
    # Fecha erc -> Nuevo campo V.Piloto
    fecha_erc = models.DateField(default=now, verbose_name="Fecha Erc")

    # Estadio ERC -> Nuevo campo V.Piloto
    estadio_erc = models.CharField(
        max_length=200,
        default="",
        verbose_name="Estadio ERC",
        choices=_estadio_erc_choices,
        blank=True,
    )

    diagnostico_epoc = models.BooleanField(
        default=False, verbose_name="Diagnóstico - EPOC"
    )
    diagnostico_hipoglicemia = models.BooleanField(
        default=False, verbose_name="Diagnóstico - Hipoglicemia"
    )
    diagnostico_falla_cardiaca = models.BooleanField(
        default=False, verbose_name="Diagnóstico - Falla cardíaca"
    )
    colesterol_total = models.FloatField(default=0, verbose_name="Colesterol total")

    # Fecha colesterol -> Nuevo campo V.Piloto
    fecha_colesterol = models.DateField(default=now, verbose_name="Fecha Colesterol")

    hdl = models.FloatField(
        default=0, verbose_name="Lipoproteína de alta densidad(hdl)"
    )
    tas = models.FloatField(default=0, verbose_name="Tensión arterial sistólica(tas)")
    tad = models.FloatField(default=75, verbose_name="tensión arterial diastólica(tad)")
    es_fumador = models.BooleanField(default=False, verbose_name="¿Es fumador?")
    nivel_riesgo_rcv = models.CharField(
        max_length=100,
        default="",
        verbose_name="Nivel de riesgo RCV",
        choices=_niveles_riesgo_rcv_choices,
        editable=False,
    )
    estatura = models.FloatField(default=0, verbose_name="Estatura")
    peso = models.FloatField(default=0, verbose_name="Peso")
    estadio = models.CharField(
        max_length=100,
        default="",
        verbose_name="Estadio",
        choices=_estadios_choices,
        blank=True,
        editable=False,
    )
    programa_nefroproteccion = models.CharField(
        max_length=100,
        default="",
        verbose_name="Programa de nefroprotección",
        blank=True,
    )

    # Métricas
    riesgo_cardiovascular = models.FloatField(
        default=0, null=True, editable=False, verbose_name="Riesgo Cardiovascular"
    )
    tfg = models.FloatField(default=0, null=True, editable=False, verbose_name="TFG")
    ultimo_seguimiento = models.DateField(
        verbose_name="Último seguimiento", default=now, editable=False
    )
    hba1c = models.FloatField(
        verbose_name="Hemoglobina glicosilada (Último registro)",
        default=0.0,
        editable=False,
    )

    eps = models.ForeignKey(
        Eps, on_delete=models.SET_NULL, verbose_name="EPS", null=True, blank=True
    )
    grupo_gestion = models.ForeignKey(
        GrupoGestion,
        on_delete=models.SET_NULL,
        verbose_name="Grupo de gestión",
        null=True,
        blank=True,
    )
    ciudad_asignacion = models.ForeignKey(
        Ciudad,
        on_delete=models.SET_NULL,
        verbose_name="Ciudad de asignación",
        null=True,
        blank=True,
        related_name="ciudad_asignacion",
    )
    # Este modelo contiene la ciudad y el departamento
    ciudad_contacto = models.ForeignKey(
        Ciudad,
        on_delete=models.SET_NULL,
        verbose_name="Ciudad de contacto",
        null=True,
        blank=True,
        related_name="ciudad_contacto",
    )

    diagnostico = models.CharField(
        max_length=100,
        default="",
        choices=_diagnosticos_choices,
        verbose_name="Diagnósticos",
        blank=True,
    )

    complicaciones_diagnostico = models.ManyToManyField(
        Complicacion, verbose_name="Complicaciones", blank=True
    )

    tratamientos = models.ManyToManyField(
        Tratamiento, verbose_name="Tratamientos", blank=True
    )

    @property
    def codigo_estado_nivel_riesgo_rcv(self):
        if self.nivel_riesgo_rcv == "Medio":
            self.nivel_riesgo_rcv = self.NIVEL_RIESGO_RCV_MODERADO

        mapper = {
            self.NIVEL_RIESGO_RCV_SIN_INFO: "0",
            self.NIVEL_RIESGO_RCV_BAJO: "1",
            self.NIVEL_RIESGO_RCV_MODERADO: "2",
            self.NIVEL_RIESGO_RCV_ALTO: "3",
            self.NIVEL_RIESGO_RCV_MUY_ALTO: "4",
        }
        return mapper.get(self.nivel_riesgo_rcv, "0")

    @property
    def codigo_estado_estadio(self):
        mapper = {
            self.ESTADIO_SIN_CALCULAR: "0",
            self.ESTADIO_1: "5",
            self.ESTADIO_2: "1",
            self.ESTADIO_3a: "2",
            self.ESTADIO_3b: "3",
            self.ESTADIO_4: "4",
            self.ESTADIO_5: "6",
        }
        return mapper.get(self.estadio, "1")

    @property
    def codigo_ultimo_seguimiento(self):
        _now = now().date()
        one_month = _now - relativedelta(months=1)
        six_months = _now - relativedelta(months=6)
        twelve_months = _now - relativedelta(months=12)

        if self.ultimo_seguimiento > one_month:
            return {
                "label": self.ULTIMO_SEGUIMIENTO_MENOS_DE_UN_MES,
                "textColor": "#0277BD",
                "backColor": "#B3E5FC",
            }
        elif one_month >= self.ultimo_seguimiento >= six_months:
            return {
                "label": self.ULTIMO_SEGUIMIENTO_DE_1_A_6_MESES,
                "textColor": "#2E7D32",
                "backColor": "#C8E6C9",
            }
        elif six_months >= self.ultimo_seguimiento > twelve_months:
            return {
                "label": self.ULTIMO_SEGUIMIENTO_DE_6_A_12_MESES,
                "textColor": "#EF6C00",
                "backColor": "#FFE0B2",
            }
        else:
            return {
                "label": self.ULTIMO_SEGUIMIENTO_MAS_DE_12_MESES,
                "textColor": "#C62828",
                "backColor": "#FFCDD2",
            }

    @property
    def num_meses_ultimo_seguimiento(self):
        diff = relativedelta(now().date(), self.ultimo_seguimiento)
        return diff.months + (12 * diff.years)

    @property
    def diagnosticos_adicionales(self):
        return [
            {"label": "HTA", "slug": "hta", "value": self.diagnostico_hta},
            {"label": "ERC", "slug": "erc", "value": self.diagnostico_erc},
            # {"label": "EPOC", "slug": "epoc", "value": self.diagnostico_epoc},
            {
                "label": "Falla cardíaca",
                "slug": "falla_cardiaca",
                "value": self.diagnostico_falla_cardiaca,
            },
            {
                "label": "Hipoglicemia",
                "slug": "hipoglicemia",
                "value": self.diagnostico_hipoglicemia,
            },
        ]

    @property
    def ultima_creatinina(self):
        ultimo_examen: ExamenPaciente = self.examenpaciente_set.order_by(
            "-fecha"
        ).first()
        return ultimo_examen.creatinina if ultimo_examen else None

    @property
    def edad_relativedelta(self):
        birthdatetime = datetime(
            year=self.fecha_nacimiento.year,
            month=self.fecha_nacimiento.month,
            day=self.fecha_nacimiento.day,
        )
        return relativedelta(now().date(), birthdatetime.date())

    def get_metas(self) -> Tuple[float, List[dict]]:
        individuales = []
        numerador = 0
        num_metas = 0
        metas_paciente = self.metapaciente_set.all()
        for meta in metas_paciente:
            to_append = meta.to_dict()
            numerador += to_append["porcentaje_cumplimiento"]
            individuales.append(to_append)
            num_metas += 1

        avance_global = (numerador / num_metas) if num_metas > 0 else 0

        return avance_global, individuales

    def actualizar_riesgo_tfg(self, save=True, creatinina_externa=0):
        from gi.utils import calcular_tfg

        current_tfg = self.tfg

        self.tfg = (
            calcular_tfg(
                genero=self.genero,
                edad=self.edad_relativedelta.years,
                peso=self.peso,
                creatinina=creatinina_externa or self.ultima_creatinina,
            )
            or current_tfg
        )
        if self.tfg is not None:
            if self.tfg > 0:
                if self.tfg > 90:
                    self.estadio_ = self.ESTADIO_1
                elif 60 < self.tfg <= 90:
                    self.estadio = self.ESTADIO_2
                elif 45 < self.tfg <= 60:
                    self.estadio = self.ESTADIO_3a
                elif 30 < self.tfg <= 45:
                    self.estadio = self.ESTADIO_3b
                elif 15 <= self.tfg <= 30:
                    self.estadio = self.ESTADIO_4
                elif self.tfg < 15:
                    self.estadio = self.ESTADIO_5
            else:
                self.estadio = self.ESTADIO_SIN_CALCULAR
        else:
            self.estadio = self.ESTADIO_SIN_CALCULAR

        if save:
            self.save()

    def actualizar_riesgocardiovascular(self, save=True):
        from gi.utils import calcular_riesgo_cardiovascular

        current_risk = self.riesgo_cardiovascular

        self.riesgo_cardiovascular = (
            calcular_riesgo_cardiovascular(
                genero=self.genero,
                edad=self.edad_relativedelta.years,
                colesterol=self.colesterol_total,
                tas=self.tas,
                diabetes=True,
                fumador=self.es_fumador,
            )
            # or current_risk
        )
        print("self.riesgo_cardiovascular----------------")
        print(self.riesgo_cardiovascular)

        if self.riesgo_cardiovascular == 0:
            self.nivel_riesgo_rcv = self.NIVEL_RIESGO_RCV_SIN_INFO
        elif self.riesgo_cardiovascular < 0.1:
            self.nivel_riesgo_rcv = self.NIVEL_RIESGO_RCV_BAJO
        elif self.riesgo_cardiovascular < 0.2:
            self.nivel_riesgo_rcv = self.NIVEL_RIESGO_RCV_MODERADO
        elif self.riesgo_cardiovascular < 0.3:
            self.nivel_riesgo_rcv = self.NIVEL_RIESGO_RCV_ALTO
        else:
            self.nivel_riesgo_rcv = self.NIVEL_RIESGO_RCV_MUY_ALTO

        if save:
            self.save()

    def actualizar_ultimo_seguimiento(self, save=True):
        self.ultimo_seguimiento = now()
        if save:
            self.save()

    def actualizar_hba1c(self, save=True):
        e = ExamenPaciente.objects.filter(fk_paciente=self).order_by("-fecha").first()
        if e and e.hemoglobina_glicosilada:
            self.hba1c = e.hemoglobina_glicosilada
            if save:
                self.save()

    @classmethod
    def get_tipos_documento(cls):
        return [{"label": t[1], "value": t[0]} for t in cls._tipos_documento_choices]

    @classmethod
    def get_generos(cls):
        return [{"label": g[1], "value": g[0]} for g in cls._generos_choices]

    @classmethod
    def get_grupos_etnicos(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._grupo_etnico_choices]

    @classmethod
    def get_estados_civiles(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._estado_civil_choices]

    @classmethod
    def get_niveles_estudio(cls):
        return [{"label": n[1], "value": n[0]} for n in cls._nivel_estudio_choices]

    @classmethod
    def get_estratos(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._estrato_choices]

    @staticmethod
    def get_departamentos_ciudades():
        cities = Ciudad.objects.annotate(label=models.F("nombre"), value=models.F("id"))
        return [
            {
                "label": e[1],
                "value": e[0],
                "cities": list(
                    cities.filter(departamento=e[0]).values("label", "value")
                ),
            }
            for e in DEPARTAMENTOS_COLOMBIA_CHOICES
        ]

    @staticmethod
    def get_ciudades():
        return list(
            Ciudad.objects.annotate(
                label=models.F("nombre"), value=models.F("id")
            ).values("label", "value")
        )

    @classmethod
    def get_tipos_diabetes(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._tipos_diabetes_choices]

    @classmethod
    def get_diagnosticos(cls):
        return [
            {"label": f"{e[0]} {e[1]}", "value": e[0]}
            for e in cls._diagnosticos_choices
        ]

    @classmethod
    def get_niveles_riesgo_rcv(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._niveles_riesgo_rcv_choices]

    @classmethod
    def get_estadios(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._estadios_choices]

    @classmethod
    def get_eps_list(cls):
        return list(
            Eps.objects.values(value=models.F("id"), label=models.F("nombre")).values(
                "label", "value"
            )
        )
    
    @classmethod
    def get_estadios_erc(cls):
        return [
            {"label": f"{e[0]} {e[1]}", "value": e[0]}
            for e in cls._estadio_erc_choices
        ]
        
    #NUEVO
    @classmethod
    def get_estadios_erc_2(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._estadios_choices_erc]
    #FIN

    @classmethod
    def get_grupos_gestion_list(cls, user):
        from .utils import get_grupos_gestion_usuario

        grupos_gestion_qs = get_grupos_gestion_usuario(user)
        return list(
            grupos_gestion_qs.values(
                value=models.F("id"), label=models.F("nombre")
            ).values("label", "value")
        )

    class Meta:
        unique_together = ("tipo_documento", "numero_documento")
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.nombres} {self.apellidos} {self.numero_documento}"


class MedicacionPaciente(models.Model):
    fk_paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, verbose_name="Paciente"
    )
    fk_medicacion = models.ForeignKey(
        Medicacion, on_delete=models.CASCADE, verbose_name="Medicación"
    )
    dosis_mg = models.FloatField(verbose_name="Dosis", default=0)
    fecha_formulacion = models.DateField(verbose_name="Fecha de formulación")
    tiempo_formulacion_meses = models.PositiveIntegerField(
        verbose_name="Tiempo de formulación"
    )

    class Meta:
        unique_together = ("fk_paciente_id", "fk_medicacion_id")
        verbose_name = "Paciente - Medicación"
        verbose_name_plural = "Paciente - Medicaciones"


class ControlPaciente(models.Model):
    fk_paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, verbose_name="Paciente"
    )
    fk_cargue = models.ForeignKey(
        "CargueBackOffice",
        on_delete=models.SET_NULL,
        verbose_name="Cargue asociado",
        null=True,
        default=None,
    )

    TIPO_HOSPITALIZACION = "Hospitalización"
    TIPO_URGENCIAS = "Urgencias"
    TIPO_FALLECIMIENTO = "Fallecimiento"

    _tipo_choices = (
        (TIPO_HOSPITALIZACION, "Hospitalización"),
        (TIPO_URGENCIAS, "Urgencias"),
        (TIPO_FALLECIMIENTO, "Fallecimiento"),
    )

    tipo = models.CharField(max_length=100, choices=_tipo_choices, verbose_name="Tipo")

    tas = models.FloatField(verbose_name="PAS", null=True, blank=True)
    tad = models.FloatField(verbose_name="PAD", null=True, blank=True)
    peso = models.FloatField(verbose_name="Peso", null=True, blank=True)
    glucometria = models.FloatField(verbose_name="Glucometría", null=True, blank=True)

    numero_eventos_hipoglicemia = models.IntegerField(
        default=0,
        verbose_name="Número de eventos de hipoglicemia desede el último control",
    )

    observaciones = models.TextField(
        default="", verbose_name="Observaciones", blank=True
    )
    tiene_soporte = models.BooleanField(default=False, verbose_name="¿Tiene soporte?")
    fecha = models.DateField(default=now, verbose_name="Fecha")

    class Meta:
        verbose_name = "Paciente - Control"
        verbose_name_plural = "Paciente - Controles"
        ordering = ("-fecha",)

    @classmethod
    def get_tipos_p(cls) -> list:
        return [{"label": z[1], "value": z[0]} for z in cls._tipo_choices]

    @classmethod
    def get_tipos(cls) -> list:
        tareas = [t.to_dict for t in Tarea.objects.all()]

        return [
            {
                "name": t["nombre"],
                "options": [
                    {"label": x["nombre"], "value": x["nombre"]} for x in t["data"]
                ],
            }
            for t in tareas
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "tas": self.tas,
            "tad": self.tad,
            "peso": self.peso,
            "glucometria": self.glucometria,
            "numero_eventos_hipoglicemia": self.numero_eventos_hipoglicemia,
            "fecha": self.fecha.strftime("%Y-%m-%d"),
            "observaciones": self.observaciones,
            "soporte": self.tiene_soporte,
        }


class HospitalizacionPaciente(models.Model):
    TIPO_HOSPITALIZACION = "Hospitalización"
    TIPO_URGENCIAS = "Urgencias"
    TIPO_FALLECIMIENTO = "Fallecimiento"

    _tipos_choices = (
        (TIPO_HOSPITALIZACION, "Hospitalización"),
        (TIPO_URGENCIAS, "Urgencias"),
        (TIPO_FALLECIMIENTO, "Fallecimiento"),
    )

    fk_paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, verbose_name="Paciente"
    )
    fk_cargue = models.ForeignKey(
        "CargueBackOffice",
        on_delete=models.SET_NULL,
        verbose_name="Cargue asociado",
        null=True,
        default=None,
    )

    diagnostico_cie = models.CharField(
        max_length=100, verbose_name="Diagnóstico CIE asociado", blank=True, default=""
    )
    tipo = models.CharField(max_length=100, choices=_tipos_choices, verbose_name="Tipo")
    era_evitable = models.BooleanField(default=False, verbose_name="¿Era evitable?")
    relacionado_con_diabetes = models.BooleanField(
        default=False, verbose_name="¿Relacionado con diabetes?"
    )
    observaciones = models.TextField(
        default="", verbose_name="Observaciones", blank=True
    )
    tiene_soporte = models.BooleanField(default=False, verbose_name="¿Tiene soporte?")
    fecha = models.DateField(default=now, verbose_name="Fecha")

    class Meta:
        verbose_name = "Paciente - Hospitalización"
        verbose_name_plural = "Paciente - Hospitalizaciones"
        ordering = ("-fecha",)

    @classmethod
    def get_tipos(cls) -> list:
        return [{"label": t[1], "value": t[0]} for t in cls._tipos_choices]

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "era_evitable": self.era_evitable,
            "relacionado_con_diabetes": self.relacionado_con_diabetes,
            "fecha": self.fecha.strftime("%Y-%m-%d"),
            "observaciones": self.observaciones,
            "soporte": self.tiene_soporte,
        }

    @classmethod
    def get_diagnosticos(cls):
        return [
            {
                "name": "HTA",
                "options": [
                    {"label": label, "value": value} for value, label in HTA_CIE_10
                ],
            },
            {
                "name": "DM",
                "options": [
                    {"label": label, "value": value} for value, label in DM_CIE_10
                ],
            },
            {
                "name": "ERC",
                "options": [
                    {"label": label, "value": value} for value, label in ERC_CIE_10
                ],
            },
            {
                "name": "OTROS",
                "options": [
                    {"label": label, "value": value} for value, label in OTROS_CIE_10
                ],
            },
        ]


class ExamenPaciente(models.Model):
    fk_paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, verbose_name="Paciente"
    )
    fk_cargue = models.ForeignKey(
        "CargueBackOffice",
        on_delete=models.SET_NULL,
        verbose_name="Cargue asociado",
        null=True,
        default=None,
    )

    tsh = models.FloatField(default=0, verbose_name="TSH")
    alat = models.FloatField(default=0, verbose_name="ALAT")
    glicemia_basal = models.FloatField(default=0, verbose_name="Glicemia basal")
    asat = models.FloatField(default=0, verbose_name="ASAT")
    microalbuminuria = models.FloatField(default=0, verbose_name="Albuminuria")
    creatinina = models.FloatField(default=0, verbose_name="Creatinina")
    hdl = models.FloatField(default=0, verbose_name="HDL")
    ldl = models.FloatField(default=0, verbose_name="LDL")
    # colesterol_total -> Campo nuevo Versión Piloto
    colesterol_total = models.FloatField(default=0, verbose_name="Colesterol total")

    # ct = trigliceridos
    ct = models.FloatField(default=0, verbose_name="Trigliceridos")
    hemoglobina_glicosilada = models.FloatField(
        default=0, verbose_name="Hemoglobina glicosilada"
    )

    fecha = models.DateField(default=now, verbose_name="Fecha")

    class Meta:
        ordering = ("-fecha",)
        verbose_name = "Paciente - Examen"
        verbose_name_plural = "Paciente - Examenes"

    def to_dict(self):
        return {
            "fecha": self.fecha.strftime("%Y-%m-%d"),
            "id": self.id,
            "tsh": self.tsh,
            "alat": self.alat,
            "glicemia": self.glicemia_basal,
            "asat": self.asat,
            "micro": self.microalbuminuria,
            "creatinina": self.creatinina,
            "hdl": self.hdl,
            "ldl": self.ldl,
            "ct": self.ct,
            "hemoglobina_glicosilada": self.hemoglobina_glicosilada,
        }


class MetaPaciente(models.Model):
    TIPO_META_PESO = "Peso"
    TIPO_META_HEMOGLOBINA_GLICOSILADA = "Hemoglobina glicosilada"
    TIPO_META_TAS = "Presión arterial sistólica"
    TIPO_META_TAD = "Presión arterial diastólica"
    TIPO_META_MICROALBUMINURIA = "Microalbuminuria"

    _tipos_choices = (
        (TIPO_META_PESO, "Peso"),
        (TIPO_META_HEMOGLOBINA_GLICOSILADA, "Hemoglobina glicosilada"),
        (TIPO_META_TAS, "Presión arterial sistólica"),
        (TIPO_META_TAD, "Presión arterial diastólica"),
        (TIPO_META_MICROALBUMINURIA, "Microalbuminuria"),
    )

    fk_paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, verbose_name="Paciente"
    )
    tipo = models.CharField(max_length=100, choices=_tipos_choices, verbose_name="tipo")
    meta = models.FloatField(default=0, verbose_name="Meta")
    fecha_inicio = models.DateField(verbose_name="Fecha inicio")
    fecha_fin = models.DateField(verbose_name="Fecha fin")

    class Meta:
        ordering = ("fecha_inicio", "fecha_fin")
        verbose_name = "Paciente - Meta"
        verbose_name_plural = "Paciente - Metas"

    @classmethod
    def get_tipos(cls):
        return [{"label": e[1], "value": e[0]} for e in cls._tipos_choices]

    def to_dict(self):
        if self.tipo == self.TIPO_META_PESO:
            control: ControlPaciente = (
                self.fk_paciente.controlpaciente_set.filter(peso__isnull=False)
                .order_by("-fecha")
                .first()
            )
            value = control.peso if control else 0
            unidad = "kg"
        elif self.tipo == self.TIPO_META_TAS:
            control: ControlPaciente = (
                self.fk_paciente.controlpaciente_set.filter(tas__isnull=False)
                .order_by("-fecha")
                .first()
            )
            value = control.tas if control else 0
            unidad = ""
        elif self.tipo == self.TIPO_META_TAD:
            control: ControlPaciente = (
                self.fk_paciente.controlpaciente_set.filter(tad__isnull=False)
                .order_by("-fecha")
                .first()
            )
            value = control.tad if control else 0
            unidad = ""
        elif self.tipo == self.TIPO_META_HEMOGLOBINA_GLICOSILADA:
            examen: ExamenPaciente = (
                self.fk_paciente.examenpaciente_set.filter(
                    hemoglobina_glicosilada__isnull=False
                )
                .order_by("-fecha")
                .first()
            )
            value = examen.hemoglobina_glicosilada if examen else 0
            unidad = "%"
        elif self.tipo == self.TIPO_META_MICROALBUMINURIA:
            examen: ExamenPaciente = (
                self.fk_paciente.examenpaciente_set.filter(
                    microalbuminuria__isnull=False
                )
                .order_by("-fecha")
                .first()
            )
            value = examen.microalbuminuria if examen else 0
            unidad = ""
        else:
            value = 0
            unidad = ""

        tiempo = self.fecha_fin - self.fecha_inicio
        cumplimiento = (self.meta / value) if value > 0 else 0
        cumplimiento = cumplimiento if cumplimiento <= 1 else 1
        return {
            "id": self.id,
            "fecha_inicio": self.fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_limite": self.fecha_fin.strftime("%Y-%m-%d"),
            "tiempo": f"{tiempo.days} días",
            "concepto": self.tipo,
            "meta": f"{self.meta}",
            "unidad": unidad,
            "cumplimiento": "{0:.1%}".format(cumplimiento),
            "porcentaje_cumplimiento": cumplimiento,
        }


class IndicadorSnapshot(models.Model):
    fk_indicador = models.ForeignKey(
        Indicador, models.PROTECT, verbose_name="Indicador"
    )
    fk_grupo_gestion = models.ForeignKey(
        GrupoGestion,
        models.SET_NULL,
        verbose_name="Grupo Gestión",
        null=True,
        blank=True,
    )
    month = models.IntegerField(verbose_name="Més")
    year = models.IntegerField(verbose_name="Año")
    value = models.FloatField(verbose_name="Valor")

    class Meta:
        verbose_name = "Historico mensual indicador"
        verbose_name_plural = "Historicos mensuales indicador"

    def __str__(self):
        return f"{self.fk_indicador} ({self.month} {self.year})"


class CargueBackOffice(models.Model):
    excel_file = models.FileField(
        upload_to="cargues/",
        verbose_name="Archivo del cargue",
        help_text="Archivo excel segun template",
    )
    month = models.IntegerField(verbose_name="Mes", default=1)
    year = models.IntegerField(verbose_name="Año", default=2022)
    upload_date = models.DateTimeField(
        verbose_name="Fecha de subida", auto_now_add=True
    )
    observations = models.TextField(
        verbose_name="Observaciones", default="", blank=True
    )
    data_type = models.CharField(
        verbose_name="Tipo del cargue", default="pacientes", blank=True, max_length=20
    )
    user = models.ForeignKey(
        User, verbose_name="Usuario", on_delete=models.SET_NULL, default=None, null=True
    )

    class Meta:
        verbose_name = "Cargue excel"
        verbose_name_plural = "Cargues excel"

    def delete_related(self):
        if self.data_type == "pacientes":
            VariablesClinicas.objects.filter(fk_cargue=self).delete()
            Paciente.objects.filter(variablesclinicas__isnull=True).delete()
        if self.data_type == "hospitalizaciones":
            HospitalizacionPaciente.objects.filter(fk_cargue=self).delete()
        if self.data_type == "controles":
            ControlPaciente.objects.filter(fk_cargue=self).delete()
        if self.data_type == "examenes":
            ExamenPaciente.objects.filter(fk_cargue=self).delete()

    def __str__(self):
        return f"Cargue {self.data_type} - {self.month} {self.year}"


class VariablesClinicas(models.Model):
    # Examenes
    fk_paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, verbose_name="Paciente"
    )
    fk_cargue = models.ForeignKey(
        CargueBackOffice,
        on_delete=models.SET_NULL,
        verbose_name="Cargue asociado",
        null=True,
        default=None,
    )

    tsh = models.FloatField(default=0, verbose_name="TSH")
    alat = models.FloatField(default=0, verbose_name="ALAT")
    glicemia_basal = models.FloatField(default=0, verbose_name="Glicemia basal")
    asat = models.FloatField(default=0, verbose_name="ASAT")
    # Fecha albuminuria -> Nuevo campo V.Piloto
    fecha_albuminuria = models.DateField(default=now, verbose_name="Fecha albuminuria")
    microalbuminuria = models.FloatField(default=0, verbose_name="Albuminuria")
    # Fecha creatinina -> Nuevo campo V.Piloto
    fecha_creatinina = models.DateField(default=now, verbose_name="Fecha creatinina")
    creatinina = models.FloatField(default=0, verbose_name="Creatinina")
    # Fecha hdl -> Nuevo campo V.Piloto
    fecha_hdl = models.DateField(default=now, verbose_name="Fecha HDL")
    hdl = models.FloatField(default=0, verbose_name="HDL")
    ldl = models.FloatField(default=0, verbose_name="LDL")
    fecha_ldl = models.DateField(default=now, verbose_name="Fecha LDL")
    # ct = trigliceridos
    ct = models.FloatField(default=0, verbose_name="Trigliceridos")
    # Fecha Hemoglobina glicosilada -> Nuevo campo V.Piloto
    fecha_hemoglobina_glicosilada = models.DateField(
        default=now, verbose_name="Fecha hemoglobina glicosilada"
    )
    hemoglobina_glicosilada = models.FloatField(
        default=0, verbose_name="Hemoglobina glicosilada"
    )
    # Fecha creatinuria -> Nuevo campo V.Piloto
    fecha_creatinuria = models.DateField(default=now, verbose_name="Fecha creatinuria")
    # relacion_microalbuminuria_creatinuria -> Nuevo campo V.Piloto
    relacion_microalbuminuria_creatinuria = models.FloatField(
        default=0, verbose_name="Relacion microalbuminuria-creatinuria"
    )
    # Evento Cardiovascular -> Nuevo campo V.Piloto
    evento_cardiovascular = models.BooleanField(
        default=False, verbose_name="Evento Cardiovascular"
    )

    # Controles
    tas = models.FloatField(verbose_name="PAS", null=True, blank=True)
    tad = models.FloatField(verbose_name="PAD", null=True, blank=True)
    peso = models.FloatField(verbose_name="Peso", null=True, blank=True)
    glucometria = models.FloatField(verbose_name="Glucometría", null=True, blank=True)

    numero_eventos_hipoglicemia = models.IntegerField(
        default=0,
        verbose_name="Número de eventos de hipoglicemia desede el último control",
    )

    fecha_hta = models.DateField(default=now, verbose_name="Fecha")
    fecha_erc = models.DateField(default=now, verbose_name="Fecha")
    fecha_dm = models.DateField(default=now, verbose_name="Fecha", null=True)

    fecha_diag_hipoglicemia = models.DateField(
        null=True, default=None, verbose_name="Fecha diagnóstico - Hipoglicemia"
    )

    numero_hospitalizaciones = models.IntegerField(
        default=0, verbose_name="Numero de hospitalizaciones en el mes"
    )

    colesterol_total = models.FloatField(default=0, verbose_name="Colesterol total")

    nivel_riesgo_rcv = models.CharField(
        max_length=100, default="", verbose_name="Nivel de riesgo RCV", editable=False
    )
    estatura = models.FloatField(default=0, verbose_name="Estatura")
    estadio = models.CharField(
        max_length=100,
        default="",
        verbose_name="Estadio enfermedad renal",
        blank=True,
        editable=False,
    )

    tfg = models.FloatField(default=0, null=True, verbose_name="TFG")
    hba1c = models.FloatField(
        verbose_name="Hemoglobina glicosilada (Último registro)",
        default=0.0,
        editable=False,
    )
    riesgo_cardiovascular = models.FloatField(
        default=0, null=True, verbose_name="Riesgo Cardiovascular"
    )

    fecha_cargue = models.DateField(default=now, verbose_name="Fecha")

    class Meta:
        verbose_name = "Paciente - Variables clinicas"
        verbose_name_plural = "Paciente - Variables clinicas"
        ordering = ("-fecha_cargue",)


class TratamientoHistorico(models.Model):
    fk_paciente = models.ForeignKey(
        Paciente, verbose_name="Paciente", on_delete=models.CASCADE
    )
    fk_tratamiento = models.ForeignKey(
        Tratamiento,
        verbose_name="Tratamiento que recibe el paciente",
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(default=False)
    date_change = models.DateField(
        default=now,
        verbose_name="Fecha en la que se realiza un cambio en el tratamiento del paciente",
    )

class Logs_cargue(models.Model):
    user = models.ForeignKey(
        User, verbose_name="Usuario", on_delete=models.SET_NULL, default=None, null=True
    )
    nombre_archivo = models.ForeignKey(
        CargueBackOffice, verbose_name="Usuario", on_delete=models.CASCADE
    )
    numero_fila = models.IntegerField(default=0, verbose_name="Número de fila")
    numero_documento = models.CharField(
        max_length=100, default="", verbose_name="Número de documento"
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    modified = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Actualización"
    )


class Error_cargue(models.Model):
    logs_cargue = models.ForeignKey(
       Logs_cargue, verbose_name="Logs Cargue", on_delete=models.CASCADE
   )
    columna = models.CharField(default="", verbose_name="Columna", max_length=100)
    mensaje_error = models.CharField(default="", verbose_name="Mensaje de error", max_length=250) 
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    modified = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Actualización"
    )



    
