<svelte:options accessors/>
<script>
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";

    export let title;
    export let buttonLabel;
    export let buttonIcon = null;
    export let readonly = false;
    export let data;

    export let quantity = '';
    export let quantityKey = '';
    export let category = '';
    export let categories = [];
    export let categoryKey = ''
    export let options = null;

    export let baseItem;

    function deleteItem(index) {
        data.splice(index, 1);
        data = data;
    }

    function addItem() {
        data = [...data, Object.assign({}, baseItem)];
    }
</script>
<div>
    <table class="naui-table mb-1 min-w-500px">
        <thead>
        <tr>
            <th class="min-w-300px">
                <div>{title}</div>
            </th>
            {#if quantityKey}
                <th>
                    <div>{quantity}</div>
                </th>
            {/if}
            {#if categoryKey}
                <th>
                    <div>{category}</div>
                </th>
            {/if}
            {#if !readonly}
            <th>
                <div></div>
            </th>
            {/if}
        </tr>
        </thead>
        <tbody>
        {#each data as item, i}
            <tr>
                <td>
                    <div>
                        {#if options}
                        <select class="naui-input min-w-300px w-100" bind:value={item.nombre}>
                            <option value="" hidden>Seleccionar</option>
                            {#each options as option}
                                <option value={option.value}>{option.label}</option>
                            {/each}
                        </select>
                        {:else}
                        <input type="text" class="naui-input min-w-300px w-100" bind:value={item.nombre} readonly={readonly}>
                        {/if}
                    </div>
                </td>
                {#if categoryKey}
                    <td>
                        <div style="min-width: 150px">
                            <NauiSelect
                                bind:value={item[categoryKey]}
                                label={category}
                                options="{categories}"/>
                        </div>
                    </td>
                {/if}
                {#if quantityKey}
                    <td>
                        <div><input type="number" class="naui-input" bind:value={item[quantityKey]}></div>
                    </td>
                {/if}
                {#if !readonly}
                <td>
                    <div>
                        <NauiButton size="small" icon="clear" iconStyle="outlined" color="accent" on:click={deleteItem.bind(this, i)}/>
                    </div>
                </td>
                {/if}
            </tr>
        {/each}
        </tbody>
    </table>
    {#if !readonly}
        <NauiButton caption={buttonLabel} icon={buttonIcon} size="small" color="accent" on:click={addItem}/>
    {/if}
</div>
<style>
    input {
        min-height: 35px;
        height: 35px;
    }

    input[type=number] {
        max-width: 100px;
    }
</style>
