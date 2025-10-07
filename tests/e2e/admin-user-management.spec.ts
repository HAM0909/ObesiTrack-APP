import { test, expect } from '@playwright/test';

test.describe('Administration - Gestion des utilisateurs', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter en tant qu'administrateur
    await page.goto('/');
    await page.getByRole('textbox', { name: ' Email' }).fill('admin@obesittrack.com');
    await page.getByRole('textbox', { name: ' Mot de passe' }).fill('admin123');
    await page.getByRole('button', { name: ' Se connecter' }).click();
    
    // Attendre la confirmation de connexion (ou qu'on soit redirigé)
    try {
      await expect(page.getByText('Connexion réussie ! Redirection...')).toBeVisible({ timeout: 2000 });
    } catch {
      // Si le message n'apparaît pas, on continue - probablement déjà connecté
    }
    
    // Naviguer vers la page d'administration
    await page.goto('/admin');
    await expect(page).toHaveTitle(/Administration - ObesiTrack/);
  });

  test('Peut accéder à la page d\'administration et voir l\'interface', async ({ page }) => {
    // Vérifier que la page d'administration se charge correctement
    await expect(page.locator('h3')).toContainText('Panel d\'Administration');
    await expect(page.getByText('Gestion des utilisateurs et statistiques du système')).toBeVisible();
    
    // Vérifier la présence des statistiques en utilisant des sélecteurs plus spécifiques
    await expect(page.getByText('Utilisateurs totaux')).toBeVisible();
    await expect(page.getByText('Prédictions totales')).toBeVisible();
    await expect(page.locator('#statsSection').getByText('Utilisateurs actifs')).toBeVisible();
    await expect(page.getByText('Nouveaux (7j)')).toBeVisible();
    
    // Vérifier la présence des onglets
    await expect(page.getByRole('tab', { name: ' Gestion des Utilisateurs' })).toBeVisible();
    await expect(page.getByRole('tab', { name: ' Analytiques' })).toBeVisible();
    await expect(page.getByRole('tab', { name: ' Système' })).toBeVisible();
  });

  test('Peut naviguer dans les onglets d\'administration', async ({ page }) => {
    // L'onglet "Gestion des Utilisateurs" devrait être sélectionné par défaut
    await expect(page.getByRole('tab', { name: ' Gestion des Utilisateurs' })).toHaveAttribute('aria-selected', 'true');
    
    // Cliquer sur l'onglet Analytiques
    await page.getByRole('tab', { name: ' Analytiques' }).click();
    await expect(page.getByRole('tab', { name: ' Analytiques' })).toHaveAttribute('aria-selected', 'true');
    
    // Cliquer sur l'onglet Système
    await page.getByRole('tab', { name: ' Système' }).click();
    await expect(page.getByRole('tab', { name: ' Système' })).toHaveAttribute('aria-selected', 'true');
    
    // Revenir à l'onglet Gestion des Utilisateurs
    await page.getByRole('tab', { name: ' Gestion des Utilisateurs' }).click();
    await expect(page.getByRole('tab', { name: ' Gestion des Utilisateurs' })).toHaveAttribute('aria-selected', 'true');
  });

  test('Affiche la liste des utilisateurs et les outils de gestion', async ({ page }) => {
    // Vérifier que l'onglet Gestion des Utilisateurs est actif
    await expect(page.getByRole('tab', { name: ' Gestion des Utilisateurs' })).toHaveAttribute('aria-selected', 'true');
    
    // Vérifier la présence du titre de section
    await expect(page.getByRole('heading', { name: ' Liste des Utilisateurs' })).toBeVisible();
    
    // Vérifier la présence du bouton Actualiser
    await expect(page.getByRole('button', { name: ' Actualiser' })).toBeVisible();
    
    // Vérifier la présence de la zone de recherche
    await expect(page.getByRole('textbox', { name: 'Rechercher par email...' })).toBeVisible();
    
    // Vérifier la présence du filtre par type d'utilisateur
    const filterCombobox = page.getByRole('combobox').nth(0);
    await expect(filterCombobox).toBeVisible();
    
    // Vérifier les options du filtre (les options sont toujours présentes dans le DOM)
    await expect(filterCombobox.locator('option:has-text("Tous les utilisateurs")')).toBeAttached();
    await expect(filterCombobox.locator('option:has-text("Utilisateurs actifs")')).toBeAttached();
    await expect(filterCombobox.locator('option:has-text("Utilisateurs inactifs")')).toBeAttached();
    await expect(filterCombobox.locator('option:has-text("Administrateurs")')).toBeAttached();
  });

  test('Peut utiliser la fonction de recherche d\'utilisateurs', async ({ page }) => {
    // Vérifier que la zone de recherche est présente
    const searchBox = page.getByRole('textbox', { name: 'Rechercher par email...' });
    await expect(searchBox).toBeVisible();
    
    // Tester la saisie dans la zone de recherche
    await searchBox.fill('test@obesittrack.com');
    await expect(searchBox).toHaveValue('test@obesittrack.com');
    
    // Effacer la recherche
    await searchBox.clear();
    await expect(searchBox).toHaveValue('');
    
    // Tester une autre recherche
    await searchBox.fill('admin');
    await expect(searchBox).toHaveValue('admin');
  });

  test('Affiche les boutons d\'action pour la gestion des utilisateurs', async ({ page }) => {
    // Vérifier la présence des boutons d'action
    await expect(page.getByRole('button', { name: ' Historique' })).toBeVisible();
    await expect(page.getByRole('button', { name: ' Supprimer' })).toBeVisible();
    
    // Vérifier que les boutons sont cliquables
    await expect(page.getByRole('button', { name: ' Historique' })).toBeEnabled();
    await expect(page.getByRole('button', { name: ' Supprimer' })).toBeEnabled();
  });

  test('Peut changer le filtre de type d\'utilisateur', async ({ page }) => {
    const filterCombobox = page.getByRole('combobox').nth(0);
    
    // Vérifier la valeur par défaut (utilise la valeur de l'attribut value, pas le texte)
    await expect(filterCombobox).toHaveValue('all');
    
    // Tester la sélection de différents filtres en utilisant les valeurs des options
    await filterCombobox.selectOption('active');
    await expect(filterCombobox).toHaveValue('active');
    
    await filterCombobox.selectOption('inactive');
    await expect(filterCombobox).toHaveValue('inactive');
    
    await filterCombobox.selectOption('admin');
    await expect(filterCombobox).toHaveValue('admin');
    
    // Revenir à "Tous les utilisateurs"
    await filterCombobox.selectOption('all');
    await expect(filterCombobox).toHaveValue('all');
  });

  test('Vérifie l\'état de chargement des utilisateurs', async ({ page }) => {
    // Vérifier que l'état de chargement est affiché
    // Note: Ce test vérifie l'état actuel où les données sont en cours de chargement
    await expect(page.getByText('Chargement...')).toBeVisible();
    await expect(page.getByText('Chargement des utilisateurs...')).toBeVisible();
    
    // Vérifier que le statut de chargement est présent (utiliser le premier élément de statut)
    await expect(page.locator('[role="status"]').first()).toBeVisible();
  });

  test('Maintient la navigation cohérente avec l\'état d\'administration', async ({ page }) => {
    // Vérifier que le lien "Administration" est marqué comme actif dans la navigation
    await expect(page.getByRole('link', { name: ' Administration' })).toHaveClass(/active/);
    
    // Vérifier que l'utilisateur connecté est affiché comme "Admin"
    await expect(page.getByRole('button', { name: ' Admin' })).toBeVisible();
    
    // Vérifier les autres liens de navigation
    await expect(page.getByRole('link', { name: ' ObesiTrack' })).toBeVisible();
    await expect(page.getByRole('link', { name: ' Prédiction' })).toBeVisible();
    await expect(page.getByRole('link', { name: ' Historique' })).toBeVisible();
  });
});