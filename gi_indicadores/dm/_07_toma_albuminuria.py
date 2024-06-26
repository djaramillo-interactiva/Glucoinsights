from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class TomaAlbuminuria(AbstractIndicador):
    def __init__(self, **kwargs):
        super(TomaAlbuminuria, self).__init__(
            **{
                "name": "Toma de albuminuria",
                "slug": "toma-albuminuria-dm",
                "description": "Pacientes con toma de Albuminuria en los últimos 12 meses sobre el total de la cohorte.",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        main = df[["Fecha", "numero_documento", "albuminuria"]].copy()

        # Se crea una columna para separas los pacientes con valores de interes en ldl
        main["albuminura_criterio"] = np.where(
            ((main["albuminuria"] != np.nan) & (main["albuminuria"] != 0)), 1, 0
        )
        print(main["albuminura_criterio"].sum())
        # main.drop(columns='dummy', inplace=True)

        # Agrupacion por numero de documento y fecha

        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()
        main["albuminura_criterio"] = main.groupby(level=0)[
            "albuminura_criterio"
        ].apply(lambda x: x.rolling(12, 1).sum())

        main["albuminura_criterio"] = np.where((main["albuminura_criterio"] > 0), 1, 0)

        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        control_albuminuria = main.copy()

        control_albuminuria.reset_index(inplace=True)
        control_albuminuria.drop(
            columns=["albuminuria", "numero_documento"], inplace=True
        )

        control_albuminuria["pacientes_cuenta"] = control_albuminuria[
            "albuminura_criterio"
        ]
        control_albuminuria["pacientes_suma"] = control_albuminuria[
            "albuminura_criterio"
        ]

        control_albuminuria = control_albuminuria.groupby("Fecha", as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_suma": "sum"}
        )
        control_albuminuria["valor"] = (
            control_albuminuria["pacientes_suma"]
            / control_albuminuria["pacientes_cuenta"]
        ).apply(lambda x: round(x, 2))

        control_albuminuria.drop(
            columns=["pacientes_cuenta", "pacientes_suma"], inplace=True
        )
        control_albuminuria.reset_index(inplace=True)

        control_albuminuria["variable"] = "ControlAlbuminuria"
        control_albuminuria["flag"] = 1

        control_albuminuria = control_albuminuria[
            ["Fecha", "variable", "valor", "flag"]
        ]

        # Deteminacion de flag
        control_albuminuria["flag"] = control_albuminuria["flag"].rolling(12, 1).sum()
        control_albuminuria["flag"] = np.where(
            (control_albuminuria["flag"] >= 13), False, True
        )
        # Se formatea para la salida
        return control_albuminuria.sort_values(by="Fecha", ascending=False)

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
        pacientes_resto = main.copy()[main["albuminura_criterio"] == 0].reset_index()

        # Se conservan las columnas de interes
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
