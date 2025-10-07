
function showAlert(containerId, message, type) {
    const alertContainer = document.getElementById(containerId);
    if (!alertContainer) return;
    const alert = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    alertContainer.innerHTML = alert;
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    window.location.href = '/';
}

function calculateBMI(weight, height) {
    if (height > 0) {
        return weight / (height * height);
    }
    return 0;
}

function formatCategory(category) {
    return category.replace(/_/g, ' ');
}

function getRiskText(prediction) {
    if (['Overweight_Level_I', 'Overweight_Level_II'].includes(prediction)) {
        return 'Modéré';
    } else if (['Obesity_Type_I'].includes(prediction)) {
        return 'Élevé';
    } else if (['Obesity_Type_II', 'Obesity_Type_III'].includes(prediction)) {
        return 'Critique';
    }
    return 'Faible';
}

function getRiskClass(prediction) {
    if (['Overweight_Level_I', 'Overweight_Level_II'].includes(prediction)) {
        return 'risk-moderate';
    } else if (['Obesity_Type_I'].includes(prediction)) {
        return 'risk-high';
    } else if (['Obesity_Type_II', 'Obesity_Type_III'].includes(prediction)) {
        return 'risk-critical';
    }
    return 'risk-low';
}