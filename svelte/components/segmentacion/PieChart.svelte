<svelte:options accessors/>
<script>
    import {createPieChart} from "../chart-helper";
    import {onMount} from "svelte";

    let canvas;
    let chartRef;

    export let title;

    export let data;
    export let labels;

    export let width = 400;
    export let height = 200;

    export let pieLabel = '';
    export let datalabels = true;
    export let percent = true;
    export let legend = true;
    export let digits = 0;

    $: datasets = [{
        data: data,
        label: pieLabel
    }]

    onMount(() => {
        const datasets = [{
            data: data,
            label: pieLabel
        }];

        chartRef = createPieChart(canvas, datasets, labels, {
            legend: legend,
            datalabels: datalabels,
            percent: percent,
            digits: digits
        });
    });
</script>

<h2 class="text-c mb-1">{title}</h2>
<canvas bind:this={canvas} {width} {height}></canvas>