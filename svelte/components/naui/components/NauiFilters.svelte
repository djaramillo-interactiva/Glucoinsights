<script>
    import { createEventDispatcher, onMount } from "svelte";
    import NauiButton from "../atoms/NauiButton.svelte";

    export let filters;
    export let grid = null;
    let _filters = [];
    let selection = [];

    const events = new createEventDispatcher()

    onMount(() => {
        updateSelect()
    });

    export function updateSelect(){
        _filters = filters.map((x) => {
            return {
                label: x.label,
                slug: x.slug,
                options: x.options,
                value: x.selected
            }
        });
    }

    export function refreshFilters(slug) {
        const filter = filters.find((f) => f.slug === slug)

        const _f = _filters.find((f) => f.slug === filter.slug)
        _f.options = filter.options

        if(filter.selected){
            _f.value = filter.selected
        }
        else{
           _f.value = null
        }

        _filters = _filters

    }

    export const runFilters = function() {
        selection = _filters.map((x) => {
            if (x.value !== null && x.value !== undefined)
                return {
                    slug: x.slug,
                    value: x.value
                }
            else {
                return null;
            }
        });
        selection = selection.filter((x) => x);
        const filtersJson = {};
        selection.forEach(s => {
            filtersJson[s.slug] = s.value
        });
        events('filtered', filtersJson);
    }

    export function clear() {
        _filters = _filters.map((x) => {
            x.value = null;
            return x;
        });
        selection = [];
        events('filtered', {});
    }
</script>
<div class="box-l sx-ii">
    <div class="{grid ? 'grid-'+grid+' gap-i' : 'box-l sx-i'} p-i">
    {#each _filters as filter (filter.slug)}
        {#if filter.options && filter.options.length > 0}
        <select bind:value={filter.value} class="naui-filter max-w-300px" on:change={runFilters} class:selected={filter.value}>
            <option selected hidden value={null}>{filter.label}</option>
            {#each filter.options as option}
                {#if option.options}
                    <optgroup label={option.name}>
                        {#each option.options as sub}
                        <option value={sub.value}>{sub.label}</option>
                        {/each}
                    </optgroup>
                {:else}
                    <option value={option.value}>{option.label}</option>
                {/if}
            {/each}
        </select>
        {/if}
    {/each}
    </div>
    <NauiButton icon="refresh" size="small" color="secondary" on:click={clear}/>
</div>

<style>
    .naui-filter.selected{
        color: var(--secondary);
        opacity: 1;
    }
</style>
