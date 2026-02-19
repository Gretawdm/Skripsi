
document.addEventListener("DOMContentLoaded", function () {
    loadPreviewChart();
    loadActualCharts();
    loadModelInfo();
});

// ==============================
// LOAD PREVIEW (PREDIKSI)
// ==============================
function loadPreviewChart() {
    fetch('/api/dashboard/prediction-preview')
        .then(res => res.json())
        .then(data => {

            if (!data.years) return;

            const ctx = document.getElementById('preview-chart');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.years,
                    datasets: [
                        {
                            label: 'Data Historis',
                            data: data.actual,
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: 'Prediksi',
                            data: data.prediction,
                            borderDash: [5,5],
                            borderWidth: 2,
                            tension: 0.3
                        }
                    ]
                }
            });

            // Update stats
            document.getElementById("projection-year").innerText =
                "Proyeksi " + data.last_prediction_year;

            document.getElementById("projection-value").innerText =
                data.last_prediction_value + " TWh";

            document.getElementById("growth-rate").innerText =
                data.growth_rate + "%";

            document.getElementById("model-accuracy").innerText =
                data.mape + "%";
        })
        .catch(err => console.log("Preview error:", err));
}


// ==============================
// LOAD DATA ASLI
// ==============================
function loadActualCharts() {
    fetch('/api/dashboard/actual-gdp')
        .then(res => res.json())
        .then(data => {

            if (!data.actual || !data.gdp) return;

            // Energy Chart
            const energyCtx = document.getElementById('energy-actual-chart');
            new Chart(energyCtx, {
                type: 'line',
                data: {
                    labels: data.actual.map(d => d.year),
                    datasets: [{
                        label: 'Energi Fosil',
                        data: data.actual.map(d => d.value),
                        borderWidth: 2,
                        tension: 0.3
                    }]
                }
            });

            // GDP Chart
            const gdpCtx = document.getElementById('gdp-actual-chart');
            new Chart(gdpCtx, {
                type: 'line',
                data: {
                    labels: data.gdp.map(d => d.year),
                    datasets: [{
                        label: 'GDP Indonesia',
                        data: data.gdp.map(d => d.value),
                        borderWidth: 2,
                        tension: 0.3
                    }]
                }
            });

        })
        .catch(err => console.log("Actual error:", err));
}


// ==============================
// LOAD INFO MODEL
// ==============================
function loadModelInfo() {
    fetch('/api/dashboard/model-info')
        .then(res => res.json())
        .then(data => {

            document.getElementById("model-mape").innerText =
                data.mape + "%";

            document.getElementById("model-version").innerText =
                data.version;

            document.getElementById("model-date").innerText =
                data.training_date;
        })
        .catch(err => console.log("Model info error:", err));
}
