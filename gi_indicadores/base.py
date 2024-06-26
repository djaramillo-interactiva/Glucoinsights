import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

base_dir = "/data/notebook_files/"
folder_bbraun_source = os.path.join(base_dir, "source")

"""
if 'df_pacientes' not in locals():
    df_resultado_detallado_previo = pd.read_excel(
        io=os.path.join(folder_bbraun_source, '.xlsx'),
        dtype={
            'Contexto': str,
            'Fecha': 'datetime64[ns]',
            'Variable': str,
            'PorcentajeCumplimiento': float,
            'Real': float,
            'Presupuesto': float,
            'CodigoEmpleado': str,
            'Porcentaje': float,
            'Consecutivo': int,
            'TipoEmpleado': str,
            'SalarioVariable': float,
            'AreaCalculo': int,
            'Apellidos': str,
            'Nombre': str,
            'FechaIngreso': 'datetime64[ns]',
            'FactorIncentivo': float,
            'FactorMes': int,
            'Liquidado': float,
            'DifMonths': int,
            'NuevoFactor': int,
            'ResultadoPresupuesto': float,
            'ResultadoRealMes': float,
            'PorcentajeCumplimientoMes': float
        }
    )
    
"""
