<script>
    import { onMount } from "svelte";

    export let value = '';
    export let label;
    export let options;
    export let required = false;
    export let showValue = false;
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
<div class="naui-field active w-100">
    <div class="naui-field-back" class:fill={fill}>
        <label class:focus={focus}>{label}</label>
        <select class="naui-input w-100" bind:value={value} {required}
                on:focusin={()=>focus=false} on:change>
            <option value="" hidden>{label}</option>
            {#each options as option, i}
                {#if option.options}
                    <optgroup label={option.name}>
                        {#each option.options as sub}
                        <option value={sub.value}>
                            {#if showValue}
                                {sub.value}
                            {/if}
                            {sub.label}
                        </option>
                        {/each}
                    </optgroup>
                {:else}
                    <option value="{option.value}">{option.label}</option>
                {/if}
            {/each}
        </select>
    </div>
</div>
<style>
    select {
        font-size: .95rem;
    }
    .naui-field-back.fill{
        background: white;
    }
</style>
