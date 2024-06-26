import pandas as pd

from gi_dashboards.dashboards.base import BaseSegment


class Tratamientos(BaseSegment):
    def __init__(self, df, **kwargs):
        from gi.models import Tratamiento

        super(Tratamientos, self).__init__(df, **kwargs)

        self.slug = "sobrepeso"
        self.chart_type = "pie"
        self.title = "IMC"
        self.labels = list(Tratamiento.objects.values_list("nombre", flat=True))
        self.chart_label = "# Paciente"

    def calc_segment(self):
        from gi.models import Paciente, Tratamiento

        df = self.dataframe
        pacientes = pd.DataFrame(
            Paciente.objects.filter(id__in=list(df["fk_paciente_id"])).values(
                "id", "tratamientos"
            )
        )
        label_value = dict(pacientes["tratamientos"].value_counts())

        for c_id in Tratamiento.objects.order_by("id").values_list("id", flat=True):
            self.patients.append(list(pacientes[pacientes.tratamientos == c_id].id))

        return list(map(int, list(label_value.values())))
