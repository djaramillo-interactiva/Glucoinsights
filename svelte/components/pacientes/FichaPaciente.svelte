<script>
    import NauiState from "../naui/atoms/NauiState.svelte";

    export let nombre;
    export let diagnostico;
    export let riesgo_rcv;
</script>
<blockquote>
    <div class="box-l sx-2">
        <div>
            <h2 class="primary mb-ii">{nombre}</h2>
            <p>Diagnóstico principal: {diagnostico}</p>
        </div>
        <div class="self-end flex sx-ii">
            <NauiState code={riesgo_rcv.code} label={riesgo_rcv.label} border={true}/>
        </div>
    </div>
</blockquote>
<style>

</style>
