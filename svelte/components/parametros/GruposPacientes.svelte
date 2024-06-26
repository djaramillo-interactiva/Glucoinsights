<svelte:options accessors/>
<script>
    import NauiSlideOver from "../naui/layout/NauiSlideOver.svelte";
    import { createEventDispatcher } from "svelte";
    import NauiInput from "../naui/atoms/NauiInput.svelte";
    import NauiCheckboxGroups from "../naui/atoms/NauiCheckboxGroups.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";

    export let data;
    export let groups;
    let itemSetting = {
        nombre: 'nombre del grupo'
    };

    let open = false;
    let newRecord = false;
    let checker = false;

    const eventDispatcher = new createEventDispatcher();

    // Borra un item de la lista
    function deleteItem(index) {
        const del = confirm(`¿Desea eliminar el grupo de pacientes "${ data[index].nombre }"?`);
        if (del) {
            const id = data[index].id;
            data.splice(index, 1);
            data = data;
            eventDispatcher('delete', { id });
        }
    }

    function editItem(grupo) {
        open = true;
        itemSetting = Object.assign({}, grupo);
        const toEnable = [ ...grupo.servicios ];
        for (const g of groups) {
            g.value = false;
            g.children.forEach(c => c.value = false);
            for (const enable of toEnable) {
                const child = g.children.find(c => c.id === enable);
                if (child) {
                    child.value = true;
                    g.value = true;
                }
            }
        }
        groups = [ ...groups ];
        newRecord = false;
    }

    function newItem() {
        open = true;
        itemSetting = { nombre: 'Nuevo grupo', order: data.length };
        newRecord = true;
    }

    function handleGroupsUpdate(event) {
        itemSetting.servicios = [];
        for (const g of event.detail) {
            for (const c of g.children) {
                itemSetting.servicios.push(c.id);
            }
        }
    }

    function save() {
        if (newRecord) {
            eventDispatcher('create', itemSetting);
        } else {
            eventDispatcher('update', itemSetting);
        }
        open = false;
    }


</script>
<div>
    <table class="naui-table mb-1">
        <thead>
        <tr>
            <th>
                <div>Nombre</div>
            </th>
            <th>
                <div class="box">#Pacientes</div>
            </th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        {#each data as grupo, i}
            <tr>
                <td style="min-width: 250px;">
                    <div style="font-weight: 600">{grupo.nombre}</div>
                </td>
                <td style="min-width: 200px;">
                    <div style="font-weight: 600" class="box">{grupo.total}</div>
                </td>
                <td>
                    <div class="box sx-ii">
                        <NauiButton icon="edit" iconStyle="outlined" color="accent" on:click={editItem.bind(this, grupo)}/>
                        <NauiButton icon="delete" iconStyle="outlined" color="accent" on:click={deleteItem.bind(this, i)}/>
                    </div>
                </td>
            </tr>
        {/each}
        </tbody>
    </table>
    <NauiButton caption="AÑADIR GRUPO" color="accent" icon="add" iconStyle="outlined" size="small" on:click={newItem}/>
    <NauiSlideOver bind:open={open} title="Editar grupo">
        <div class="mb-1">
            <NauiInput class="w-100" type="text" label="Nombre del grupo" bind:value="{itemSetting.nombre}"/>
        </div>

        <NauiCheckboxGroups {groups} on:update={handleGroupsUpdate}/>

        <div slot="actions">
            <div class="max-w-300px mx-auto">
                <NauiButton className="w-100" caption="GUARDAR" color="accent" mode="stroked" on:click={save}/>
            </div>
        </div>
    </NauiSlideOver>

</div>
