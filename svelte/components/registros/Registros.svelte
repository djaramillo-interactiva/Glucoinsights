<svelte:options accessors/>
<script>
    import {createEventDispatcher} from "svelte";
    import NauiExplorer from "../naui/pages/NauiExplorer.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import NauiSlideOver from "../naui/layout/NauiSlideOver.svelte";
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";
    import NauiTextarea from "../naui/atoms/NauiTextarea.svelte";
    import NauiTable from "../naui/components/NauiTable.svelte";
    import NauiLoading from "../naui/components/NauiLoading.svelte";

    let dispatch = createEventDispatcher();
    let isLoading = false;

    export let months = [];
    export let years = [];

    export let data = [];
    export let filters = [
        {
            label: 'Periodo',
            slug: 'month',
            options: months
        },
        {
            label: 'Año',
            slug: 'year',
            options: years
        }
    ]
    export let columns = [];
    export let selected = false;
    export let templateUrl = '';

    let newRegister = {
        year: null,
        month: null,
        observations: '',
        file: null
    };

    // Overlay
    let file = null;
    let form = null;
    let openCreate = false;
    let fileUploadColumns = [
        {
            slug: 'filename',
            label: 'Archivo',
            class: '',
            type: 'text',
            order: false
        },
        {
            slug: 'upload',
            label: '',
            class: '',
            boxClass: 'box-r w-100 sx-1 pr-1',
            type: 'actions',
            order: false
        },
    ]
    let fileUploadData = [
        {
            filename: ' - ',
            upload: [
                {
                    icon: 'upload',
                    iconStyle: 'outlined',
                    slug: 'upload'
                },
                {
                    icon: 'delete',
                    iconStyle: 'outlined',
                    slug: 'delete'
                }
            ]
        }
    ]

    function hasChecked() {
        selected = data.some(d => d.selected);
    }

    function handleAction(ev) {
        if (ev.detail.action === 'upload') {
            file.click();
        } else if (ev.detail.action === 'delete') {
            file.value = null;
            handleFile(null);
        }
    }

    function handleFile(ev) {
        newRegister.file = ev ? ev.target.files[0] : null;
        fileUploadData[0].filename = newRegister.file ? newRegister.file.name : ' - ';
    }

    function deleteRegisters() {
        const toDelete = data.filter(d => d.selected).map(d => d.id);
        dispatch('delete', {'data': toDelete});
    }

    function validateForm() {
        if (form.reportValidity()) {
            dispatch('save', newRegister);
        }
        isLoading = true;
    }
</script>
<div class="pt-i">
    <NauiLoading isVisible= {isLoading} />
    <NauiExplorer {columns}
                  {data}
                  {filters}
                  grid="2"
                  hideSearch={true}
                  on:filter
                  on:input
                  on:next
                  paginate={true}
                  on:checked={hasChecked}>
        <div slot="table-actions">
            <div class="box-l sx-ii">
                {#if selected}
                    <NauiButton caption="ELIMINAR"
                                color="accent"
                                mode="stroked"
                                size="small"
                                on:click={deleteRegisters}/>
                {/if}
                <NauiButton size="small" on:click={() => {openCreate = true;}} caption="CREAR REGISTRO" color="solid" mode="accent"
                            icon="add"/>
                <NauiButton size="small" download href={`https://glucoinsight.interactiva.net.co/${templateUrl}`} caption="DESCARGAR PLANTILLA" mode="stroked" target="_blank"/>
            </div>
        </div>
    </NauiExplorer>
</div>
<NauiSlideOver bind:open={openCreate} title="Crear nuevo registro">
    <form bind:this={form}>
        <div class="mb-1">
            <NauiSelect bind:value={newRegister.month} label="Periodo" options="{months}" required={true}/>
        </div>
        <div class="mb-1">
            <NauiSelect bind:value={newRegister.year} label="Año" options="{years}" required/>
        </div>

        <div class="mb-1">
            <NauiTextarea label="Observaciones" bind:value={newRegister.observations}/>
        </div>

        <div class="relative">
            <NauiTable columns={fileUploadColumns} bind:data={fileUploadData} on:action={handleAction}/>
            <input type="file" bind:this={file}
                   style="width: 1px; height: 1px; opacity: 0; position: absolute; z-index: -99; top: 20px; right: 80px;"
                   on:change={handleFile} required>
        </div>
    </form>

    <div slot="actions">
        <div class="max-w-300px mx-auto">
            <NauiButton on:click={validateForm} caption="GUARDAR" mode="outline" color="accent" className="w-100"/>
        </div>
    </div>
</NauiSlideOver>