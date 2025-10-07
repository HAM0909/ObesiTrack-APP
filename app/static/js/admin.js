
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAdminAuth()) {
        window.location.href = 'login.html';
        return;
    }

    loadDashboard();
    loadUsers();
});

function checkAdminAuth() {
    const token = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('user_info');

    if (token && userInfo) {
        const user = JSON.parse(userInfo);
        if (user.is_admin) {
            document.getElementById('userEmail').textContent = user.email;
            return true;
        } else {
            showAlert('Accès refusé : droits administrateur requis', 'danger');
            return false;
        }
    }
    return false;
}

async function loadDashboard() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/admin/stats/dashboard', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const dashboardStats = await response.json();
            updateDashboardStats(dashboardStats);
            createAnalyticsCharts(dashboardStats);
            loadSystemInfo();
        } else {
            throw new Error('Erreur lors du chargement du dashboard');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement du dashboard', 'danger');
    }
}

function updateDashboardStats(dashboardStats) {
    const stats = dashboardStats.overview;
    document.getElementById('totalUsers').textContent = stats.total_users;
    document.getElementById('totalPredictions').textContent = stats.total_predictions;
    document.getElementById('activeUsers').textContent = stats.active_users;
    document.getElementById('recentUsers').textContent = stats.recent_users;
}

async function loadUsers(page = 1, search = '') {
    try {
        const token = localStorage.getItem('access_token');
        let url = `/admin/users?page=${page}&per_page=10`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const users = await response.json();
            const filteredUsers = users;
            displayUsers(filteredUsers);
            document.getElementById('usersLoadingState').style.display = 'none';
        } else {
            throw new Error('Erreur lors du chargement des utilisateurs');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des utilisateurs', 'danger');
        document.getElementById('usersLoadingState').innerHTML =
            '<p class="text-danger">Erreur lors du chargement</p>';
    }
}

function displayUsers(filteredUsers) {
    const container = document.getElementById('usersList');

    if (filteredUsers.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">Aucun utilisateur trouvé</p>';
        return;
    }

    const usersHTML = filteredUsers.map(user => {
        const joinDate = new Date(user.created_at).toLocaleDateString('fr-FR');
        const statusBadge = user.is_active ?
            '<span class="badge-user">Actif</span>' :
            '<span class="badge-inactive">Inactif</span>';
        const roleBadge = user.is_admin ?
            '<span class="badge-admin">Admin</span>' :
            '<span class="badge-user">Utilisateur</span>';

        return `
            <div class="user-card" onclick="showUserDetails(${user.id})">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="user-email">${user.email}</div>
                        <div class="user-info">
                            <i class="fas fa-calendar me-1"></i>Inscrit le ${joinDate}
                        </div>
                        <div class="mt-2">
                            ${roleBadge}
                            ${statusBadge}
                        </div>
                    </div>
                    <div class="text-end">
                        <button class="btn btn-outline-primary btn-action" onclick="event.stopPropagation(); showUserDetails(${user.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success btn-action" onclick="event.stopPropagation(); toggleUserStatus(${user.id})">
                            <i class="fas fa-toggle-${user.is_active ? 'on' : 'off'}"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="event.stopPropagation(); confirmDeleteUser(${user.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = usersHTML;
}

async function showUserDetails(userId) {
    let selectedUserId = userId;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/admin/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            displayUserDetailsModal(user);
        } else {
            throw new Error('Erreur lors du chargement des détails');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des détails utilisateur', 'danger');
    }
}

function displayUserDetailsModal(user) {
    const joinDate = new Date(user.created_at).toLocaleDateString('fr-FR');
    const lastUpdate = new Date(user.updated_at).toLocaleDateString('fr-FR');
    const predictionsCount = user.predictions ? user.predictions.length : 0;

    const modalBody = document.getElementById('userModalBody');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>Inscrit le:</strong> ${joinDate}</p>
                <p><strong>Dernière mise à jour:</strong> ${lastUpdate}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Status:</strong> ${user.is_active ? 'Actif' : 'Inactif'}</p>
                <p><strong>Rôle:</strong> ${user.is_admin ? 'Admin' : 'Utilisateur'}</p>
                <p><strong>Nombre de prédictions:</strong> ${predictionsCount}</p>
            </div>
        </div>
    `;

    new bootstrap.Modal(document.getElementById('userModal')).show();
}

function createAnalyticsCharts(dashboardStats) {
    const categoryCtx = document.getElementById('categoryDistributionChart').getContext('2d');
    new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(dashboardStats.category_distribution),
            datasets: [{
                data: Object.values(dashboardStats.category_distribution),
                backgroundColor: [
                    '#28a745', '#17a2b8', '#ffc107',
                    '#fd7e14', '#dc3545', '#6f42c1', '#e83e8c'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    const dailyCtx = document.getElementById('dailyPredictionsChart').getContext('2d');
    new Chart(dailyCtx, {
        type: 'line',
        data: {
            labels: dashboardStats.daily_predictions.map(d => new Date(d.date).toLocaleDateString('fr-FR')),
            datasets: [{
                label: 'Prédictions',
                data: dashboardStats.daily_predictions.map(d => d.count),
                borderColor: '#dc3545',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

async function loadSystemInfo() {
    // This is a placeholder for a future implementation
    const modelInfo = document.getElementById('modelInfo');
    modelInfo.innerHTML = '<p>Informations sur le modèle non disponibles.</p>';

    const systemHealth = document.getElementById('systemHealth');
    systemHealth.innerHTML = '<p>État du système non disponible.</p>';

    const databaseStats = document.getElementById('databaseStats');
    databaseStats.innerHTML = '<p>Statistiques de la base de données non disponibles.</p>';
}

function searchUsers() {
    const search = document.getElementById('searchUsers').value;
    loadUsers(1, search);
}

function filterUsers() {
    // This is a placeholder for a future implementation
    console.log("Filtrage des utilisateurs...");
}

function refreshUsers() {
    loadUsers();
}

function confirmDeleteUser(userId) {
    let selectedUserId = userId;
    new bootstrap.Modal(document.getElementById('confirmDeleteModal')).show();
}

async function deleteUser() {
    const selectedUserId = window.selectedUserId;
    if (!selectedUserId) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/admin/users/${selectedUserId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showAlert('Utilisateur supprimé avec succès', 'success');
            bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal')).hide();
            loadUsers();
        } else {
            throw new Error('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression de l'utilisateur', 'danger');
    }
}

async function toggleUserStatus(userId) {
    // This is a placeholder for a future implementation
    console.log("Changement du statut de l'utilisateur", userId);
}

async function toggleAdminStatus(userId) {
    // This is a placeholder for a future implementation
    console.log("Changement des droits de l'utilisateur", userId);
}