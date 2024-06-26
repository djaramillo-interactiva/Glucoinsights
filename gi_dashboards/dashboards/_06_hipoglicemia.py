from gi_dashboards.dashboards.base import BaseDiagnosticSegment


class Hipoglicemia(BaseDiagnosticSegment):
    def __init__(self, df, **kwargs):
        super(Hipoglicemia, self).__init__(df, **kwargs)

        self.slug = "hipoglicemia"
        self.title = "Hipoglicemia"
        self.attribute = "fecha_diag_hipoglicemia"
