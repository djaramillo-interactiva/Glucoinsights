from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class MetaHemoglobina(AbstractIndicador):
    def __init__(self, **kwargs):
        super(MetaHemoglobina, self).__init__(
            **{
                "name": "Meta de Hba1c",
                "slug": "meta-hemoglobina-dm",
                "description": "Pacientes con toma de Hba1c en los últimos 12 meses con valor menor a 7, sobre total pacientes con toma de Hba1c en los últimos 12 meses.",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        main = df[["Fecha", "numero_documento", "hba1c"]].copy()

        # Agrupacion, inicial, por numero de documento y fecha para generar multiindex

        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()

        main["control"] = main.groupby(level=0)["hba1c"].apply(
            lambda x: x.rolling(12, 1).apply(
                lambda s: s[s > 0].iloc[-1] if not s[s > 0].empty else 0
            )
        )
        main.reset_index(inplace=True)

        main = main[main["control"] > 0]

        # Se separan los registros segun criterio de hba1c generndo unos y ceros, el valor de la variable se omite
        main["control"] = np.where((main["control"] < 7), 1, 0)

        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        meta_de_hba1c = main.copy()

        meta_de_hba1c.drop(columns=["hba1c"], inplace=True)

        meta_de_hba1c["pacientes_cuenta"] = meta_de_hba1c["control"]
        meta_de_hba1c["pacientes_suma"] = meta_de_hba1c["control"]

        meta_de_hba1c = meta_de_hba1c.groupby("Fecha", as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_suma": "sum"}
        )
        meta_de_hba1c["valor"] = (
            meta_de_hba1c["pacientes_suma"] / meta_de_hba1c["pacientes_cuenta"]
        ).apply(lambda x: round(x, 2))

        # Se eliminan columnas que pierden interes

        meta_de_hba1c.drop(columns=["pacientes_cuenta", "pacientes_suma"], inplace=True)

        # Formatear para salida
        meta_de_hba1c.reset_index(inplace=True)
        meta_de_hba1c["variable"] = "MetaDeHbA1C"
        meta_de_hba1c["flag"] = 1
        meta_de_hba1c = meta_de_hba1c[["Fecha", "variable", "valor", "flag"]]

        # Deteminacion de flag

        meta_de_hba1c["flag"] = meta_de_hba1c["flag"].rolling(12, 1).sum()
        meta_de_hba1c["flag"] = np.where((meta_de_hba1c["flag"] >= 12), False, True)

        # Se formatea para la salida
        return meta_de_hba1c.sort_values(by="Fecha", ascending=False)

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
