<svelte:options accessors/>
<script>
    import NauiState from "../../naui/atoms/NauiState.svelte";
    import {createEventDispatcher, onMount} from "svelte";
    import NauiSelect from "../../naui/atoms/NauiSelect.svelte";

    const events = new createEventDispatcher();

    export let tiposIndicador = [];
    export let registros = [];
    export let chartsData = {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        }
    };

    let selectedIndicador = '';
    let indicadorTitle = '';

    let chartObj = null;

    let calculoHipertension = {
        label: 'Indefinido',
        code: '0'
    }

    onMount(() => {
        if(tiposIndicador.length > 0) {
            selectedIndicador = tiposIndicador[0].value ? tiposIndicador[0].value : '';
            indicadorTitle = tiposIndicador[0].label ? tiposIndicador[0].label : ''
        }
        // updateCharts();
        setTimeout(()=> {
            events('indicador', selectedIndicador);
        }, 200);
    });

    function updateCalculoHipertension(registrosTensionArterial) {
        let label = 'Indefinido';
        let code = '0';
        if (registrosTensionArterial.length > 0) {
            let ultimoRegistro = registrosTensionArterial[registrosTensionArterial.length - 1];
            try {
                if (ultimoRegistro.tas < 120 && ultimoRegistro.tad < 80) {
                    label = 'Presión normal';
                    code = '1';
                }
                if (ultimoRegistro.tas >= 120 && ultimoRegistro.tas < 130 && ultimoRegistro.tad < 80) {
                    label = 'Presión elevada';
                    code = '2';
                }
                if ((ultimoRegistro.tas >= 130 && ultimoRegistro.tas < 140) || (ultimoRegistro.tad >= 80 && ultimoRegistro.tad < 90)) {
                    label = 'Hipertensión Nivel 1';
                    code = '3';
                }
                if (ultimoRegistro.tas >= 140 || ultimoRegistro.tad >= 90) {
                    label = 'Hipertensión Nivel 2';
                    code = '4';
                }
                if (ultimoRegistro.tas > 180 || ultimoRegistro.tad > 120) {
                    label = 'Crisis de hipertensión';
                    code = '6';
                }
            } catch (e) {
            }
        }

        calculoHipertension = {label, code}
    }

    export function updateCharts() {
        const labels = [];
        let dataChart = {
            registros: [],
            recomendados: []
        };
        let dataChart2 = {
            registros: [],
            recomendados: []
        };

        let datosCompletosTensionArterial = []

        console.log(registros);

        registros
            .map(r => {
                return {
                    ...r,
                    fechaObj: new Date(Date.parse(r.fecha))
                }
            })
            .sort((a, b) => a.fechaObj - b.fechaObj)
            .forEach(r => {
                labels.push(r.fecha);

                dataChart.registros.push({
                    x: r.fecha,
                    y: r.valor
                });
                dataChart.recomendados.push({
                    x: r.fecha,
                    y: r.recomendados.valor
                });
                if (r.valor2 && r.recomendados.valor2) {
                    dataChart2.registros.push({
                        x: r.fecha,
                        y: r.valor2
                    });
                    dataChart2.recomendados.push({
                        x: r.fecha,
                        y: r.recomendados.valor2
                    });
                    datosCompletosTensionArterial.push({
                        tas: r.valor,
                        tad: r.valor2,
                    });
                }
            });

        chartsData.data.labels = labels;

        if (dataChart2.registros.length > 0) {
            chartsData.data.datasets = [
                {
                    data: dataChart.recomendados,
                    label: 'Meta PAS'
                },
                {
                    data: dataChart.registros,
                    label: 'PAS'
                },
                {
                    data: dataChart2.recomendados,
                    label: 'Meta PAD'
                },
                {
                    data: dataChart2.registros,
                    label: 'PAD'
                }
            ];
        }
        else {
            chartsData.data.datasets = [
                {
                    data: dataChart.recomendados,
                    label: 'Meta'
                },
                {
                    data: dataChart.registros,
                    label: indicadorTitle
                }
            ];
        }

        chartObj = chartHelper.createLineChart(
            document.getElementById('chart-canvas'),
            chartsData.data.datasets,
            chartsData.data.labels,
            {
                time: true
            }
        );
        updateCalculoHipertension(datosCompletosTensionArterial);
    }

    function remove(registro) {
        events('remove', registro);
    }

    function indicadorSelected(ev) {
        selectedIndicador = ev.target.value;
        const ind = tiposIndicador.find(f => f.value === selectedIndicador);
        if (ind) {
            indicadorTitle = ind.label;
        }
        events('indicador', selectedIndicador);
    }
</script>
<div>
    <h2>Seguimiento</h2>
    <div class="py-1 max-w-300px">
        <NauiSelect label="Seleccionar indicador" options={tiposIndicador} bind:value={selectedIndicador} on:change={indicadorSelected}/>
    </div>
    <div class:hidden={selectedIndicador === ''}>
        <div>
            <div class="radius p-1 shadow mb-2">
                <div class="box-b mb-1">
                    <h3 class="primary">{indicadorTitle}</h3>
                    {#if selectedIndicador === 'tension_arterial'}
                        <div class="back-gray py-i px-1 box-l sx-15">
                            <strong>Clasificación</strong>
                            <NauiState
                                bind:code={calculoHipertension.code}
                                bind:label="{calculoHipertension.label}"
                                border="true"/>
                        </div>
                    {/if}
                </div>
                <canvas id="chart-canvas" width="1000" height="400"></canvas>
            </div>
        </div>

        <div class="max-w-600px">
            <table class="naui-table w-100 mb-1">
                <thead>
                    <tr>
                        <th>
                            <div class="box">Fecha</div>
                        </th>
                        <th>
                            <div class="box">{indicadorTitle}</div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                {#each registros as registro, i (registro.id)}
                    <tr>
                        <td>
                            <div class="box">{registro.fecha}</div>
                        </td>
                        <td>
                            <div class="box">
                                {registro.valor}
                                {#if registro.valor2}/ {registro.valor2}{/if}
                            </div>
                        </td>
                    </tr>
                {/each}
                </tbody>
            </table>
        </div>
    </div>
</div>