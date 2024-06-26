<svelte:options accessors/>
<script>
    import {onMount} from "svelte";

    export let messages = [];

    onMount(() => {
        setTimeout(() => {
            messages.forEach(m => alert(m.text))
        }, 500);
    });
</script>
<div></div>
<style>

</style>