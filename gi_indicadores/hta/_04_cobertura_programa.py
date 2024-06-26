from gi_indicadores.indicador import AbstractIndicador


class CoberturaProgramaHTA(AbstractIndicador):
    def __init__(self, **kwargs):
        super(CoberturaProgramaHTA, self).__init__(
            **{
                "name": "CoberturaPrograma",
                "slug": "cobertura-programa-hta",
                "description": "Pacientes con HTA que han sido valorados en los últimos 6 meses por médicos, enfermeras o especialistas sobre el total de pacientes con HTA.",
                "label": "Tasa",
                "tipo": "HTA",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 0.8, "trend": True}
