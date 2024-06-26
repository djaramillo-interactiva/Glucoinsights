from gi_indicadores.indicador import AbstractIndicador


class IncidenciaHTA(AbstractIndicador):
    def __init__(self, **kwargs):
        super(IncidenciaHTA, self).__init__(
            **{
                "name": "Incidencia HTA",
                "slug": "indidencia-hta",
                "description": "Pacientes afiliados (Activos y Suspendidos) con diagnóstico nuevo de hipertensión arterial en el último año.",
                "label": "Tasa",
                "tipo": "HTA",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 3, "trend": True}
