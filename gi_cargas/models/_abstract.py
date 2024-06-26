import uuid
from io import BytesIO
from typing import List, Tuple

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from pandas import DataFrame, read_excel, Series

from gi_cargas.configuraciones import TIME_ZONE


def _upload_cargue_masivo(instance, filename):
    instance: AbstractCargueMasivo
    return "/".join(["cargues-masivos", instance._meta.model_name, filename])


class AbstractValidators:
    settings: dict = {}

    def __init__(self, **kwargs):
        self.settings = kwargs.get("settings", {})


class AbstractCargueMasivo(models.Model):
    _help_text = "Por favor cargue un archivo Excel o CSV, donde en la primera hoja esté la información a cargar"
    uuid = models.UUIDField(verbose_name="uuid", default=uuid.uuid4)
    archivo = models.FileField(
        upload_to=_upload_cargue_masivo, verbose_name="Archivo", help_text=_help_text
    )
    esta_procesado = models.BooleanField(
        default=False, verbose_name="¿Está procesado?", editable=False
    )
    cargue_exitoso = models.BooleanField(default=False, verbose_name="¿Cargue exitoso?")

    registros_leidos = models.PositiveIntegerField(
        default=0, verbose_name="Registros leidos"
    )
    registros_cargados = models.PositiveIntegerField(
        default=0, verbose_name="Registros cargados"
    )

    usuario = models.ForeignKey(
        User, verbose_name="Usuario", on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_cargue = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de cargue"
    )

    error_model = None
    settings: dict = {}

    class Meta:
        abstract = True

    def __str__(self):
        return f"Archivo de carga {self.id}"

    @property
    def to_dict(self):
        return {
            "uuid": self.uuid,
            "esta_procesado": self.esta_procesado,
            "cargue_exitoso": self.cargue_exitoso,
            "registros_leidos": self.registros_leidos,
            "usuario": self.usuario.username if self.usuario else None,
        }

    def modify_df_function(self, df: DataFrame):
        return df

    def get_query_to_delete_function(self, df: DataFrame):
        return {}

    def load_data(self):
        if not self.esta_procesado:
            bytes_io: BytesIO = self.archivo.file.file
            bytes_io.seek(0)
            df: DataFrame = read_excel(
                bytes_io,
                header=self.settings.get("header"),
                sheet_name=self.settings.get("sheet_name"),
            )
            df["NumeroFila"] = df.reset_index().index
            df["NumeroFila"] = df["NumeroFila"] + 2
            df["IdCargueMasivo"] = self.id

            (
                missing_columns_message,
                missing_columns_list,
            ) = AbstractCargueMasivo.validate_file_columns(
                df=df,
                all_columns=self.settings.get("all_columns", []),
                id_cargue_masivo=self.id,
            )
            num_missing_columns = len(missing_columns_list)

            if num_missing_columns > 0:
                duplicates_message, rows_with_duplicates = "", []
                mandatory_columns_message, rows_with_empty_values = "", []
            else:
                df = df[
                    ["IdCargueMasivo", "NumeroFila"]
                    + self.settings.get("all_columns", [])
                ]
                (
                    duplicates_message,
                    rows_with_duplicates,
                ) = AbstractCargueMasivo.validate_duplicates(
                    df=df, unique_columns=self.settings.get("unique_columns")
                )
                (
                    mandatory_columns_message,
                    rows_with_empty_values,
                ) = AbstractCargueMasivo.validate_mandatory_columns(
                    df=df, mandatory_columns=self.settings["mandatory_columns"]
                )
            num_rows_with_duplicates = len(rows_with_duplicates)
            num_rows_with_empty_values = len(rows_with_empty_values)

            df_is_correct = all(
                [
                    num_missing_columns == 0,
                    num_rows_with_duplicates == 0,
                    num_rows_with_empty_values == 0,
                ]
            )

            error_processing, error_processing_message = (
                True,
                "El archivo no fue cargado",
            )

            if df_is_correct:
                try:
                    df = df.astype(dtype=self.settings["dtypes_dict"])
                    df.rename(columns=self.settings["rename_dict"], inplace=True)
                except Exception as e:
                    error_processing_message = "Error en el procesamiento"
            self.esta_procesado = True
            self.cargue_exitoso = not error_processing
            self.registros_leidos = len(df.index)
            self.registros_cargados = len(df.index)

    @staticmethod
    def validate_file_columns(
        df: DataFrame, all_columns: List[str], id_cargue_masivo: int
    ) -> Tuple[str, List[dict]]:
        error_message = ""
        missing_columns_list = []
        df_columns = df.columns.tolist()
        if len(all_columns) > 0:
            missing_columns = ""
            for c in all_columns:
                if c not in df_columns:
                    missing_columns += f"<li>{c}</li>"
                    missing_columns_list.append(
                        {"Mensaje": f"Columna {c}", "IdCargueMasivo": id_cargue_masivo}
                    )

            if missing_columns:
                error_message = (
                    "<p>Las siguientes columnas no se encuentran en el archivo:</p>"
                )
                error_message += f"<ul>{missing_columns}</ul>"

        return error_message, missing_columns_list

    @staticmethod
    def validate_duplicates(df: DataFrame, unique_columns: List[str]) -> List[any]:
        rows_with_duplicates = []
        if len(unique_columns) > 0:
            df_duplicates = df[df.duplicated(unique_columns, keep="first")]
            df_duplicates = df_duplicates[
                unique_columns + ["NumeroFila", "IdCargueMasivo"]
            ]
            df_duplicates.drop_duplicates(
                unique_columns + ["NumeroFila", "IdCargueMasivo"], inplace=True
            )

            def get_error(row: Series):
                rows_with_duplicates.append(row.to_dict())

            if len(df_duplicates.index) > 0:
                df_duplicates.apply(get_error, axis=1)
        return rows_with_duplicates

    @staticmethod
    def validate_mandatory_columns(
        df: DataFrame, mandatory_columns: List[str]
    ) -> List[str]:
        rows = []
        if len(mandatory_columns) > 0:
            for c in mandatory_columns:
                filter_df = df[(df[c].isnull()) | (df[c] == "")]
                filter_df.drop_duplicates(
                    [c] + ["NumeroFila", "IdCargueMasivo"], inplace=True
                )
                if len(filter_df.index) > 0:

                    def get_error(row: Series):
                        rows.append(row.to_dict())

                    filter_df.apply(get_error, axis=1)
        return rows

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.load_data()
        super(AbstractCargueMasivo, self).save(
            force_insert, force_update, using, update_fields
        )


class AbstractErrorCargue(models.Model):
    tipo_error = models.CharField(max_length=100, verbose_name="Tipo error")
    numero_fila = models.PositiveIntegerField(
        verbose_name="Número de fila", default=0, null=True
    )
    mensaje = models.TextField(max_length=100, verbose_name="Mensaje", default="")

    usuario = models.ForeignKey(
        User, verbose_name="Usuario", on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_cargue = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha del error"
    )

    class Meta:
        abstract = True

    @staticmethod
    def get_dataframe(queryset) -> DataFrame:
        _queryset = queryset.annotate(
            TipoError=F("tipo_error"),
            NumeroFila=F("numero_fila"),
            Mensaje=F("mensaje"),
            Usuario=F("usuario__username"),
            FechaCargue=F("fecha_cargue"),
        ).values(
            "TipoError",
            "NumeroFila",
            "Mensaje",
            "Usuario",
            "FechaCargue",
        )

        df = DataFrame(list(_queryset))
        df["FechaCargue"] = df["FechaCargue"].dt.tz_convert(tz=TIME_ZONE)
        df["FechaCargue"] = df["FechaCargue"].dt.strftime("%Y-%m-%d %H:%M:%S")
        return df
