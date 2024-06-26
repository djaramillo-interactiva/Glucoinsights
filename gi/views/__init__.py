from ._sesion import LoginView, LogoutView
from ._registros import (
    RegistrosView,
    CargarArchivoPacientesView,
    DescargarBaseDeDatosView,
    CargaRegistrosView,
    DownloadExcelView,
)
from ._segmentacion import (
    VariablasClinicasView,
    SegmentacionGruposView,
    DetallesVariable,
)
from ._seguimiento import (
    SeguimientoPacientesView,
    DatosPacienteView,
    PerfilamientoPacienteView,
    TareasPacienteView,
    IndicadoresPacienteView,
    MetasPacienteView,
    SeguimientoGruposView,
    GrupoPacientesView,
    SeguimientoPacientesApiView,
    ControlesPacienteView,
    ExamenesPacienteView,
    HospitalizacionesPacienteView,
    TendenciasPacienteView,
)
from ._indicadores import (
    IndicadoresHtaView,
    IndicadoresDmView,
    IndicadoresErcView,
    OtrosIndicadoresView,
    DetalleIndicadorView,
    CalcIndicadorView,
)
from ._parametros import (
    GruposEtareosView,
    IndicadoresView,
    TareasView,
    GruposPacientesView,
    MedicacionView,
)
from ._usuarios import (
    AdministracionUsuariosView,
    AdministracionUsuariosApiView,
    UpdateAdminView,
)
