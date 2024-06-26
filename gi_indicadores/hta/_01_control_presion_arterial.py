from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class ControlPresionArterialHTA(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlPresionArterialHTA, self).__init__(
            **{
                "name": "Toma de presion arterial",
                "slug": "Toma-presion-arterial-hta",
                "description": "Pacientes con HTA en control de presión arterial (menor a 140/90) sobre total de pacientes con HTA.",
                "label": "Tasa",
                "tipo": "HTA",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df
        drop_cols = [
            "colesterol_total",
            "hdl",
            "IMC",
            "hba1c",
            "ldl",
            "albuminuria",
            "creatinina",
        ]
        main = df.copy()
        main.drop(columns=drop_cols, inplace=True)
        main["control"] = np.where(((main["tas"] <= 140) & (main["tad"] <= 90)), 1, 0)
        return main.sort_values(by="Fecha", ascending=False)

    def calc(self, **kwargs) -> DataFrame:
        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        main["pacientes"] = 1
        # Se suman los valores del dataframe con agrupación por fecha para numerador y denominador por fecha
        main = main.groupby(["Fecha"], as_index=False)[["control", "pacientes"]].apply(
            sum
        )
        main.reset_index(inplace=True)
        # Se establece una columna con el nombre del indicador
        main["variable"] = "ControlPresionArterial"
        # Se determina el flag que indica si el indicador, por mes, conto con data suficiente en el calculo
        main["flag"] = False
        # Se determina el valor del indicador como un cociente
        main["valor"] = (main["control"] / main["pacientes"]).apply(
            lambda x: round(x, 2)
        )
        # Se formatea para la salida
        return main[["Fecha", "variable", "valor", "flag"]]

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

        pacientes_resto = main.copy()[main["control"] == 0].reset_index()
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
