from gi_dashboards.dashboards.base import BaseDiagnosticSegment


class Erc(BaseDiagnosticSegment):
    def __init__(self, df, **kwargs):
        super(Erc, self).__init__(df, **kwargs)

        self.slug = "renal"
        self.title = "Insuficiencia renal"
        self.attribute = "fecha_erc"
