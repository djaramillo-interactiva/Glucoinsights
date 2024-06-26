<script>
    import { createEventDispatcher } from 'svelte';

    export let title;
    export let open;
    export let maxWidth = 'none';
    const eventDispatcher = new createEventDispatcher();

    function close(){
        open = false;
        eventDispatcher('close');
    }
</script>

<div>
    <aside class:active={open} class="flex-col shadow" style="max-width: {maxWidth}">
        <div class="py-ii px-15 back-gray">
            <div class="box-l sx-1">
                <div class="btn-icon" on:click={close}>
                    <span class="material-icons-outlined accent">arrow_back</span>
                </div>
                <h5 class="primary">{title}</h5>
            </div>
        </div>
        <div class="p-15 flex-100 overflow-y-scroll no-scrollbar">
            <slot>

            </slot>
        </div>
        <div class="p-1">
            <slot name="actions">

            </slot>
        </div>
    </aside>
    <div class="slide-over-overlay" class:active={open} on:click={close}></div>
</div>
<style>
    aside {
        position: fixed;
        right: 0;
        top: 0;
        bottom: 0;
        min-width: 400px;
        width: max-content;
        z-index: 40;
        background: white;
        transform: translateX(100%);
        transition: 0.2s ease-in-out all;
    }

    aside.active {
        transform: translateX(0%);
    }

    .slide-over-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: rgba(0, 0, 0, 0.1);
        z-index: 30;
        opacity: 0;
        transition: 0.2s ease-in-out all;
    }

    .slide-over-overlay.active {
        opacity: 1;
        bottom: 0;
    }
</style>
