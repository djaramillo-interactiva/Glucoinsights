<script>
    import NauiFilters from "../naui/components/NauiFilters.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import NauiSlideOver from "../naui/layout/NauiSlideOver.svelte";
    import NauiInput from "../naui/atoms/NauiInput.svelte";
    import NauiSelect from "../naui/atoms/NauiSelect.svelte";
    import {createEventDispatcher, onMount} from "svelte";
    import {getLimitesPeriodo} from "../utils";
    import NauiDatePicker from "../naui/atoms/NauiDatePicker.svelte";

    const events = new createEventDispatcher();

    export let data = [];
    export let filteredData = [];
    export let filters;

    let open = false;
    let examenEditable = nuevoExamen();
    let filtersComponent;

    onMount(() => {
        filteredData = data;
    });

    export const upsertExamen = function (nExamen) {
        if (nExamen.id) {
            let index = data.findIndex(c => c.id === nExamen.id);
            if (index >= 0) {
                data[index] = nExamen;
                alert('El registro se actualizó correctamente');
            } else {
                data.push(nExamen);
                data = data;
                alert('El registro se creó correctamente');
            }
            filtersComponent.runFilters();
        }
    }

    function nuevoExamen() {
        let now = new Date();
        let monthStr = now.getMonth() < 10 ? `0${now.getMonth() + 1}` : (now.getMonth() + 1);
        let dateStr = now.getDate() < 10 ? `0${now.getDate()}` : now.getDate();
        return {
            id: null,
            alat: 0,
            asat: 0,
            creatinina: 0,
            fecha: `${now.getFullYear()}-${monthStr}-${dateStr}`,
            glicemia: 0,
            micro: 0,
            hdl: 0,
            ldl: 0,
            ct: 0,
            tsh: 0,
            hemoglobina_glicosilada: 0
        };
    }

    function create() {
        examenEditable = nuevoExamen();
        open = true;
    }

    function edit(examen) {
        examenEditable = examen;
        open = true;
    }

    function save() {
        events('guardarExamen', examenEditable);
        examenEditable = nuevoExamen();
        open = false;
    }

    function filter(event) {
        let filterObj = event.detail;
        let limitesPeriodo = getLimitesPeriodo(filterObj.periodo);
        filteredData = data.filter(e => {
            let response = true;
            if (response && filterObj.periodo !== undefined && limitesPeriodo) {
                try {
                    let dateObj = new Date(e.fecha)
                    response = response && dateObj >= limitesPeriodo.li && dateObj <= limitesPeriodo.ls;
                } catch (e) {
                    console.error(e);
                }
            }
            return response
        })
    }

</script>

<div class="py-15">
    <div class="box-b">
        <NauiFilters bind:this={filtersComponent} {filters} on:filtered={filter}/>
        <NauiButton caption="AGREGAR REGISTRO" icon="add" mode="stroked" color="accent" size="small" on:click={create}/>
    </div>
    <div class="py-15">
        <table class="naui-table w-100">
            <thead>
            <tr>
                <th>
                    <div>Fecha</div>
                </th>
                <th>
                    <div class="box py-ii">TSH<br>(µU/mL)</div>
                </th>
                <th>
                    <div class="box py-ii">ALAT<br>(U/L)</div>
                </th>
                <th>
                    <div class="box py-ii">Glicemia<br>basal(mg/dl)</div>
                </th>
                <th>
                    <div class="box py-ii">ASAT<br>(U/L)</div>
                </th>
                <th>
                    <div class="box py-ii">Albuminuria<br>en 24h (mg)</div>
                </th>
                <th>
                    <div class="box py-ii">Creatinina<br>sérica (mg/dl)</div>
                </th>
                <th>
                    <div class="box py-ii">HDL</div>
                </th>
                <th>
                    <div class="box py-ii">LDL</div>
                </th>
                <th>
                    <div class="box py-ii">CT</div>
                </th>
                <th>
                    <div class="box py-ii">HbA1c</div>
                </th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            {#each filteredData as examen, i (examen.id)}
                <tr>
                    <td>
                        <div class="box">{examen.fecha}</div>
                    </td>
                    <td>
                        <div class="box">{examen.tsh}</div>
                    </td>
                    <td>
                        <div class="box">{examen.alat}</div>
                    </td>
                    <td>
                        <div class="box">{examen.glicemia}</div>
                    </td>
                    <td>
                        <div class="box">{examen.asat}</div>
                    </td>
                    <td>
                        <div class="box">{examen.micro}</div>
                    </td>
                    <td>
                        <div class="box">{examen.creatinina}</div>
                    </td>
                    <td>
                        <div class="box">{examen.hdl}</div>
                    </td>
                    <td>
                        <div class="box">{examen.ldl}</div>
                    </td>
                    <td>
                        <div class="box">{examen.ct}</div>
                    </td>
                    <td>
                        <div class="box">{examen.hemoglobina_glicosilada}</div>
                    </td>
                    <td>
                        <div class="box">
                            <NauiButton icon="chevron_right" color="accent" on:click={edit.bind(this, examen)}/>
                        </div>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="12">
                        <div>
                            <h2>No se encontraron exámenes</h2>
                        </div>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
    <NauiSlideOver title="Agregar registro" bind:open={open}>
        <div class="sy-1">
            <NauiDatePicker bind:value={examenEditable.fecha} label="Fecha"/>
            <NauiInput bind:value={examenEditable.tsh} label="TSH" type="number" />
            <NauiInput bind:value={examenEditable.alat} label="ALAT" type="number" />
            <NauiInput bind:value={examenEditable.glicemia} label="Glicemia basal" type="number" />
            <NauiInput bind:value={examenEditable.asat} label="ASAT" type="number" />
            <NauiInput bind:value={examenEditable.micro} label="Microalbuminura 24h" type="number" />
            <NauiInput bind:value={examenEditable.creatinina} label="Creatinina Seric." type="number" />
            <div class="grid-3 gap-1">
                <NauiInput bind:value={examenEditable.hdl} label="HDL" type="number" />
                <NauiInput bind:value={examenEditable.ldl} label="LDL" type="number" />
                <NauiInput bind:value={examenEditable.ct} label="CT" type="number" />
            </div>
            <NauiInput bind:value={examenEditable.hemoglobina_glicosilada} label="HbA1c" type="number" />
        </div>
        <div slot="actions">
            <div class="max-w-300px mx-auto">
                <NauiButton on:click={save} caption="GUARDAR" color="accent" mode="stroked" className="w-100" />
            </div>
        </div>

    </NauiSlideOver>
</div>
