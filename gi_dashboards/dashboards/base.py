from typing import List

import pandas as pd
from django.urls import reverse
from django.utils.functional import cached_property


class BaseSegment:
    title: str = ""
    labels: List = []
    slug: str = ""
    chart_type: str = ""
    dataframe: pd.DataFrame = None
    chart_label: str = ""
    digits: int = 0
    patients: List = None

    def __init__(self, dataframe, **kwargs):
        self.dataframe = dataframe
        self.patients = []
        if kwargs.get("large"):
            self.large = kwargs["large"]

    @cached_property
    def get_chart_data(self):
        data = {"labels": self.labels, "values": []}
        if self.dataframe.empty:
            data["values"] = [0 for _ in range(len(self.labels))]
        else:
            data["values"] = self.calc_segment()
        cd = {
            "type": self.chart_type,
            "title": self.title,
            "slug": self.slug,
            "href": reverse("gi:detalle-variable", kwargs={"slug": self.slug}),
            "data": data,
        }
        if self.chart_type == "bar":
            cd["barLabel"] = self.chart_label
        else:
            cd["pieLabel"] = self.chart_label
        if self.digits:
            cd["digits"] = self.digits
        if hasattr(self, "large"):
            cd["large"] = self.large
        return cd

    def calc_segment(self, *args, **kwargs):
        raise NotImplementedError

    def get_patients(self, index):
        if self.patients:
            return self.patients[index]
        return []


class BaseDiagnosticSegment(BaseSegment):
    attribute = ""

    def __init__(self, df, **kwargs):
        super(BaseDiagnosticSegment, self).__init__(df, **kwargs)
        self.chart_type = "pie"
        self.labels = [["Si"], ["No"]]
        self.chart_label = "# Paciente"
        self.patients = []

    def calc_segment(self):
        df = self.dataframe
        segment = df[df[self.attribute].notnull()]
        invert = df[df[self.attribute].isnull()]

        self.patients.append(segment.fk_paciente_id)
        self.patients.append(invert.fk_paciente_id)

        self.labels[0].append(f"{len(segment)} paciente(s)")
        self.labels[1].append(f"{len(invert)} paciente(s)")
        return [len(segment), len(invert)]
