from typing import Tuple, List

from pandas import DataFrame, Timestamp, to_datetime

from gi_indicadores.indicador import AbstractIndicador
from dateutil.relativedelta import relativedelta


class PerdidaTFG(AbstractIndicador):
    def __init__(self, **kwargs):
        super(PerdidaTFG, self).__init__(
            **{
                "name": "Pérdida de tasa de filtración glomerular (TFG)",
                "slug": "perdida-tfg",
                "description": "Pacientes con pérdida de TFG de 5ml/min/año sobre total de cohorte.",
                "label": "Tasa",
                "tipo": "ERC",
            }
        )

    def get_column_filter(selft, df: DataFrame):
        import numpy as np

        if df.empty:
            return df

        # Pacientes que han perdido 5ml/min/año
        # Sobre total de cohorte

        main = df[["Fecha", "numero_documento", "tfg"]].copy()

        main = main.groupby(["numero_documento", "Fecha"], as_index=True).sum()

        # Con la configuracion actual del .rolling se esta tomando la diferencia entre el mes en cuestion y el numero 12 hacia atras, contando el mes en cuestion (por ejemplo el valor de diciembre menos el valor del enero inmediatamente anterior)
        # ToDo pregutar por el oreden de la resta, en este momento esta el mas antiguo mesno el mas nuevo
        main["control"] = main.groupby(level=0)["tfg"].apply(
            lambda x: x.rolling(12, 1).apply(
                lambda s: (
                    s[s > 0].iloc[0] - s[s > 0].iloc[-1]
                    if not s[s > 0].empty
                    else np.nan
                )
            )
        )

        # ToDo Preguntar si los negativos (un aumeto de TFG tiene sentido?) se cuentan en la poblacion
        # ToDo Preguntar si el numerador son los pacientes con exactamente 5 de perdida de TFG o los mayores oiguales a 5
        main["control"] = np.where((main["control"] >= 5), 1, 0)

        return main

    def calc(self, **kwargs) -> DataFrame:
        import numpy as np

        df = kwargs.get("df")
        if df.empty:
            return df
        main = self.get_column_filter(df=df)
        perdida_tfg = main.copy()

        perdida_tfg.reset_index(inplace=True)

        # Se reiran columnas que no son de interes
        perdida_tfg.drop(columns="tfg", inplace=True)

        perdida_tfg["pacientes_cuenta"] = perdida_tfg["control"]
        perdida_tfg["pacientes_suma"] = perdida_tfg["control"]

        # Se detemina, por mes, la poblacion y los pacientes que cumplen el criterio
        perdida_tfg = perdida_tfg.groupby("Fecha", as_index=True).agg(
            {"pacientes_cuenta": "count", "pacientes_suma": "sum"}
        )
        perdida_tfg["valor"] = (
            perdida_tfg["pacientes_suma"] / perdida_tfg["pacientes_cuenta"]
        ).apply(lambda x: round(x, 2))

        # Se eliminan columnas que pierden interes

        perdida_tfg.drop(columns=["pacientes_cuenta", "pacientes_suma"], inplace=True)

        # Formatear para salida
        perdida_tfg.reset_index(inplace=True)
        perdida_tfg["variable"] = "PerdidaDeTFG"
        perdida_tfg["flag"] = 1
        perdida_tfg = perdida_tfg[["Fecha", "variable", "valor", "flag"]]

        # Deteminacion de flag
        perdida_tfg["flag"] = perdida_tfg["flag"].rolling(12, 1).sum()
        perdida_tfg["flag"] = np.where((perdida_tfg["flag"] >= 12), False, True)

        # Se formatea para la salida
        return perdida_tfg.sort_values(by="Fecha", ascending=False)

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
        pacientes_resto.reset_index(inplace=True)
        # Se conservan las columnas de interes
        pacientes_resto = pacientes_resto[["Fecha", "numero_documento"]]

        pacientes_resto = pacientes_resto[
            pacientes_resto.Fecha
            == Timestamp(year=int(kwargs["year"]), month=int(kwargs["month"]), day=1)
        ]

        return pacientes_resto.numero_documento.unique().tolist()
