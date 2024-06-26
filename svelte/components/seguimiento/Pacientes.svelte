<svelte:options accessors/>
<script>
    import {createEventDispatcher} from "svelte";
    import NauiExplorer from "../naui/pages/NauiExplorer.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import NauiSlideOver from "../naui/layout/NauiSlideOver.svelte";
    import NauiCheckbox from "../naui/atoms/NauiCheckbox.svelte";

    const dispatch = createEventDispatcher();
    export let count = 0;
    export let pages = 0;
    export let filters = [];
    export let columns;
    export let data;
    export let routeCreate = '';
    export let paginate = false
    export let groups = [];
    export let cities = [];
    export let diagnoses = [];
    export let hideSearch = false;
    export let grid = 6
    let explorer;
    let open = false;
    let groupsSelected = groups.some(g => g.selected);

    function addToGroup() {
        open = true;
        groups.forEach(g => g.value = false);
        groups = [...groups];
    }

    function saveGroups() {
        const saveData = {
            pacientes: data.filter(p => p.selected).map(p => p.id),
            grupos: groups.filter(g => g.value).map(g => g.id)
        };
        dispatch('save', saveData);
    }

    export function getParams() {
        return explorer.getParams()
    }

    export function updateData(response) {
        data = response.data || [];
        count = response.total || 0;
        pages = response.pages || 0;
        explorer.updatePages(pages);
    }

    function setGroups() {
        groupsSelected = data.some(g => g.selected);
    }

    function descargarReporte() {
        dispatch('descargarReporte', explorer.getParams());
    }

</script>
<NauiExplorer
        bind:this={explorer}
        on:filter
        on:input
        on:checked={setGroups}
        searchLabel="Buscar por nombre o ID de paciente"
        {grid}
        {count}
        {filters}
        {columns}
        {data}
        {paginate}
        {pages}
        {hideSearch}
        on:next>
    <div slot="actions">
        <div class="flex sx-ii">
            {#if groups.length > 0 && groupsSelected}
                <div class="box-l sx-ii">
                    <NauiButton caption="AGREGAR A GRUPO"
                                size="small"
                                icon="add"
                                color="accent"
                                mode="stroked"
                                on:click={addToGroup}/>
                </div>
            {/if}
            {#if routeCreate}
                <NauiButton size="small" href="{routeCreate}" caption="CREAR PACIENTE" color="solid" mode="accent" icon="add"/>
            {/if}
            {#if !hideSearch}
                <NauiButton size="small" on:click={descargarReporte} caption="DESCARGAR REPORTE" mode="stroked"/>
            {/if}
        </div>
    </div>
</NauiExplorer>
<NauiSlideOver title="Agregar a grupo" bind:open={open}>
    {#each groups as group (group.id)}
        <NauiCheckbox {...group} bind:value={group.value}/>
    {/each}
    <div slot="actions">
        <div class="max-w-300px mx-auto">
            <NauiButton caption="GUARDAR" mode="stroked" color="accent" className="w-100" on:click={saveGroups}/>
        </div>
    </div>
</NauiSlideOver>
