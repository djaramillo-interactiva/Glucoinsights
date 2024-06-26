from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class MetaLdl(AbstractIndicador):
    def __init__(self, **kwargs):
        super(MetaLdl, self).__init__(
            **{
                "name": "Meta de LDL",
                "slug": "meta-ldl-dm",
                "description": "Pacientes con toma de LDL en los últimos 12 meses con valor menor a < 100 mg /dl, sobre total pacientes con toma de LDL en los últimos 12 meses.",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        main = df[["Fecha", "numero_documento", "ldl"]].copy()

        # Agrupacion, inicial, por numero de documento y fecha para generar multiindex

        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()

        main["control"] = main.groupby(level=0)["ldl"].apply(
            lambda x: x.rolling(12, 1).apply(
                lambda s: s[s > 0].iloc[-1] if not s[s > 0].empty else 0
            )
        )
        main.reset_index(inplace=True)

        main = main[main["control"] > 0]

        # Se separan los registros segun criterio de hba1c generndo unos y ceros, el valor de la variable se omite
        main["control"] = np.where((main["control"] < 100), 1, 0)

        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        meta_de_ldl = main.copy()

        meta_de_ldl.drop(columns=["ldl"], inplace=True)

        meta_de_ldl["pacientes_cuenta"] = meta_de_ldl["control"]
        meta_de_ldl["pacientes_suma"] = meta_de_ldl["control"]

        meta_de_ldl = meta_de_ldl.groupby("Fecha", as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_suma": "sum"}
        )
        meta_de_ldl["valor"] = (
            meta_de_ldl["pacientes_suma"] / meta_de_ldl["pacientes_cuenta"]
        ).apply(lambda x: round(x, 2))

        # Se eliminan columnas que pierden interes

        meta_de_ldl.drop(columns=["pacientes_cuenta", "pacientes_suma"], inplace=True)

        # Formatear para salida
        meta_de_ldl.reset_index(inplace=True)
        meta_de_ldl["variable"] = "MetaDeLDL"
        meta_de_ldl["flag"] = 1
        meta_de_ldl = meta_de_ldl[["Fecha", "variable", "valor", "flag"]]

        # Deteminacion de flag
        meta_de_ldl["flag"] = meta_de_ldl["flag"].rolling(12, 1).sum()
        meta_de_ldl["flag"] = np.where((meta_de_ldl["flag"] >= 12), False, True)

        # Se formatea para la salida
        return meta_de_ldl.sort_values(by="Fecha", ascending=False)

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
        pacientes_resto = main.copy()[main["control"] == 0]

        # Se conservan las columnas de interes
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
