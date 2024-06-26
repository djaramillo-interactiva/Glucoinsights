import pandas as pd

from gi_dashboards.dashboards.base import BaseSegment


class Demografico(BaseSegment):
    def __init__(self, df, **kwargs):
        super(Demografico, self).__init__(df, **kwargs)
        from gi.models import Ciudad

        self.slug = "demografica"
        self.chart_type = "bar"
        self.title = "Distribución demográfica"
        self.labels = list(Ciudad.objects.order_by("id").values_list("nombre"))
        self.chart_label = ""

    def calc_segment(self):
        from gi.models import Paciente, Ciudad

        pacientes = pd.DataFrame(
            Paciente.objects.filter(
                id__in=list(self.dataframe["fk_paciente_id"])
            ).values()
        )
        values = []
        for c_id in Ciudad.objects.order_by("id").values_list("id", flat=True):
            data = pacientes[pacientes.ciudad_asignacion_id == c_id]
            values.append(len(data))
            self.patients.append(list(data.id))
        return values
