import pandas as pd

from gi_dashboards.dashboards.base import BaseSegment


class Genero(BaseSegment):
    def __init__(self, df, **kwargs):
        super(Genero, self).__init__(df, **kwargs)

        self.slug = "genero"
        self.chart_type = "pie"
        self.title = "Género"
        self.labels = ["Femenino", "Masculino", "No especificado"]
        self.chart_label = "# Pacientes"

    def calc_segment(self):
        from gi.models import Paciente

        df = self.dataframe
        pacientes = pd.DataFrame(
            Paciente.objects.filter(id__in=list(df["fk_paciente_id"])).values()
        )
        f = pacientes[pacientes.genero == Paciente.GENERO_FEMENINO]
        m = pacientes[pacientes.genero == Paciente.GENERO_MASCULINO]
        na = pacientes[(pacientes.genero == "") & (pacientes.genero.isnull())]

        values = [f, m, na]
        for val in values:
            self.patients.append(val.id)

        return list(map(lambda x: len(x), values))
