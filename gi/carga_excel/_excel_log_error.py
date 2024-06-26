import os
from django.conf import settings

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def generar_reporte_excel(logs_cargue):
    # Crear un DataFrame vacío
    df = pd.DataFrame(columns=['Numero_fila', 'Numero_documento', 'Username_cargue', 'Nombre archivo', 'Columna', 'Mensaje de error'])

    for log in logs_cargue:
        lista_errores = log.error_cargue_set.all().order_by('id')
        for lista_error in lista_errores:
            df = df.append({
                'Numero_fila': log.numero_fila,
                'Numero_documento': log.numero_documento,
                'Username_cargue': log.user.username,
                'Nombre archivo': log.nombre_archivo.excel_file.name,  # Usar el nombre del archivo, no el objeto FieldFile
                'Columna': lista_error.columna,
                'Mensaje de error': lista_error.mensaje_error
            }, ignore_index=True)

    # Crear un libro de trabajo y obtener la hoja de trabajo
    wb = Workbook()
    ws = wb.active

    # Escribir el DataFrame en la hoja de trabajo
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    # Obtén la ruta absoluta de la carpeta media/cargues
    output_path = os.path.join(settings.MEDIA_ROOT, 'cargues')

    # Guardar el libro de trabajo en un archivo
    wb.save(os.path.join(output_path, "reporte.xlsx"))
