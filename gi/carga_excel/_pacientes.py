import datetime

from django.db.models import F, BooleanField, DateField
from django.db.transaction import atomic
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.http import FileResponse

from gi.carga_excel import BaseDto
from gi.models import Paciente, GrupoGestion, Ciudad, Eps, GrupoPacientes, Error_cargue, Logs_cargue, CargueBackOffice

from gi.carga_excel._cargue_ciudades import cargue_ciudad
from gi.carga_excel._funciones_validacion import validar_string, validar_n_enteros, validar_n_float, validar_fecha, fecha_comodin
from gi.carga_excel._add_error import add_error, errores, add_user_id, user_loggin_id

from gi.carga_excel._excel_log_error import generar_reporte_excel



text_comodin = "NSC"

cargue_generos_choices = {"m": "Masculino", "f": "Femenino"}

cargue_grupo_etnico_choices = {
    1: "Indigena",
    2: "ROM (gitano)",
    3: "Raizal del archipiélago de San Andrés y Providencia",
    4: "Palenquero de San Basilio",
    5: "Negro(a), mulato(a), afro colombiano(a) o afro descendiente",
    6: "Ninguna de las anteriores",
}

cargue_eps = {
    "C": "Régimen Contributivo",
    "S": "Régimen Subsidiado",
    "P": "Régimen de excepción",
    "E": "Régimen especial",
    "N": "No asegurado",
}

estado_civil = {
    "Soltero": "Soltero",
    "Casado": "Casado",
    "Unión libre": "Unión libre",
    "Viudo": "Viudo",
    "No se cargo estado civil":"No se cargo estado civil",
}

tipos_documento = {
    "RC": "RC",
    "TI": "TI",
    "CC": "CC",
    "CE": "CE",
    "PS": "PS",
    "MI":"MI.",
    "AI": "AI",
    "CD": "CD",
    "SP": "SP",
    "PE": "PE",
    "PPT":"PPT",
    "No se cargo tipo de documento": "No se cargo tipo de docuento",
}

nivel_estudio = {
    "Primaria": "Primaria",
    "Bachiller": "Bachiller",
    "Técnico/Tecnólogo": "Técnico/Tecnólogo",
    "Universitario": "Universitario",
    "Posgrado": "Posgrado",
    "No se cargo nivel de estudio":"No se cargo nivel de estudio",
}

cargue_tipo_diabetes = {
    1: "Diabetes tipo I",
    2: "Diabetes tipo II",
    3: "No tiene DM",
    4: "Otros (Posquirúrgica, postrasplante, secundaria a medicamentos, MODY)",
}

cargue_etiologia_de_la_erc = {
    4: "Enfermedad poliquística renal",
    5: "Otras",
    6: "Desconocida o paciente en abandono (solo aplica para pacientes con ERC confirmada)",
    7: "Diabetes.",
    8: "Enfermedad vascular renal (incluye Nefroangioesclerosis por hipertensión arterial).",
    9: "Sospecha de glomerulonefritis sin biopsia renal.",
    10: "Glomeruloesclerosis focal y segmentaria.",
    11: "Nefropatía membranosa",
    12: "Nefropatía por IgA",
    13: "Vasculitis",
    14: "Lupus eritematoso sistémico.",
    15: "Glomerulopatía familiar o genética (incluye Alport).",
    16: "Otra glomerulonefritis.",
    17: "Síndrome hemolítico urémico.",
    18: "Nefropatía tóxica (incluye analgésicos).",
    19: "Nefritis intersticial.",
    20: "Paraproteinemia (incluye mieloma múltiple).",
    21: "Nefropatía postparto.",
    22: "Litiasis.",
    23: "Displasia o hipoplasia renal congénita.",
    24: "Perdida de unidad renal por trauma o cirugía.",
    25: "Carcinoma renal.",
    26: "Nefropatía por reflujo vesicoureteral.",
    27: "Obstrucción de cuello de la vejiga (Incluye HPB, cáncer de próstata, valvas, etc.),",
    28: "Nefropatía obstructiva de causa diferente a 27 (incluye cáncer de cuello uterino, tumores retroperitoneales, etc.)",
    98: "No aplica, no tiene ERC",
    55: "No aplica, paciente reportado por ente territorial por prestación de servicios no incluidos en el plan de beneficios",
}

cargue_estadio_erc = {
    "1": "Paciente con TFGe mayor o igual a 90 ml/min Normal o elevado",
    "2": "Paciente con TFGe entre 60 y menor de 89 ml/min Levemente disminuido",
    "3a": "Paciente con TFGe entre 45 y menor de 59 ml/min Leve a moderadamente disminuido",
    "3b": "Paciente con TFGe entre 30 y menor de 44 ml/min Moderada a severamente disminuido",
    "4": "Paciente con TFGe entre 15 y menor de 29 ml/min Severamente disminuido",
    "5": "Paciente con TFGe menor de 15 ml/min Fallo renal",
    "0": "Estadio sin calcular",
}


