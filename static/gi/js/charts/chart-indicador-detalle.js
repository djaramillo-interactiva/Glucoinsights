(function () {
    const indicadorDatasets = [
        {
            data: Array(12).fill(meta),
            label: 'Meta'
        },
        {
            data: indicadoresData,
            label: 'Tendencia'
        }
    ];

    chartHelper.createLineChart(
        document.getElementById('tendencia-indicador'),
        indicadorDatasets,
        months,
        {
            yLabel: indicadorTitle
        }
    );
})();
