import pandas as pd

from gi_dashboards.dashboards.base import BaseSegment


class EstadoCivil(BaseSegment):
    def __init__(self, df, **kwargs):
        super(EstadoCivil, self).__init__(df, **kwargs)
        from gi.models import Paciente

        self.slug = "estado_civil"
        self.chart_type = "pie"
        self.title = "Estado civil"
        self.labels = list(map(lambda x: x["label"], Paciente.get_estados_civiles()))
        self.chart_label = "# Pacientes"

    def calc_segment(self):
        from gi.models import Paciente

        df = self.dataframe
        pacientes = pd.DataFrame(
            Paciente.objects.filter(id__in=list(df["fk_paciente_id"])).values()
        )
        values = []
        for es in Paciente.get_estados_civiles():
            data = pacientes[pacientes.estado_civil == es["value"]]
            values.append(len(data))
            self.patients.append(list(data.id))

        return values
