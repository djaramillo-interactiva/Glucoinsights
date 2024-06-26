<script>
    export let active = false;
</script>
<div>
    <label class="switch">
        <input type="checkbox" bind:checked={active}>
        <span class="slider round"></span>
    </label>
</div>
<style>
    /* Switch */
    /* The switch - the box around the slider */
    .switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }

    /* Hide default HTML checkbox */
    .switch input {
        display: none;
    }

    /* The slider */
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        -webkit-transition: .4s;
        transition: .4s;
    }

    .slider:before {
        position: absolute;
        content: "NO";
        font-weight: 600;
        color: #888;
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        -webkit-transition: .4s;
        transition: .4s;
        text-align: center;
        font-size: .8rem;
        line-height: 26px;
    }

    input:checked + .slider {
        background-color: #1abc9c;
    }

    input:focus + .slider {
        box-shadow: 0 0 1px #2196F3;
    }

    input:checked + .slider:before {
        color: #D95A1C;
        font-weight: 600;
        content: "SI";
        -webkit-transform: translateX(26px);
        -ms-transform: translateX(26px);
        transform: translateX(26px);
    }

    /* Rounded sliders */
    .slider.round {
        border-radius: 34px;
    }

    .slider.round:before {
        border-radius: 50%;
    }

    span.slider.disabled {
        cursor: default;
    }
</style>
