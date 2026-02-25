document.addEventListener("DOMContentLoaded", () => {
    console.log("JS loaded ✅");

    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }

    // Variable untuk simpan prediksi official
    let officialPredictionData = null;
    let currentChart = null;
    let simChart = null;

    // Load chart prediksi official dan model metrics
    loadOfficialPrediction();
    loadModelMetrics();

    // Handle Simulasi Form - CALL API TAPI TIDAK SIMPAN
    const simForm = document.getElementById('simulation-form');
    if (simForm) {
        simForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const scenario = document.getElementById('sim-scenario').value;
            const year = parseInt(document.getElementById('sim-year').value);
            
            // Get max years dari official prediction
            const maxYears = officialPredictionData?.maxYears || 5;
            const yearsToPredict = year - 2025 + 1;  // Hitung dari 2025
            
            // Validasi: tidak boleh melebihi max years dari admin
            if (yearsToPredict > maxYears) {
                alert(`Admin hanya memprediksi ${maxYears} tahun. Silakan pilih tahun maksimal ${2025 + maxYears - 1}.`);
                return;
            }
            
            // Mapping scenario value
            const scenarioMap = {
                'optimistic': 'optimis',
                'moderate': 'moderat',
                'pessimistic': 'pesimistis'
            };
            
            try {
                // Panggil API predict TANPA save_to_database
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        scenario: scenarioMap[scenario],
                        years: yearsToPredict,
                        save_to_database: false  // PENTING: tidak disimpan!
                    })
                });
                
                const data = await response.json();
                
                console.log('Simulation response:', data);
                
                if (data.status === 'success' && data.predictions) {
                    // Format predictions dengan tahun (mulai dari 2025)
                    const predictions = data.predictions.map((value, index) => ({
                        year: 2025 + index,
                        value: value
                    }));
                    
                    console.log('Formatted predictions:', predictions);
                    
                    // Update chart dengan hasil simulasi
                    renderSimChart(officialPredictionData.historical, predictions, scenario, scenarioMap[scenario]);
                      
                    // Update hasil simulasi
                    const targetPrediction = predictions.find(p => p.year === year);
                    if (targetPrediction) {
                        document.getElementById('sim-value').textContent = targetPrediction.value.toFixed(2);
                        // Ambil tahun & nilai terakhir dari historical official
                        const historical = officialPredictionData.historical;
                        const lastHistorical = historical[historical.length - 1];
                        const baseYear = lastHistorical.year;
                        const baseValue = lastHistorical.value;
                        const change = ((targetPrediction.value - baseValue) / baseValue * 100).toFixed(1);
                        // Update sim-change card
                        const simChangeEl = document.getElementById('sim-change');
                        if (simChangeEl) {
                            simChangeEl.textContent = `${change > 0 ? '+' : ''}${change}%`;
                        }
                        // Update baseline-year card
                        const baselineYearEl = document.getElementById('baseline-year');
                        if (baselineYearEl) {
                            baselineYearEl.textContent = baseYear;
                        }
                        // Update info
                        const scenarioNames = {
                            'optimistic': 'optimis (pertumbuhan PDB tinggi)',
                            'moderate': 'moderat (pertumbuhan PDB stabil)',
                            'pessimistic': 'pesimis (pertumbuhan PDB rendah)'
                        };
                        document.getElementById('sim-info').textContent =
                            `Dengan skenario ${scenarioNames[scenario]}, ` +
                            `konsumsi energi fosil Indonesia diprediksi mencapai ${targetPrediction.value.toFixed(2)} TWh pada tahun ${year}. ` +
                            `Ini menunjukkan ${change > 0 ? 'peningkatan' : 'penurunan'} ${Math.abs(change)}% dari tahun ${baseYear}.`;
                    }
                    
                    // Show result & reset button
                    document.getElementById('sim-result').style.display = 'block';
                    document.getElementById('resetToOfficial').style.display = 'inline-block';
                    document.getElementById('sim-result').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    console.error('API error:', data);
                    alert('Gagal menjalankan simulasi: ' + (data.error || data.message || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error simulasi:', error);
                alert('Terjadi kesalahan saat menjalankan simulasi: ' + error.message);
            }
        });
    }

    // Handle Reset Button
    const resetBtn = document.getElementById('resetToOfficial');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // Kembalikan chart ke prediksi official
            if (officialPredictionData) {
                loadChart(officialPredictionData.historical, officialPredictionData.predictions, 'moderat');
            }
            
            // Hide result & reset button
           document.getElementById('sim-result').style.display = 'none';
           resetBtn.style.display = 'none';
           //Destroy grafik simulasi
           if (simChart) { simChart.destroy(); simChart = null; }
            
            // Reset form
            document.getElementById('sim-scenario').value = 'moderate';
            document.getElementById('sim-year').value = '2030';
        });
    }

    async function loadOfficialPrediction() {
        try {
            // Load ALL historical data (untuk landing page tampilkan semua)
            const energyRes = await fetch('/api/data/energy?limit=1000');
            const energyResponse = await energyRes.json();
            
            // Load prediction data (official - moderat) - NEW ENDPOINT
            const predictionRes = await fetch('/api/prediction/latest');
            const predictionInfo = await predictionRes.json();
            
            console.log('Energy response:', energyResponse);
            console.log('Prediction info:', predictionInfo);
            
            // Extract data array from response
            const energyData = energyResponse.success ? energyResponse.data : energyResponse;
            
            if (energyData && energyData.length > 0) {
                const historical = energyData.map(item => ({
                    year: item.year,
                    value: item.fossil_fuels__twh
                }));
                
                const predictions = predictionInfo.predictions || [];
                const maxYears = predictionInfo.years || 5;
                
                console.log('📊 Data loaded successfully:');
                console.log(`  - Historical: ${historical.length} data points (${historical[0]?.year}-${historical[historical.length-1]?.year})`);
                console.log(`  - Predictions: ${predictions.length} data points`);
                console.log(`  - Forecast years: ${maxYears} years`);
                
                // Simpan data official
                officialPredictionData = { 
                    historical, 
                    predictions, 
                    maxYears 
                };
                
                // Update stats cards
                updateStatsCards(historical, predictions);
                
                // Generate dropdown options berdasarkan max years dari admin
                generateYearOptions(maxYears);
                
                // Load chart
                loadChart(historical, predictions, 'moderat');
            } else {
                console.error('No energy data available');
                alert('Data energi tidak tersedia. Silakan hubungi admin.');
            }
        } catch (error) {
            console.error('Error loading official prediction:', error);
            alert('Gagal memuat data: ' + error.message);
        }
    }
    
    function updateStatsCards(historical, predictions) {
        try {
            // Get last historical value (2024)
            const lastHistorical = historical[historical.length - 1];
            const lastValue = lastHistorical.value;
            
            // Get last prediction value and year
            const lastPrediction = predictions[predictions.length - 1];
            const projectionYear = lastPrediction.year;
            const projectionValue = lastPrediction.prediction_value || lastPrediction.value;
            
            // Update Proyeksi card
            const projYearEl = document.getElementById('projection-year');
            const projValueEl = document.getElementById('projection-value');
            if (projYearEl) {
                projYearEl.textContent = `Proyeksi ${projectionYear}`;
            }
            if (projValueEl) {
                projValueEl.textContent = `${projectionValue.toLocaleString('id-ID', {maximumFractionDigits: 0})} TWh`;
            }
            
            // Calculate growth rate
            const growthRate = ((projectionValue - lastValue) / lastValue * 100).toFixed(1);
            const growthEl = document.getElementById('growth-rate');
            if (growthEl) {
                growthEl.textContent = `${growthRate > 0 ? '+' : ''}${growthRate}%`;
            }
            
            console.log('✅ Stats cards updated:', {
                projectionYear,
                projectionValue,
                lastValue,
                growthRate
            });
        } catch (error) {
            console.error('❌ Error updating stats cards:', error);
        }
    }
    
    function generateYearOptions(maxYears) {
        const yearSelect = document.getElementById('sim-year');
        if (!yearSelect) return;
        
        // Clear existing options
        yearSelect.innerHTML = '';
        
        // Generate options from 2025 to 2025 + maxYears - 1
        const startYear = 2025;  // Mulai dari tahun setelah data terakhir (2024)
        for (let i = 0; i < maxYears; i++) {
            const year = startYear + i;
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (i === maxYears - 1) {
                option.selected = true; // Select last year as default
            }
            yearSelect.appendChild(option);
        }
        
        console.log(`Generated ${maxYears} year options (${startYear} - ${startYear + maxYears - 1})`);
    }

    function loadChart(historical, predictions, scenario) {
        const ctx = document.getElementById('preview-chart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (currentChart) {
            currentChart.destroy();
        }
        
        const years = historical.map(d => d.year);
        const values = historical.map(d => d.value);
        
        // Extract prediction years and values
        const predYears = predictions.map(d => d.year);
        const predValues = predictions.map(d => d.prediction_value || d.value);
        
        console.log('Chart data - Historical years:', years.slice(-3));
        console.log('Chart data - Prediction years:', predYears);
        console.log('Chart data - Prediction values:', predValues);
        
        const datasets = [{
            label: 'Data Historis',
            data: values,
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 3
        }];
        
        if (predictions.length > 0) {
            const scenarioLabel = scenario === 'moderat' ? 'Prediksi Official (Moderat)' : `Simulasi (${scenario.charAt(0).toUpperCase() + scenario.slice(1)})`;
            const scenarioColor = scenario === 'moderat' ? '#53B863' : '#ffc107';
            
            datasets.push({
                label: scenarioLabel,
                data: new Array(years.length).fill(null).concat(predValues),
                borderColor: scenarioColor,
                backgroundColor: 'transparent',
                borderWidth: 3,
                borderDash: [5, 5],
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#ff69b4'
            });
        }
        
        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years.concat(predYears),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        callbacks: {
                            title: function(context) {
                                return 'Tahun ' + context[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    const value = context.parsed.y.toFixed(2);
                                    label += value + ' TWh';
                                    
                                    // Add context info
                                    const year = parseInt(context.label);
                                    if (year <= 2024) {
                                        return [label, '📊 Data Aktual'];
                                    } else {
                                        return [label, '🎯 Prediksi Model ARIMAX'];
                                    }
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Konsumsi Energi Fosil (TWh)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Tahun'
                        }
                    }
                }
            }
        });
    }

    function updateChartWithSimulation(predictions, scenario) {
        if (!officialPredictionData) return;
        
        loadChart(officialPredictionData.historical, predictions, scenario);
    }

    function renderSimChart(historical, predictions, scenarioEn, scenarioId) {
    const ctx = document.getElementById('sim-chart');
    if (!ctx) return;

    // Destroy chart lama kalau ada
    if (simChart) {
        simChart.destroy();
    }

    const histYears = historical.map(d => d.year);
    const histValues = historical.map(d => d.value);
    const predYears = predictions.map(d => d.year);
    const predValues = predictions.map(d => typeof d.value === 'number' ? d.value : d.prediction_value);

    // Warna berdasarkan skenario
    const colorMap = {
        'optimistic': { border: '#2e7d32', bg: 'rgba(46,125,50,0.12)' },
        'moderate':   { border: '#ffc107', bg: 'rgba(255,193,7,0.12)' },
        'pessimistic':{ border: '#e53935', bg: 'rgba(229,57,53,0.12)' }
    };
    const color = colorMap[scenarioEn] || colorMap['moderate'];

    const scenarioLabel = {
        'optimistic': 'Simulasi Optimis',
        'moderate': 'Simulasi Moderat',
        'pessimistic': 'Simulasi Pesimis'
    }[scenarioEn] || 'Simulasi';

    // Gabungkan semua label tahun
    const allYears = histYears.concat(predYears);

    simChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allYears,
            datasets: [
                {
                    label: 'Data Historis',
                    data: histValues,
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33,150,243,0.08)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 2,
                    fill: true
                },
                {
                    label: scenarioLabel,
                    data: new Array(histYears.length).fill(null).concat(predValues),
                    borderColor: color.border,
                    backgroundColor: color.bg,
                    borderWidth: 3,
                    borderDash: [6, 4],
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: color.border,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'top' },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleFont: { size: 13, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 10,
                    callbacks: {
                        title: ctx => 'Tahun ' + ctx[0].label,
                        label: ctx => {
                            if (ctx.parsed.y === null) return null;
                            const year = parseInt(ctx.label);
                            const suffix = year <= 2024 ? ' TWh (Aktual)' : ' TWh (Simulasi)';
                            return ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(2) + suffix;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: { display: true, text: 'Konsumsi Energi Fosil (TWh)' },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: {
                    title: { display: true, text: 'Tahun' },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                }
            }
        }
    });
}

    const btn = document.getElementById("refreshBtn");
    if (!btn) {
        console.error("refreshBtn tidak ditemukan");
        return;
    }

     function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    }

    btn.addEventListener("click", async () => {
        console.log("Refresh diklik");

      startLoading(true);

      setText("energy-status", "Updating...");
      setText("gdp-status", "Updating...");

        try {
            const res = await fetch("/update-data");
            const json = await res.json();

            console.log(json);

            document.getElementById("energyStatus").innerText = "Updated";
            document.getElementById("energyTime").innerText =
                new Date().toLocaleString();

            document.getElementById("gdpStatus").innerText = "Updated";
            document.getElementById("gdpTime").innerText =
                new Date().toLocaleString();

            alert("Data berhasil diperbarui");
        } catch (e) {
          console.error("ERROR UPDATE:", e);
          alert("Gagal update data: " + e.message);
        } finally {
        stopLoading();
      }


        btn.disabled = false;
        btn.innerText = "🔄 Refresh Data";
    });
});

