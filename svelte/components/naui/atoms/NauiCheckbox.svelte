<script>
    export let label = '';
    export let color = '';
    export let value = false;
    export let disabled = false;
</script>

<div>
    <label class="flex pointer py-ii">
        <input hidden
               class="self-start"
               type="checkbox"
               bind:checked={value}
               {disabled}
               on:input>
        <span class="{color} checkmark" class:mr-ii={label}></span>
        {#if label}
            <span>{label}</span>
        {/if}
    </label>
</div>

<style>
    input {
        position: absolute;
        opacity: 0;
        cursor: pointer;
        height: 0;
        width: 0;
    }

    .checkmark {
        height: 17px;
        width: 17px;
        min-width: 17px;
        border-radius: 3px;
        border: 2px solid var(--border-color);
    }

    input:checked + .checkmark {
        background-color: #999;
        border: 2px solid #999;
        position: relative;
    }

    input:checked + .checkmark:after {
        content: '';
        width: 4px;
        height: 9px;
        left: 4px;
        border-radius: 2px;
        top: 0;
        border-right: 2px solid white;
        border-bottom: 2px solid white;
        transform: rotate(45deg);
        position: absolute;
    }

    input:checked + .checkmark.primary {
        background-color: var(--primary);
        border: 2px solid var(--primary);
    }

    input:checked + .checkmark.secondary {
        background-color: var(--secondary);
        border: 2px solid var(--secondary);
    }

    input:checked + .checkmark.accent {
        background-color: var(--accent);
        border: 2px solid var(--accent);
    }

    label {
        position: relative;
    }

    label:before {
        content: '';
        display: block;
        height: 36px;
        width: 36px;
        background-color: rgba(0, 0, 0, 0.05);
        border-radius: 50%;
        position: absolute;
        top: calc(50% - 18px);
        left: -9px;
        opacity: 0;
        transition: .001s ease-in-out all;
    }

    label:active:before {
        opacity: 1;
    }
</style>
