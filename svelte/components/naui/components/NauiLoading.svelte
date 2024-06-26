<script>
    export let isVisible = false;
</script>
  
{#if isVisible}
    <div class="loading">
        <h2 class="h2-loading">Cargando</h2>
        <img src="https://glucoinsight.interactiva.net.co/media/load.gif" alt="gif carga data" width="150px">
    </div>
{/if}
  
<style>
    .loading {
        width: 100%;
        height: 100vh;
        position: absolute;
        background-color: #fff;
        z-index: 100;
        top: 0;
        left: 0;
        opacity: 0.6;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .h2-loading {
        font-size: 1em;
        font-weight: 600;
        margin: 0;
    }
</style>