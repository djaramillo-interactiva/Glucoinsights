<svelte:options accessors/>
<script>
    import NauiFilters from "../naui/components/NauiFilters.svelte";
    import {onMount} from "svelte";
    import IndValue from "./IndValue.svelte";

    export let filters = [];
    let currentFilters = {};
    let reload = false
    export let data = [];
    export let hideDetails = false;
    export let nav = null;
    export let httpRequest = () => {
    }

    export let groups = [];
    let filtersComponent;
    let current_year;
    let changeYear=true

    onMount(() => {
        reload = true;
        const fdjson = localStorage.getItem('filtros-indicadores');
        filters[1].options=filters[0].options[0].meses;
        if (fdjson) {
            try {
                currentFilters = JSON.parse(fdjson);
                filters[0].selected=currentFilters.year;
                const selectedOption=filters[0].options.find((option)=>option.value===filters[0].selected);
                filters[1].options=selectedOption.meses;
                filters[1].selected=currentFilters.mes;

            } catch (e) {
                currentFilters = {}
            }

        }
        filters = filters
        filtersComponent.updateSelect()
        setTimeout(() => {
            reload = false;
        }, 50);
    });

    function hasWarning(ind) {
        return (ind.metric.value < ind.metric.target) === ind.metric.trend;
    }

    async function filter(evt) {

        const {detail} = evt;
        localStorage.setItem('filtros-indicadores', JSON.stringify(detail))
        if(detail.year!==current_year)
        {
           changeYear = true;
           current_year=detail.year
        }


        const slug='mes';

        const filter = filters.find((f) => f.slug === slug)

        if(detail.year){
        filter.options = filters[0].options.find((year)=>year.value===detail.year).meses
        }
        else{
            filters[1].options=filters[0].options[0].meses;
        }


        if(changeYear)
        {
            filtersComponent.refreshFilters(slug);
            changeYear=false;
        }



        currentFilters = detail;
        groups = [...groups];
        reload = true;
        setTimeout(() => {
            reload = false;
        }, 5)
    }
</script>
<div>
    <NauiFilters {filters} on:filtered={filter} bind:this={filtersComponent}/>
    {#if !reload}
        <div class="mt-1">
            {#each groups as group}
                {#if group.data?.length > 0}
                    {#if group.title}
                        <h2>{group?.title}</h2>
                    {/if}
                    <div class="py-1">
                        <table class="naui-table w-100">
                            <thead>
                            <tr>
                                {#if nav}
                                    <th></th>
                                {/if}
                                <th style="width: 50%">
                                    <div>Indicadores</div>
                                </th>
                                <th style="width:35%" class="text-c">
                                    <div class="box">Valor actual</div>
                                </th>
                                {#if !hideDetails}
                                    <th class="text-c">
                                        <div class="box">Detalles</div>
                                    </th>
                                {/if}
                                {#if nav}
                                    <th></th>
                                {/if}
                            </tr>
                            </thead>
                            <tbody>
                            {#each group.data as ind, i (ind.slug)}
                                <tr>
                                    {#if nav}
                                        <td class="box">
                                            <a href="{nav.back}" class="accent">
                                                <span class="material-icons-outlined accent">chevron_left</span>
                                                <!--i class="fal fa-chevron-circle-left accent"></i-->
                                            </a>
                                        </td>
                                    {/if}
                                    <td>
                                        <div>
                                            <div class="py-1">
                                                <h4 class="mb-ii">{i + 1}. {ind.nombre}
                                                    {#if hasWarning(ind)}
                                                        <!--i class="ml-3 fas fa-exclamation-triangle with-warning"></i-->
                                                        <span class="material-icons-outlined accent">warning_amber</span>
                                                    {/if}
                                                </h4>
                                                <p>{ind.descripcion}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <IndValue {httpRequest}
                                                  filters="{currentFilters}"
                                                  {ind}/>
                                    </td>
                                    {#if !hideDetails}
                                        <td>
                                            <div class="box">
                                                <a href="{ind.route}" class="btn-icon">
                                                    <span class="material-icons-outlined accent">chevron_right</span>
                                                </a>
                                            </div>
                                        </td>
                                    {/if}
                                    {#if nav}
                                        <td class="box">
                                            <a href="{nav.forward}" class="accent">
                                                <span class="material-icons-outlined accent">add_circle</span>
                                            </a>
                                        </td>
                                    {/if}
                                </tr>
                            {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            {:else}
                No se han registrado indicadores
            {/each}
        </div>
    {/if}
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

    .g-indicadores .first {
        border-right: 1px solid var(--border-color);
    }

    .with-warning {
        color: var(--state-code-3);
    }
</style>
