<svelte:options accessors/>
<script>
    import NauiCheckbox from "../naui/atoms/NauiCheckbox.svelte";
    import NauiInput from "../naui/atoms/NauiInput.svelte";

    export let current;

    let searchTerm = "";
    let filteredList = []

    $: {
        let gruposGestionArray = []
        if (current) {
            gruposGestionArray = (current.grupos_gestion || []).filter(item => item.label.toLowerCase().includes(searchTerm.toLowerCase()))
            gruposGestionArray.sort(o => o.value ? -1 : 1);
        }
        filteredList = gruposGestionArray;
    }
</script>
<div class="flex-col max-h-100">
    <div class="mb-ii">
        <NauiInput label="Nombre del usuario"
                   bind:value={current.name}/>
    </div>
    <div class="mb-ii">
        <NauiInput label="Correo"
                   bind:value={current.correo}/>
    </div>
    <div class="mb-ii">
        <NauiCheckbox label="¿Todos los grupos de gestión?"
                   bind:value={current.todos_grupos_gestion}/>
    </div>
    <div class:hidden={current.todos_grupos_gestion} class="mb-ii pt-1">
        <h2 class="mb-ii">Grupos de gestión</h2>
        <div class="mb-ii">
            <input class="naui-input w-100" type="text" bind:value={searchTerm} placeholder="Buscar grupo de gestión">
        </div>
    </div>
    <div class:hidden={current.todos_grupos_gestion} class="flex-100" style="overflow-y:scroll">
        {#each filteredList as i}
            <NauiCheckbox label="{i.label}"
                          bind:value={i.value}/>
        {/each}
    </div>

</div>
