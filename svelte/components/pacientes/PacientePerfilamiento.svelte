<svelte:options accessors/>
<script>
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import ValoracionRiesgoRCV from "../widgets/ValoracionRiesgoRCV.svelte";
    import Imc from "../widgets/Imc.svelte";
    import NauiCheckbox from "../naui/atoms/NauiCheckbox.svelte";
    import NauiSwitch from "../naui/atoms/NauiSwitch.svelte";
    import NauiInput from "../naui/atoms/NauiInput.svelte";
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import {createEventDispatcher} from "svelte";
    import NauiState from "../naui/atoms/NauiState.svelte";
    import { loop_guard } from "svelte/internal";

    const events = new createEventDispatcher();

    export let complicaciones = [];
    export let grupos = [];
    export let diabetesTipos = [];
    export let diagnosticos = [];
    export let estadios_erc = [];
    export let diagnosticosAdicionales = [];
    export let tratamientos = [];
    export let data = {};

    let open = false;
    let searchBox;
    const meses = [
        {label: 'Enero', value: '01'},
        {label: 'Febrero', value: '02'},
        {label: 'Marzo', value: '03'},
        {label: 'Abril', value: '04'},
        {label: 'Mayo', value: '05'},
        {label: 'Junio', value: '06'},
        {label: 'Julio', value: '07'},
        {label: 'Agosto', value: '08'},
        {label: 'Septiembre', value: '09'},
        {label: 'Octubre', value: '10'},
        {label: 'Noviembre', value: '11'},
        {label: 'Diciembre', value: '12'}
    ];

    const code_estadio = {
        '1':'20',
        '2':'21',
        '3a':'22',
        '3b':'23',
        '4':'24',
        '5':'25',
        '0':'26',
    }

    const label_estadio = {
        '1':'Estadio 1',
        '2':'Estadio 2',
        '3a':'Estadio 3a',
        '3b':'Estadio 3b',
        '4':'Estadio 4',
        '5':'Estadio 5',
        '0':'Sin Calcular',
    }

    let code;
    let label;

    $: {

        if (label_estadio[data.estadio_erc] === undefined) {
            label = label_estadio['0'];
        } else {
            label = label_estadio[data.estadio_erc];
        }

    }

    $: {
        if (code_estadio[data.estadio_erc] === undefined) {
            code = code_estadio['0'];
        } else {
            code = code_estadio[data.estadio_erc];
        }
    }

    
    
    const anios = getYears();

    function getYears() {
        const response = [];
        let currentYear = new Date().getFullYear();
        let counter = 0;
        while (counter <= 10) {
            let value = (currentYear - counter).toString();
            response.push({label: value, value: value})
            counter++;
        }
        return response;
    }

    function submit() {
        events('submit', {
            ...data,
            complicaciones,
            grupos,
            diagnosticosAdicionales,
            tratamientos
        });
    }


