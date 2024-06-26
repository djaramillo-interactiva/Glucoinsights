from gi_dashboards.dashboards.base import BaseSegment


class Hemoglobina(BaseSegment):
    def __init__(self, df, **kwargs):
        super(Hemoglobina, self).__init__(df, **kwargs)

        self.slug = "hemoglobina"
        self.chart_type = "pie"
        self.title = "Hemoglobina glicosilada"
        self.labels = ["HbA1c <= 6.5", "> 6.5 < 7", "HbA1c > 7", "Sin registro"]
        self.chart_label = "# Paciente"

    def calc_segment(self):
        df = self.dataframe
        condition_with_register = (df.hemoglobina_glicosilada < 1) | (
            df.hemoglobina_glicosilada.isnull()
        )
        no_register = df[condition_with_register]
        with_register = df[~condition_with_register]
        lt_6_5 = with_register[with_register.hemoglobina_glicosilada <= 6.5]
        gt_6_5 = with_register[
            (with_register.hemoglobina_glicosilada <= 7)
            & (with_register.hemoglobina_glicosilada > 6.5)
        ]
        gt_7 = with_register[with_register.hemoglobina_glicosilada > 7]
        values = [lt_6_5, gt_6_5, gt_7, no_register]

        for val in values:
            self.patients.append(list(val.fk_paciente_id))

        return list(map(lambda x: len(x), values))
