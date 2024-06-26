<svelte:options accessors/>
<script>
    import {createEventDispatcher} from 'svelte';
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";

    export let data;
    const baseItem = {
        nombre: '',
        edad_inicio: 0,
        edad_fin: 0
    };
    const dispatch = new createEventDispatcher();

    function deleteItem(index) {
        data.splice(index, 1);
        data = data;
    }

    function addItem() {
        data = [...data, Object.assign({}, baseItem)];
    }

    function save() {
        dispatch('save');
    }

</script>
<div>
    <table class="naui-table mb-1">
        <thead>
        <tr>
            <th  style="min-width: 200px">
                <div>Nombre grupo</div>
            </th>
            <th style="min-width: 120px">
                <div>Edad inicio</div>
            </th>
            <th style="min-width: 120px">
                <div>Edad fin</div>
            </th>
            <th style="min-width: 55px;"></th>
        </tr>
        </thead>
        <tbody>
        {#each data as item, i}
            <tr>
                <td>
                    <div><input type="text" class="naui-input" style="height: 35px" bind:value={item.nombre}></div>
                </td>
                <td>
                    <div><input type="number" class="naui-input" style="height: 35px" bind:value={item.edad_inicio}>
                    </div>
                </td>
                <td>
                    <div><input type="number" class="naui-input" style="height: 35px" bind:value={item.edad_fin}></div>
                </td>
                <td>
                    <div>
                        <NauiButton size="small" icon="clear" iconStyle="outlined" color="accent" on:click={deleteItem.bind(this, i)}/>
                    </div>
                </td>
            </tr>
        {/each}
        </tbody>
    </table>
    <div class="box-l sx-ii">
        <NauiButton caption="AÑADIR GRUPO" icon="add" size="small" color="accent" on:click={addItem}/>
    </div>
    <NauiFloatingAction>
        <NauiButton caption="GUARDAR" icon="save" iconStyle="outlined" color="accent" mode="solid" on:click={save}/>
    </NauiFloatingAction>
</div>
<style>
    .naui-input {
        min-height: 35px;
        height: 35px;
    }

    .naui-input[type=number] {
        max-width: 100px;
    }
</style>
