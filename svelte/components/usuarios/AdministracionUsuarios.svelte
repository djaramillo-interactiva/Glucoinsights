<svelte:options accessors/>
<script>
    import NauiExplorer from "../naui/pages/NauiExplorer.svelte";
    import NauiSlideOver from "../naui/layout/NauiSlideOver.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import ManageUsuario from "./ManageUsuario.svelte";
    import NauiConfirm from "../naui/components/NauiConfirm.svelte";
    import {createEventDispatcher} from "svelte";

    export let count = 0;
    export let pages = 0;
    export let filters = [];
    export let columns;
    export let data;
    export let paginate = false;
    export let grupos_gestion = [];
    export let selectedItems = []
    $: showDeleteAction = selectedItems.length > 0;
    let explorer;
    let confirmCmpt;

    const dispatch = createEventDispatcher();

    let searchTerm = "";

    let edit = false;
    let current;

    function handleUpdateUser(obj) {
        dispatch('save', obj);
        edit = false;
    }

    function createUser() {
        current = {
            name: '',
            todos_grupos_gestion: false,
            grupos_gestion: grupos_gestion.map((i) => {
                return {
                    slug: i.slug,
                    label: i.label,
                    value: false
                }
            }),
            correo: ''
        }
        edit = true
    }

    function handleActions(evt) {
        const {action, slug} = evt.detail;

        switch (action) {
            case 'edit':
                const find = data.find((d) => d.slug === slug)
                if (find) {
                    edit = true;
                    current = JSON.parse(JSON.stringify({
                        id: find.slug,
                        name: find.name,
                        todos_grupos_gestion: find.todos_grupos_gestion === 'Sí',
                        grupos_gestion: grupos_gestion.map((i) => {
                            return {
                                slug: i.slug,
                                label: i.label,
                                value: !!find.grupos_gestion.find(_i => _i.slug === i.slug)
                            }
                        }),
                        correo: find.mail
                    }))
                }
                break;
            default:
                alert(`action: ${action} does not implemented`);
        }
    }

    function updateUser() {
        const obj = {
            id: current.id,
            name: current.name,
            todos_grupos_gestion: current.todos_grupos_gestion,
            grupos_gestion: current.todos_grupos_gestion ? [] : current.grupos_gestion.filter(i => !!i.value),
            email: current.correo
        };
        handleUpdateUser(obj);
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

    function handleChecked(evt) {
        selectedItems = evt.detail;
    }

    async function deleteUser() {
        const status = await confirmCmpt.show({
            message: 'Desea eliminar los usuarios?'
        });
        if (status) {
            dispatch('delete', selectedItems);
        }
    }

    export function refresh() {
        explorer.clear();
    }
</script>
<div>
    <NauiExplorer bind:this={explorer}
                  bind:count={count}
                  {filters}
                  {columns}
                  {data}
                  {paginate}
                  {pages}
                  on:filter
                  on:action={handleActions}
                  on:next
                  on:order
                  on:checked={handleChecked}>
        <div slot="actions">
            <div class="flex sx-ii">
                {#if showDeleteAction}
                    <NauiButton caption="BORRAR USUARIOS"
                                size="small"
                                color="solid"
                                icon="delete" iconStyle="outlined"
                                on:click={deleteUser}/>
                {/if}
                <NauiButton caption="CREAR USUARIO"
                            size="small"
                            color="solid"
                            mode="accent"
                            icon="add"
                            on:click={createUser}/>
            </div>
        </div>
    </NauiExplorer>
    <NauiSlideOver title="Datos del usuario"
                   maxWidth="300px"
                   bind:open={edit}>
        {#if (current && edit)}
            <ManageUsuario {current}/>
        {/if}
        <div slot="actions">
            <div class="max-w-300px mx-auto">
                <NauiButton caption="GUARDAR"
                            className="w-100"
                            mode="stroked"
                            color="accent"
                            on:click={updateUser}/>
            </div>
        </div>
    </NauiSlideOver>
    <NauiConfirm bind:this={confirmCmpt}>
    </NauiConfirm>
</div>
<style>

</style>