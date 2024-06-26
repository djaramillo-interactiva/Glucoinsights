<script>
    export let label;
    export let code;
    export let border=false;
    export let className = '';
    export let styleText = '';
</script>

<div class="state {className}" style="{styleText}" class:border={border}>
    <div class="color-code {'state-code-'+code}"></div>
    <span>{label}</span>
</div>
<style>
    .state{
        display: flex;
        align-items: center;
        height: 35px;
        padding: 7px;
        border-radius:var(--border-radius, 4px);
    }
    .state.border{
        border: 1px solid #E6E6E6;
        background: white;
    }
    .color-code{
        margin-right:.5rem;
        height: 20px;
        width: 20px;
        border-radius: 3px;
    }

    span {
        font-size: .9rem;
    }
</style>
