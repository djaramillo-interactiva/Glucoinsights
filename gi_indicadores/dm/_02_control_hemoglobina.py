from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class ControlHemoglobina(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlHemoglobina, self).__init__(
            **{
                "name": "Toma de Hba1c",
                "slug": "toma-hemoglobina-dm",
                "description": "Pacientes con toma de Hba1c en los últimos 6 meses sobre total de la cohorte.",
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
            "IMC",
            "ldl",
            "albuminuria",
            "creatinina",
        ]
        main = df.copy()
        main.drop(columns=drop_cols, inplace=True)

        # Columna TOMA es 1 si tiene valor en ese mes o 0 si no.
        main["toma"] = np.where(
            ((main["hba1c"] != np.nan) & (main["hba1c"] != 0)), 1, 0
        )
        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        # Agrupamos por multindex y aplicamos rolling individal (paciente) a una columna de control
        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()
        main["control"] = main.groupby(level=0)["toma"].apply(
            lambda x: x.rolling(6, 1).sum()
        )

        main["control"] = np.where((main["control"] > 0), 1, 0)

        control_hemoglobina = main.copy()

        control_hemoglobina.drop(columns=["hba1c", "toma"], inplace=True)

        # Contar y sumar pacientes por mes
        control_hemoglobina.reset_index(inplace=True)
        control_hemoglobina["pacientes"] = control_hemoglobina["control"]
        control_hemoglobina["pacientes_control"] = control_hemoglobina["control"]
        control_hemoglobina = control_hemoglobina.groupby(["Fecha"], as_index=True).agg(
            {"pacientes": "count", "pacientes_control": "sum"}
        )
        control_hemoglobina["valor"] = (
            control_hemoglobina["pacientes_control"] / control_hemoglobina["pacientes"]
        ).apply(lambda x: round(x, 2))

        # Formatear para salida
        control_hemoglobina.reset_index(inplace=True)
        control_hemoglobina["variable"] = "controlHemoglobina"
        control_hemoglobina["flag"] = 1
        control_hemoglobina = control_hemoglobina[
            ["Fecha", "variable", "valor", "flag"]
        ]

        # Calculamos el flag
        control_hemoglobina["flag"] = control_hemoglobina["flag"].rolling(6, 1).sum()
        control_hemoglobina["flag"] = np.where(
            (control_hemoglobina["flag"] >= 6), False, True
        )

        # Se formatea para la salida
        return control_hemoglobina.sort_values(by="Fecha", ascending=False)

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

        pacientes_resto = main.copy()[main["toma"] == 0].reset_index()
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
