<script>
    import {onMount} from "svelte";
    import Loader from "./Loader.svelte";

    let loading = false;
    export let ind;
    export let filters = {}
    export let httpRequest = () => {
    }
    onMount(() => {
        getData();
    });

    function getData() {
        loading = true;
        httpRequest({
            method: 'GET',
            url: [ind.route, 'calc'].join('/'),
            data: filters ?? {}
        }).then((res) => {
            const {metric} = res.indicador;
            ind.metric = metric;
            ind = {...ind};
            loading = false;
        });
    }

    function hasWarning(ind) {
        return (ind.metric.value < ind.metric.target) === ind.metric.trend;
    }
</script>
<div class="box">
    <div class="grid-2 py-ii items-center mx-auto g-indicadores">
        <div class="text-r first pr-1">
            <small class="indicador-label">
                {#if !loading}{ind.metric.label}{:else}<span class="white">.</span>{/if}
            </small>
            {#if loading}
                <Loader/>
            {:else}
                <div class="indicador"
                     class:with-warning={hasWarning(ind)}>{ind.metric.value}</div>
            {/if}
        </div>
        <div class="text-l second pl-1">
            <small class="indicador-label">Meta</small>
            {#if loading}
                <Loader/>
            {:else}
                <div class="indicador meta">{ind.metric.target}</div>
            {/if}
        </div>
    </div>
</div>

<style>
    .indicador-label {
        font-weight: 600;
        color: #4D4D4D;
        margin-bottom: .25rem;
        display: block;
        font-size: 12px;
    }

    .indicador {
        font-size: 20px;
        font-weight: bold;
    }

    .indicador.meta{
        color: #bbb;
    }

    .g-indicadores .first {
        border-right: 1px solid var(--border-color);
    }

    .with-warning {
        color: var(--state-code-3);
    }
</style>
