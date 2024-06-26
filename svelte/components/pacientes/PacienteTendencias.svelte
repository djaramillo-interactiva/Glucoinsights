<svelte:options accessors/>
<script>
    import PacienteIndicadores from "./tendencias/PacienteIndicadores.svelte";
    import PacienteMetas from "./tendencias/PacienteMetas.svelte";

    import { onMount } from "svelte";

    export let metasConfig = {
        global: '',
        registros: [],
        tipos: []
    };
    export let tiposIndicador;

    export let upsertMeta = (nMeta) => {};

    let indicadoresComponent;
    let registrosIndicador;
    let metasComponent;

    onMount(() => {
        upsertMeta = metasComponent.upsertMeta;
    });

    export function updateIndicadores(registros) {
        registrosIndicador = registros;
        setTimeout(() => {
            indicadoresComponent.updateCharts();
        }, 100);
    }
</script>
<div class="py-15">
    <PacienteMetas bind:this={metasComponent}
                   global={metasConfig.global}
                   detalles={metasConfig.registros}
                   tiposMeta={metasConfig.tipos}
                   on:metaAgregada/>

    <PacienteIndicadores bind:this={indicadoresComponent}
                         bind:registros={registrosIndicador}
                         {tiposIndicador}
                         on:indicador/>
</div>
<style>

</style>