<svelte:options accessors/>
<script>
    import NauiCheckbox from "./NauiCheckbox.svelte";
    import {createEventDispatcher} from "svelte";

    const dispatch = new createEventDispatcher();

    export let label;
    export let value;
    export let children = [];

    $: {
        changeValues(children);
    }

    function changeValues(newValue) {
        if (value) {
            dispatch('update', {
                label,
                value: !!value,
                children: children.filter(v => !!v.value)
            });
        } else {
            dispatch('update', {
                label,
                value: !!value,
                children: []
            });
        }
    }
</script>

<div>
    <NauiCheckbox {label} bind:value={value}/>
    {#if value}
        <div class="children">
            {#each children as child}
                <NauiCheckbox {...child} on:value={changeValues} bind:value={child.value}/>
            {/each}
        </div>
    {/if}
</div>

<style>
    .children {
        padding-left: 1rem;
    }
</style>