</script>
<div>
    <fieldset>
        <legend>Diagnóstico principal</legend>
        <div class="box-l sx-1">
            <div class="min-w-200px">
                <NauiSelect label="Tipo de diabetes" options={diabetesTipos} bind:value={data.tipoDiabetes}/>
            </div>
            <div class="min-w-400px">
                <NauiSelect label="Diagnósticos CIE10" options={diagnosticos} bind:value={data.diagnostico}/>
            </div>
            <div class="">
                <NauiSelect label="Año del diagnóstico" options={anios} bind:value={data.anio_diagnostico}/>
            </div>
            <div class="">
                <NauiSelect label="Mes del diagnóstico" options={meses} bind:value={data.mes_diagnostico}/>
            </div>
        </div>
    </fieldset>
    <fieldset>
        <legend>Diagnósticos Adicionales</legend>
        <div class="box-l sx-2">
            {#each diagnosticosAdicionales as diagnostico (diagnostico.slug)}
                <div>
                    <NauiCheckbox label={diagnostico.label} bind:value={diagnostico.value}/>
                </div>
            {/each}
        </div>
    </fieldset>

    <fieldset>
        <legend>Función renal</legend>
        <div class="mb-2">
            <div class="flex-row sx-1">
                <div class="flex-2">
                    <NauiInput value={data.riesgo_tfg.creatinina}
                               isDisabled={true}
                               type="number"
                               label="Último registro de creatinina" />
                </div>
                <!-- <div class="flex-1">
                    <NauiInput value={data.riesgo_tfg.riesgo}
                               isDisabled={true}
                               type="number"
                               label="TFG" />
                </div> -->

                <div class="flex-4">
                    <NauiSelect label="Estadio ERC" options={estadios_erc} bind:value={data.estadio_erc}/>
                </div>
                
                <div class="flex-3 py-i px-iii radius box-l sx-ii self-end" style="height: 50px;">
                    <NauiState
                               code={code}
                               label={label}
                               border="true" styleText="min-width: 120px;"/>
                </div>
            </div>
        </div>

        {#if diagnosticosAdicionales.filter(d => d.slug === 'erc' && d.value).length > 0 }
            <p>¿El paciente se encuentra en algún programa de nefroprotección?</p>
            <div class="box-l mt-1 sx-2">
                <div class="self-end">
                    <NauiSwitch bind:active={data.programa_nefroproteccion.activo}/>
                </div>
                <div class="min-w-300px">
                    <NauiInput label="Nombre del programa" type="text" bind:value={data.programa_nefroproteccion.nombre}/>
                </div>
            </div>
        {/if}
    </fieldset>
    <!-- <fieldset>
        <legend>Complicaciones</legend>
        <p>Seleccione las complicaciones con las que cuenta el paciente</p>
        <div class="gComplicaciones mt-2 max-w-900px">
            {#each complicaciones as complicacion (complicacion.slug)}
                <NauiCheckbox label={complicacion.label} bind:value={complicacion.value}/>
            {/each}
        </div>
    </fieldset>
    <fieldset>
        <legend>Tratamientos</legend>
        <p>Seleccione los tratamientos </p>
        <div class="gComplicaciones mt-2 max-w-900px">
            {#each tratamientos as t (t.slug)}
                <NauiCheckbox label={t.label} bind:value={t.value}/>
            {/each}
        </div>
    </fieldset> -->
    <fieldset>
        <legend>Valoración inicial del riesgo Framingham</legend>
        <ValoracionRiesgoRCV
                bind:colesterolTotal={data.riesgo_rcv.colesterolTotal}
                bind:hdl={data.riesgo_rcv.hdl}
                bind:tas={data.riesgo_rcv.tas}
                bind:tad={data.riesgo_rcv.tad}
                bind:fumador={data.riesgo_rcv.fumador}
                bind:nivelRiesgo={data.riesgo_rcv.nivel}
                bind:codigoEstado={data.riesgo_rcv.codigoEstado}/>
    </fieldset>
    <fieldset>
        <legend>Índice de masa corporal</legend>
        <Imc bind:estatura={data.estatura} bind:peso={data.peso}/>
    </fieldset>
    <fieldset>
        <legend>Grupos de pacientes a los que pertecene</legend>
        {#each grupos as grupo (grupo.slug)}
            <div class="mb-1">
                <NauiCheckbox label={grupo.label} bind:value={grupo.value}/>
            </div>
        {/each}
    </fieldset>

    <NauiFloatingAction>
        <NauiButton type="submit"
                    caption="GUARDAR"
                    icon="save"
                    iconStyle="outlined"
                    color="accent"
                    mode="solid"
                    on:click={submit}/>
    </NauiFloatingAction>
</div>
<style>
    .gComplicaciones {
        display: grid;
        width: 100%;
        grid-template-columns: repeat(3, 1fr);
        grid-gap: .5rem 3rem;
    }
</style>
