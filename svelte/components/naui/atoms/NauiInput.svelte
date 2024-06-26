<script>
    import { onMount } from "svelte";

    export let label;
    export let type = 'text';
    export let value;
    export let isDisabled = false;
    export let step = '0.1';
    let fill = false;
    let focus = false;

    onMount(() => {
        setStatus();
    });

    function setStatus() {
        if (value !== '' && value !== undefined) {
            fill = true;
        } else {
            fill = false;
        }
        focus = false;
    }
</script>
<div class="naui-field" class:active={fill}>
    <div class="naui-field-back" class:fill={fill}>
        <label class:focus={focus}>{label}</label>
        {#if type === 'email'}
            <input
                    class="naui-input w-100"
                    readonly={isDisabled}
                    type="email"
                    bind:value={value}
                    on:input
                    on:focus={()=> fill=true}
                    on:focusin={()=>focus=false}
            />
        {:else if type === 'password'}
            <input
                    class="naui-input w-100"
                    readonly={isDisabled}
                    type="password"
                    bind:value={value}
                    on:input
                    on:focus={()=> fill=true}
                    on:focusin={()=>focus=false}
            />
        {:else if type === 'number'}
            <input
                    class="naui-input w-100"
                    readonly={isDisabled}
                    type="number"
                    step={step}
                    bind:value={value}
                    on:input
                    on:change
                    on:focus={()=>fill=true}
                    on:focusin={()=>focus=false}
                    placeholder="Sin información"
            />
        {:else}
            <input
                    class="naui-input w-100"
                    readonly={isDisabled}
                    type="text"
                    bind:value={value}
                    on:input
                    on:focus={()=> fill=true}
                    on:focusin={()=>focus=false}
            />
        {/if}
    </div>
</div>
<style>
    .naui-field-back.fill{
        background: white;
    }
</style>
