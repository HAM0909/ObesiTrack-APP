// Global logout function available on all pages
window.logout = function() {
    try {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
    } catch (_) {}
    // Redirect to login/home
    window.location.href = '/';
};

// Main app logic
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    const isProtected = path === '/app' || path === '/history';

    // Enforce authentication on protected pages only
    const token = localStorage.getItem('access_token');
    if (isProtected && !token) {
        alert('Authentification requise. Veuillez vous connecter.');
        window.location.href = '/';
        return;
    }

    const predictionForm = document.getElementById('predictionForm');
    const resultContainer = document.getElementById('resultContainer');
    const loadingSpinner = document.getElementById('loading-spinner');

    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            if (loadingSpinner) loadingSpinner.style.display = 'block';
            if (resultContainer) resultContainer.style.display = 'none';

            try {
                // Collect form data
                const formData = new FormData(predictionForm);
                const data = {};

                for (let [key, value] of formData.entries()) {
                    // Convert numeric values when appropriate
                    if (value !== '' && !isNaN(value)) {
                        value = Number(value);
                    }
                    data[key.toLowerCase()] = value;
                }

                const jwt = localStorage.getItem('access_token');
                const response = await fetch('/api/prediction/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(jwt ? { 'Authorization': `Bearer ${jwt}` } : {})
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    let detail = '';
                    try {
                        const errJson = await response.json();
                        detail = errJson?.detail || '';
                    } catch (_) {}

                    if (response.status === 401 || response.status === 403) {
                        alert(detail || 'Session expirée ou non authentifiée. Veuillez vous reconnecter.');
                        window.location.href = '/';
                        return;
                    }

                    throw new Error(`HTTP ${response.status}: ${detail || response.statusText}`);
                }

                const result = await response.json();

                // Display results
                if (resultContainer) {
                    // Calculate BMI
                    const heightM = (Number(data.height) || 0) / 100; // Convert cm to meters
                    const bmi = heightM > 0 ? (Number(data.weight) || 0) / (heightM * heightM) : 0;
                    const bmiCategory = getBMICategory(bmi);

                    // Generate recommendations based on the prediction
                    const recommendations = generateRecommendations(result.prediction || '', data);

                    resultContainer.innerHTML = `
                        <div class="card shadow-lg">
                            <div class="card-header bg-primary text-white">
                                <h3 class="mb-0">Résultat de la Prédiction</h3>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="bmi-indicator mb-4">
                                            <h4>Catégorie prédite:</h4>
                                            <p class="display-4 text-primary">${result.prediction}</p>
                                            ${typeof result.confidence === 'number' ? `<p class="text-muted">Indice de confiance: ${(result.confidence * 100).toFixed(1)}%</p>` : ''}
                                            ${result.risk_level ? `<span class="badge risk-${String(result.risk_level).toLowerCase()}">Risque: ${result.risk_level}</span>` : ''}
                                        </div>
                                        <div class="bmi-info">
                                            <h5>Informations IMC</h5>
                                            <p>IMC: ${bmi.toFixed(1)}</p>
                                            <p>Catégorie IMC: ${bmiCategory}</p>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="recommendations">
                                            <h5>Recommandations</h5>
                                            <ul class="list-group">
                                                ${recommendations.map(rec => 
                                                    `<li class="list-group-item">
                                                        <i class="fas fa-check-circle text-success me-2"></i>${rec}
                                                    </li>`
                                                ).join('')}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    resultContainer.style.display = 'block';
                }

            } catch (error) {
                console.error('Error:', error);
                alert('Une erreur est survenue lors de la prédiction. Veuillez réessayer.');
            } finally {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
            }
        });
    }

    // BMI helper wiring
    const weightInput = document.getElementById('weight');
    const heightInput = document.getElementById('height');
    const bmiResult = document.getElementById('bmi-result');

    function calculateBMI() {
        if (weightInput && heightInput && bmiResult) {
            const weight = parseFloat(weightInput.value);
            const height = parseFloat(heightInput.value) / 100; // convert cm to m
            if (weight && height) {
                const bmi = (weight / (height * height)).toFixed(1);
                bmiResult.textContent = `IMC: ${bmi} - ${getBMICategory(Number(bmi))}`;
            }
        }
    }

    if (weightInput && heightInput) {
        weightInput.addEventListener('input', calculateBMI);
        heightInput.addEventListener('input', calculateBMI);
    }

    // Utilities
    function getBMICategory(bmi) {
        if (bmi < 18.5) return 'Sous-poids';
        if (bmi < 25) return 'Normal';
        if (bmi < 30) return 'Surpoids';
        if (bmi < 35) return 'Obésité classe I';
        if (bmi < 40) return 'Obésité classe II';
        return 'Obésité classe III';
    }

    function generateRecommendations(prediction, userData) {
        const recommendations = [];
        const p = String(prediction || '');

        if (p.includes('Obesity')) {
            recommendations.push(
                "Consultez un professionnel de santé pour un suivi personnalisé",
                "Adoptez une alimentation équilibrée et variée",
                "Pratiquez une activité physique régulière",
                "Surveillez votre apport calorique quotidien"
            );
            if (userData.favc === 'yes') recommendations.push("Réduisez la consommation d'aliments à haute teneur calorique");
            if (Number(userData.ch2o) < 2) recommendations.push("Augmentez votre consommation d'eau (objectif: 2L par jour)");
            if (Number(userData.faf) === 0) recommendations.push("Commencez une activité physique adaptée progressivement");
        } else if (p.includes('Overweight')) {
            recommendations.push(
                "Maintenez une activité physique régulière",
                "Surveillez votre alimentation",
                "Buvez suffisamment d'eau (2L par jour)",
                "Privilégiez les aliments faibles en calories"
            );
        } else {
            recommendations.push(
                "Continuez vos bonnes habitudes",
                "Maintenez une activité physique régulière",
                "Gardez une alimentation équilibrée"
            );
        }
        return recommendations;
    }
});