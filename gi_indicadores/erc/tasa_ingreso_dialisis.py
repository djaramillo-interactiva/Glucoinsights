from gi_indicadores.indicador import AbstractIndicador


class TasaIngresoDialisis(AbstractIndicador):
    def __init__(self, **kwargs):
        super(TasaIngresoDialisis, self).__init__(
            **{
                "name": "Tasa Ingreso a Dialisis",
                "slug": "tasa-ingreso-dialisis",
                "description": "Pacientes con enfermedad renal crónica en hemodialisis, dialisis peritoneal en el último mes.",
                "label": "Tasa",
                "tipo": "ERC",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 4.2, "trend": True}