diagnostico = {
    "E10": "DIABETES MELLITUS INSULINODEPENDIENTE",
    "E100": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMA",
    "E101": "DIABETES MELLITUS INSULINODEPENDIENTE CON CETOACIDOSIS",
    "E102": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMPLICACIONES RENALES",
    "E103": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMPLICACIONES OFTALMICAS",
    "E104": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMPLICACIONES NEUROLOGICAS",
    "E105": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMPLICACIONES CIRCULATORIAS PERIFERICAS",
    "E106": "DIABETES MELLITUS INSULINODEPENDIENTE CON OTRAS COMPLICACIONES ESPECIFICADAS",
    "E107": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMPLICACIONES MULTIPLES",
    "E108": "DIABETES MELLITUS INSULINODEPENDIENTE CON COMPLICACIONES NO ESPECIFICADAS",
    "E109": "DIABETES MELLITUS INSULINODEPENDIENTE SIN MENCION DE COMPLICACION",
    "E11" : "DIABETES MELLITUS NO INSULINODEPENDIENTE",
    "E110": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMA",
    "E111": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON CETOACIDOSIS",
    "E112": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMPLICACIONES RENALES",
    "E113": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMPLICACIONES OFTALMICAS",
    "E114": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMPLICACIONES NEUROLOGICAS",
    "E115": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMPLICACIONES CIRCULATORIAS PERIFERICAS",
    "E116": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON OTRAS COMPLICACIONES ESPECIFICADAS",
    "E117": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMPLICACIONES MULTIPLES",
    "E118": "DIABETES MELLITUS NO INSULINODEPENDIENTE CON COMPLICACIONES NO ESPECIFICADAS",
    "E119": "DIABETES MELLITUS NO INSULINODEPENDIENTE SIN MENCION DE COMPLICACION",
    "E12": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION",
    "E120": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMA",
    "E121": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON CETOACIDOSIS",
    "E122": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMPLICACIONES RENALES",
    "E123": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMPLICACIONES OFTALMICAS",
    "E124": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMPLICACIONES NEUROLOGICAS",
    "E125": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMPLICACIONES CIRCULATORIAS PERIFERICAS",
    "E126": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON OTRAS COMPLICACIONES ESPECIFICADAS",
    "E127": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMPLICACIONES MULTIPLES",
    "E128": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION CON COMPLICACIONES NO ESPECIFICADAS",
    "E129": "DIABETES MELLITUS ASOCIADA CON DESNUTRICION SIN MENCION DE COMPLICACION",
    "E13": "OTRAS DIABETES MELLITUS ESPECIFICADAS",
    "E130": "DIABETES MELLITUS ESPECIFICADA CON COMA",
    "E131": "DIABETES MELLITUS ESPECIFICADA CON CETOACIDOSIS",
    "E132": "DIABETES MELLITUS ESPECIFICADA CON COMPLICACIONES RENALES",
    "E133": "DIABETES MELLITUS ESPECIFICADA CON COMPLICACIONES OFTALMICAS",
    "E134": "DIABETES MELLITUS ESPECIFICADA CON COMPLICACIONES NEUROLOGICAS",
    "E135": "DIABETES MELLITUS ESPECIFICADA CON COMPLICACIONES CIRCULATORIAS PERIFERICAS",    
    "E136": "DIABETES MELLITUS ESPECIFICADA CON OTRAS COMPLICACIONES ESPECIFICADAS",
    "E137": "DIABETES MELLITUS ESPECIFICADA CON COMPLICACIONES MULTIPLES",
    "E138": "DIABETES MELLITUS ESPECIFICADA CON COMPLICACIONES NO ESPECIFICADAS",
    "E139": "DIABETES MELLITUS ESPECIFICADA SIN MENCION DE COMPLICACION",
    "E14": "DIABETES MELLITUS, NO ESPECIFICADA",
    "E140": "DIABETES MELLITUS, NO ESPECIFICADA CON COMA",
    "E141": "DIABETES MELLITUS, NO ESPECIFICADA CON CETOACIDOSIS",
    "E142": "DIABETES MELLITUS, NO ESPECIFICADA CON COMPLICACIONES RENALES",
    "E143": "DIABETES MELLITUS, NO ESPECIFICADA CON COMPLICACIONES OFTALMICAS",
    "E144": "DIABETES MELLITUS, NO ESPECIFICADA CON COMPLICACIONES NEUROLOGICAS",
    "E145": "DIABETES MELLITUS, NO ESPECIFICADA CON COMPLICACIONES CIRCULATORIAS PERIFERICAS",
    "E146": "DIABETES MELLITUS, NO ESPECIFICADA CON OTRAS COMPLICACIONES ESPECIFICADAS",
    "E147": "DIABETES MELLITUS, NO ESPECIFICADA CON COMPLICACIONES MULTIPLES",
    "E148": "DIABETES MELLITUS, NO ESPECIFICADA CON COMPLICACIONES NO ESPECIFICADAS",
    "E149": "DIABETES MELLITUS, NO ESPECIFICADA SIN MENCION DE COMPLICACION",
    "O240": "DIABETES MELLITUS PREEXISTENTE INSULINODEPENDIENTE, EN EL EMBARAZO",
    "O241": "DIABETES MELLITUS PREEXISTENTE NO INSULINODEPENDIENTE, EN EL EMBARAZO",
    "O242": "DIABETES MELLITUS PREEXISTENTE RELACIONADA CON DESNUTRICIÓN, EN EL EMBARAZO",
    "O243": "DIABETES MELLITUS PREEXISTENTE SIN OTRA ESPECIFICACIÓN, EN EL EMBARAZO",
    "R730": "ANORMALIDADES DE LA PRUEBA DE TOLERANCIA A LA GLUCOSA",
    "E161": "OTRAS HIPOGLICEMIAS",
    "R739": "HIPERGLICEMIA, NO ESPECIFICADA",
    "E101": "DIABETES MELLITUS INSULINODEPENDIENTE, CON CETOACIDOSIS",
    "No se cargo el diagnóstico CIE10": "No se cargo el diagnóstico CIE10",
}


ESTADIO1 = 1
ESTADIO2 = 2
ESTADIO3a = 3
ESTADIO3b = 4
ESTADIO4 = 5
ESTADIO5 = 6
ESTADIO_SIN_CALCULAR = 7

