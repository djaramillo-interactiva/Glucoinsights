<svelte:options accessors/>
<script>
    import { createEventDispatcher } from "svelte";
    export let placeholder;
    /*
    Add delay to handle search
     */
    let term;
    let timer;
    const debounce = v => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            term = v;
            handleTerm();
        }, 300);
    }
    const dispatch = createEventDispatcher()

    function handleTerm() {
        dispatch('search', term);
    }

    export function clear() {
        term = '';
    }
</script>

<div>
    <input type="text"
           class="naui-input w-100"
           on:keyup={({ target: { value } }) => debounce(value)}
           {placeholder}>
</div>