<svelte:options accessors/>
<script>
    import NauiCheckboxGroup from "./NauiCheckboxGroup.svelte";
    import {createEventDispatcher} from "svelte";

    const dispatch = new createEventDispatcher();
    export let groups = [];

    function handleUpdate(event) {
        let filtered = JSON.parse(JSON.stringify(groups.filter(g => !!g.value)));
        filtered.forEach((group) => {
            group.children = group.children.filter(g => !!g.value);
        });
        filtered = filtered.filter(g => g.children.length > 0);
        dispatch('update', filtered);
    }
</script>

<div>
    {#each groups as group}
        <NauiCheckboxGroup {...group}
                           bind:value={group.value}
                           on:update={handleUpdate}>
        </NauiCheckboxGroup>
    {/each}
</div>
