<svelte:options accessors/>
<script>
    import NauiFloatingAction from "../naui/components/NauiFloatingAction.svelte";
    import NauiButton from "../naui/atoms/NauiButton.svelte";

    export let data;
    export let submit = () => {
    };

    export function getPostData() {
        const postData = [];
        for (const tipo of data) {
            for (const indicador of tipo.indicadores) {
                postData.push(indicador);
            }
        }
        return postData;
    }

    function toggle() {
        this.classList.toggle('open');
    }
</script>
<div class="max-w-800px">
    {#each data as block, i}
        <div on:click={toggle} class="panel-bar box-b py-iii px-ii border-bottom pointer" class:open={i===0}>
            <h2>{block.title}</h2>
            <div class="pt-i">
                <span class="material-icons-outlined">expand_more</span>
            </div>
        </div>
        <div class="mb-1 panel-area py-15 px-ii">
            <table class="naui-table">
                <thead>
                <tr>
                    <th style="min-width: 200px">
                        <div>Indicador</div>
                    </th>
                    <th>
                        <div>Descripción</div>
                    </th>
                    <th>
                        <div>Meta</div>
                    </th>
                </tr>
                </thead>
                <tbody>
                {#each block.indicadores as ind}

                    <tr>
                        <td>
                            <div class="py-1"><strong>{ind.nombre}</strong></div>
                        </td>
                        <td>
                            <div class="py-1"><p>{ind.descripcion}</p></div>
                        </td>
                        <td>
                            <div class="py-1"><input class="naui-input" style="max-width: 100px" type="number" bind:value={ind.meta}></div>
                        </td>
                    </tr>
                {/each}
                </tbody>
            </table>
        </div>
    {/each}
</div>
<NauiFloatingAction>
    <NauiButton caption="GUARDAR" icon="save" iconStyle="outlined" color="accent" mode="solid" on:click={submit} />
</NauiFloatingAction>

<style>
    .panel-bar + .panel-area{
        display: none;
    }

    .panel-bar.open + .panel-area{
        display: block;
    }

    .panel-bar.open .material-icons-outlined{
        transform: rotate(180deg);
    }
</style>
