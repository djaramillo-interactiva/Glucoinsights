<svelte:options accessors/>
<script>
    import NauiButton from "../../naui/atoms/NauiButton.svelte";
    import NauiSlideOver from "../../naui/layout/NauiSlideOver.svelte";
    import NauiSelect from "../../naui/atoms/NauiSelect.svelte";
    import NauiInput from "../../naui/atoms/NauiInput.svelte";
    import NauiDatePicker from "../../naui/atoms/NauiDatePicker.svelte";
    import { createEventDispatcher } from "svelte";

    const events = new createEventDispatcher();

    export let global = '';
    export let detalles = [];
    export let tiposMeta = [];

    let open = false;
    let metaEditable = nuevaMeta();

    export const upsertMeta = function(nMeta) {
        if (nMeta.id) {
            let index = detalles.findIndex(m => m.id === nMeta.id);
            if (index >= 0) {
                detalles[index] = nMeta;
                alert('El registro se actualizó correctamente');
            }
            else {
                detalles.push(nMeta);
                detalles = detalles;
                alert('El registro se creó correctamente');
            }
            location.reload();
        }
    }

    function nuevaMeta() {
        let now = new Date();
        let monthStr = now.getMonth() < 10 ? `0${now.getMonth() + 1}` : (now.getMonth() + 1);
        let dateStr = now.getDate() < 10 ? `0${now.getDate()}` : now.getDate();
        return {
            id: null,
            fecha_inicio: `${now.getFullYear()}-${monthStr}-${dateStr}`,
            fecha_limite: `${now.getFullYear()}-${monthStr}-${dateStr}`,
            tiempo: '',
            concepto: '',
            meta: 0,
            cumplimiento: '',
            unidad: ''
        };
    }

    function edit(meta) {
        metaEditable = meta;
        open = true;
    }

    function create() {
        metaEditable = nuevaMeta();
        open = true;
    }

    function submit() {
        events('metaAgregada', metaEditable);
        open = false;
    }

</script>
<div>
    <fieldset>
        <h2 class="mb-1">Metas del paciente</h2>
        <div class="box-b mb-1">
            <div class="kpi box-l">
                <div class="back-primary px-2 py-iii">
                    <h5 class="white">Cumplimiento global de metas</h5>
                </div>
                <div class="py-iii px-2 back-gray">
                    <h5>{global}</h5>
                </div>
            </div>
        </div>
        <div class="pt-ii pb-1">
            <table class="naui-table w-100 mb-1">
                <thead>
                <tr>
                    <th>
                        <div class="box">Fecha de inicio</div>
                    </th>
                    <th>
                        <div class="box">Fecha límite</div>
                    </th>
                    <th>
                        <div class="box">Tiempo</div>
                    </th>
                    <th>
                        <div>Concepto</div>
                    </th>
                    <th>
                        <div class="box">Meta</div>
                    </th>
                    <th>
                        <div class="box">Cumplimiento</div>
                    </th>
                    <th></th>
                </tr>
                </thead>
                <tbody>
                {#each detalles as meta, i (meta.id)}
                    <tr>
                        <td>
                            <div class="box">{meta.fecha_inicio}</div>
                        </td>
                        <td>
                            <div class="box">{meta.fecha_limite}</div>
                        </td>
                        <td>
                            <div class="box">{meta.tiempo}</div>
                        </td>
                        <td>
                            <div>{meta.concepto}</div>
                        </td>
                        <td>
                            <div class="box">{meta.meta} {meta.unidad}</div>
                        </td>
                        <td>
                            <div class="box">{meta.cumplimiento}</div>
                        </td>
                        <td>
                            <div class="box">
                                <NauiButton icon="pencil" color="accent" on:click={edit.bind(this, meta)}/>
                            </div>
                        </td>
                    </tr>
                {:else}
                    <tr>
                        <td colspan="7">
                            <div>
                                <h2>No se encontraron metas</h2>
                            </div>
                        </td>
                    </tr>
                {/each}
                </tbody>
            </table>

            <NauiButton caption="AGREGAR META" icon="add" color="accent"  size="small" on:click={create}/>
        </div>
    </fieldset>
    <NauiSlideOver title="Agregar meta" bind:open={open}>
        <div class="sy-1">
            <NauiSelect bind:value={metaEditable.concepto} label="Tipo de meta" options={tiposMeta} />
            <NauiInput bind:value={metaEditable.meta} type="number" label="Meta" />
            <NauiDatePicker bind:value={metaEditable.fecha_inicio} label="Fecha inicio"/>
            <NauiDatePicker bind:value={metaEditable.fecha_limite} label="Fecha límite"/>
        </div>
        <div slot="actions">
            <div class="max-w-300px mx-auto">
                <NauiButton on:click={submit} caption="GUARDAR" mode="stroked" color="accent" className="w-100"/>
            </div>
        </div>
    </NauiSlideOver>
</div>
<style>

</style>
