<script>
    import { onMount } from "svelte";

    export let label;
    export let value;
    export let isDisabled = false;
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
        <textarea class="naui-input w-100"
                  readonly={isDisabled}
                  placeholder={fill ? '' : label}
                  bind:value={value}
                  on:input
                  on:focus={()=> fill=true}
                  on:focusin={()=>focus=false}></textarea>
    </div>
</div>
<style>
    .naui-field-back.fill{
        background: white;
    }
</style>
