import pandas as pd

from gi_dashboards.dashboards.base import BaseSegment


class Escolaridad(BaseSegment):
    def __init__(self, df, **kwargs):
        from gi.models import Paciente

        super(Escolaridad, self).__init__(df, large=True, **kwargs)

        self.slug = "escolaridad"
        self.chart_type = "bar"
        self.title = "Pacientes por nivel de estudios"
        self.labels = list(map(lambda x: x["label"], Paciente.get_niveles_estudio()))
        self.chart_label = "# Pacientes"

    def calc_segment(self):
        df = self.dataframe
        from gi.models import Paciente

        pacientes = pd.DataFrame(
            Paciente.objects.filter(id__in=list(df["fk_paciente_id"])).values(
                "id", "nivel_estudios"
            )
        )

        values = []
        for ne in Paciente.get_niveles_estudio():
            data = pacientes[pacientes.nivel_estudios == ne["value"]]
            values.append(len(data))
            self.patients.append(list(data.id))

        return values
