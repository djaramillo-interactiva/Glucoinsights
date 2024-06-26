from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class TomaCreatinina(AbstractIndicador):
    def __init__(self, **kwargs):
        super(TomaCreatinina, self).__init__(
            **{
                "name": "Toma de creatinina",
                "slug": "toma-de-creatinina-dm",
                "description": "Pacientes con toma de Creatinina en los últimos 12 meses sobre el total de la cohorte.",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        main = df[["Fecha", "numero_documento", "creatinina"]].copy()

        # main['dummy']=np.random.randint(0, 5, main.shape[0])

        # Se crea una columna para separas los pacientes con valores de interes en ldl
        main["creatinina_criterio"] = np.where(
            ((main["creatinina"] != np.nan) & (main["creatinina"] != 0)), 1, 0
        )
        print(main["creatinina_criterio"].sum())
        # main.drop(columns='dummy', inplace=True)

        # Agrupacion por numero de documento y fecha

        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()
        main["creatinina_criterio"] = main.groupby(level=0)[
            "creatinina_criterio"
        ].apply(lambda x: x.rolling(12, 1).sum())

        main["creatinina_criterio"] = np.where((main["creatinina_criterio"] > 0), 1, 0)

        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)
        control_creatinina = main.copy()
        control_creatinina.reset_index(inplace=True)

        control_creatinina.drop(
            columns=["creatinina", "numero_documento"], inplace=True
        )

        control_creatinina["pacientes_cuenta"] = control_creatinina[
            "creatinina_criterio"
        ]
        control_creatinina["pacientes_suma"] = control_creatinina["creatinina_criterio"]

        control_creatinina = control_creatinina.groupby("Fecha", as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_suma": "sum"}
        )
        control_creatinina["valor"] = (
            control_creatinina["pacientes_suma"]
            / control_creatinina["pacientes_cuenta"]
        ).apply(lambda x: round(x, 2))

        control_creatinina.drop(
            columns=["pacientes_cuenta", "pacientes_suma"], inplace=True
        )
        control_creatinina.reset_index(inplace=True)

        control_creatinina["variable"] = "ControlCreatinina"
        control_creatinina["flag"] = 1

        control_creatinina = control_creatinina[["Fecha", "variable", "valor", "flag"]]

        # Deteminacion de flag
        control_creatinina["flag"] = control_creatinina["flag"].rolling(12, 1).sum()
        control_creatinina["flag"] = np.where(
            (control_creatinina["flag"] >= 12), False, True
        )

        # Se formatea para la salida
        return control_creatinina.sort_values(by="Fecha", ascending=False)

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
        pacientes_resto = main.copy()[main["creatinina_criterio"] == 0]

        pacientes_resto.reset_index(inplace=True)

        # Se conservan las columnas de interes
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
