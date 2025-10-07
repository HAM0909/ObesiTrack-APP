let currentPage = 1;
let totalPages = 1;
let predictions = [];
let filteredPredictions = [];
let currentFilter = 'all';
let selectedPredictionId = null;
let weightChart = null;
let categoryChart = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) {
        window.location.href = 'login.html';
        return;
    }
    loadHistory();
});

function checkAuth() {
    const token = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('user_info');
    
    if (token && userInfo) {
        const user = JSON.parse(userInfo);
        document.getElementById('userEmail').textContent = user.email;
        if (user.is_admin) {
            document.getElementById('adminLink').style.display = 'block';
        }
        return true;
    }
    return false;
}

async function loadHistory() {
    try {
        const token = localStorage.getItem('access_token');
        
        // Skip stats for now - endpoint doesn't exist yet
        // TODO: Create stats endpoint later
        
        const historyResponse = await fetch(`/api/prediction/history?limit=50`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (historyResponse.ok) {
            const data = await historyResponse.json();
            predictions = data; // API returns array directly, not wrapped in object
            filteredPredictions = predictions;
            totalPages = 1; // For now, no pagination
            
            // Generate simple stats from predictions data
            if (predictions.length > 0) {
                const stats = generateStatsFromPredictions(predictions);
                updateStats(stats);
            }
            
            displayPredictions();
            updatePagination();
            createCharts();
            
            document.getElementById('loadingState').style.display = 'none';
            
            if (predictions.length === 0) {
                document.getElementById('emptyState').style.display = 'block';
            }
        } else {
            throw new Error('Erreur lors du chargement de l\'historique');
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('alertContainer', 'Erreur lors du chargement de l\'historique', 'danger');
        document.getElementById('loadingState').innerHTML = '<p class="text-danger">Erreur lors du chargement</p>';
    }
}

function generateStatsFromPredictions(predictions) {
    if (predictions.length === 0) {
        return {
            total_predictions: 0,
            average_confidence: 0,
            last_bmi: 0,
            days_since_first: 0
        };
    }
    
    const totalPredictions = predictions.length;
    const avgConfidence = predictions.reduce((sum, p) => sum + p.confidence, 0) / totalPredictions;
    
    // Get latest prediction for BMI
    const latest = predictions[0]; // Assuming sorted by date desc
    const lastBMI = calculateBMI(latest.weight, latest.height);
    
    // Calculate days since first prediction
    const firstDate = new Date(predictions[predictions.length - 1].created_at);
    const daysDiff = Math.floor((Date.now() - firstDate.getTime()) / (1000 * 60 * 60 * 24));
    
    return {
        total_predictions: totalPredictions,
        average_confidence: avgConfidence,
        last_bmi: lastBMI,
        days_since_first: daysDiff
    };
}

function updateStats(stats) {
    document.getElementById('totalPredictions').textContent = stats.total_predictions;
    document.getElementById('avgConfidence').textContent = (stats.average_confidence * 100).toFixed(0) + '%';
    document.getElementById('lastBMI').textContent = stats.last_bmi.toFixed(1);
    document.getElementById('daysSinceFirst').textContent = stats.days_since_first;
}

function displayPredictions() {
    const container = document.getElementById('predictionsList');
    
    if (filteredPredictions.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">Aucune prédiction trouvée</p>';
        return;
    }

    const predictionsHTML = filteredPredictions.map(prediction => {
        const date = new Date(prediction.created_at);
        const bmi = calculateBMI(prediction.weight, prediction.height);
        const riskClass = getRiskClass(prediction.prediction);
        
        return `
            <div class="prediction-item" onclick="showPredictionDetails(${prediction.id})">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="prediction-category">${formatCategory(prediction.prediction)}</div>
                        <div class="prediction-date">
                            <i class="fas fa-calendar me-1"></i>
                            ${date.toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </div>
                        <div class="mt-2">
                            <span class="bmi-badge">IMC: ${bmi.toFixed(1)}</span>
                            <span class="risk-badge ${riskClass} ms-2">${getRiskText(prediction.prediction)}</span>
                        </div>
                    </div>
                    <div class="text-end">
                        <div class="text-muted small">Confiance</div>
                        <div class="fw-bold">${(prediction.confidence * 100).toFixed(0)}%</div>
                        <div class="confidence-bar" style="width: 80px;">
                            <div class="confidence-fill" style="width: ${prediction.confidence * 100}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = predictionsHTML;
}

function showPredictionDetails(predictionId) {
    selectedPredictionId = predictionId;
    const prediction = predictions.find(p => p.id === predictionId);
    
    if (!prediction) return;

    const bmi = calculateBMI(prediction.weight, prediction.height);
    const date = new Date(prediction.created_at);
    
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-primary">Informations personnelles</h6>
                <table class="table table-sm">
                    <tr><td>Âge:</td><td>${prediction.age} ans</td></tr>
                    <tr><td>Taille:</td><td>${prediction.height} m</td></tr>
                    <tr><td>Poids:</td><td>${prediction.weight} kg</td></tr>
                    <tr><td>IMC:</td><td class="fw-bold">${bmi.toFixed(2)}</td></tr>
                </table>
                
                <h6 class="text-success">Habitudes alimentaires</h6>
                <table class="table table-sm">
                    <tr><td>Légumes:</td><td>${prediction.fcvc}</td></tr>
                    <tr><td>Repas/jour:</td><td>${prediction.ncp}</td></tr>
                    <tr><td>Grignotage:</td><td>${prediction.caec}</td></tr>
                </table>
            </div>
            
            <div class="col-md-6">
                <h6 class="text-warning">Activité physique</h6>
                <table class="table table-sm">
                    <tr><td>Sport/semaine:</td><td>${prediction.faf}</td></tr>
                    <tr><td>Temps écrans:</td><td>${prediction.tue}</td></tr>
                </table>
                
                <h6 class="text-info">Mode de vie</h6>
                <table class="table table-sm">
                    <tr><td>Alcool:</td><td>${prediction.calc}</td></tr>
                    <tr><td>Transport:</td><td>${prediction.mtrans}</td></tr>
                </table>
                
                <h6 class="text-danger">Résultat</h6>
                <div class="text-center">
                    <div class="fs-5 fw-bold mb-2">${formatCategory(prediction.prediction)}</div>
                    <div class="mb-2">${getRiskText(prediction.prediction)}</div>
                    <div>Confiance: <strong>${(prediction.confidence * 100).toFixed(1)}%</strong></div>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <h6>Probabilités détaillées</h6>
            <div class="row">
                ${Object.entries(prediction.probabilities).map(([category, prob]) => `
                    <div class="col-md-6 mb-2">
                        <div class="d-flex justify-content-between">
                            <span>${formatCategory(category)}:</span>
                            <span>${(prob * 100).toFixed(1)}%</span>
                        </div>
                        <div class="progress" style="height: 6px;">
                            <div class="progress-bar bg-primary" style="width: ${prob * 100}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="mt-3 text-muted small">
            <i class="fas fa-calendar me-1"></i>
            Prédiction effectuée le ${date.toLocaleDateString('fr-FR')} à ${date.toLocaleTimeString('fr-FR')}
        </div>
    `;

    new bootstrap.Modal(document.getElementById('predictionModal')).show();
}

async function deletePrediction() {
    // Delete functionality not implemented yet in backend
    showAlert('alertContainer', 'Fonction de suppression non disponible pour le moment', 'warning');
}

function filterPredictions(category) {
    currentFilter = category;
    
    document.querySelectorAll('.btn-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    if (category === 'all') {
        filteredPredictions = predictions;
    } else {
        filteredPredictions = predictions.filter(p => p.prediction === category);
    }
    
    displayPredictions();
}

function createCharts() {
    if (predictions.length === 0) return;

    const weightData = predictions.slice(0, 10).reverse().map(p => ({
        x: new Date(p.created_at).toLocaleDateString('fr-FR'),
        y: p.weight
    }));

    const weightCtx = document.getElementById('weightChart').getContext('2d');
    if (weightChart) weightChart.destroy();
    
    weightChart = new Chart(weightCtx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Poids (kg)',
                data: weightData,
                borderColor: '#2c5aa0',
                backgroundColor: 'rgba(44, 90, 160, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Poids (kg)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    const categories = {};
    predictions.forEach(p => {
        categories[p.prediction] = (categories[p.prediction] || 0) + 1;
    });

    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    if (categoryChart) categoryChart.destroy();
    
    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categories).map(formatCategory),
            datasets: [{
                data: Object.values(categories),
                backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1', '#e83e8c']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

function updatePagination() {
    const paginationList = document.getElementById('paginationList');
    const paginationNav = document.getElementById('paginationNav');
    
    if (totalPages <= 1) {
        paginationNav.style.display = 'none';
        return;
    }
    
    paginationNav.style.display = 'block';
    paginationList.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="changePage(${i})">${i}</a>`;
        paginationList.appendChild(li);
    }
}

function changePage(page) {
    currentPage = page;
    loadHistory();
}

function refreshHistory() {
    loadHistory();
}