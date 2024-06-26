<svelte:options accessors/>
<script>
    import DynamicQuantTable from '../widgets/DynamicQuantTable.svelte';
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import { createEventDispatcher } from 'svelte';

    export let data;
    export let serviceOptions = [];
    const baseItem = { nombre: '', cantidad: 0 };
    const dispatch = createEventDispatcher();

    function getCharIndex(index) {
        return String.fromCharCode(65 + index);
    }

    function save() {
        dispatch('save', data);
    }

    function add() {
        data = [ ...data, { nombre: '', data: [] } ];
    }

    function remove(index) {
        data.splice(index, 1);
        data = data;
    }

</script>
<div class="max-w-800px">
    <div class="mb-2">
        {#each data as tarea, i (tarea.id)}
            <div class="py-15 mb-1">
                <div class="grid-1-3">
                    <div>
                        <h2>{tarea.nombre || '<Ingrese nombre>'}</h2>
                    </div>
                    <div>
                        <div class="grid-2-1">
                            <input type="text" class="naui-input min-w-500px mb-15" bind:value={tarea.nombre}
                                   readonly={tarea.readonly}>
                            {#if !tarea.readonly}
                                <div class="pl-15">
                                    <NauiButton icon="delete" iconStyle="outlined" color="accent" on:click={remove.bind(this, i)}/>
                                </div>
                            {/if}
                        </div>
                        <DynamicQuantTable
                                {baseItem}
                                readonly={tarea.readonly}
                                bind:data={tarea.data}
                                title="Nombre del servicio"
                                quantity="Cantidad"
                                quantityKey="cantidad"
                                options={serviceOptions}
                                min={1}
                                buttonLabel="AÑADIR SERVICIO"
                                buttonIcon="add"/>
                    </div>
                </div>
            </div>
            <div class="separator"></div>
        {/each}
        <div class="pt-1">
            <NauiButton caption="AÑADIR GRUPO DE TAREAS" icon="add" size="small" mode="stroked" color="accent"
                        on:click={add}/>
        </div>
    </div>

    <NauiFloatingAction>
        <NauiButton caption="GUARDAR" icon="save" iconStyle="outlined" color="accent" mode="solid" on:click={save}/>
    </NauiFloatingAction>
</div>
<style>
    .separator {
        height: 2px;
        background: #eee;
    }
</style>
