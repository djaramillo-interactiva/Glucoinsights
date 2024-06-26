import datetime

from django.db.models import Model
from pandas import DataFrame


class BaseDto:
    model: Model

    def __init__(self, df):
        self.df: DataFrame = df

    @classmethod
    def get_model_fields(cls):
        fields_dict = {}
        empty_patient = cls.model()

        for field in cls.model._meta.get_fields():
            if not field.is_relation and field.name != "id":
                value = getattr(empty_patient, field.name)
                if isinstance(value, datetime.datetime):
                    fields_dict[field.name] = value.date()
                else:
                    fields_dict[field.name] = value
        return fields_dict
