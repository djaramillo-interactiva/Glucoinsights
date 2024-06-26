from gi_indicadores.indicador import AbstractIndicador


class ControlDMDiagnosticados(AbstractIndicador):
    def __init__(self, **kwargs):
        super(ControlDMDiagnosticados, self).__init__(
            **{
                "name": "Toma DM Diagnosticados",
                "slug": "toma-dm-diagnosticados",
                "description": "Expresa la proporción de pacientes con diagnóstico de DM que se encuentran en programa, quienes se encuentran con HbA1C en metas últimos seis meses.",
                "label": "Tasa",
                "tipo": "DM",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 15, "trend": True}
