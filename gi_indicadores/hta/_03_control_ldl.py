from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class ControlLdlHTA(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlLdlHTA, self).__init__(
            **{
                "name": "Toma de LDL",
                "slug": "toma-ldl-hta",
                "description": "Pacientes diabéticos con control cifras de tension arterial menor a 140/90.",
                "label": "Tasa",
                "tipo": "HTA",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        main = df[["Fecha", "numero_documento", "ldl"]].copy()

        # Se crea una columna para separas los pacientes con valores de interes en ldl
        main["ldl_criterio"] = np.where(
            ((main["ldl"] != np.nan) & (main["ldl"] != 0)), 1, 0
        )
        print(main["ldl_criterio"].sum())
        # main.drop(columns='dummy', inplace=True)

        # Agrupacion por numero de documento y fecha

        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()
        main["ldl_criterio"] = main.groupby(level=0)["ldl"].apply(
            lambda x: x.rolling(12, 1).sum()
        )
        main["ldl_criterio"] = np.where((main["ldl_criterio"] > 0), 1, 0)

        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)

        control_ldl = main.copy()

        control_ldl.reset_index(inplace=True)
        control_ldl.drop(columns=["ldl", "numero_documento"], inplace=True)

        control_ldl["pacientes_cuenta"] = control_ldl["ldl_criterio"]
        control_ldl["pacientes_suma"] = control_ldl["ldl_criterio"]

        control_ldl = control_ldl.groupby("Fecha", as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_suma": "sum"}
        )
        control_ldl["valor"] = (
            control_ldl["pacientes_suma"] / control_ldl["pacientes_cuenta"]
        ).apply(lambda x: round(x, 2))

        control_ldl.drop(columns=["pacientes_cuenta", "pacientes_suma"], inplace=True)
        control_ldl.reset_index(inplace=True)

        control_ldl["variable"] = "ControlLDL"
        control_ldl["flag"] = 1

        control_ldl = control_ldl[["Fecha", "variable", "valor", "flag"]]

        # Deteminacion de flag
        control_ldl["flag"] = control_ldl["flag"].rolling(12, 1).sum()
        control_ldl["flag"] = np.where((control_ldl["flag"] >= 13), False, True)

        # Se formatea para la salida
        return control_ldl.sort_values(by="Fecha", ascending=False)

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

        pacientes_resto = main.copy()[main["ldl_criterio"] == 0].reset_index()
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