// Function untuk load model metrics dari database
async function loadModelMetrics() {
    try {
        const response = await fetch('/api/model/metrics');
        const data = await response.json();

        console.log("last_actual_year:", data.last_actual_year);
console.log("last_actual_value:", data.last_actual_value);

        
        if (data.success && data.metrics) {
            const metrics = data.metrics;
            // Update akurasi di stats card
            const accuracyEl = document.getElementById('model-accuracy');
            if (accuracyEl) {
                accuracyEl.textContent = metrics.accuracy + '%';
            }
            // Update MAPE di evaluasi model
            const mapeEl = document.getElementById('model-mape');
            if (mapeEl) {
                mapeEl.textContent = metrics.mape.toFixed(2) + '%';
            }
            // Update model version
            const versionEl = document.getElementById('model-version');
            if (versionEl) {
                versionEl.textContent = metrics.order;
            }
            // Update training date
            const dateEl = document.getElementById('model-date');
            if (dateEl) {
                dateEl.textContent = metrics.training_date || 'N/A';
            }
            // Update model-accuracy-summary for layman
            const summaryEl = document.getElementById('model-accuracy-summary');
            if (summaryEl && metrics.mape !== undefined && metrics.mape !== null) {
                const accuracy = 100 - metrics.mape;
                summaryEl.textContent = accuracy >= 0 ? accuracy.toFixed(1) + '%' : 'N/A';
            } else if (summaryEl) {
                summaryEl.textContent = 'N/A';
            }
            console.log('✅ Model metrics loaded:', metrics);
        } else {
            console.warn('⚠️ No active model metrics found');
            // Set fallback values
            const accuracyEl = document.getElementById('model-accuracy');
            if (accuracyEl) accuracyEl.textContent = 'N/A';
            const mapeEl = document.getElementById('model-mape');
            if (mapeEl) mapeEl.textContent = 'N/A';
            const versionEl = document.getElementById('model-version');
            if (versionEl) versionEl.textContent = 'N/A';
            const dateEl = document.getElementById('model-date');
            if (dateEl) dateEl.textContent = 'N/A';
            // Set fallback for summary
            const summaryEl = document.getElementById('model-accuracy-summary');
            if (summaryEl) summaryEl.textContent = 'N/A';
        }
    } catch (error) {
        console.error('❌ Error loading model metrics:', error);
        // Set error indicator
        const accuracyEl = document.getElementById('model-accuracy');
        if (accuracyEl) accuracyEl.innerHTML = '<i class="bi bi-exclamation-circle"></i>';
        
        const mapeEl = document.getElementById('model-mape');
        if (mapeEl) mapeEl.innerHTML = '<i class="bi bi-exclamation-circle"></i>';
    }
}