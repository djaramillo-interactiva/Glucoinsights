from gi_indicadores.indicador import AbstractIndicador


class PrevalenciaERC(AbstractIndicador):
    def __init__(self, **kwargs):
        super(PrevalenciaERC, self).__init__(
            **{
                "name": "Prevalencia ERC",
                "slug": "prevalencia-erc",
                "description": "Expresa la proporción de casos con ERC diagnosticada respecto a la población afiliada mayor de 18 años.",
                "label": "Tasa",
                "tipo": "ERC",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 2, "trend": True}
