import { test, expect } from '@playwright/test';

test.describe('Tests de Sécurité Admin', () => {
  test.beforeEach(async ({ page }) => {
    // Naviguer vers la page de connexion
    await page.goto('http://127.0.0.1:8001/');
  });

  test('SÉCURITÉ RÉSOLUE: Utilisateur non-admin ne peut plus accéder à la page admin', async ({ page }) => {
    // Se connecter avec un utilisateur non-admin
    await page.fill('textbox >> nth=0', 'test@obesittrack.com');
    await page.fill('textbox >> nth=1', 'test123');
    await page.click('button:has-text("Se connecter")');
    
    // Attendre la redirection
    await page.waitForURL(/\/app$/);
    
    // SÉCURITÉ AMÉLIORÉE: Écouter les dialogues d'alerte
    let alertMessage = '';
    page.on('dialog', async dialog => {
      alertMessage = dialog.message();
      await dialog.accept();
    });
    
    // Tenter d'accéder à la page admin directement
    await page.goto('http://127.0.0.1:8001/admin');
    
    // Attendre un peu pour laisser le temps au JavaScript de s'exécuter
    await page.waitForTimeout(1000);
    
    // Vérifier que l'alerte d'accès refusé a été affichée
    expect(alertMessage).toContain('Accès refusé. Seuls les administrateurs peuvent accéder à cette page');
    
    // L'utilisateur devrait être redirigé vers /app après l'alerte
    await expect(page).toHaveURL(/\/app$/);
    
    // L'utilisateur ne doit PAS voir les éléments admin
    await expect(page.locator('h3:has-text("Panel d\'Administration")')).toHaveCount(0);
    
    console.log('✅ SÉCURITÉ VÉRIFIÉE: Utilisateur non-admin bloqué avec succès!');
  });

  test('Vérification que l\'utilisateur admin peut accéder', async ({ page }) => {
    // Se connecter avec l'utilisateur admin
    await page.fill('textbox >> nth=0', 'admin@obesittrack.com');
    await page.fill('textbox >> nth=1', 'admin123');
    await page.click('button:has-text("Se connecter")');
    
    // Attendre la redirection
    await page.waitForURL(/\/app$/);
    
    // Accéder à la page admin
    await page.goto('http://127.0.0.1:8001/admin');
    
    // L'admin devrait pouvoir voir la page
    await expect(page.locator('h3')).toContainText('Panel d\'Administration');
    await expect(page.locator('[role="tab"]').first()).toContainText('Gestion des Utilisateurs');
  });

  test('Test des appels API avec utilisateur non-admin', async ({ page }) => {
    // Se connecter avec utilisateur non-admin
    await page.fill('textbox >> nth=0', 'test@obesittrack.com');
    await page.fill('textbox >> nth=1', 'test123');
    await page.click('button:has-text("Se connecter")');
    
    await page.waitForURL(/\/app$/);
    
    // Tenter d'appeler l'API admin directement
    const response = await page.request.get('http://127.0.0.1:8001/admin/users', {
      headers: {
        'Authorization': `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`
      }
    });
    
    // L'API devrait refuser l'accès (403 Forbidden)
    expect(response.status()).toBe(403);
  });

  test('Test des appels API avec utilisateur admin', async ({ page }) => {
    // Se connecter avec l'admin
    await page.fill('textbox >> nth=0', 'admin@obesittrack.com');
    await page.fill('textbox >> nth=1', 'admin123');
    await page.click('button:has-text("Se connecter")');
    
    await page.waitForURL(/\/app$/);
    
    // L'API admin devrait fonctionner
    const response = await page.request.get('http://127.0.0.1:8001/admin/users', {
      headers: {
        'Authorization': `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`
      }
    });
    
    // L'API devrait autoriser l'accès (200 OK)
    expect(response.status()).toBe(200);
  });
});