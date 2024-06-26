<svelte:options accessors/>
<script>
    import PieChart from "./PieChart.svelte";
    import BarChart from "./BarChart.svelte";
    import LineChart from "./LineChart.svelte";
    import NauiFilters from "../naui/components/NauiFilters.svelte";

    export let segments = [];
    export let filters;

    let filtersCmpt;
    export let loading = false;

    export function updateCharts(newData) {
        segments = [];
        setTimeout(() => {
            loading = false;
            segments = newData;
        });
    }
</script>

<div class="py-15 chart-container">
    <div class="box-b mb-1">
        <NauiFilters bind:this={filtersCmpt} {filters} grid="6" on:filtered/>
        <div>
            <slot name="table-actions"/>
        </div>
    </div>
    {#if loading}
        <div class="charts-cover">
            <div class="fa-3x">
                <i class="fas fa-circle-notch fa-spin"></i>
            </div>
        </div>
    {/if}
    <div class="grid-2 gap-2">
        {#each segments as segment}
            <div class="p-15 shadow radius 2" style="grid-column: span {segment.large ? 2 : 1}">
                {#if segment.type === 'pie'}
                    <PieChart bind:this="{segment.ref}"
                              title="{segment.title}"
                              bind:data="{segment.data.values}"
                              bind:labels="{segment.data.labels}"
                              digits={segment.digits}
                              width="{segment.large ? 800 : 400}"
                              pieLabel="{segment.pieLabel}"/>
                {:else if segment.type === 'bar'}
                    <BarChart bind:this="{segment.ref}"
                              title="{segment.title}"
                              bind:data="{segment.data.values}"
                              bind:labels="{segment.data.labels}"
                              width="{segment.large ? 800 : 400}"
                              barLabel="{segment.barLabel}"/>
                {:else if segment.type === 'line'}
                    <LineChart bind:this="{segment.ref}"
                               title="{segment.title}"
                               bind:data="{segment.data.values}"
                               bind:labels="{segment.data.labels}"/>
                {/if}
                {#if segment.href}
                    <div class="box-r mt-1 pointer">
                        <a class="btn accent outline small" href="{segment.href}">
                            <span>DETALLES</span>
                        </a>
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>
<style>
    .charts-cover {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.8);
        text-align: center;
        padding-top: 15rem;
        font-size: 36px;
    }

    .chart-container.py-15 {
        position: relative;
    }
</style>