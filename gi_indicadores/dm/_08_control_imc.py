from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class ControlIMC(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlIMC, self).__init__(
            **{
                "name": "Control IMC",
                "slug": "control-imc-dm",
                "description": "Pacientes con valor de IMC entre 20-25 sobre el total de la cohorte",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        drop_cols = [
            "colesterol_total",
            "hdl",
            "tas",
            "tad",
            "ldl",
            "albuminuria",
            "creatinina",
            "hba1c",
        ]
        main = df.copy()
        main.drop(columns=drop_cols, inplace=True)

        # Se crea una columna para separas los pacientes con 20<=IMC<=25
        main["imc_criterio"] = np.where(
            ((main["IMC"] <= 25) & (main["IMC"] >= 20)), 1, 0
        )

        return main

    def calc(self, **kwargs) -> DataFrame:
        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        control_IMC = main.copy()

        control_IMC.drop(columns="IMC", inplace=True)

        # Se crean columnas para almacenar cuentas y suma de criterio por mes
        control_IMC["pacientes_cuenta"] = control_IMC["imc_criterio"]
        control_IMC["pacientes_imc"] = control_IMC["imc_criterio"]

        control_IMC = control_IMC.groupby(["Fecha"], as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_imc": "sum"}
        )
        control_IMC.reset_index(inplace=True)
        control_IMC["variable"] = "ControlIMC"
        control_IMC["valor"] = (
            control_IMC["pacientes_imc"] / control_IMC["pacientes_cuenta"]
        )
        control_IMC.drop(columns=["pacientes_cuenta", "pacientes_imc"], inplace=True)
        control_IMC["flag"] = False

        # Se formatea para la salida
        return control_IMC.sort_values(by="Fecha", ascending=False)

    def calc_value(self, **kwargs):
        df = self.calc(**kwargs)
        main = df.to_dict(orient="records") if not df.empty else []
        # TODO: trend
        return {"value": main[0]["valor"] if len(main) > 0 else 0, "trend": True}

    def get_historic(self, **kwargs) -> Tuple[List[str], List[float]]:
        df = self.calc(**kwargs)
        try:
            newest_date = df["Fecha"].max()
            oldest_date = newest_date - relativedelta(years=1)
            df = df[
                (to_datetime(df.Fecha) >= oldest_date)
                & (to_datetime(df.Fecha) <= newest_date)
            ]
            df = df.sort_values(by="Fecha", ascending=True)
        except:
            pass
        data = df.to_dict(orient="records") if not df.empty else []
        fechas = [d.get("Fecha").strftime("%Y-%m") for d in data]
        values = [d.get("valor", 0) for d in data]
        return fechas, values

    def get_pacientes_interes(self, **kwargs):
        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df)

        # Se filtran los pacientes que no cumplen con el criterio del indicador
        pacientes_resto = main.copy()[main["imc_criterio"] == 0]

        # Se conservan las columnas de interes
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
