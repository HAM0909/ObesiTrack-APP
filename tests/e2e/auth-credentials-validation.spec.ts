import { test, expect } from '@playwright/test';

/**
 * E2E Test: Authentication and Credentials Validation
 * 
 * This test verifies the complete authentication flow including:
 * - Login page accessibility
 * - Demo credential validation  
 * - Successful authentication and redirect
 * - Protected route access after login
 * - Form accessibility after authentication
 * 
 * Scenario: User encounters "Could not validate credentials" and needs to verify auth flow
 */

test.describe('Authentication and Credentials Validation', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8000');
  });

  test('should display login page with demo credentials', async ({ page }) => {
    // Verify login page loads correctly
    await expect(page).toHaveTitle(/Connexion - ObesiTrack/);
    await expect(page.getByRole('heading', { name: 'ObesiTrack' })).toBeVisible();
    
    // Verify demo credentials are displayed
    await expect(page.getByText('admin@obesittrack.com / admin123')).toBeVisible();
    await expect(page.getByText('test@obesittrack.com / test123')).toBeVisible();
    
    // Verify form elements are present
    await expect(page.getByRole('textbox', { name: /Email/ })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /Mot de passe/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Se connecter/ })).toBeVisible();
  });

  test('should successfully authenticate with admin credentials', async ({ page }) => {
    // Fill login form with admin demo credentials
    await page.getByRole('textbox', { name: /Email/ }).fill('admin@obesittrack.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('admin123');
    
    // Submit login form
    await page.getByRole('button', { name: /Se connecter/ }).click();
    
    // Verify success message appears
    await expect(page.getByText('Connexion réussie ! Redirection...')).toBeVisible();
    
    // Wait for redirect and verify we reach the prediction page
    await page.waitForURL('**/app');
    await expect(page).toHaveTitle(/Prédiction d'Obésité - ObesiTrack/);
    await expect(page.getByRole('heading', { name: /Prédiction d'Obésité par IA/ })).toBeVisible();
  });

  test('should successfully authenticate with test user credentials', async ({ page }) => {
    // Fill login form with test user credentials
    await page.getByRole('textbox', { name: /Email/ }).fill('test@obesittrack.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('test123');
    
    // Submit login form
    await page.getByRole('button', { name: /Se connecter/ }).click();
    
    // Verify success message and redirect
    await expect(page.getByText('Connexion réussie ! Redirection...')).toBeVisible();
    await page.waitForURL('**/app');
    await expect(page).toHaveTitle(/Prédiction d'Obésité - ObesiTrack/);
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Try to login with invalid credentials
    await page.getByRole('textbox', { name: /Email/ }).fill('invalid@example.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('wrongpassword');
    
    // Submit login form
    await page.getByRole('button', { name: /Se connecter/ }).click();
    
    // Should remain on login page with error (or handle according to app behavior)
    // Note: This tests the negative case that caused the "Could not validate credentials" error
    await expect(page).toHaveURL('http://localhost:8000/');
  });

  test('should access prediction form after successful authentication', async ({ page }) => {
    // Login with admin credentials
    await page.getByRole('textbox', { name: /Email/ }).fill('admin@obesittrack.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('admin123');
    await page.getByRole('button', { name: /Se connecter/ }).click();
    
    // Wait for redirect to prediction page
    await page.waitForURL('**/app');
    
    // Verify all form sections are accessible
    await expect(page.getByRole('heading', { name: /Informations personnelles/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Habitudes alimentaires/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Activité physique/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Mode de vie/ })).toBeVisible();
    
    // Verify critical form fields are present and accessible
    await expect(page.getByRole('combobox', { name: /Genre/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Âge/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Taille/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Poids/ })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /Antécédents familiaux/ })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /Habitude de fumer/ })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /Surveillance des calories/ })).toBeVisible();
    
    // Verify prediction button is accessible
    await expect(page.getByRole('button', { name: /Analyser avec l'IA/ })).toBeVisible();
  });

  test('should navigate between authenticated pages', async ({ page }) => {
    // Login first
    await page.getByRole('textbox', { name: /Email/ }).fill('admin@obesittrack.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('admin123');
    await page.getByRole('button', { name: /Se connecter/ }).click();
    await page.waitForURL('**/app');
    
    // Navigate to history page
    await page.getByRole('link', { name: /Historique/ }).click();
    await page.waitForURL('**/history');
    
    // Verify history page loads correctly
    await expect(page).toHaveTitle(/Historique - ObesiTrack/);
    
    // Navigate back to prediction page
    await page.getByRole('link', { name: /Prédiction/ }).click();
    await page.waitForURL('**/app');
    await expect(page).toHaveTitle(/Prédiction d'Obésité - ObesiTrack/);
  });

  test('should maintain authentication session across page refreshes', async ({ page }) => {
    // Login and reach prediction page
    await page.getByRole('textbox', { name: /Email/ }).fill('admin@obesittrack.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('admin123');
    await page.getByRole('button', { name: /Se connecter/ }).click();
    await page.waitForURL('**/app');
    
    // Refresh the page
    await page.reload();
    
    // Should still be authenticated and on the prediction page
    await expect(page).toHaveURL(/.*\/app/);
    await expect(page).toHaveTitle(/Prédiction d'Obésité - ObesiTrack/);
    await expect(page.getByRole('heading', { name: /Prédiction d'Obésité par IA/ })).toBeVisible();
  });
});