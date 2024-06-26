<script>
    import NauiInput from "../naui/atoms/NauiInput.svelte";
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";
    import NauiState from "../naui/atoms/NauiState.svelte";

    export let colesterolTotal = 0;
    export let hdl = 0;
    export let tas = 0;
    export let tad = 0;
    export let fumador = false
    export let nivelRiesgo = '';
    export let codigoEstado = 1;

    const siNO = [
        {
            label: 'SI',
            value: true
        },
        {
            label: 'NO',
            value: false
        }
    ]
</script>
<div class="flex-row sx-1">
    <div class="flex-2">
        <NauiInput type="number" label="Colesterol total" bind:value={colesterolTotal}/>
    </div>
    <div class="flex-2">
        <NauiInput type="number" label="HDL" bind:value={hdl}/>
    </div>
    <div class="flex-1">
        <NauiInput type="number" label="PAS" bind:value={tas}/>
    </div>
    <div class="flex-1">
        <NauiInput type="number" label="PAD" bind:value={tad}/>
    </div>
    <div class="flex-2">
        <NauiSelect label="Fumador" bind:value={fumador} options={siNO}/>
    </div>
    <div class="back-gray flex-3 py-i px-iii radius box-l sx-ii self-end" style="height: 50px;">
        <p><strong>Riesgo de Framingham</strong></p>
        <NauiState code={codigoEstado} label={nivelRiesgo} border="true" styleText="min-width: 120px;"/>
    </div>
</div>
