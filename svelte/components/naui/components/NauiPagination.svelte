<svelte:options accessors/>
<script>
    /*
    IPagination {
        total: number;
        page: number;
    }
    data: IPagination
    */
    import {createEventDispatcher} from "svelte";

    export let data;
    const dispatch = createEventDispatcher();
    let first = 1;
    let items = [1, 2, 3, 4, 5];

    function getFirst() {
        if (data.page <= 3 || data.total <= 5) {
            first = 1;
        } else {
            first = data.page - 2
            if ((data.total - first) < 5) {
                first = data.total - 4;
            }
        }
        dispatch('next', data.page);
    }

    function nextPage() {
        if (data.page < data.total) {
            data.page++;
        }
        getFirst();
    }

    function prevPage() {
        if (data.page > 1) {
            data.page--;
        }
        getFirst();
    }

    function goToPage(index) {
        data.page = index;
        getFirst();
    }
</script>
<div>
    <div class="box-l pagination-wrap shadow">
        {#if data?.total > 1}
            <div class="pagination">
                <div class="currentPage">
                    Página {data.page} / {data.total}
                </div>
                {#if data.total > 5}
                    <div class="pag-item word box-c" on:click={goToPage.bind(this, 1)}>
                        <span>Primero</span>
                    </div>
                {/if}
                {#if data.total > 1 }
                    <div class="prev pag-item box-c" on:click={prevPage}>
                        <span style="font-size: 18px" class="material-icons-outlined">navigate_before</span>
                    </div>
                {/if}
                {#each items as item, i}
                    {#if ((first + i) <= data.total)}
                        <div class:active="{data.page === first + i}"
                             class="pag-item box-c"
                             on:click={goToPage.bind(first, first + i)}>
                            <span>{first + i}</span>
                        </div>
                    {/if}
                {/each}
                {#if data.total > 1}
                    <div class="next pag-item box-c" on:click={nextPage}>
                        <span style="font-size: 18px" class="material-icons-outlined">navigate_next</span>
                    </div>
                {/if}

                {#if data.total > 5}
                    <div class="pag-item word box-c"
                         on:click={goToPage.bind(this, data.total)}>
                        <span>Último</span>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>
<style>
    .pagination-wrap {
        position: fixed;
        bottom: 0;
        background: white;
        padding: 1rem;
    }


    .currentPage {
        background-color: #f4f5f6;
        color: #555;
        font-size: .9rem;
        padding: .6rem 1rem;
        border-radius: 7px;
        margin-right: 1rem;
    }

    .pagination {
        display: flex;
    }

    .pag-item {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        border: 1px solid #ddd;
        text-align: center;
        font-size: .9rem;
        margin-right: .25rem;
        color: #333;
        cursor: pointer;
    }

    .pag-item:hover {
        background-color: #f4f5f6;
    }

    .pag-item:active {
        background-color: #e7e8e9;
    }

    .pag-item.active {
        background-color: #3498db;
        border-color: #3498db;
        color: #fff;
    }

    .pag-item.active span {
        color: white;
    }

    .pag-item.prev, .pag-item.next {
        line-height: 30px;
    }

    /* First - last */
    .pag-item.word {
        width: max-content;
        border-radius: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        font-size: .85rem;
    }

    .pagination-wrap {
        padding-top: .75rem;
        border-radius: 1rem 1rem 0 0;
    }
</style>
