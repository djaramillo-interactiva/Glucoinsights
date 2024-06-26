from gi_indicadores.indicador import AbstractIndicador


class ControlHTADiagnosticados(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlHTADiagnosticados, self).__init__(
            **{
                "name": "Control HTA Diagnosticados",
                "slug": "control-hta-diagnosticados",
                "description": "Expresa la proporción de pacientes con diagnóstico de hipertensión arterial, quienes se encuentran con dos cifras de tensión arterial controladas en los últimos siete meses.",
                "label": "Tasa",
                "tipo": "Otros",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 4.2, "trend": True}
