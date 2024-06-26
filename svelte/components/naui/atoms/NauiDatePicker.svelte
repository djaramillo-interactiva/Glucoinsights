<script>
    import { onMount } from "svelte";

    export let label;
    export let value;
    let fill = false;
    let focus = false;
    let isDisabled = false;

    onMount(() => {
        setStatus();
    });

    function setStatus() {
        focus = false;
    }
</script>
<div class="naui-field active">
    <label class:focus={focus}>{label}</label>
    <input
            class="naui-input w-100"
            type="date"
            bind:value={value}
            on:input
            on:focusin={()=>focus=false}
    />
</div>
