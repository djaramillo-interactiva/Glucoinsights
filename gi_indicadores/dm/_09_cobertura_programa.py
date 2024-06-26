from gi_indicadores.indicador import AbstractIndicador


class CoberturaPrograma(AbstractIndicador):
    def __init__(self, **kwargs):
        super(CoberturaPrograma, self).__init__(
            **{
                "name": "Cobertura Programa",
                "slug": "cobertura-programa",
                "description": "Pacientes que han sido valorados en los últimos 6 meses por médicos, enfermeras o especialistas sobre el total de la cohorte.",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 1.2, "trend": True}
