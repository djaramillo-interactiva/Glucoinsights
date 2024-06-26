<svelte:options accessors/>
<script>
    import {createBarChart} from "../chart-helper";
    import {onMount} from "svelte";

    let canvas;
    let chartRef;

    export let title;

    export let data;
    export let labels;
    export let barLabel = '';

    export let width = 400;
    export let height = 200;

    export let datalabels = true;
    export let yLabel = null;
    export let legend = false;

    onMount(() => {
        const datasets = [{
            data: data,
            label: barLabel
        }];

        chartRef = createBarChart(canvas, datasets, labels, {
            datalabels: datalabels,
            yLabel: yLabel,
            legend: legend
        });
    });
</script>

<h2 class="text-c mb-1">{title}</h2>
<canvas bind:this={canvas} {width} {height}></canvas>
