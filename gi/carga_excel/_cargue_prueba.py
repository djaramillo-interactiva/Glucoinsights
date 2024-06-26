import pandas as pd
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from . import dto_mapper
from ._pacientes import CargaPacienteDto
from ._variables_clinicas import CargaVariablesClinicas
from gi.models import CargueBackOffice


@receiver(post_save, sender=CargueBackOffice)
def create_models_after_load_excel(sender, instance: CargueBackOffice, **kwargs):
    print("post save callback")
    route = instance.excel_file.file.file.name
    if instance.data_type == "pacientes":
        user = instance.user
        ejecutar_cargue(
            user, route, month=int(instance.month), year=int(instance.year), cargue=instance
        )
    else:
        cargar_relacionados(route, instance)

    print("post save callback")


def ejecutar_cargue(user, route, month=1, year=2022, cargue=None):
    ############################Para cargue desde drive
    # import ssl
    # ssl._create_default_https_context = ssl._create_unverified_context
    # sheet_id = '1yIHX0N6V6jZAkbpHYyTp3o6iSJuA8aaV41AGpdnpG_0'
    # sheet_name = 'paciente-examenes-controles'
    # url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:xslx&sheet={sheet_name}"
    # url='https://docs.google.com/spreadsheets/d/1yIHX0N6V6jZAkbpHYyTp3o6iSJuA8aaV41AGpdnpG_0/edit#gid=0'
    #####################################


    df = pd.read_excel(route)
    data_patient = CargaPacienteDto(df)
    data_patient.save_patients(user)
    data_variables_c = CargaVariablesClinicas(
        df=df, year=year, month=month, cargue=cargue
    )
    data_variables_c.save_variables()


def cargar_relacionados(route, cargue: CargueBackOffice):
    dto_model = dto_mapper[cargue.data_type]
    df = pd.read_excel(route)
    carga = dto_model(df)
    total, errors = carga.save_registros(cargue)
