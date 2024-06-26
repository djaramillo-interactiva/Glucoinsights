(function () {
    if (window.hasOwnProperty('cardioVascularData')) {
        const cardovascularDatasets = [{
            data: cardioVascularData.values,
            label: '# Pacientes',
        }];

        chartHelper.createPieChart(
            document.getElementById('presencia-cardiovascular'),
            cardovascularDatasets,
            cardioVascularData.labels,
            {
                datalabels: true,
                percent: true
            }
        );
    }
    if (window.hasOwnProperty('sobrepesoData')) {
        const sobrepesoDatasets = [{
            data: sobrepesoData.values,
            label: '# Pacientes',
        }];
        chartHelper.createPieChart(
            document.getElementById('presencia-sobrepeso'),
            sobrepesoDatasets,
            sobrepesoData.labels,
            {
                datalabels: true,
                percent: false
            }
        )
    }
    if (window.hasOwnProperty('insuficienciaRenalData')) {
        const insuficienciaDatasets = [{
            data: insuficienciaRenalData.values,
            label: '# Pacientes'
        }];
        chartHelper.createPieChart(
            document.getElementById('insuficiencia-renal'),
            insuficienciaDatasets,
            insuficienciaRenalData.labels,
            {
                datalabels: true,
                percent: true
            }
        )
    }
    if (window.hasOwnProperty('estadiosData')) {
        const eDatasets = [{
            data: estadiosData.values,
            label: '# Pacientes'
        }];
        chartHelper.createPieChart(
            document.getElementById('estadios'),
            eDatasets,
            estadiosData.labels,
            {
                datalabels: true,
                percent: false
            }
        )
    }
})();
