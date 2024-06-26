<script>
    import NauiButton from "../atoms/NauiButton.svelte";
    import { createEventDispatcher } from "svelte";

    export let data = [];
    export let displayCode = false;
    export let displayDescription = false;
    export let codeLabel = 'Cod.';
    export let nameLabel = 'Name';
    export let descriptionLabel = 'Description';
    export let countLabel = 'count';

    let withCode = true;

    const events = new createEventDispatcher();

    function onClick(slug) {
        events('click', slug)
    }

</script>
<table class="naui-table mb-3">
    <thead>
    <tr>
        {#if displayCode}
            <th>
                <div>{codeLabel}</div>
            </th>
        {/if}
        <th style="min-width: 200px">
            <div>{nameLabel}</div>
        </th>
        {#if displayDescription}
            <th>
                <div>{descriptionLabel}</div>
            </th>
        {/if}
        <th style="min-width: 100px">
            <div class="box">{countLabel}</div>
        </th>
        <th style="min-width: 100px"></th>
    </tr>
    </thead>
    <tbody>
    {#each data as item, i (item.slug)}
        <tr>
            {#if displayCode}
                <td>
                    <div>
                        <strong>
                            {#if item.code}
                                {item.code}
                            {:else}
                                {item.slug}
                            {/if}
                        </strong>
                    </div>
                </td>
            {/if}
            <td>
                <div>{item.name}</div>
            </td>
            {#if displayDescription}
                <td>
                    <div>{item.description}</div>
                </td>
            {/if}
            <td>
                <div class="box">{item.count}</div>
            </td>
            <td>
                <div class="box">
                    {#if item.route}
                        <NauiButton href={item.route} icon="chevron_right" color="accent"/>
                    {:else}
                        <NauiButton icon="chevron_right" color="accent" on:click={onClick.bind(this, item.slug)}/>
                    {/if}
                </div>
            </td>
        </tr>
    {/each}

    </tbody>
</table>
