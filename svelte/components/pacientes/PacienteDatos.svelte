<svelte:options accessors/>
<script>
    import NauiInput from "../naui/atoms/NauiInput.svelte";
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";
    import NauiDatePicker from "../naui/atoms/NauiDatePicker.svelte";
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import { createEventDispatcher } from "svelte";

    const events = new createEventDispatcher();

    export let paciente = {
        id: null,
        nombres: '',
        apellidos: '',
        tipo_documento: '',
        numero_documento: '',
        fecha_nacimiento: '',
        genero: '',
        grupo_etnico: '',
        estado_civil: '',
        nivel_estudios: '',
        estrato: '',

        departamento_contacto: '',
        ciudad_contacto_id: null,
        direccion: '',
        barrio: '',
        telefono: '',
        telefono_emergencia: '',

        eps_id: null,
        grupo_gestion_id: null,
        ciudad_asignacion_id: null,
        fecha_afiliacion: ''
    };
    export let parametros;

    function submit(){
        events('submit', paciente);
    }

</script>
<div>
    <form id="main-form" on:submit|preventDefault={submit}>
        <fieldset>
            <legend>Información general</legend>
            <div class="grid-5 gap-1">
                <input type="hidden" name="id" bind:value={paciente.id}>
                <NauiInput type="text" label="Nombres" bind:value={paciente.nombres}/>
                <NauiInput type="text" label="Apellidos" bind:value={paciente.apellidos}/>
                <NauiSelect label="Tipo de documento"
                            options={parametros.tipos_documento}
                            placeholder="Tipo de documento"
                            bind:value={paciente.tipo_documento}/>
                <NauiInput type="number" label="Identificación" bind:value={paciente.numero_documento}/>
                <NauiDatePicker label="Fecha de nacimiento" bind:value={paciente.fecha_nacimiento}/>
                <NauiSelect label="Género"
                            options={parametros.generos}
                            placeholder="Género"
                            bind:value={paciente.genero}/>
                <NauiSelect label="Grupo étnico"
                            options={parametros.grupos_etnicos}
                            placeholder="Grupo étnico"
                            bind:value={paciente.grupo_etnico}/>
                <NauiSelect label="Estado civil"
                            options={parametros.estados_civiles}
                            placeholder="Estado civil"
                            bind:value={paciente.estado_civil}/>
                <NauiSelect label="Nivel de estudios"
                            options={parametros.niveles_estudio}
                            placeholder="Nivel de estudios"
                            bind:value={paciente.nivel_estudios}/>            
            </div>
        </fieldset>
        <fieldset>
            <legend>Información de contacto</legend>
            <div class="grid-5 gap-1">
                <NauiSelect label="Ciudad / municipio"
                            options={parametros.ciudades}
                            bind:value={paciente.ciudad_contacto_id}/>
                <NauiInput type="text" label="Teléfono paciente" bind:value={paciente.telefono}/>
            </div>
        </fieldset>
        <fieldset>
            <legend>Asignación</legend>
            <div class="grid-5 gap-1">
                <NauiSelect label="Regimen de afiliación"
                            options={parametros.eps}
                            bind:value={paciente.eps_id}/>
                <NauiSelect label="Grupo sede"
                            options={parametros.grupos_gestion}
                            bind:value={paciente.grupo_gestion_id}/>
                <NauiSelect label="Ciudad"
                            options={parametros.ciudades}
                            bind:value={paciente.ciudad_asignacion_id}/>
                <NauiDatePicker label="Fecha afiliación" bind:value={paciente.fecha_afiliacion}/>
            </div>
        </fieldset>
        <NauiFloatingAction>
            <NauiButton type="submit" caption="GUARDAR" iconStyle="outlined" icon="save" color="accent" mode="solid"/>
        </NauiFloatingAction>
    </form>
</div>
<style>

</style>
