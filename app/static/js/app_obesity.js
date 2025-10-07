document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = '/';
        return;
    }

    fetch('/api/auth/users/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.email) {
            document.getElementById('userEmail').textContent = data.email;
            if (data.is_admin) {
                document.getElementById('adminLink').style.display = 'block';
            }
        } else {
            logout();
        }
    })
    .catch(() => logout());

    const predictionForm = document.getElementById('predictionForm');
    predictionForm.addEventListener('submit', function (e) {
        e.preventDefault();
        handlePrediction();
    });
});

function logout() {
    localStorage.removeItem('accessToken');
    window.location.href = '/';
}

async function handlePrediction() {
    const token = localStorage.getItem('accessToken');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = '';

    const data = {
        Age: parseFloat(document.getElementById('age').value),
        FCVC: parseFloat(document.getElementById('fcvc').value),
        NCP: parseFloat(document.getElementById('ncp').value),
        CAEC: document.getElementById('caec').value,
        FAF: parseFloat(document.getElementById('faf').value),
        TUE: parseFloat(document.getElementById('tue').value),
        CALC: document.getElementById('calc').value,
        MTRANS: document.getElementById('mtrans').value,
        Weight: parseFloat(document.getElementById('weight').value),
        Height: parseFloat(document.getElementById('height').value)
    };

    loadingOverlay.style.display = 'flex';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Une erreur est survenue lors de la prédiction.');
        }

        const result = await response.json();
        displayResults(result);

    } catch (error) {
        showAlert(`<strong>Erreur !</strong> ${error.message}`, 'danger');
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

function displayResults(result) {
    document.getElementById('noResultsMessage').style.display = 'none';
    document.getElementById('resultsDisplay').style.display = 'block';

    const categoryText = document.getElementById('categoryText');
    const riskBadge = document.getElementById('riskBadge');
    const bmiValue = document.getElementById('bmiValue');
    const confidenceText = document.getElementById('confidenceText');
    const confidenceFill = document.getElementById('confidenceFill');

    categoryText.textContent = result.prediction;
    bmiValue.textContent = result.bmi.toFixed(2);
    
    const confidence = result.probabilities[result.prediction];
    confidenceText.textContent = `${(confidence * 100).toFixed(1)}%`;
    confidenceFill.style.width = `${confidence * 100}%`;

    setRiskBadge(riskBadge, result.prediction);
    renderChart(result.probabilities);
}

function setRiskBadge(element, prediction) {
    let riskLevel = 'risk-low';
    let riskText = 'Faible';

    if (['Overweight_Level_I', 'Overweight_Level_II'].includes(prediction)) {
        riskLevel = 'risk-moderate';
        riskText = 'Modéré';
    } else if (['Obesity_Type_I'].includes(prediction)) {
        riskLevel = 'risk-high';
        riskText = 'Élevé';
    } else if (['Obesity_Type_II', 'Obesity_Type_III'].includes(prediction)) {
        riskLevel = 'risk-critical';
        riskText = 'Critique';
    }
    
    element.className = `risk-badge ${riskLevel}`;
    element.textContent = `Risque : ${riskText}`;
}

let probabilityChart = null;
function renderChart(probabilities) {
    const ctx = document.getElementById('probabilityChart').getContext('2d');
    const labels = Object.keys(probabilities);
    const data = Object.values(probabilities);

    if (probabilityChart) {
        probabilityChart.destroy();
    }

    probabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Probabilités par catégorie',
                data: data,
                backgroundColor: 'rgba(74, 144, 226, 0.6)',
                borderColor: 'rgba(74, 144, 226, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1.0,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += (context.parsed.y * 100).toFixed(2) + '%';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    const alert = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    alertContainer.innerHTML = alert;
}