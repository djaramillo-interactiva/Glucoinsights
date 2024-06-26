import NauiExplorer from './naui/pages/NauiExplorer.svelte';
import NauiIndex from './naui/pages/NauiIndex.svelte';
import NauiSnackbar from './naui/components/NauiSnackbar.svelte';

import GruposEtareos from './parametros/GruposEtareos.svelte';
import Indicadores from './parametros/Indicadores.svelte';
import Tareas from './parametros/Tareas.svelte';
import GruposPacientes from './parametros/GruposPacientes.svelte';
import Medicacion from './parametros/Medicacion.svelte';

import Pacientes from './seguimiento/Pacientes.svelte';

import FichaPaciente from './pacientes/FichaPaciente.svelte';
import PacienteControles from './pacientes/PacienteControles.svelte';
import PacienteHospitalizaciones from './pacientes/PacienteHospitalizaciones.svelte';
import PacienteExamenes from './pacientes/PacienteExamenes.svelte';
import PacienteDatos from './pacientes/PacienteDatos.svelte';
import PacientePerfilamiento from './pacientes/PacientePerfilamiento.svelte';
import PacienteTareas from './pacientes/PacienteTareas.svelte';
import PacienteTendencias from './pacientes/PacienteTendencias.svelte';

import IndicadoresPoblacion from './indicadores/IndicadoresPoblacion.svelte';
import AdministracionUsuarios from './usuarios/AdministracionUsuarios.svelte';

import VariablesClinicas from './segmentacion/VariablesClinicas.svelte';

import 'configurable-date-input-polyfill';
import Registros from "./registros/Registros.svelte";

export default {
    medicacion: Medicacion,
    nauiExplorer: NauiExplorer,
    nauiIndex: NauiIndex,
    nauiSnackbar: NauiSnackbar,

    gruposEtareos: GruposEtareos,
    indicadores: Indicadores,
    tareas: Tareas,
    gruposPacientes: GruposPacientes,

    variablesClinicas: VariablesClinicas,

    pacientes: Pacientes,

    fichaPaciente: FichaPaciente,
    pacienteControles: PacienteControles,
    pacienteHospitalizaciones: PacienteHospitalizaciones,
    pacienteExamenes: PacienteExamenes,
    pacienteDatos: PacienteDatos,
    pacientePerfilamiento: PacientePerfilamiento,
    pacienteTareas: PacienteTareas,
    pacienteTendencias: PacienteTendencias,

    indicadoresPoblacion: IndicadoresPoblacion,
    administracionUsuarios: AdministracionUsuarios,
    registros: Registros,
};
