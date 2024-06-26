<svelte:options accessors/>
<script>
    import NauiInput from "../naui/atoms/NauiInput.svelte";
    import NauiState from "../naui/atoms/NauiState.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import { createEventDispatcher } from "svelte";

    const events = new createEventDispatcher();

    export let grupos = [];
    export let medicamentos = [];
    export let medicamentosOptions = [];

    function eliminarMedicacion(indexMedicacion) {
        medicamentos.splice(indexMedicacion, 1);
        medicamentos = medicamentos;
    }

    function agregarMedicacion() {
        let now = new Date();
        let monthStr = now.getMonth() < 10 ? `0${now.getMonth() + 1}` : (now.getMonth() + 1);
        let dateStr = now.getDate() < 10 ? `0${now.getDate()}` : now.getDate();
        let newMedicamento = {
            medicamento: "",
            dosis: 0,
            fecha_formulacion: `${now.getFullYear()}-${monthStr}-${dateStr}`,
            tiempo_formulacion: 0
        };
        medicamentos = [...medicamentos, newMedicamento]
    }

    function submit() {
        events('submit', medicamentos);
    }
</script>
<div>
    <fieldset>
        <legend>Grupos asignados</legend>
        {#each grupos as grupo (grupo.id)}
            <fieldset>
                <div class="max-w-300px">
                    <NauiInput type="text" label="Nombre del grupo" value={grupo.nombre} isDisabled={true}/>
                </div>
            </fieldset>
            {#each grupo.tareas as tarea (tarea.id)}
                <fieldset>
                    <legend>{tarea.nombre}</legend>
                    <table class="naui-table">
                        <thead>
                        <tr>
                            <th class="min-w-200px">
                                <div>Concepto</div>
                            </th>
                            <th>
                                <div class="box">Realizados</div>
                            </th>
                            <th>
                                <div class="box">Recomendados por periodo</div>
                            </th>
                            <th>
                                <div class="box">Estado</div>
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        {#each tarea.data as item (item.id)}
                            <tr>
                                <td>
                                    <div>{item.concepto}</div>
                                </td>
                                <td>
                                    <div class="box">{item.realizados}</div>
                                </td>
                                <td>
                                    <div class="box">{item.recomendados}</div>
                                </td>
                                <td>
                                    <div class="box">
                                        <NauiState {...item.estado}/>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                        </tbody>
                    </table>
                </fieldset>
            {/each}
            {:else}
            <h3>Paciente no tiene grupos asignados</h3>
        {/each}
    </fieldset>
    <fieldset>
        <legend>Medicación</legend>
        <table class="naui-table mb-1 min-w-700px">
            <thead>
            <tr>
                <th class="min-w-300px">
                    <div>Medicamento</div>
                </th>
                <th>
                    <div>Dosis (mg)</div>
                </th>
                <th>
                    <div>Fecha formulación</div>
                </th>
                <th>
                    <div>Tiempo formulación (meses)</div>
                </th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            {#each medicamentos as med, i}
                <tr>
                    <td>
                        <div>
                            <select class="naui-input min-w-300px" bind:value={med.medicamento}>
                                <option value="" hidden>Medicamento</option>
                                {#each medicamentosOptions as group}
                                    {#if group.options.length > 0}
                                        <optgroup label="{group.name}">
                                            {#each group.options as option}
                                                <option value="{option.slug}">{option.label}</option>
                                            {/each}
                                        </optgroup>
                                    {/if}
                                {/each}
                            </select>
                        </div>
                    </td>
                    <td>
                        <div>
                            <input class="naui-input" bind:value={med.dosis} type="number"/>
                        </div>
                    </td>
                    <td>
                        <div>
                            <input type="date" bind:value={med.fecha_formulacion} class="naui-input"/>
                        </div>
                    </td>
                    <td>
                        <div>
                            <input class="naui-input" bind:value={med.tiempo_formulacion} type="number"/>
                        </div>
                    </td>
                    <td>
                        <div>
                            <NauiButton on:click={eliminarMedicacion.bind(this, i)} icon="clear" size="small" iconStyle="outlined" color="accent"/>
                        </div>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
        <NauiButton on:click={agregarMedicacion} caption="AÑADIR MEDICAMENTO" size="small" icon="add" color="accent"/>
    </fieldset>
    <NauiFloatingAction>
        <NauiButton on:click={submit} caption="GUARDAR"  iconStyle="outlined" icon="save" color="accent" mode="solid"/>
    </NauiFloatingAction>
</div>
<style>

</style>
