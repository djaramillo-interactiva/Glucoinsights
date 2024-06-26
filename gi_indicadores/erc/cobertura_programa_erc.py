from gi_indicadores.indicador import AbstractIndicador


class CoberturaProgramaERC(AbstractIndicador):
    def __init__(self, **kwargs):
        super(CoberturaProgramaERC, self).__init__(
            **{
                "name": "Cobertura Programa ERC",
                "slug": "cobertura-programa-erc",
                "description": "Pacientes con enfermedad renal crónica con valoración por profesionales del programa en los últimos 6 meses (UAP-UR) /pacientes con enfermedad renal crónica",
                "label": "Tasa",
                "tipo": "ERC",
            }
        )

    def calc_value(self, **kwargs):
        return {"value": 4.2, "trend": True}
