from gi_dashboards.dashboards.base import BaseSegment
import pandas as pd
from gi.models import Paciente

class Estadios(BaseSegment):
    def __init__(self, df, **kwargs):
        from gi.models import Paciente

        super(Estadios, self).__init__(df, **kwargs)

        self.slug = "estadios"
        self.chart_type = "bar"
        self.title = "Pacientes por estadíos ERC"
        self.labels = list(map(lambda x: x["label"], Paciente.get_estadios()))
        self.chart_label = "# Pacientes"

    def calc_segment(self):
        
        pacientes = pd.DataFrame(
            Paciente.objects.filter(
                id__in=list(self.dataframe["fk_paciente_id"])
            ).values()
        )
        
        # print(pacientes)

        df = self.dataframe
        # print(df)
        values = []
        # print(df.estadio)
        print(pacientes.estadio_erc)
        for estadio in Paciente.get_estadios_erc_2():
            data = pacientes[pacientes.estadio_erc == estadio["value"]]
            print(estadio["value"])
            values.append(len(data))
            self.patients.append(list(data.id))

        return values
