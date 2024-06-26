<svelte:options accessors/>
<script lang="ts">
    import NauiCheckbox from "../atoms/NauiCheckbox.svelte";
    import NauiState from "../atoms/NauiState.svelte";
    import NauiButton from "../atoms/NauiButton.svelte";

    import {createEventDispatcher} from "svelte";
    import NauiTag from "../atoms/NauiTag.svelte";

    export let columns = [];
    export let data;
    export let total;

    const dispatch = createEventDispatcher();

    $:cols = columns.length;
    $: {
        listenChanges(data)
    }

    let ordering = {
        by: '',
        dir: 1
    };

    function updateSelected(ev) {
        data.forEach(d => {
            d.selected = ev.target.checked;
        });
        data = [...data];
    }

    function listenChanges(newValue) {
        dispatch('checked', newValue.filter(i => i.selected));
    }

    function setOrdering(slug) {
        if (ordering.by === slug) {
            ordering.dir *= -1;
        } else {
            ordering.dir = -1;
        }
        ordering.by = slug;
        if (total > data.length) {
            dispatch('order', ordering);
        } else {
            data.sort((a, b) => {
                const test = a[slug].localeCompare(b[slug]);
                return test * -(ordering.dir);
            });
            data = data;
        }
    }
</script>
<div>
    <table class="naui-table w-100">
        <thead>
        <tr>
            {#each columns as col}
                <th style="width: {col.width}" class="{col.class}">
                    <div>
                        {#if col.type === 'checkbox'}
                            <NauiCheckbox on:input={updateSelected}/>
                        {:else}
                            {#if col.order}
                                <div class="box-l pointer" on:click={setOrdering.bind(this, col.slug)}>
                                    <div class="flex-col box mr-i">
                                        {#if ordering.by === col.slug}
                                            {#if ordering.dir === 1}
                                                <div class="order-caret">
                                                    <i class="fa fa-caret-up self-start"></i>
                                                </div>
                                            {:else}
                                                <div class="order-caret">
                                                    <i class="fa fa-caret-down self-end"></i>
                                                </div>
                                            {/if}
                                        {:else}
                                            <div class="order-caret">
                                                <i class="fa fa-caret-up self-end"></i>
                                            </div>
                                            <div class="order-caret">
                                                <i class="fa fa-caret-down self-start"></i>
                                            </div>
                                        {/if}
                                    </div>
                                    <div class="primary">{col.label}</div>
                                </div>
                            {:else}
                                {col.label}
                            {/if}
                        {/if}
                    </div>
                </th>
            {/each}
        </tr>
        </thead>
        <tbody>
        {#each data as item (item.slug)}
            <tr>
                {#each columns as col}
                    <td>
                        <div>
                            {#if col.type === 'text'}
                                {item[col.slug]}
                            {:else if col.type === 'checkbox'}
                                <NauiCheckbox label="" bind:value={item.selected}/>
                            {:else if col.type === 'state'}
                                <NauiState code={item[col.slug].code}
                                           label={item[col.slug].label}/>
                            {:else if col.type === 'tag'}
                                <NauiTag label="{item[col.slug].label}" textColor="{item[col.slug].textColor}"
                                         backColor="{item[col.slug].backColor}"
                                         borderColor="{item[col.slug].backColor}"/>
                            {:else if col.type === 'actions'}
                                <div class="{col.boxClass || 'box sx-ii'}">
                                    {#each item[col.slug] || [] as action}
                                        {#if action.route}
                                            <NauiButton href={action.route} iconStyle="{action.iconStyle}" icon="{action.icon}" color="accent"/>
                                        {:else}
                                            <NauiButton icon="{action.icon}" iconStyle="{action.iconStyle}"
                                                        color="accent"
                                                        on:click={() => dispatch('action', {action: action.slug, slug:item.slug})}/>
                                        {/if}
                                    {/each}
                                </div>
                            {:else if col.type === 'list'}
                                {item[col.slug].map(i => i.label.trim()).join(', ')}
                            {/if}
                        </div>
                    </td>
                {/each}
            </tr>

        {:else}
            <tr>
                <td colspan="{cols}">
                    <div>
                        <h2>No se han encontrado registros</h2>
                    </div>
                </td>
            </tr>
        {/each}
        </tbody>
    </table>
</div>
<style>
    .order-caret {
        line-height: 5px;
        font-size: .8rem;
        opacity: .5;
        height: 15px;
        width: 15px;
        display: flex;
        justify-content: center;
        cursor: pointer;
    }

    .order-caret i {
        line-height: 8px;
    }

    .order-caret:hover {
        opacity: .8;
    }

    .order-caret:active {
        opacity: 1;
    }

    .el-actions {
        justify-content: flex-start;
    }
</style>
