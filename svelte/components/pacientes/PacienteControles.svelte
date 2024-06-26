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
    import NauiInput from "../naui/atoms/NauiInput.svelte";

    const events = new createEventDispatcher();

    export let filters;
    export let data = [];
    export let filteredData = [];
    export let tiposControles = [];

    let open = false;
    let controlEditable = nuevoControl();
    let filtersComponent;

    onMount(() => {
        filteredData = data;
    });

    export const upsertControl = function (nControl) {
        if (nControl.id) {
            let index = data.findIndex(c => c.id === nControl.id);
            if (index >= 0) {
                data[index] = nControl;
                alert('El registro se actualizó correctamente');
            } else {
                data.push(nControl);
                data = data;
                alert('El registro se creó correctamente');
            }
            filtersComponent.runFilters();
        }
    }

    function nuevoControl() {
        let now = new Date();
        let monthStr = now.getMonth() < 10 ? `0${now.getMonth() + 1}` : (now.getMonth() + 1);
        let dateStr = now.getDate() < 10 ? `0${now.getDate()}` : now.getDate();
        return {
            id: null,
            tipo: '',
            tas: null,
            tad: null,
            peso: null,
            glucometria: null,
            numero_eventos_hipoglicemia: 0,
            fecha: `${now.getFullYear()}-${monthStr}-${dateStr}`,
            observaciones: '',
            soporte: false
        };
    }

    function create() {
        controlEditable = nuevoControl();
        open = true;
    }

    function edit(control) {
        controlEditable = control;
        open = true;
    }

    function save() {
        events('guardarControl', controlEditable);
        controlEditable = nuevoControl();
        open = false;
    }

    function checkGlucometria() {
        console.log()
        if (!controlEditable.glucometria) {
            controlEditable.glucometria = null;
        } else if (controlEditable.glucometria < 10) {
            controlEditable.glucometria = 10;
        } else if (controlEditable.glucometria > 400) {
            controlEditable.glucometria = 400;
        }
        controlEditable = controlEditable;
    }

    function filter(event) {
        let filterObj = event.detail;
        let limitesPeriodo = getLimitesPeriodo(filterObj.periodo);
        filteredData = data.filter(c => {
            let response = true;
            if (response && filterObj.tipo_control !== undefined) {
                response = response && c.tipo === filterObj.tipo_control;
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
            return response
        });
    }

</script>
<div class="py-15">
    <div class="box-b">
        <NauiFilters bind:this={filtersComponent} {filters} on:filtered={filter}/>
        <NauiButton caption="AGREGAR CONTROL" icon="add" mode="stroked" color="accent" size="small" on:click={create}/>
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
                <th>
                    <div class="box">Presión arterial</div>
                </th>
                <th>
                    <div class="box">Peso</div>
                </th>
                <th>
                    <div class="box">Glucometría</div>
                </th>
                <th>
                    <div class="box">Número de eventos de hipoglicemia <br/> desde el último control</div>
                </th>
                <th class="text-c">
                    <div>Observaciones</div>
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
            {#each filteredData as control, i (control.id)}
                <tr>
                    <td>
                        <div>{control.tipo}</div>
                    </td>
                    <td>
                        <div class="box">{control.fecha}</div>
                    </td>
                    <td>
                        <div class="box">
                            {#if control.tas && control.tad}
                                {control.tas} / {control.tad}
                            {:else}
                                N/A
                            {/if}
                        </div>
                    </td>
                    <td>
                        <div class="box">
                            {control.peso ? control.peso : 'N/A'}
                        </div>
                    </td>
                    <td>
                        <div class="box">
                            {control.glucometria ? control.glucometria : 'N/A'}
                        </div>
                    </td>
                    <td>
                        <div>{control.numero_eventos_hipoglicemia}</div>
                    </td>
                    <td>
                        <div>{control.observaciones}</div>
                    </td>
                    <td>
                        <div class="box">
                            {#if control.soporte}
                                <i class="material-icons">check</i>
                            {:else}
                                <i class="material-icons">clear</i>
                            {/if}
                        </div>
                    </td>
                    <td>
                        <div class="box">
                            <NauiButton icon="chevron_right" color="accent" on:click={edit.bind(this, control)}/>
                        </div>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="9">
                        <div>
                            <h2>No se encontraron controles</h2>
                        </div>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
    <NauiSlideOver title="Agregar control" bind:open={open}>
        <div class="mb-1">
            <NauiSelect bind:value={controlEditable.tipo} label="Tipo de control" options="{tiposControles}" />
        </div>
        <div class="mb-1">
            <NauiDatePicker bind:value={controlEditable.fecha} label="Fecha"/>
        </div>
        <div class="mb-1">
            <div class="grid-2 gap-1">
                <NauiInput bind:value={controlEditable.tas} type="number" label="PAS"/>
                <NauiInput bind:value={controlEditable.tad} type="number" label="PAD"/>
            </div>
        </div>
        <div class="mb-1">
            <NauiInput bind:value={controlEditable.peso} type="number" label="Peso"/>
        </div>
        <div class="mb-1">
            <NauiInput bind:value={controlEditable.glucometria} on:change={checkGlucometria}
                       step="10"
                       type="number"
                       label="Glucometría (mg/dl)"/>
        </div>
        <div class="mb-1">
            <NauiInput bind:value={controlEditable.numero_eventos_hipoglicemia}
                       type="number"
                       label="Número de eventos de hipoglicemia desde el último control"/>
        </div>
        <div class="box-l sx-1 mb-1">
            <p>¿Tiene soporte?</p>
            <NauiSwitch bind:active={controlEditable.soporte}/>
        </div>
        <NauiTextarea label="Observaciones" bind:value={controlEditable.observaciones} />
        <div slot="actions">
            <div class="max-w-300px mx-auto">
                <NauiButton on:click={save} caption="GUARDAR" mode="stroked" color="accent" className="w-100" />
            </div>
        </div>
    </NauiSlideOver>
</div>
