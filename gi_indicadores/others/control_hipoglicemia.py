from gi_indicadores.indicador import AbstractIndicador


class ControlHipoglicemia(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlHipoglicemia, self).__init__(
            **{
                "name": "Toma Hipoglicemia",
                "slug": "toma-hipoglicemia",
                "description": "% de pacientes con registros de eventos de hipoglicemia en el ultimo control.",
                "label": "Porcentaje",
                "tipo": "HTA",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 4.2, "trend": True}
