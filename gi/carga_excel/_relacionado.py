from django.db.models import Q
from django.db.transaction import atomic
from django.forms import BooleanField

from gi.carga_excel import BaseDto
from gi.models import ExamenPaciente, HospitalizacionPaciente, ControlPaciente, Paciente

import datetime

cargue_tipo_controles_choices = {
    1: "Hospitalización",
    2: "Urgencias",
    3: "Fallecimiento",
}


class CargaRelacionadoDto(BaseDto):
    @classmethod
    def get_fields_dict(cls):
        return {"paciente": "", **cls.get_model_fields()}

    @atomic()
    def save_registros(self, cargue):
        df = self.df
        errors = []
        df.fillna("", inplace=True)
        count = 0
        for row in df.itertuples():
            obj = self.model()
            try:
                p = Paciente.objects.get(numero_documento=row.numero_de_documento)
            except Paciente.DoesNotExist:
                errors.append(
                    f"Paciente con número de documento {row.numero_de_documento} no existe."
                )
                continue
            except Exception as e:
                errors.append(f"Error en los datos: {str(e)}")
                continue

            for field in self.get_model_fields():
                row_value = getattr(row, field)
                field_obj = self.model._meta.get_field(field)

                if type(field_obj) == BooleanField and type(row_value) != bool:
                    setattr(p, field, bool(row_value))
                elif not row_value:
                    setattr(p, field, field_obj.default)
                else:
                    setattr(obj, field, row_value)

                # Validations TYT Interactiva
                if (
                    field_obj.attname == "tipo"
                    and row_value in cargue_tipo_controles_choices
                ):
                    setattr(obj, field, cargue_tipo_controles_choices[row_value])
                elif field_obj.attname == "tipo":
                    setattr(obj, field, "Sin información")

                ## Fecha
                if (field_obj.attname == "fecha") and isinstance(
                    row_value, datetime.date
                ):
                    setattr(obj, field, row_value)
                elif field_obj.attname == "fecha":
                    fecha_actual = datetime.datetime.now()
                    setattr(obj, field, fecha_actual)

                # Campos 1=Si, 2=No
                if (
                    field_obj.attname == "tiene_soporte"
                    or field_obj.attname == "era_evitable"
                    or field_obj.attname == "relacionado_con_diabetes"
                ) and row_value == 1:
                    setattr(obj, field, 1)
                elif (
                    field_obj.attname == "tiene_soporte"
                    or field_obj.attname == "era_evitable"
                    or field_obj.attname == "relacionado_con_diabetes"
                ):
                    setattr(obj, field, 0)

            count += 1
            obj.fk_paciente = p
            obj.fk_cargue = cargue
            obj.save()
        return count, len(errors)


class CargaExamenesDto(CargaRelacionadoDto):
    model = ExamenPaciente


class CargaHospitalizacionesDto(CargaRelacionadoDto):
    model = HospitalizacionPaciente


class CargaControlesDto(CargaRelacionadoDto):
    model = ControlPaciente


dto_mapper = {
    "controles": CargaControlesDto,
    "hospitalizaciones": CargaHospitalizacionesDto,
    "examenes": CargaExamenesDto,
}
