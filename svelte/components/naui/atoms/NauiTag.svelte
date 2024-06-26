<script>
    export let label;
    export let backColor = '#fafafa';
    export let borderColor = null;
    export let textColor = null;

    $: _borderColor = borderColor ? borderColor : (textColor ? textColor : 'inherit');
    $: _background = backColor ? backColor : '#fafafa';
    $: _color = textColor ? textColor : 'var(--text-color)';

</script>
<div class="naui-tag box" style="border-color: {_borderColor}; background:{backColor}">
    <span style="color:{_color};">{label}</span>
</div>
