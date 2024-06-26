<script>
    import NauiFilters from "../naui/components/NauiFilters.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import NauiSlideOver from "../naui/layout/NauiSlideOver.svelte";
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";
    import NauiSwitch from "../naui/atoms/NauiSwitch.svelte";
    import NauiTextarea from "../naui/atoms/NauiTextarea.svelte";
    import {createEventDispatcher, onMount} from "svelte";
    import {getLimitesPeriodo} from "../utils";
    import NauiDatePicker from "../naui/atoms/NauiDatePicker.svelte";

    const events = new createEventDispatcher();

    export let filters;
    export let data = [];
    export let filteredData = [];
    export let tiposHospitalizaciones = [];
    export let diagnosticos = [];

    let open = false;
    let hospitalizacionEditable = nuevaHospitalizacion();
    let filtersComponent;

    onMount(() => {
        filteredData = data;
    });

    export const upsertHospitalizacion = function (nHospitalizacion) {
        if (nHospitalizacion.id) {
            let index = data.findIndex(c => c.id === nHospitalizacion.id);
            if (index >= 0) {
                data[index] = nHospitalizacion;
                alert('El registro se actualizó correctamente');
            } else {
                data.push(nHospitalizacion);
                data = data;
                alert('El registro se creó correctamente');
            }
            filtersComponent.runFilters();
        }
    }

    function nuevaHospitalizacion() {
        let now = new Date();
        let monthStr = now.getMonth() < 10 ? `0${now.getMonth() + 1}` : (now.getMonth() + 1);
        let dateStr = now.getDate() < 10 ? `0${now.getDate()}` : now.getDate();
        return {
            id: null,
            tipo: '',
            era_evitable: false,
            relacionado_con_diabetes: false,
            fecha: `${now.getFullYear()}-${monthStr}-${dateStr}`,
            observaciones: '',
            soporte: false
        };
    }

    function create() {
        hospitalizacionEditable = nuevaHospitalizacion();
        open = true;
    }

    function edit(hospitalizacion) {
        hospitalizacionEditable = hospitalizacion;
        open = true;
    }

    function save() {
        events('guardarHospitalizacion', hospitalizacionEditable);
        hospitalizacionEditable = nuevaHospitalizacion();
        open = false;
    }

    function filter(event) {
        let filterObj = event.detail;
        let limitesPeriodo = getLimitesPeriodo(filterObj.periodo);
        filteredData = data.filter(c => {
            let response = true;
            if (response && filterObj.tipo_hospitalizacion !== undefined) {
                response = response && c.tipo === filterObj.tipo_hospitalizacion;
            }
            if (response && filterObj.periodo !== undefined && limitesPeriodo) {
                try {
                    let dateObj = new Date(c.fecha)
                    response = response && dateObj >= limitesPeriodo.li && dateObj <= limitesPeriodo.ls;
                } catch (e) {
                    console.error(e);
                }
            }
            if (response && filterObj.tiene_soporte !== undefined) {
                response = response && c.soporte === filterObj.tiene_soporte;
            }
            if (response && filterObj.era_evitable !== undefined) {
                response = response && c.era_evitable === filterObj.era_evitable;
            }
            if (response && filterObj.relacionado_con_diabetes !== undefined) {
                response = response && c.relacionado_con_diabetes === filterObj.relacionado_con_diabetes;
            }
            return response
        });
    }

</script>
<div class="py-15">
    <div class="box-b">
        <NauiFilters bind:this={filtersComponent} {filters} on:filtered={filter}/>
        <NauiButton caption="AGREGAR HOSPITALIZACION" icon="add" mode="stroked" color="accent" size="small" on:click={create}/>
    </div>
    <div class="py-15">
        <table class="naui-table w-100">
            <thead>
            <tr>
                <th style="width: 200px">
                    <div>Tipo</div>
                </th>
                <th style="width:150px;">
                    <div class="box">Fecha</div>
                </th>
                <th class="text-c">
                    <div>Observaciones</div>
                </th>
                <th>
                    <div class="box">¿Era evitable?</div>
                </th>
                <th>
                    <div class="box">¿Relacionado con diabetes?</div>
                </th>
                <th>
                    <div class="box">Soporte</div>
                </th>
                <th>
                    <div class="box">Editar</div>
                </th>
            </tr>
            </thead>
            <tbody>
            {#each filteredData as hospitalizacion, i (hospitalizacion.id)}
                <tr>
                    <td>
                        <div>{hospitalizacion.tipo}</div>
                    </td>
                    <td>
                        <div class="box">{hospitalizacion.fecha}</div>
                    </td>
                    <td>
                        <div>{hospitalizacion.observaciones}</div>
                    </td>
                    <td>
                        <div class="box">
                            {#if hospitalizacion.era_evitable}
                                <i class="material-icons">check</i>
                            {:else}
                                <i class="material-icons">clear</i>
                            {/if}
                        </div>
                    </td>
                    <td>
                        <div class="box">
                            {#if hospitalizacion.relacionado_con_diabetes}
                                <i class="material-icons">check</i>
                            {:else}
                                <i class="material-icons">clear</i>
                            {/if}
                        </div>
                    </td>
                    <td>
                        <div class="box">
                            {#if hospitalizacion.soporte}
                                <i class="material-icons">check</i>
                            {:else}
                                <i class="material-icons">clear</i>
                            {/if}
                        </div>
                    </td>
                    <td>
                        <div class="box">
                            <NauiButton icon="chevron_right" color="accent" on:click={edit.bind(this, hospitalizacion)}/>
                        </div>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="7">
                        <div>
                            <h2>No se encontraron hospitalizaciones</h2>
                        </div>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
    <NauiSlideOver title="Agregar hospitalizacion" bind:open={open}>
        <div class="mb-1">
            <NauiSelect bind:value={hospitalizacionEditable.tipo} label="Tipo de hospitalización" options="{tiposHospitalizaciones}" />
        </div>
        <div class="mb-1">
            <NauiDatePicker bind:value={hospitalizacionEditable.fecha} label="Fecha"/>
        </div>
        <div class="mb-1">
            <NauiSelect bind:value={hospitalizacionEditable.diagnostico} label="Diagnóstico CIE 10" options="{diagnosticos}" showValue="{true}"/>
        </div>
        <div class="box-l sx-1 mb-1">
            <p>¿Era evitable?</p>
            <NauiSwitch bind:active={hospitalizacionEditable.era_evitable} />
        </div>
        <div class="box-l sx-1 mb-1">
            <p>¿Relacionado con diabetes?</p>
            <NauiSwitch bind:active={hospitalizacionEditable.relacionado_con_diabetes} />
        </div>
        <div class="box-l sx-1 mb-1">
            <p>¿Tiene soporte?</p>
            <NauiSwitch bind:active={hospitalizacionEditable.soporte} />
        </div>
        <NauiTextarea label="Observaciones" bind:value={hospitalizacionEditable.observaciones} />
        <div slot="actions">
            <div class="max-w-300px mx-auto">
                <NauiButton on:click={save} caption="GUARDAR" mode="stroked" color="accent" className="w-100" />
            </div>
        </div>
    </NauiSlideOver>
</div>
