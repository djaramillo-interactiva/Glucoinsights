from gi_dashboards.dashboards.base import BaseSegment


class Imc(BaseSegment):
    def __init__(self, df, **kwargs):
        super(Imc, self).__init__(df, **kwargs)

        self.slug = "sobrepeso"
        self.chart_type = "pie"
        self.title = "IMC"
        self.labels = [
            "Obesidad_3",
            "Obesidad_2",
            "Obesidad_1",
            "Sobrepeso",
            "Normal",
        ]
        self.chart_label = "# Paciente"
        self.digits = 2

    def calc_segment(self):
        df = self.dataframe
        base_qs = df[(df.peso > 0) & (df.estatura > 0)]
        base_qs["imc"] = (base_qs["peso"] * 100**2) / (base_qs["estatura"] ** 2)

        normal = base_qs[(base_qs.imc >= 18.5) & (base_qs.imc < 24.9)]
        sobrepeso = base_qs[(base_qs.imc >= 25) & (base_qs.imc < 30)]
        # obesidad = base_qs[(base_qs.imc >= 30)]
        Obesidad_1 = base_qs[(base_qs.imc >= 30) & (base_qs.imc <= 34.9)]
        Obesidad_2 = base_qs[(base_qs.imc >= 35) & (base_qs.imc <= 39.9)]
        Obesidad_3 = base_qs[(base_qs.imc >= 40)]
        # desnutricion = base_qs[(base_qs.imc < 20)]

        values = [
            Obesidad_3,
            Obesidad_2,
            Obesidad_1,
            sobrepeso,
            # obesidad,
            normal,
            # desnutricion,
        ]

        for val in values:
            self.patients.append(list(val.fk_paciente_id))

        return list(map(lambda x: len(x), values))
