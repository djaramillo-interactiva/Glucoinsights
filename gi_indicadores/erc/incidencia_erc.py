from gi_indicadores.indicador import AbstractIndicador


class IncidenciaERC(AbstractIndicador):
    def __init__(self, **kwargs):
        super(IncidenciaERC, self).__init__(
            **{
                "name": "Incidencia ERC",
                "slug": "incidencia-erc",
                "description": "Pacientes afiliados con diagnóstico nuevo de enfermedad renal crónica en el último año.",
                "label": "Tasa",
                "tipo": "ERC",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 4.2, "trend": True}
