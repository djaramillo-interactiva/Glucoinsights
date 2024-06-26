from gi_indicadores.indicador import AbstractIndicador


class ControlObesidad(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlObesidad, self).__init__(
            **{
                "name": "Toma Obesidad",
                "slug": "toma-obesidad",
                "description": "% De pacientes con diagnostico de obesidad y sobrepeso.",
                "label": "Porcentaje",
                "tipo": "Otros",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 4.2, "trend": True}
