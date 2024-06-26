<script>
    import NauiState from "../naui/atoms/NauiState.svelte";
    import NauiInput from "../naui/atoms/NauiInput.svelte";

    export let estatura = 0;
    export let peso = 0;
    let imc = 25;
    let code = '';
    let label = 'Sin información';

    $: {
        if(estatura === "Sin información" || peso === "Sin información"){
            imc = "Sin información"
            
        }
        else {
            imc = (estatura !== 0 ? (peso / Math.pow(estatura / 100, 2)) : 0).toFixed(2);
            if (imc < 20) {
                label = 'Bajo peso';
                code = 4;
            } else if (imc < 25) {
                label = 'Normal';
                code = 1;
            } else if (imc < 30) {
                label = 'Sobrepeso';
                code = 3;
            } else if (imc >= 30 & imc <= 34.9) {
                label = 'Obesidad 1';
                code = 2;
            } else if (imc >= 35 & imc <= 39.9) {
                label = 'Obesidad 2';
                code = 3;
            } else if (imc >= 40) {
                label = 'Obesidad 3';
                code = 4;
            }
        }
    }
        
    

</script>
<div class="flex sx-1 max-w-700px">
    <div class="flex-2">
        <NauiInput type="number" label="Estatura (Cms)" bind:value={estatura}/>
    </div>
    <div class="flex-2">
        <NauiInput type="number" label="Peso (Kg)" bind:value={peso}/>
    </div>
    <div class="back-gray flex-3 py-i px-iii radius box-l sx-15 self-end" style="height: 50px;">
        <p><strong>IMC {imc}</strong></p>
        <NauiState {code} {label} border="true" styleText="min-width: 120px;"/>
    </div>
</div>
