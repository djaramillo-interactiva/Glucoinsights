<svelte:options accessors/>
<script>
    import DynamicQuantTable from "../widgets/DynamicQuantTable.svelte";
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import { createEventDispatcher } from "svelte";

    const dispatch = new createEventDispatcher();

    export let data;
    export let categories = [];
    const buttonLabel = 'AÑADIR';
    const buttonIcon = 'plus';
    const baseItem = {nombre: '', categoria: ''}

    function save(){
        dispatch('save', data);
    }

</script>
<div>
    <DynamicQuantTable
            title="Nombre medicamento"
            category="Categoría"
            categoryKey="categoria"
            buttonLabel="AÑADIR"
            buttonIcon="add"
            {baseItem}
            {categories}
            bind:data={data} />
    <NauiFloatingAction>
        <NauiButton caption="GUARDAR" icon="save" iconStyle="outlined" color="accent" mode="solid" on:click={save} />
    </NauiFloatingAction>

</div>



<style>

</style>
