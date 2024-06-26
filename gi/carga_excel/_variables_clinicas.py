import datetime
import logging

import pandas as pd
from django.db.models import F, BooleanField, FloatField, IntegerField, DateField
from gi.models import Paciente, GrupoGestion, Ciudad, Eps, GrupoPacientes, Error_cargue, Logs_cargue, CargueBackOffice
from django.contrib.auth.models import User
from gi.carga_excel._excel_log_error import generar_reporte_excel


from django.db.transaction import atomic

from gi.carga_excel import BaseDto
from gi.models import Paciente, VariablesClinicas, CargueBackOffice
from pandas import DataFrame

from gi.carga_excel._funciones_validacion import validar_string, validar_n_enteros, validar_n_float, validar_fecha, ajustar_decimales, fecha_comodin
from gi.carga_excel._add_error import add_error, errores, add_errors_array, errores_total, user_loggin_id, add_user_id
from gi.carga_excel._pacientes import text_comodin

from django.conf import settings

cargue_albuminuria_choices = {
    9888: "No aplica, paciente en TRR",
    9999: "No se realizó el laboratorio",
    5555: "No aplica, paciente reportado por ente territorial por prestación de servicios no incluidos en el plan de beneficios",
}


class CargaVariablesClinicas(BaseDto):
    fields = VariablesClinicas._meta.get_fields()
    model = VariablesClinicas
    day = 1

    def __init__(
        self, df, month: int = 1, year: int = 2005, cargue: CargueBackOffice = None
    ):
        self.df: DataFrame = df
        self.month = month
        self.year = year
        self.cargue = cargue

    @classmethod
    def get_fields_dict(cls):
        to_exclude = []

        fields = cls.get_model_fields()
        for field in to_exclude:
            del fields[field]
        return {**cls.get_model_fields(), **cls.get_related_fields()}

    @classmethod
    def get_related_fields(cls):
        return {"fk_paciente": ""}

    @atomic()
    def save_variables(self):
        df = self.df
        df.fillna("", inplace=True)
        load_date = datetime.date(year=self.year, month=self.month, day=self.day)

        numero_fila = 0
        userid = user_loggin_id[0]

        for row in df.itertuples():  # Para cada una de las filas del dataset
            numero_fila = numero_fila+1
            paciente_row = Paciente.objects.get(numero_documento=row.numero_documento)

            # print("VC")
            # print(paciente_row.numero_documento)
            documento_p = paciente_row.numero_documento
            v, status = VariablesClinicas.objects.get_or_create(
                fk_paciente=paciente_row, fecha_cargue=load_date
            )
            v.fk_cargue = self.cargue
            # v.fecha_cargue = load_date
            # v = VariablesClinicas()

            to_exclude = [
                "fecha_albuminuria",
                "fecha_creatinina",
                "fecha_hdl",
                "fecha_ldl",
                "fecha_hemoglobina_glicosilada",
                "fecha_creatinuria",
                "fecha_erc",
                "fecha_hta",
            ]

            fields = self.get_model_fields()
            # print(fields)
            for field in to_exclude:
                del fields[field]

            for (
                field
            ) in fields.keys():  # Para cada uno de los campos, no excluidos del modelo.

                if field != "fecha_cargue":
                    try:
                        row_value = getattr(row, field)
                    except AttributeError:
                        row_value = None
                    field_obj = VariablesClinicas._meta.get_field(field)

                    if type(field_obj) == DateField:
                        if row_value == "" or pd.isnull(row_value):
                            setattr(v, field, None)
                        else:
                            if type(row_value) == str:
                                setattr(
                                    v,
                                    field,
                                    datetime.datetime.strptime(row_value, "%Y-%m-%d"),
                                )
                            else:
                                setattr(v, field, row_value)

                    elif type(field_obj) == BooleanField and type(row_value) != bool:
                        setattr(v, field, bool(row_value))

                    elif type(field_obj) == FloatField:
                        setattr(v, field, row_value or 0.0)

                        # if self.status_patien:
                        #     setattr(v, field,
                        #             row_value or 0.0)
                        # elif not row_value:
                        #     valor_anterior = getattr(VariablesClinicas.objects.filter(fk_paciente=self.p.id).order_by(
                        #         '-fecha_cargue').first(), field)
                        #     setattr(v, field, valor_anterior)
                        # else:
                        #     setattr(v, field, row_value)

                    elif type(field_obj) == IntegerField:
                        setattr(v, field, row_value or 0)
                    else:
                        setattr(v, field, row_value)

            paciente_variables = VariablesClinicas.objects.filter(
                fk_paciente=paciente_row
            )
            ultima_fecha_cargue = (
                paciente_variables.values_list("fecha_cargue", flat=True)
                .order_by("-fecha_cargue")
                .first()
            )

            # Validar campo glucometria, campo flotante, default 0

            if hasattr(row, "glucometria"):

                glucometria = row.glucometria
                validar_funcion = 0

                try:
                    if isinstance(glucometria, int) or isinstance(glucometria, float):
                        validar_funcion = glucometria
                except ValueError:
                    validar_funcion = 0
                
                resultado_glucometria = None

                valglucometria = validar_n_float(validar_funcion)

                if(valglucometria):

                    if(valglucometria['flotante']):
                        resultado_flotante = valglucometria['flotante']
                        resultado_error = valglucometria['error']

                        add_error(numero_fila,documento_p ,resultado_error, "glucometria")
                        resultado_glucometria = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p, valglucometria['error'], "glucometria")    
                        resultado_glucometria = 0
                        
                else:
                    resultado_glucometria = glucometria

                v.glucometria = resultado_glucometria

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

                        # add_error(resultado_error, "colesterol_total")
                        resultado_colesterol_total = resultado_flotante
                    else:
                        # add_error(valcolesterol_total['error'], "colesterol_total")    
                        resultado_colesterol_total = 0

                else:
                    resultado_colesterol_total = colesterol_total

                v.colesterol_total = resultado_colesterol_total

            colesterol_total_row = v.colesterol_total

            #     try:
            #         v.colesterol_total = float(row.colesterol_total)
            #     except ValueError:
            #         v.colesterol_total = 0

            # colesterol_total_row = v.colesterol_total    

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

                        # add_error(resultado_error, "tas")
                        resultado_tas = resultado_flotante
                    else:
                        # add_error(valtas['error'], "tas")    
                        resultado_tas = 0

                else:
                    resultado_tas = tas

                v.tas = resultado_tas

            tas_row = resultado_tas

            # Validar campo creatinina, campo flotante, default 0
            # campo creatinina
            if hasattr(row, "creatinina"):

                creatinina = row.creatinina
                validar_funcion = 0
                
                try:
                    if isinstance(creatinina, int) or isinstance(creatinina, float):
                        validar_funcion = creatinina
                except ValueError:
                    validar_funcion = 0
                
                resultado_creatinina = None

                valcreatinina = validar_n_float(validar_funcion)

                if(valcreatinina):

                    if(valcreatinina['flotante']):
                        resultado_flotante = valcreatinina['flotante']
                        resultado_error = valcreatinina['error']

                        add_error(numero_fila,documento_p, resultado_error, "creatinina")
                        resultado_creatinina = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p, valcreatinina['error'], "creatinina")    
                        resultado_creatinina = 0

                else:
                    resultado_creatinina = creatinina

                v.creatinina = resultado_creatinina

            creatinina_row = v.creatinina

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

                        # add_error(resultado_error, "peso")
                        resultado_peso = resultado_flotante
                    else:
                        # add_error(valpeso['error'], "peso")    
                        resultado_peso = 0
                else:
                    resultado_peso = peso

                v.peso = resultado_peso

            peso_row = v.peso

            # Para actualizar la tfg y el estadio
            if (
                not v.tfg
            ):  # En el caso de que la tfg en el dataset del cargue este vacio
                # peso_row = getattr(v, "peso")

                peso_tfg = peso_row
                creatinina_tfg = creatinina_row

                conjunto_variables = paciente_variables.filter(
                    fecha_cargue__lt=load_date
                )

                if peso_row <= 0:
                    peso_tfg = (
                        conjunto_variables.values_list("peso", flat=True)
                        .filter(peso__isnull=False, peso__gt=0)
                        .order_by("-fecha_cargue")
                        .first()
                    )

                if creatinina_row <= 0:
                    creatinina_tfg = (
                        conjunto_variables.values_list("creatinina", flat=True)
                        .filter(creatinina__isnull=False, creatinina__gt=0)
                        .order_by("-fecha_cargue")
                        .first()
                    )

                if (
                    creatinina_tfg
                    and peso_tfg
                    and paciente_row.genero
                    and paciente_row.fecha_nacimiento
                ):
                    paciente_temporal_tfg = Paciente(
                        genero=paciente_row.genero,
                        fecha_nacimiento=paciente_row.fecha_nacimiento,
                        peso=peso_tfg,
                    )
                    paciente_temporal_tfg.actualizar_riesgo_tfg(
                        creatinina_externa=creatinina_tfg, save=False
                    )
                    tfg_v = paciente_temporal_tfg.tfg
                    estadio_v = paciente_temporal_tfg.estadio
                else:
                    tfg_v = None
                    estadio_v = Paciente().ESTADIO_SIN_CALCULAR

                setattr(v, "tfg", tfg_v)
                setattr(v, "estadio", estadio_v)
            else:
                paciente_temporal_tfg = Paciente(tfg=v.tfg)
                paciente_temporal_tfg.actualizar_riesgo_tfg(save=False)
                setattr(v, "estadio", paciente_temporal_tfg.estadio)

            # Para actualizar el riesgo y el nivel de riesgo cardio vascular
            if (
                not v.riesgo_cardiovascular
            ):  # En el caso de que la riesgo_cardiovascular en el dataset del cargue este vacio
                # colesterol_total_row = getattr(v, "colesterol_total")
                # tas_row = getattr(v, "tas")

                colesterol_total_tfg = colesterol_total_row
                tas_tfg = tas_row

                conjunto_variables = paciente_variables.filter(
                    fecha_cargue__lt=load_date
                )

                if colesterol_total_row <= 0:
                    colesterol_total_tfg = (
                        conjunto_variables.values_list("colesterol_total", flat=True)
                        .filter(colesterol_total__isnull=False, colesterol_total__gt=0)
                        .order_by("-fecha_cargue")
                        .first()
                    )

                if tas_row <= 0:
                    tas_tfg = (
                        conjunto_variables.values_list("tas", flat=True)
                        .filter(tas__isnull=False, tas__gt=0)
                        .order_by("-fecha_cargue")
                        .first()
                    )

                if (
                    tas_tfg
                    and colesterol_total_tfg
                    and paciente_row.genero
                    and paciente_row.fecha_nacimiento
                ):
                    paciente_temporal_rvc = Paciente(
                        genero=paciente_row.genero,
                        fecha_nacimiento=paciente_row.fecha_nacimiento,
                        colesterol_total=colesterol_total_tfg,
                        tas=tas_tfg,
                        es_fumador=paciente_row.es_fumador,
                    )
                    paciente_temporal_rvc.actualizar_riesgocardiovascular(save=False)
                    rvc_v = paciente_temporal_rvc.riesgo_cardiovascular
                    rvc_n_v = paciente_temporal_rvc.nivel_riesgo_rcv
                else:
                    rvc_v = None
                    rvc_n_v = Paciente().NIVEL_RIESGO_RCV_BAJO

                setattr(v, "riesgo_cardiovascular", rvc_v)
                setattr(v, "nivel_riesgo_rcv", rvc_n_v)
            else:
                paciente_temporal_rvc = Paciente(
                    riesgo_cardiovascular=v.riesgo_cardiovascular
                )
                paciente_temporal_rvc.actualizar_riesgocardiovascular(save=False)
                setattr(v, "nivel_riesgo_rcv", paciente_temporal_rvc.nivel_riesgo_rcv)

            # setattr(v, 'fk_paciente', paciente_row)

            # Validations TYT Interactiva

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

                        # add_error(resultado_error, "tad")
                        resultado_tad = resultado_flotante
                    else:
                        # add_error(valtad['error'], "tad")    
                        resultado_tad = 0
                else:
                    resultado_tad = tad

                v.tad = resultado_tad

            # fecha_erc -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_erc"):

                fecha_erc = row.fecha_erc

                valfecha_erc = validar_fecha(fecha_erc)
                resultado_fecha_erc = None
                if(valfecha_erc):
                    add_error(numero_fila,documento_p,valfecha_erc, "fecha_erc")
                    resultado_fecha_erc = fecha_comodin
                else:
                    resultado_fecha_erc = fecha_erc

                v.fecha_erc = resultado_fecha_erc

            #     v.fecha_erc = row.fecha_erc
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     v.fecha_erc = fecha_actual

            # fecha_colesterol -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_colesterol"):

                fecha_colesterol = row.fecha_colesterol

                valfecha_colesterol = validar_fecha(fecha_colesterol)
                resultado_fecha_colesterol = None
                if(valfecha_colesterol):
                    resultado_fecha_colesterol = fecha_comodin
                else:
                    resultado_fecha_colesterol = fecha_colesterol

                v.fecha_colesterol = resultado_fecha_colesterol                

            #     v.fecha_colesterol = row.fecha_colesterol
            # else:
            #     fecha_actual = datetime.datetime.now()
            #     v.fecha_colesterol = fecha_actual


            # microalbuminuria = albuminuria

            # campo albuminuria, default 0
            # Opciones validas:
            # 9888: "No aplica, paciente en TRR",
            # 9999: "No se realizó el laboratorio",
            # 5555: "No aplica, paciente reportado por ente territorial por prestación de servicios no incluidos en el plan de beneficios",

            if hasattr(row, "albuminuria"):
                if row.albuminuria in cargue_albuminuria_choices:
                    v.microalbuminuria = row.albuminuria
                else:
                    
                    albuminuria = row.albuminuria
                    validar_funcion = 0

                    try:
                        if isinstance(albuminuria, int) or isinstance(albuminuria, float):
                            validar_funcion = albuminuria
                    except ValueError:
                        validar_funcion = 0

                    resultado_albuminuria = None    

                    valalbuminuria = validar_n_float(validar_funcion)        

                    if(valalbuminuria):

                        if(valalbuminuria['flotante']):
                            resultado_flotante = valalbuminuria['flotante']
                            resultado_error = valalbuminuria['error']

                            add_error(numero_fila,documento_p,resultado_error, "albuminuria")
                            resultado_albuminuria = resultado_flotante
                        else:
                            add_error(numero_fila,documento_p,valalbuminuria['error'], "albuminuria")    
                            resultado_albuminuria = 0
                    else:
                        resultado_albuminuria = albuminuria

                    v.microalbuminuria = resultado_albuminuria

            # fecha_hta -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_hta"):

                fecha_hta = row.fecha_hta

                valfecha_hta = validar_fecha(fecha_hta)
                resultado_fecha_hta = None
                if(valfecha_hta):
                    add_error(numero_fila,documento_p,valfecha_hta, "fecha_hta")
                    resultado_fecha_hta = fecha_comodin
                else:
                    resultado_fecha_hta = fecha_hta

                v.fecha_hta = resultado_fecha_hta            

            # fecha_albuminuria -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_albuminuria"):
                
                valfecha_albuminuria = validar_fecha(row.fecha_albuminuria)
                resultado_fecha_albuminuria = None
                if(valfecha_albuminuria):
                    add_error(numero_fila,documento_p,valfecha_albuminuria, "fecha_albuminuria")
                    resultado_fecha_albuminuria = fecha_comodin
                else:
                    resultado_fecha_albuminuria = row.fecha_albuminuria

                v.fecha_albuminuria = resultado_fecha_albuminuria

            # fecha_creatinina -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_creatinina"):

                valfecha_creatinina = validar_fecha(row.fecha_creatinina)
                resultado_fecha_creatinina = None
                if(valfecha_creatinina):
                    add_error(numero_fila,documento_p,valfecha_creatinina, "fecha_creatinina")
                    resultado_fecha_creatinina = fecha_comodin
                else:
                    resultado_fecha_creatinina = row.fecha_creatinina
            
                v.fecha_creatinina = resultado_fecha_creatinina


            # fecha_hdl -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_hdl"):

                valfecha_hdl = validar_fecha(row.fecha_hdl)
                resultado_fecha_hdl = None
                if(valfecha_hdl):
                    add_error(numero_fila, documento_p, valfecha_hdl, "fecha_hdl")
                    resultado_fecha_hdl = fecha_comodin
                else:
                    resultado_fecha_hdl = row.fecha_hdl
            
                v.fecha_hdl = resultado_fecha_hdl

            # fecha_ldl -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_ldl"):

                valfecha_ldl = validar_fecha(row.fecha_ldl)
                resultado_fecha_ldl = None
                if(valfecha_ldl):
                    add_error(numero_fila, documento_p, valfecha_ldl, "fecha_ldl")
                    resultado_fecha_ldl = fecha_comodin
                else:
                    resultado_fecha_ldl = row.fecha_ldl

                v.fecha_ldl = resultado_fecha_ldl 

            # ct = trigliceridos, default 0, campo flotante
            if hasattr(row, "trigliceridos"):

                trigliceridos = row.trigliceridos
                validar_funcion = 0

                try:
                    if isinstance(trigliceridos, int) or isinstance(trigliceridos, float):
                        validar_funcion = trigliceridos
                except ValueError:
                    validar_funcion = 0

                resultado_valtrigliceridos = None

                valtrigliceridos = validar_n_float(validar_funcion)        

                if(valtrigliceridos):

                    if(valtrigliceridos['flotante']):
                        resultado_flotante = valtrigliceridos['flotante']
                        resultado_error = valtrigliceridos['error']

                        add_error(numero_fila,documento_p, resultado_error, "trigliceridos")
                        resultado_valtrigliceridos = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p, valtrigliceridos['error'], "trigliceridos")    
                        resultado_valtrigliceridos = 0
                else:
                    resultado_valtrigliceridos = trigliceridos

                v.ct = resultado_valtrigliceridos

            # fecha_hemoglobina_glicosilada -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_hemoglobina_glicosilada"):

                valfecha_hemoglobina_glicosilada = validar_fecha(row.fecha_hemoglobina_glicosilada)
                resultado_fecha_hemoglobina_glicosilada = None
                if(valfecha_hemoglobina_glicosilada):
                    add_error(numero_fila,documento_p, valfecha_hemoglobina_glicosilada, "fecha_hemoglobina_glicosilada")
                    resultado_fecha_hemoglobina_glicosilada = fecha_comodin
                else:
                    resultado_fecha_hemoglobina_glicosilada = row.fecha_hemoglobina_glicosilada

                v.fecha_hemoglobina_glicosilada = resultado_fecha_hemoglobina_glicosilada


            # fecha_creatinuria -> Nuevo campo V.Piloto
            if hasattr(row, "fecha_creatinuria"):

                valfecha_creatinuria = validar_fecha(row.fecha_creatinuria)
                resultado_fecha_creatinuria = None
                if(valfecha_creatinuria):
                    add_error(numero_fila,documento_p,valfecha_creatinuria, "fecha_creatinuria")
                    resultado_fecha_creatinuria = fecha_comodin
                else:
                    resultado_fecha_creatinuria = row.fecha_creatinuria
            
                v.fecha_creatinuria = resultado_fecha_creatinuria

            # evento_cardiovascular -> Nuevo campo V.Piloto
            if hasattr(row, "evento_cardiovascular") and row.evento_cardiovascular == 2:
                v.evento_cardiovascular = 0

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

                        # add_error(resultado_error, "estatura")
                        resultado_estatura = resultado_flotante
                    else:
                        # add_error(valestatura['error'], "estatura")    
                        resultado_estatura = 0
                else:
                    resultado_estatura = estatura

                v.estatura = resultado_estatura    

                # try:
                #     v.estatura = float(row.estatura)
                #     if v.estatura < 100:
                #         v.estatura = float(row.estatura * 100)
                # except ValueError:
                #     v.estatura = 0

            # Validar campo numero_eventos_hipoglicemia, campo numérico, default 0

            if hasattr(row, "numero_eventos_hipoglicemia"):
                # try:
                #     v.numero_eventos_hipoglicemia = int(row.numero_eventos_hipoglicemia)
                # except ValueError:
                #     v.numero_eventos_hipoglicemia = 0

                longitud_numero_eventos_hipoglicemia = 11
                numero_eventos_hipoglicemia = row.numero_eventos_hipoglicemia

                valnumero_eventos_hipoglicemia = validar_n_enteros(numero_eventos_hipoglicemia,  longitud_numero_eventos_hipoglicemia)
                resultado_numero_eventos_hipoglicemia = None
                if(valnumero_eventos_hipoglicemia):

                    if(valnumero_eventos_hipoglicemia['entero']):
                        resultado_entero = valnumero_eventos_hipoglicemia['entero']
                        resultado_error = valnumero_eventos_hipoglicemia['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "numero_eventos_hipoglicemia")
                            resultado_numero_eventos_hipoglicemia = 0
                    else:
                        add_error(numero_fila,documento_p,valnumero_eventos_hipoglicemia['error'], "numero_eventos_hipoglicemia")
                        resultado_numero_eventos_hipoglicemia = 0

                else:
                    resultado_numero_eventos_hipoglicemia = numero_eventos_hipoglicemia

                v.numero_eventos_hipoglicemia = resultado_numero_eventos_hipoglicemia

            # Validar campo tsh, campo flotante, default 0

            if hasattr(row, "tsh"):

                tsh = row.tsh
                validar_funcion = 0

                try:
                    if isinstance(tsh, int) or isinstance(tsh, float):
                        validar_funcion = tsh
                except ValueError:        
                    validar_funcion = 0

                resultado_tsh = None

                valtsh = validar_n_float(validar_funcion)

                if(valtsh):

                    if(valtsh['flotante']):
                        resultado_flotante = valtsh['flotante']
                        resultado_error = valtsh['error']

                        add_error(numero_fila,documento_p,resultado_error, "tsh")
                        resultado_tsh = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valtsh['error'], "tsh")    
                        resultado_tsh = 0

                else:
                    resultado_tsh = tsh

                v.tsh = resultado_tsh

            # Validar campo alat, campo flotante, default 0

            if hasattr(row, "alat"):

                alat = row.alat
                validar_funcion = 0

                try:
                    if isinstance(alat, int) or isinstance(alat, float):
                        validar_funcion = alat
                except ValueError:        
                    validar_funcion = 0

                resultado_alat = None

                valalat = validar_n_float(validar_funcion)

                if(valalat):

                    if(valalat['flotante']):
                        resultado_flotante = valalat['flotante']
                        resultado_error = valalat['error']

                        add_error(numero_fila,documento_p,resultado_error, "alat")
                        resultado_alat = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valalat['error'], "alat")    
                        resultado_alat = 0

                else:
                    resultado_alat = alat

                v.alat = resultado_alat

            # Validar campo glicemia_basal, campo flotante, default 0

            if hasattr(row, "glicemia_basal"):

                glicemia_basal = row.glicemia_basal
                validar_funcion = 0

                try:
                    if isinstance(glicemia_basal, int) or isinstance(glicemia_basal, float):
                        validar_funcion = glicemia_basal
                except ValueError:
                    validar_funcion = 0

                resultado_glicemia_basal = None

                valglicemia_basal = validar_n_float(validar_funcion)       

                if(valglicemia_basal):

                    if(valglicemia_basal['flotante']):
                        resultado_flotante = valglicemia_basal['flotante']
                        resultado_error = valglicemia_basal['error']

                        add_error(numero_fila,documento_p,resultado_error, "glicemia_basal")
                        resultado_glicemia_basal = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valglicemia_basal['error'], "glicemia_basal")    
                        resultado_glicemia_basal = 0
                else:
                    resultado_glicemia_basal = glicemia_basal

                v.glicemia_basal = resultado_glicemia_basal

            # Validar campo asat, campo flotante, default 0

            if hasattr(row, "asat"):

                asat = row.asat
                validar_funcion = 0
               
                try:
                    if isinstance(asat, int) or isinstance(asat, float):
                        validar_funcion = asat
                except ValueError:
                    validar_funcion = 0

                resultado_asat = None

                valasat = validar_n_float(validar_funcion)        

                if(valasat):

                    if(valasat['flotante']):
                        resultado_flotante = valasat['flotante']
                        resultado_error = valasat['error']

                        add_error(numero_fila,documento_p,resultado_error, "asat")
                        resultado_asat = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valasat['error'], "asat")    
                        resultado_asat = 0
                else:
                    resultado_asat = asat

                v.asat = resultado_asat


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

                        # add_error(numero_fila,documento_p,resultado_error, "hdl")
                        resultado_hdl = resultado_flotante
                    else:
                        # add_error(numero_fila,documento_p,valhdl['error'], "hdl")
                        resultado_hdl = 0
                else:
                    resultado_hdl = hdl

                v.hdl = resultado_hdl
                

            # Validar campo ldl, campo flotante, default 0

            if hasattr(row, "ldl"):

                ldl = row.ldl
                validar_funcion = 0

                try:
                    if isinstance(ldl, int) or isinstance(ldl, float):
                        validar_funcion = ldl
                except ValueError:
                    validar_funcion = 0

                resultado_ldl = None

                valldl = validar_n_float(validar_funcion)

                if(valldl):

                    if(valldl['flotante']):
                        resultado_flotante = valldl['flotante']
                        resultado_error = valldl['error']

                        add_error(numero_fila,documento_p,resultado_error, "ldl")
                        resultado_ldl = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valldl['error'], "ldl")
                        resultado_ldl = 0
                else:
                    resultado_ldl = ldl

                v.ldl = resultado_ldl

            # Validar campo hemoglobina_glicosilada, campo flotante, default 0

            if hasattr(row, "hemoglobina_glicosilada"):

                hemoglobina_glicosilada = row.hemoglobina_glicosilada
                validar_funcion = 0

                try:
                    if isinstance(hemoglobina_glicosilada, int) or isinstance(hemoglobina_glicosilada, float):
                        validar_funcion = hemoglobina_glicosilada
                except ValueError:
                    validar_funcion = 0

                resultado_hemoglobina_glicosilada = None    

                valhemoglobina_glicosilada = validar_n_float(validar_funcion)

                if(valhemoglobina_glicosilada):

                    if(valhemoglobina_glicosilada['flotante']):
                        resultado_flotante = valhemoglobina_glicosilada['flotante']
                        resultado_error = valhemoglobina_glicosilada['error']

                        add_error(numero_fila,documento_p,resultado_error, "hemoglobina_glicosilada")
                        resultado_hemoglobina_glicosilada = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valhemoglobina_glicosilada['error'], "hemoglobina_glicosilada")
                        resultado_hemoglobina_glicosilada = 0
                else:
                    resultado_hemoglobina_glicosilada = hemoglobina_glicosilada

                v.hemoglobina_glicosilada = resultado_hemoglobina_glicosilada    

            # Validar campo numero_hospitalizaciones, campo numerico, default 0

            if hasattr(row, "numero_hospitalizaciones"):

                longitud_numero_hospitalizaciones = 11
                numero_hospitalizaciones = row.numero_hospitalizaciones

                valnumero_hospitalizaciones = validar_n_enteros(numero_hospitalizaciones,  longitud_numero_hospitalizaciones)
                resultado_numero_hospitalizaciones = None
                if(valnumero_hospitalizaciones):

                    if(valnumero_hospitalizaciones['entero']):
                        resultado_entero = valnumero_hospitalizaciones['entero']
                        resultado_error = valnumero_hospitalizaciones['error']

                        if resultado_entero is not None:
                            add_error(numero_fila,documento_p,resultado_error, "numero_hospitalizaciones")
                            resultado_numero_hospitalizaciones = resultado_entero
                    else:
                        add_error(numero_fila,documento_p,valnumero_hospitalizaciones['error'], "numero_hospitalizaciones")
                        resultado_numero_hospitalizaciones = 0    

                else:
                    resultado_numero_hospitalizaciones = numero_hospitalizaciones

                v.numero_hospitalizaciones = resultado_numero_hospitalizaciones    

            # Validar campo relacion_microalbuminuria_creatinuria, campo numerico, default 0

            if hasattr(row, "relacion_microalbuminuria_creatinuria"):

                relacion_microalbuminuria_creatinuria = row.relacion_microalbuminuria_creatinuria
                validar_funcion = 0

                try:
                    if isinstance(relacion_microalbuminuria_creatinuria, int) or isinstance(relacion_microalbuminuria_creatinuria, float):
                        validar_funcion = relacion_microalbuminuria_creatinuria
                except ValueError:
                    validar_funcion = 0

                resultado_relacion_microalbuminuria_creatinuria = None

                valrelacion_microalbuminuria_creatinuria = validar_n_float(validar_funcion)

                if(valrelacion_microalbuminuria_creatinuria):

                    if(valrelacion_microalbuminuria_creatinuria['flotante']):
                        resultado_flotante = valrelacion_microalbuminuria_creatinuria['flotante']
                        resultado_error = valrelacion_microalbuminuria_creatinuria['error']

                        add_error(numero_fila,documento_p,resultado_error, "relacion_microalbuminuria_creatinuria")
                        resultado_relacion_microalbuminuria_creatinuria = resultado_flotante
                    else:
                        add_error(numero_fila,documento_p,valrelacion_microalbuminuria_creatinuria['error'], "relacion_microalbuminuria_creatinuria")
                        resultado_relacion_microalbuminuria_creatinuria = 0    

                else:
                    resultado_relacion_microalbuminuria_creatinuria = relacion_microalbuminuria_creatinuria

                v.relacion_microalbuminuria_creatinuria = resultado_relacion_microalbuminuria_creatinuria    

            v.save()
            
            newest = (
                VariablesClinicas.objects.filter(fk_paciente=paciente_row)
                .order_by("-fecha_cargue")
                .first()
            )

            if newest:
                paciente_row.estadio = newest.estadio
                paciente_row.tfg = newest.tfg
                paciente_row.save()
        
        add_errors_array(errores)
        
        sort_array_errors = [] 
        errores_totales = errores_total[0]
        
        for i in range(len(errores_totales)):
            sort_array_errors.append(errores_totales[i]["numero_fila"])
  
        sort_array_errors.sort()

        filas_errores = list(set(sort_array_errors))

        if len(sort_array_errors) > 0:
            longitud = sort_array_errors[-1]
        else:
            longitud = 0


        # print(sort_array_errors)

        save_errors = [] 

        for fila in filas_errores:
            for error in errores_total[0]:
                if error["numero_fila"] == fila:
                    save_errors.append(error)

        
        # print(save_errors)

        def get_document(fila):
            longitud_array = len(save_errors)
            for i in range(longitud_array):
                if fila == save_errors[i]["numero_fila"]:
                    return(save_errors[i]["documento_p"])


        for fila_aux in filas_errores:
            fila = fila_aux
            documento = get_document(fila)
            usuario = User.objects.get(id=userid)
            archivo = CargueBackOffice.objects.last()
            new_log = Logs_cargue(user = usuario, nombre_archivo = archivo, numero_fila = fila, numero_documento = documento)  

            new_log.save()
            for error in save_errors:
                if error["numero_fila"] == fila_aux:
                    columna = error['columna']
                    mensaje = error['mensaje_error']
                    new_errores = Error_cargue(logs_cargue = new_log, columna = columna, mensaje_error = mensaje )
                    new_errores.save()

        del errores_total[:]

        logs_cargue = Logs_cargue.objects.select_related('nombre_archivo', 'user').prefetch_related('error_cargue_set').order_by('id')

        generar_reporte_excel(logs_cargue)

        save_errors.clear()
        errores_total.clear()
        errores.clear()