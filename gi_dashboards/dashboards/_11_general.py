import pandas as pd
from dateutil.relativedelta import relativedelta

from gi_dashboards.dashboards.base import BaseSegment


class General(BaseSegment):
    def __init__(self, df, **kwargs):
        super(General, self).__init__(df, **kwargs)

        self.slug = "general"
        self.chart_type = "pie"
        self.title = "Segmentación general"
        self.labels = [
            "Menos de 1 mes",
            "De 1 a 6 meses",
            "De 6 a 12 meses",
            "Más de 12 meses",
        ]
        self.chart_label = "# Pacientes"

    def calc_segment(self):
        # base_qs = self.dataframe
        from gi.models import VariablesClinicas

        base_qs = pd.DataFrame(
            VariablesClinicas.objects.all().values("fecha_cargue", "fk_paciente_id")
        )
        base_qs["fecha_cargue"] = pd.to_datetime(base_qs["fecha_cargue"])
        base_qs = base_qs.groupby("fk_paciente_id").agg("first").reset_index()
        base_qs = base_qs[["fk_paciente_id", "fecha_cargue"]]
        _now = pd.to_datetime("today")  # now()
        one_month = _now - relativedelta(months=1)
        six_months = _now - relativedelta(months=6)
        twelve_months = _now - relativedelta(months=12)

        lt_one_month = base_qs[base_qs.fecha_cargue > one_month]
        one_to_six_months = base_qs[
            (base_qs.fecha_cargue <= one_month) & (base_qs.fecha_cargue > six_months)
        ]
        six_to_twelve_months = base_qs[
            (base_qs.fecha_cargue <= six_months)
            & (base_qs.fecha_cargue > twelve_months)
        ]
        gt_twelve_months = base_qs[(base_qs.fecha_cargue <= twelve_months)]

        values = [
            lt_one_month,
            one_to_six_months,
            six_to_twelve_months,
            gt_twelve_months,
        ]

        for value in values:
            self.patients.append(list(value.fk_paciente_id))

        return list(map(lambda x: len(x), values))
