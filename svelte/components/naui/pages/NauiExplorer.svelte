<svelte:options accessors/>
<script>
    import NauiTable from "../components/NauiTable.svelte";
    import NauiFilters from "../components/NauiFilters.svelte";
    import NauiPagination from "../components/NauiPagination.svelte";
    import {createEventDispatcher} from "svelte";

    export let count = 0;
    export let pages = 0;
    export let searchLabel = 'Buscar por palabra clave';
    export let countLabel = 'registros';
    export let filters = [];
    export let hideSearch = false;
    export let columns;
    export let data;
    export let paginate = false;
    export let paginator = {
        total: pages,
        page: 1
    }
    export let grid;

    const dispatch = createEventDispatcher();

    let filtersCmpt;
    let table;
    let edit = false
    let searchVal = ''
    let term;
    let selectedFilters = {};
    let timer;
    let ordering = {};

    const debounce = v => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            term = v;
            emitFilters();
        }, 300);
    }

    // console.log(filters)

    const newTFG = filters.find(name => name.slug === 'riesgo_tfg');
    console.log(newTFG);

    if(newTFG){
        filters[3].options = filters[3].options.map(option => {
            if (option.value === '0') {
                return { label: 'Sin calcular', value: '0' };
            }else if(option.value === '1'){
                return { label: 'Estadio 1', value: '1' };
            }else if(option.value === '2'){
                return { label: 'Estadio 2', value: '2' };
            }else if(option.value === '3a'){
                return { label: 'Estadio 3a', value: '3a' };
            }else if(option.value === '3b'){
                return { label: 'Estadio 3b', value: '3b' };
            }else if(option.value === '4'){
                return { label: 'Estadio 4', value: '4' };
            }else if(option.value === '5'){
                return { label: 'Estadio 5', value: '5' };
            }
            
            else {
                return option;
            }
        });
    }

    function handleFilter(evt) {
        selectedFilters = JSON.parse(JSON.stringify(evt.detail));
        if (Object.keys(selectedFilters).length === 0) {
            searchVal = '';
            term = ''
        }
        emitFilters();
    }

    function handleOrder(evt) {
        ordering = evt.detail;
        emitFilters();
    }

    function emitFilters() {
        paginator.page = 1;
        dispatch('filter', {
            term,
            filters: selectedFilters,
            ordering
        });
    }

    export function getParams() {
        const params = {
            page: paginator.page
        }
        if (term) {
            params.term = term
        }
        const order = {};
        if (ordering.by && ordering.dir) {
            order.order_by = ordering.by;
            order.order_dir = ordering.dir === 1 ? 'd' : 'a';
        }
        return {
            ...params,
            ...selectedFilters,
            ...order
        };
    }

    export function updatePages(pages) {
        paginator.total = pages;
        paginator = paginator;
    }

    export function clear() {
        term = '';
        filtersCmpt.clear();
    }

</script>
<div>
    <div class="box-b">
        {#if !hideSearch}
            <div class="box-l sx-ii">
                <div class="search-wrap relative">
                    <input class="naui-input search-input"
                           type="text"
                           on:keyup={({ target: { value } }) => debounce(value)}
                           bind:value={searchVal}
                           placeholder={searchLabel}/>
                    <span class="material-icons primary">search</span>
                </div>
                <div class="radius py-ii px-1 back-gray">
                    <strong>
                        {count.toLocaleString('es-CO', {minimumFractionDigits: 0})}
                    </strong> {countLabel}
                </div>
            </div>
        {/if}
        <div>
            <slot name="actions"/>
        </div>
    </div>
    {#if filters}
        <div class="py-1">
            <div class="box-b">
                <NauiFilters bind:this={filtersCmpt} {filters} {grid} on:filtered={handleFilter}/>
                <div>
                    <slot name="table-actions"/>
                </div>
            </div>
            <slot name="filter-actions"></slot>
        </div>
    {/if}
    <NauiTable {data}
               bind:this={table}
               bind:total={count}
               {columns}
               on:action={(evt) => dispatch('action', evt.detail)}
               on:checked
               on:order={handleOrder}/>
    {#if paginate}
        <NauiPagination bind:data={paginator}
                        on:next/>
    {/if}
</div>
<style>
    .search-input {
        min-width: 400px;
        border-radius: 3rem;
        padding-left: 2.5rem;
    }

    .search-wrap .material-icons {
        position: absolute;
        left: .75rem;
        top: 10px;
    }
</style>