counter = []
class CargaPacienteDto(BaseDto):
    fields = Paciente._meta.get_fields()
    model = Paciente
    # tipo_diabetes_mapper = {
    #     "": Paciente.TIPO_DIABETES_SIN_CLASIFICACION,
    #     Paciente.TIPO_DIABETES_1.lower(): Paciente.TIPO_DIABETES_1,
    #     Paciente.TIPO_DIABETES_2.lower(): Paciente.TIPO_DIABETES_2,
    #     Paciente.TIPO_DIABETES_2_I.lower(): Paciente.TIPO_DIABETES_2_I,
    #     Paciente.TIPO_DIABETES_SIN_CLASIFICACION.lower(): Paciente.TIPO_DIABETES_SIN_CLASIFICACION,
    # }

    @classmethod
    def get_fields_dict(cls):
        to_exclude = ["tfg", "estadio"]

        fields = cls.get_model_fields()
        for field in to_exclude:
            del fields[field]
        return {**cls.get_model_fields(), **cls.get_related_fields()}

    @classmethod
    def get_related_fields(cls):
        return {
            "eps": "",
            "grupo_gestion": "",
            "ciudad_asignacion": "",
            "ciudad_contacto": "",
        }

    @classmethod
    def get_dto_qs(cls, qs):
        return (
            qs.values(*cls.get_model_fields().keys())
            .annotate(
                eps=F("eps__nombre"),
                grupo_gestion=F("grupo_gestion__nombre"),
                ciudad_asignacion=F("ciudad_asignacion__nombre"),
                ciudad_contacto=F("ciudad_contacto__nombre"),
            )
            .values(*cls.get_fields_dict().keys())
        )
    

    @atomic()
    def save_patients(self, user):
        df = self.df
        df.fillna("", inplace=True)
        default_date = datetime.date(year=2005, month=1, day=1)
        new_paciente_flag = False

        groups = []

        numero_fila = 0

        add_user_id(user.id)

        # print("user")
        # print(userid)

        for row in df.itertuples():

            numero_fila = numero_fila+1
            
            p = Paciente.objects.filter(numero_documento=row.numero_documento).first()

            

            if not p:
                new_paciente_flag = True
                p = Paciente()
            
            fecha_diagnostico = row.fecha_diagnostico_diabetes
            if fecha_diagnostico and type(fecha_diagnostico) != datetime.date:
                try:
                    fecha_diagnostico = datetime.date(
                        year=str(fecha_diagnostico), month=1, day=1
                    )
                except TypeError:
                    fecha_diagnostico = default_date
            else:
                fecha_diagnostico = default_date
            p.fecha_diagnostico = fecha_diagnostico

            # print("Pacientes")
            # print(p.numero_documento)
            documento_p = str(p.numero_documento)

            to_exclude = [
                "fecha_afiliacion",
                "fecha_diagnostico",
                "fecha_erc",
                "fecha_colesterol",
                "fecha_diagnostico_hipertension_renal"
            ]

            no_reverse = [
                "diagnostico_erc",
                "diagnostico_epoc",
                "diagnostico_hipoglicemia",
                "diagnostico_falla_cardiaca",
            ]  # Campos que no deben pasar de True a False

            fields = self.get_model_fields()

            fields["grupo_pacientes"] = ""
            # print(fields)
            for field in to_exclude:
                del fields[field]

            for field in fields.keys():
                documento_p = str(p.numero_documento)

                try:
                    row_value = getattr(row, field)
                except AttributeError:
                    row_value = None  
                if field == "grupo_pacientes":

                    valgrupo_pacientes = validar_string(row_value, 100)

                    if(valgrupo_pacientes):
                        add_error(numero_fila, documento_p, valgrupo_pacientes, "grupo_pacientes")
                        resultado_grupo_pacientes = "Grupo paciente no definido"
                    else:
                        resultado_grupo_pacientes = row_value

                    groups.append((p, resultado_grupo_pacientes))
                    continue
                field_obj = Paciente._meta.get_field(field)

                if field == "hba1c":
                    p.hba1c = row_value or 0.0
                    continue
                elif field == "fecha_diagnostico":
                    continue
                # elif field == "tipo_diabetes":
                #     setattr(p, field, self.tipo_diabetes_mapper[row_value.lower()])
                elif field == "numero_documento":

                    numero_documento = row_value
                    longitud_numero_documento = 100

                    valnumero_documento = validar_n_enteros(numero_documento,  longitud_numero_documento)
                    resultado_numero_documento = None
                    if(valnumero_documento):

                        if(valnumero_documento['entero']):
                            resultado_entero = valnumero_documento['entero']
                            resultado_error = valnumero_documento['error']

                            if resultado_entero is not None:
                                add_error(numero_fila,documento_p,resultado_error, "numero_documento")
                                resultado_numero_documento = numero_documento
                        else:
                            add_error(numero_fila,documento_p,valnumero_documento['error'], "numero_documento")
                            resultado_numero_documento = numero_documento

                    else:
                        resultado_numero_documento = numero_documento  

                    p.numero_documento = resultado_numero_documento
                    continue    
                elif field == "fecha_nacimiento":

                    nueva_fecha_comodin = datetime.datetime.strptime(fecha_comodin, "%Y-%m-%d")

                    valfecha_nacimiento = validar_fecha(row_value)
                    resultado_fecha_nacimiento = None

                    if(valfecha_nacimiento):
                        add_error(numero_fila,documento_p,valfecha_nacimiento, "fecha_nacimiento")
                        resultado_fecha_nacimiento = nueva_fecha_comodin
                    else:
                        resultado_fecha_nacimiento = row_value  

                    p.fecha_nacimiento = resultado_fecha_nacimiento
                    continue
                elif (
                    field == "fecha_afiliacion"
                    or field == "ultimo_seguimiento"
                    and not row_value
                ):
                    setattr(p, field, fecha_diagnostico)
                elif (
                    type(field_obj) == DateField
                    and row_value
                    and type(row_value) == str
                ):
                    setattr(p, field, datetime.datetime.strptime(row_value, "%Y-%m-%d"))
                elif type(field_obj) == BooleanField and type(row_value) != bool:
                    # Condicional interno para evitar pasar de True a False en ciertos campos
                    if field in no_reverse and not getattr(p, field):
                        setattr(p, field, bool(row_value))
                    elif field not in no_reverse:
                        setattr(p, field, bool(row_value))
                elif not row_value:
                    setattr(p, field, field_obj.default)
                else:
                    setattr(p, field, row_value)

            # TYT Interactiva Validations
            if hasattr(row, "nombre_1") and hasattr(row, "nombre_2"):
                valnombre1 = ""
                valnombre2 = ""
                resultado_nombre1 = ""
                resultado_nombre2 = ""
                valnombre1 = validar_string(row.nombre_1, 100)
                valnombre2 = validar_string(row.nombre_2, 100)

                if(valnombre1):
                    add_error(numero_fila,documento_p,valnombre1, "nombre_1")
                    resultado_nombre1 = f'{text_comodin} nombre_1'
                else:
                    resultado_nombre1 = row.nombre_1

                if(valnombre2):
                    add_error(numero_fila,documento_p,valnombre2, "nombre_2")
                    resultado_nombre2 = f'{text_comodin} nombre_2'
                else:
                    resultado_nombre2 = row.nombre_2

                p.nombres = f"{resultado_nombre1} {resultado_nombre2}"

            if hasattr(row, "apellido_1") and hasattr(row, "apellido_2"):
                valapellido1 = ""
                valapellido2 = ""
                resultado_apellido1 = ""
                resultado_apellido2 = ""
                valapellido1 = validar_string(row.apellido_1, 100)
                valapellido2 = validar_string(row.apellido_2, 100)

                if(valapellido1):
                    add_error(numero_fila,documento_p, valapellido1, "apellido_1")
                    resultado_apellido1 = f'{text_comodin} apellido_1'
                else:
                    resultado_apellido1 = row.apellido_1

                if(valapellido2):
                    add_error(numero_fila,documento_p,valapellido2, "apellido_2")
                    resultado_apellido2 = f'{text_comodin} apellido_2'
                else:
                    resultado_apellido2 = row.apellido_2

                p.apellidos = f"{resultado_apellido1} {resultado_apellido2}"

            # tipo_documento -> validacion del campo -> NOT NULL
            if (
                hasattr(row, "tipo_documento")
                and str(row.tipo_documento).strip() in tipos_documento
            ):
                p.tipo_documento = row.tipo_documento
            else:
                resultado_tipo_documento = ""
                valtipo_documento = validar_string(row.tipo_documento, 100)

                if(valtipo_documento):
                    add_error(numero_fila,documento_p,valtipo_documento, "tipo_documento")
                    resultado_tipo_documento = tipos_documento["No se cargo tipo de documento"]
                else:
                    add_error(numero_fila,documento_p,"El valor no es una opcion valida", "tipo_documento")
                    resultado_tipo_documento = tipos_documento["No se cargo tipo de documento"]

                p.tipo_documento = resultado_tipo_documento   
            
            # Validación campo genero M, F, default = ""
            if hasattr(row, "genero"):
                if (
                    row.genero == "M"
                    or row.genero == "m"
                    or row.genero == "F"
                    or row.genero == "f"
                ):
                    genero = row.genero.lower()    

                    if genero in cargue_generos_choices:
                        p.genero = cargue_generos_choices[genero]
                else:

                    valgenero = validar_string(row.genero, 100)

                    if(valgenero):
                        add_error(numero_fila,documento_p,valgenero, "genero")
                        resultado_genero = "No se cargo género"
                    else:
                        add_error(numero_fila,documento_p,"El valor no es una opcion valida", "genero")
                        resultado_genero = "No se cargo género"

                    p.genero = resultado_genero

            # grupo_etnico -> Validacion del campo -> NOT NULL 
            if (
                hasattr(row, "grupo_etnico")
                and row.grupo_etnico in cargue_grupo_etnico_choices
            ):
                p.grupo_etnico = cargue_grupo_etnico_choices[row.grupo_etnico]

            else:

                longitud_grupo_etnico = 1
                grupo_etnico = row.grupo_etnico

                valgrupo_etnico = validar_n_enteros(grupo_etnico,  longitud_grupo_etnico)
                resultado_grupo_etnico = None
                if(valgrupo_etnico):

                    if(valgrupo_etnico['entero']):
                        resultado_entero = valgrupo_etnico['entero']
                        resultado_error = valgrupo_etnico['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "grupo_etnico")
                            resultado_grupo_etnico = cargue_grupo_etnico_choices[6]
                    else:
                        add_error(numero_fila,documento_p,valgrupo_etnico['error'], "grupo_etnico")
                        resultado_grupo_etnico = cargue_grupo_etnico_choices[6]

                else:
                    resultado_grupo_etnico = cargue_grupo_etnico_choices[6]

                p.grupo_etnico = resultado_grupo_etnico

            # estado_civil -> validacion del campo -> NOT NULL
            if (
                hasattr(row, "estado_civil")
                and str(row.estado_civil).strip() in estado_civil
            ):
                p.estado_civil = row.estado_civil

            else:

                resultado_estado_civil = ""
                valestado_civil = validar_string(row.estado_civil, 100)

                if(valestado_civil):
                    add_error(numero_fila,documento_p,valestado_civil, "estado_civil")
                    resultado_estado_civil = estado_civil["No se cargo estado civil"]
                else:
                    add_error(numero_fila,documento_p,"El valor no es una opcion valida", "estado_civil")
                    resultado_estado_civil = estado_civil["No se cargo estado civil"]

                p.estado_civil = resultado_estado_civil    


            # nivel_estudios -> validacion del campo -> NOT NULL
            if (
                hasattr(row, "nivel_estudios")
                and str(row.nivel_estudios).strip() in nivel_estudio
            ):
                p.nivel_estudios = row.nivel_estudios

            else:

                resultado_nivel_estudios = ""
                valnivel_estudios = validar_string(row.nivel_estudios, 100)

                if(valnivel_estudios):
                    add_error(numero_fila,documento_p,valnivel_estudios, "nivel_estudios")
                    resultado_nivel_estudios = nivel_estudio["No se cargo nivel de estudio"]
                else:
                    add_error(numero_fila,documento_p,"El valor no es una opcion valida", "nivel_estudios")
                    resultado_nivel_estudios = nivel_estudio["No se cargo nivel de estudio"]

                p.nivel_estudios = resultado_nivel_estudios

            # fecha_afiliacion -> NOT NULL
            if hasattr(row, "fecha_afiliacion"):
                # p.fecha_afiliacion = row.fecha_afiliacion

                fecha_afiliacion = row.fecha_afiliacion

                valfecha_afiliacion = validar_fecha(fecha_afiliacion)
                resultado_fecha_afiliacion = None
                if(valfecha_afiliacion):
                    add_error(numero_fila, documento_p, valfecha_afiliacion, "fecha_afiliacion")
                    resultado_fecha_afiliacion = fecha_comodin
                else:
                    resultado_fecha_afiliacion = fecha_afiliacion

                p.fecha_afiliacion = resultado_fecha_afiliacion

            # fecha_diagnostico = fecha_diagnostico_diabetes
            if hasattr(row, "fecha_diagnostico_diabetes"):

                fecha_diagnostico_diabetes = row.fecha_diagnostico_diabetes

                valfecha_diagnostico_diabetes = validar_fecha(fecha_diagnostico_diabetes)
                resultado_fecha_diagnostico_diabetes = None
                if(valfecha_diagnostico_diabetes):
                    add_error(numero_fila,documento_p,valfecha_diagnostico_diabetes, "fecha_diagnostico_diabetes")
                    resultado_fecha_diagnostico_diabetes = fecha_comodin
                else:
                    resultado_fecha_diagnostico_diabetes = fecha_diagnostico_diabetes

                p.fecha_diagnostico = resultado_fecha_diagnostico_diabetes

            #     p.fecha_diagnostico = row.fecha_diagnostico_diabetes
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     p.fecha_diagnostico = fecha_actual


            # diagnostico

            if (hasattr(row, "diagnostico")
                and str(row.diagnostico).strip() in diagnostico ):

                p.diagnostico = row.diagnostico 
            else:
                resultado_diagnostico = ""
                valdiagnostico = validar_string(row.diagnostico, 100)

                if(valdiagnostico):
                    add_error(numero_fila,documento_p,valdiagnostico, "diagnostico")
                    resultado_diagnostico = "No se cargo el diagnóstico CIE10"
                else:
                    add_error(numero_fila,documento_p,"El valor no es una opcion valida", "diagnostico")
                    resultado_diagnostico = "No se cargo el diagnóstico CIE10"

                p.diagnostico = resultado_diagnostico

            # fecha_diagnostico_hipertension_renal -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_diagnostico_hipertension_renal"):

                fecha_diagnostico_hipertension_renal = row.fecha_diagnostico_hipertension_renal

                valfecha_diagnostico_hipertension_renal = validar_fecha(fecha_diagnostico_hipertension_renal)
                resultado_fecha_diagnostico_hipertension_renal = None
                if(valfecha_diagnostico_hipertension_renal):
                    add_error(numero_fila,documento_p,valfecha_diagnostico_hipertension_renal, "fecha_diagnostico_hipertension_renal")
                    resultado_fecha_diagnostico_hipertension_renal = fecha_comodin
                else:
                    resultado_fecha_diagnostico_hipertension_renal = fecha_diagnostico_hipertension_renal

                p.fecha_diagnostico_hipertension_renal = resultado_fecha_diagnostico_hipertension_renal

            #     p.fecha_diagnostico_hipertension_renal = (
            #         row.fecha_diagnostico_hipertension_renal
            #     )
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     p.fecha_diagnostico_hipertension_renal = fecha_actual

            # Tipo Diabetes
            if (
                hasattr(row, "tipo_diabetes")
                and row.tipo_diabetes in cargue_tipo_diabetes
            ):
                p.tipo_diabetes = cargue_tipo_diabetes[row.tipo_diabetes]
            else:
                # p.tipo_diabetes = cargue_tipo_diabetes[3]

                longitud_tipo_diabetes = 1
                tipo_diabetes = row.tipo_diabetes

                valtipo_diabetes = validar_n_enteros(tipo_diabetes,  longitud_tipo_diabetes)
                resultado_tipo_diabetes = None
                if(valtipo_diabetes):

                    if(valtipo_diabetes['entero']):
                        resultado_entero = valtipo_diabetes['entero']
                        resultado_error = valtipo_diabetes['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "tipo_diabetes")
                            resultado_tipo_diabetes = cargue_tipo_diabetes[3]
                    else:
                        add_error(numero_fila,documento_p,valtipo_diabetes['error'], "tipo_diabetes")
                        resultado_tipo_diabetes = cargue_tipo_diabetes[3]

                else:
                    resultado_tipo_diabetes = cargue_tipo_diabetes[3]

                p.tipo_diabetes = resultado_tipo_diabetes

            # Eps == regimen_de_afiliacion
            if (
                hasattr(row, "regimen_de_afiliacion")
                and row.regimen_de_afiliacion in cargue_eps
            ):
                p.eps = Eps.objects.get_or_create(
                    nombre=cargue_eps[row.regimen_de_afiliacion]
                )[0]
            else:

                resultado_regimen_de_afiliacion = ""
                valregimen_de_afiliacion = validar_string(row.regimen_de_afiliacion, 100)

                if(valregimen_de_afiliacion):
                    add_error(numero_fila,documento_p,valregimen_de_afiliacion, "regimen_de_afiliacion")
                    resultado_regimen_de_afiliacion = Eps.objects.get_or_create(nombre="Sin información")[0]
                else:
                    add_error(numero_fila,documento_p,"El valor no es una opcion valida", "regimen_de_afiliacion")
                    resultado_regimen_de_afiliacion = Eps.objects.get_or_create(nombre="Sin información")[0]
                    
                p.eps = resultado_regimen_de_afiliacion


            # grupo_gestion == grupo_sede
            if hasattr(row, "grupo_sede"):
            
                resultado_grupo_sede = ""    
                valgrupo_sede = validar_string(row.grupo_sede, 100)

                if(valgrupo_sede):
                    add_error(numero_fila,documento_p,valgrupo_sede, "grupo_sede")
                    resultado_grupo_sede = GrupoGestion.objects.get_or_create(
                        nombre="Grupo sede no definido")[0]
                else:
                    resultado_grupo_sede = GrupoGestion.objects.get_or_create(
                    nombre=row.grupo_sede)[0]

                p.grupo_gestion = resultado_grupo_sede    

            # ciudad_contacto == municipio_de_residencia
            if (
                hasattr(row, "municipio_de_residencia")
                and row.municipio_de_residencia in cargue_ciudad
            ):
                p.ciudad_contacto = Ciudad.objects.get_or_create(
                    nombre=cargue_ciudad[row.municipio_de_residencia]
                )[0]
                # p.ciudad_asignacion = Ciudad.objects.get_or_create(
                #     nombre=cargue_ciudad[row.municipio_de_residencia]
                # )[0]
            else:
                # p.ciudad_contacto = Ciudad.objects.get_or_create(nombre="Sin información")[0]
                # p.ciudad_asignacion = Ciudad.objects.get_or_create(nombre="Sin información")[0]

                longitud_municipio_de_residencia = 11
                municipio_de_residencia = row.municipio_de_residencia

                valmunicipio_de_residencia = validar_n_enteros(municipio_de_residencia,  longitud_municipio_de_residencia)
                resultado_municipio_de_residencia = None
                if(valmunicipio_de_residencia):

                    if(valmunicipio_de_residencia['entero']):
                        resultado_entero = valmunicipio_de_residencia['entero']
                        resultado_error = valmunicipio_de_residencia['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "municipio_de_residencia")
                    else:
                        add_error(numero_fila,documento_p,valmunicipio_de_residencia['error'], "municipio_de_residencia")

                else:
                    resultado_municipio_de_residencia = municipio_de_residencia

                p.ciudad_contacto = Ciudad.objects.get_or_create(nombre="Sin información")[0]

            # telefono
            if hasattr(row, "telefono"):
                
                longitud_telefono = 10
                telefono = row.telefono

                valtelefono = validar_n_enteros(telefono,  longitud_telefono)
                resultado_telefono = None
                if(valtelefono):

                    if(valtelefono['entero']):
                        resultado_entero = valtelefono['entero']
                        resultado_error = valtelefono['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "telefono")
                            resultado_telefono = 0
                    else:
                        add_error(numero_fila,documento_p,valtelefono['error'], "telefono")
                        resultado_telefono = 0

                else:
                    resultado_telefono = telefono

                p.telefono = resultado_telefono


            # ciudad_asignacion == ciudad_de_atencion
            if (
                hasattr(row, "ciudad_de_atencion")
                and row.ciudad_de_atencion in cargue_ciudad
            ):
                p.ciudad_asignacion = Ciudad.objects.get_or_create(
                    nombre=cargue_ciudad[row.ciudad_de_atencion]
                )[0]
            else:

                longitud_ciudad_de_atencion = 11
                ciudad_de_atencion = row.ciudad_de_atencion

                valciudad_de_atencion = validar_n_enteros(ciudad_de_atencion,  longitud_ciudad_de_atencion)
                resultado_municipio_de_residencia = None
                if(valciudad_de_atencion):

                    if(valciudad_de_atencion['entero']):
                        resultado_entero = valciudad_de_atencion['entero']
                        resultado_error = valciudad_de_atencion['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "ciudad_de_atencion")
                    else:
                        add_error(numero_fila,documento_p,valciudad_de_atencion['error'], "ciudad_de_atencion")

                else:
                    resultado_ciudad_de_atencion = ciudad_de_atencion    

                p.ciudad_asignacion = Ciudad.objects.get_or_create(nombre="Sin información")[0]      
            
                # p.ciudad_asignacion = Ciudad.objects.get_or_create(
                #     nombre=row.ciudad_de_atencion
                # )[0]

            if not p.riesgo_cardiovascular:
                p.actualizar_riesgocardiovascular(save=False)

            #  etiologia_de_la_erc
            if (
                hasattr(row, "etiologia_de_la_erc")
                and row.etiologia_de_la_erc in cargue_etiologia_de_la_erc
            ):
                p.etiologia_erc = cargue_etiologia_de_la_erc[row.etiologia_de_la_erc]
                if row.etiologia_de_la_erc == 98 or row.etiologia_de_la_erc == 55:
                    p.diagnostico_erc = 0
                else:
                    p.diagnostico_erc = 1
            else:
                # p.etiologia_erc = ""
                # p.diagnostico_erc = 0

                longitud_etiologia_de_la_erc = 2
                etiologia_de_la_erc = row.etiologia_de_la_erc

                valetiologia_de_la_erc = validar_n_enteros(etiologia_de_la_erc,  longitud_etiologia_de_la_erc)
                resultado_etiologia_de_la_erc = None
                if(valetiologia_de_la_erc):

                    if(valetiologia_de_la_erc['entero']):
                        resultado_entero = valetiologia_de_la_erc['entero']
                        resultado_error = valetiologia_de_la_erc['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "etiologia_de_la_erc")
                            resultado_etiologia_de_la_erc = ""
                    else:
                        add_error(numero_fila,documento_p,valetiologia_de_la_erc['error'], "etiologia_de_la_erc")
                        resultado_etiologia_de_la_erc = ""

                else:
                    resultado_etiologia_de_la_erc = ""

                p.etiologia_erc = resultado_etiologia_de_la_erc
                p.diagnostico_erc = 0

            # fecha_hta -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_hta"):

                fecha_hta = row.fecha_hta

                valfecha_hta = validar_fecha(fecha_hta)
                resultado_fecha_hta = None
                if(valfecha_hta):
                    resultado_fecha_hta = fecha_comodin
                else:
                    resultado_fecha_hta = fecha_hta

                p.fecha_hta = resultado_fecha_hta

            #     p.fecha_hta = row.fecha_hta
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     p.fecha_hta = fecha_actual

            # fecha_erc -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_erc"):

                fecha_erc = row.fecha_erc

                valfecha_erc = validar_fecha(fecha_erc)
                resultado_fecha_erc = None
                if(valfecha_erc):
                    resultado_fecha_erc = fecha_comodin
                else:
                    resultado_fecha_erc = fecha_erc

                p.fecha_erc = resultado_fecha_erc

            #     p.fecha_erc = row.fecha_erc
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     p.fecha_erc = fecha_actual

            # estadio_erc -> validacion del campo -> NOT NULL
            if (
                hasattr(row, "estadio_erc")
                and str(row.estadio_erc).strip() in cargue_estadio_erc
            ):
                p.estadio_erc = row.estadio_erc

            else:

                resultado_estadio_erc = ""
                valestadio_erc = validar_string(row.estadio_erc, 100)

                if(valestadio_erc):
                    add_error(numero_fila,documento_p,valestadio_erc, "estadio_erc")
                    resultado_estadio_erc = 0
                else:
                    add_error(numero_fila,documento_p,"El valor no es una opcion valida", "estadio_erc")
                    resultado_estadio_erc = 0

                p.estadio_erc = resultado_estadio_erc

            # fecha_colesterol -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_colesterol"):

                fecha_colesterol = row.fecha_colesterol

                valfecha_colesterol = validar_fecha(fecha_colesterol)
                resultado_fecha_colesterol = None
                if(valfecha_colesterol):
                    add_error(numero_fila,documento_p,valfecha_colesterol, "fecha_colesterol")
                    resultado_fecha_colesterol = fecha_comodin
                else:
                    resultado_fecha_colesterol = fecha_colesterol

                p.fecha_colesterol = resultado_fecha_colesterol

            #     p.fecha_colesterol = row.fecha_colesterol
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     p.fecha_colesterol = fecha_actual

            if hasattr(row, "diagnostico_hta"):

                longitud_diagnostico_hta = 1
                diagnostico_hta = row.diagnostico_hta

                valdiagnostico_hta = validar_n_enteros(diagnostico_hta,  longitud_diagnostico_hta)
                resultado_diagnostico_hta = None
                if(valdiagnostico_hta):

                    if(valdiagnostico_hta['entero']):
                        resultado_entero = valdiagnostico_hta['entero']
                        resultado_error = valdiagnostico_hta['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "diagnostico_hta")
                            resultado_diagnostico_hta = False
                    else:
                        add_error(numero_fila,documento_p,valdiagnostico_hta['error'], "diagnostico_hta")
                        resultado_diagnostico_hta = False

                else:
                    resultado_diagnostico_hta = diagnostico_hta

                    if resultado_diagnostico_hta == 1:
                        resultado_diagnostico_hta = True
                    else:
                        resultado_diagnostico_hta = False

                p.diagnostico_hta = resultado_diagnostico_hta

                # if row.diagnostico_hta == 1:
                #     p.diagnostico_hta = True
                # else:
                #     p.diagnostico_hta = False

            # Validar campo es_fumador 1 == SI, 2 == NO, default= No

            if hasattr(row, "es_fumador"):

                longitud_es_fumador = 1
                es_fumador = row.es_fumador

                vales_fumador = validar_n_enteros(es_fumador,  longitud_es_fumador)
                resultado_es_fumador = None
                if(vales_fumador):

                    if(vales_fumador['entero']):
                        resultado_entero = vales_fumador['entero']
                        resultado_error = vales_fumador['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "es_fumador")
                            resultado_es_fumador = False
                    else:
                        add_error(numero_fila,documento_p,vales_fumador['error'], "es_fumador")
                        resultado_es_fumador = False

                else:
                    resultado_es_fumador = es_fumador

                    if resultado_es_fumador == 1:
                        resultado_es_fumador = True
                    else:
                        resultado_es_fumador = False

                p.es_fumador = resultado_es_fumador


                # if row.es_fumador == 1:
                #     p.es_fumador = True
                # else:
                #     p.es_fumador = False

            # Validar campo diagnostico_hipoglicemia = 1 == Si, 2 == No, default= No

            if hasattr(row, "diagnostico_hipoglicemia"):

                diagnostico_hipoglicemia = row.diagnostico_hipoglicemia

                if diagnostico_hipoglicemia == 1:
                    diagnostico_hipoglicemia = True
                elif(diagnostico_hipoglicemia == 2):
                    diagnostico_hipoglicemia = False
                else:
                    diagnostico_hipoglicemia = False
                    add_error(numero_fila,documento_p,"El dato no es 1 (Si) o 2 (No)", "diagnostico_hipoglicemia")

                p.diagnostico_hipoglicemia = diagnostico_hipoglicemia

                # if row.diagnostico_hipoglicemia == 1:
                #     p.diagnostico_hipoglicemia = True
                # else:
                #     p.diagnostico_hipoglicemia = False

            # Validar campo diagnostico_erc = 1 == Si, 2 == No, default = No

            if hasattr(row, "diagnostico_erc"):
                if row.diagnostico_erc == 1:
                    p.diagnostico_erc = True
                else:
                    p.diagnostico_erc = False

            # Validar campo tas, campo flotante, default 0

            if hasattr(row, "tas"):

                tas = row.tas
                validar_funcion = 0

                try:
                    if isinstance(tas, int) or isinstance(tas, float):
                        validar_funcion = tas
                except ValueError:
                    validar_funcion = 0

                resultado_tas = None

                valtas = validar_n_float(validar_funcion)

                if(valtas):

                    if(valtas['flotante']):
                        resultado_flotante = valtas['flotante']
                        resultado_error = valtas['error']

                        add_error(numero_fila,documento_p,resultado_error, "tas")
                        resultado_tas = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valtas['error'], "tas")
                        resultado_tas = 0

                else:
                    resultado_tas = tas

                p.tas = resultado_tas

                # try:
                #     p.tas = float(row.tas)
                # except ValueError:
                #     p.tas = 0

            # Validar campo tad, campo flotante, default 0

            if hasattr(row, "tad"):

                tad = row.tad
                validar_funcion = 0

                try:
                    if isinstance(tad, int) or isinstance(tad, float):
                        validar_funcion = tad
                except ValueError:
                    validar_funcion = 0

                resultado_tad = None

                valtad = validar_n_float(validar_funcion)

                if(valtad):

                    if(valtad['flotante']):
                        resultado_flotante = valtad['flotante']
                        resultado_error = valtad['error']

                        add_error(numero_fila,documento_p,resultado_error, "tad")
                        resultado_tad = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valtad['error'], "tad")
                        resultado_tad = 0
                else:
                    resultado_tad = tad

                p.tad = resultado_tad

                # try:
                #     p.tad = float(row.tad)
                # except ValueError:
                #     p.tad = 0

            # Validar campo estatura, campo flotante, default 0

            if hasattr(row, "estatura"):

                estatura = row.estatura
                validar_funcion = 0

                try:
                    if isinstance(estatura, int) or isinstance(estatura, float):
                        validar_funcion = estatura
                except ValueError:
                    validar_funcion = 0

                resultado_estatura = None

                valestatura = validar_n_float(validar_funcion)

                if(valestatura):

                    if(valestatura['flotante']):
                        resultado_flotante = valestatura['flotante']
                        resultado_error = valestatura['error']

                        add_error(numero_fila,documento_p,resultado_error, "estatura")
                        resultado_estatura = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valestatura['error'], "estatura")
                        resultado_estatura = 0
                else:
                    resultado_estatura = estatura

                p.estatura = resultado_estatura
                # try:
                #     p.estatura = float(row.estatura)
                #     if p.estatura < 100:
                #         p.estatura = float(row.estatura * 100)
                # except ValueError:
                #     p.estatura = 0

            # Validar campo peso, campo flotante, default 0

            if hasattr(row, "peso"):

                peso = row.peso
                validar_funcion = 0

                try:
                    if isinstance(peso, int) or isinstance(peso, float):
                        validar_funcion = peso
                except ValueError:
                    validar_funcion = 0

                resultado_peso = None

                valpeso = validar_n_float(validar_funcion)

                if(valpeso):

                    if(valpeso['flotante']):
                        resultado_flotante = valpeso['flotante']
                        resultado_error = valpeso['error']

                        add_error(numero_fila,documento_p,resultado_error, "peso")
                        resultado_peso = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valpeso['error'], "peso")
                        resultado_peso = 0
                else:
                    resultado_peso = peso

                p.peso = resultado_peso

                # try:
                #     p.peso = float(row.peso)
                # except ValueError:
                #     p.peso = 0


             # Validar campo programa_nefroproteccion
            if hasattr(row, "programa_nefroproteccion"):

                programa_nefroproteccion = ""
                resultado_programa_nefroproteccion = ""
                valprograma_nefroproteccion = validar_string(row.programa_nefroproteccion, 100)

                if(valprograma_nefroproteccion):
                    add_error(numero_fila,documento_p,valprograma_nefroproteccion, "programa_nefroproteccion")
                    resultado_programa_nefroproteccion = f'{text_comodin} programa_nefroproteccion'
                else:
                    resultado_programa_nefroproteccion = row.programa_nefroproteccion

                p.programa_nefroproteccion = resultado_programa_nefroproteccion


            # Validar campo hdl, campo flotante, default 0

            if hasattr(row, "hdl"):
                hdl = row.hdl
                validar_funcion = 0

                try:
                    if isinstance(hdl, int) or isinstance(hdl, float):
                        validar_funcion = hdl
                except ValueError:
                    validar_funcion = 0
                
                resultado_hdl = None

                valhdl = validar_n_float(validar_funcion)

                if(valhdl):

                    if(valhdl['flotante']):
                        resultado_flotante = valhdl['flotante']
                        resultado_error = valhdl['error']

                        add_error(numero_fila,documento_p,resultado_error, "hdl")
                        resultado_hdl = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valhdl['error'], "hdl")
                        resultado_hdl = 0
                else:
                    resultado_hdl = hdl

                p.hdl = resultado_hdl

            # Validar campo colesterol_total, campo flotante, default 0

            if hasattr(row, "colesterol_total"):

                colesterol_total = row.colesterol_total
                validar_funcion = 0

                try:
                    if isinstance(colesterol_total, int) or isinstance(colesterol_total, float):
                        validar_funcion = colesterol_total
                except ValueError:
                    validar_funcion = 0

                resultado_colesterol_total = None

                valcolesterol_total = validar_n_float(validar_funcion)

                if(valcolesterol_total):

                    if(valcolesterol_total['flotante']):
                        resultado_flotante = valcolesterol_total['flotante']
                        resultado_error = valcolesterol_total['error']

                        add_error(numero_fila,documento_p,resultado_error, "colesterol_total")
                        resultado_colesterol_total = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valcolesterol_total['error'], "colesterol_total")
                        resultado_colesterol_total = 0

                else:
                    resultado_colesterol_total = colesterol_total

                p.colesterol_total = resultado_colesterol_total

            p.save()

        for patient, group in groups:
            self.save_patient_group(patient, group)

    def save_patient_group(self, patient, group_name):
        if group_name:
            grupo_pacientes = GrupoPacientes.objects.filter(nombre=group_name).first()
            if not grupo_pacientes:
                grupo_pacientes = GrupoPacientes(
                    nombre=group_name, slug=slugify(group_name), order=0
                )
                grupo_pacientes.save()
            grupo_pacientes.pacientes.add(patient)
 
