from gi_dashboards.dashboards.base import BaseDiagnosticSegment


class CardioVascular(BaseDiagnosticSegment):
    def __init__(self, df, **kwargs):
        super(CardioVascular, self).__init__(df, **kwargs)

        self.slug = "cardiovascular"
        self.title = "Enfermedad cardiovascular instaurada"
        self.attribute = "fecha_hta"
