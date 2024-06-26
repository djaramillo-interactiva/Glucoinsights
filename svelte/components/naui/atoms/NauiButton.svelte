<script lang="ts">
    export let caption = null;
    export let icon = null;
    export let iconStyle = null;
    export let mode = '';
    export let className = '';
    export let size = '';
    export let color = '';
    export let type = 'button';
    export let href = null;
    export let download = false;
    export let disabled = false;

    $: iconClass = iconStyle ? 'material-icons-' + iconStyle : 'material-icons';

</script>
{#if caption}
    {#if href}
        <a class="btn {mode} {color} {size} {className}" class:disabled={disabled} href="{href}" download={download ? '' : undefined}>
            {#if icon}
                <span class="{iconClass}">{icon}</span>
            {/if}
            <span>{caption}</span>
        </a>
    {:else}
        <button on:click class="btn {mode} {color} {size} {className}" class:disabled={disabled}>
            {#if icon}
                <span class="{iconClass}">{icon}</span>
            {/if}
            <span>{caption}</span>
        </button>
    {/if}
{:else if icon}
    {#if href}
        <a class="btn-icon {size}" class:disabled={disabled} href="{href}" download={download ? '' : undefined}>
            <span class="{iconClass} {color}">{icon}</span>
        </a>
    {:else}
        <button on:click class="btn-icon {size}" class:disabled={disabled}>
            <span class="{iconClass} {color}">{icon}</span>
        </button>
    {/if}
{/if}
<style>
    :host {
        display: block;
    }

    .btn.disabled{
        background: #ddd;
        color:#888;
        cursor: not-allowed;
    }
</style>
