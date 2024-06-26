from gi_indicadores.indicador import AbstractIndicador


class PrevalenciaHTA(AbstractIndicador):
    def __init__(self, **kwargs):
        super(PrevalenciaHTA, self).__init__(
            **{
                "name": "Prevalencia HTA",
                "slug": "prevalencia-hta",
                "description": "Expresa la proporción de casos con  HTA diagnosticada  respecto a la población afiliada  (Activos y Suspendidos)>= 18  años.",
                "label": "Porcentaje",
                "tipo": "HTA",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 1, "trend": True}
