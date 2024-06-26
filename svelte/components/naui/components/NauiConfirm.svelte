<svelte:options accessors/>
<script>
    export function show(params) {
        return new Promise((resolve) => {
            let status = confirm(params.message);
            resolve(!!status);
        })
    }
</script>
