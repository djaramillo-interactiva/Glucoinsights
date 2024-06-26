var chartHelper = (function () {
    const DEFAULT_COLORS = [
        {
            backgroundColor: '#005ad2',
            pointBackgroundColor: '#005ad2'
        },
        {
            backgroundColor: '#2196F3',
            pointBackgroundColor: '#2196F3'
        },
        {
            backgroundColor: '#00BCD4',
            pointBackgroundColor: '#00BCD4'
        },
        {
            backgroundColor: '#39B0C1',
            pointBackgroundColor: '#39B0C1'
        },
        {
            backgroundColor: '#009688',
            pointBackgroundColor: '#009688'
        },
        {
            backgroundColor: '#4CAF50',
            pointBackgroundColor: '#4CAF50'
        },
        {
            backgroundColor: '#8BC34A',
            pointBackgroundColor: '#8BC34A'
        },
        {
            backgroundColor: '#CDDC39',
            pointBackgroundColor: '#CDDC39'
        },
        {
            backgroundColor: '#FFEB3B',
            pointBackgroundColor: '#FFEB3B'
        },
        {
            backgroundColor: '#F2f2f2',
            pointBackgroundColor: '#F2f2f2'
        }
    ];

    const bgColors = DEFAULT_COLORS.map(d => d.backgroundColor);
    const bgBorderColors = DEFAULT_COLORS.map(d => d.pointBackgroundColor);

    function createBarChart(element, datasets, labels, options = {}) {
        if (!element) {
            return null;
        }

        const ctx = element.getContext('2d');
        const barChartOptions = {
            legend: {
                display: !!options.legend
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: !!options.yLabel,
                        labelString: options.yLabel || null
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            plugins: {
                datalabels: {
                    display: !!options.datalabels
                }
            }
        };

        for (const ds of datasets) {
            ds.backgroundColor = bgColors;
            ds.borderColor = bgBorderColors;
        }

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets,
                borderWidth: 1
            },
            plugins: [ChartDataLabels],
            options: barChartOptions
        });
    }

    function createPieChart(element, datasets, labels, options = {}) {
        if (!element) {
            return null;
        }
        const ctx = element.getContext('2d');

        for (const ds of datasets) {
            ds.backgroundColor = bgColors;
            ds.borderColor = bgBorderColors;
        }

        new Chart(ctx, {
            type: 'pie',
            data: {
                datasets: datasets,
                labels: labels
            },
            plugins: [ChartDataLabels],
            options: {
                legend: {
                    display: true,
                    position: 'bottom',
                },
                plugins: {
                    datalabels: {
                        display: true,
                        formatter: (value, ctx) => {
                            if (options.percent) {
                                const total = datasets[0].data.reduce((t, d) => t + d);
                                return ((value / total) * 100).toFixed(0) + '%';
                            } else {
                                return value;
                            }
                        },
                        color: '#fff',
                        font: {
                            size: options.fontSize || 14
                        }
                    }
                }
            }
        });
    }

    function createLineChart(element, datasets, labels, options = {}) {
        if (!element) {
            return null;
        }
        const ctx = element.getContext('2d');
        datasets.forEach((ds, i) => {
            ds.borderColor = bgColors[i];
            ds.fill = false;
        })
        const lineChartOptions = {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: !!options.yLabel,
                        labelString: options.yLabel || null
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            plugins: {
                datalabels: {
                    display: false
                }
            }
        }
        if (options.time) {
            lineChartOptions.scales.xAxes = [{
                type: 'time',
                distribution: 'linear',
                time: {
                    unit: 'months'
                }
            }];
        }

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: lineChartOptions
        });
    }

    return {createBarChart, createPieChart, createLineChart}
})()