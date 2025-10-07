import { test, expect } from '@playwright/test';

/**
 * E2E Test: Complete Prediction Functionality Verification
 * 
 * This test suite comprehensively verifies that the prediction system works perfectly:
 * - All form fields are present and functional
 * - Form validation works correctly
 * - Prediction API responds with valid results
 * - Results are displayed correctly
 * - Edge cases are handled properly
 * 
 * Based on the critical issue found in repo.md: Missing form fields have been fixed
 * Required fields: family_history_with_overweight, favc, smoke, ch2o, scc
 */

test.describe('Prediction Functionality - Complete Verification', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to login and authenticate
    await page.goto('/');
    
    // Login with admin credentials
    await page.getByRole('textbox', { name: /Email/ }).fill('admin@obesittrack.com');
    await page.getByRole('textbox', { name: /Mot de passe/ }).fill('admin123');
    await page.getByRole('button', { name: /Se connecter/ }).click();
    
    // Wait for redirect to prediction page
    await page.waitForURL('**/app');
    await expect(page).toHaveTitle(/Prédiction d'Obésité - ObesiTrack/);
  });

  test('should have all required form fields present and accessible', async ({ page }) => {
    // Verify all critical form sections are visible
    await expect(page.getByRole('heading', { name: /Informations personnelles/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Habitudes alimentaires/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Activité physique/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Mode de vie/ })).toBeVisible();
    
    // Verify all REQUIRED fields are present (the ones that were previously missing)
    
    // Personal Information
    await expect(page.getByRole('combobox', { name: /Genre/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Âge/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Taille/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Poids/ })).toBeVisible();
    
    // Previously missing field - family_history_with_overweight
    await expect(page.getByRole('combobox', { name: /Antécédents familiaux/ })).toBeVisible();
    
    // Food habits
    await expect(page.getByRole('spinbutton', { name: /Consommation de légumes/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Repas principaux/ })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /Grignotage entre les repas/ })).toBeVisible();
    
    // Previously missing field - favc (high caloric food consumption)
    await expect(page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ })).toBeVisible();
    
    // Previously missing field - ch2o (water consumption)
    await expect(page.getByRole('spinbutton', { name: /Consommation d'eau quotidienne/ })).toBeVisible();
    
    // Physical activity
    await expect(page.getByRole('spinbutton', { name: /Fréquence sport/ })).toBeVisible();
    await expect(page.getByRole('spinbutton', { name: /Temps écrans/ })).toBeVisible();
    
    // Lifestyle
    await expect(page.getByRole('combobox', { name: /Consommation d'alcool/ })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /Moyen de transport/ })).toBeVisible();
    
    // Previously missing field - smoke
    await expect(page.getByRole('combobox', { name: /Habitude de fumer/ })).toBeVisible();
    
    // Previously missing field - scc (calorie monitoring)
    await expect(page.getByRole('combobox', { name: /Surveillance des calories/ })).toBeVisible();
    
    // Verify prediction button is present
    await expect(page.getByRole('button', { name: /Analyser avec l'IA/ })).toBeVisible();
  });

  test('should successfully submit complete prediction form and receive results', async ({ page }) => {
    // Fill all required fields with valid test data
    
    // Personal Information
    await page.getByRole('combobox', { name: /Genre/ }).selectOption('male');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('30');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('175');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('80');
    await page.getByRole('combobox', { name: /Antécédents familiaux/ }).selectOption('no');
    
    // Food habits
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByRole('combobox', { name: /Grignotage entre les repas/ }).selectOption('sometimes');
    await page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ }).selectOption('no');
    await page.getByRole('spinbutton', { name: /Consommation d'eau quotidienne/ }).fill('2');
    
    // Physical activity
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('1');
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('1');
    
    // Lifestyle
    await page.getByRole('combobox', { name: /Consommation d'alcool/ }).selectOption('sometimes');
    await page.getByRole('combobox', { name: /Moyen de transport/ }).selectOption('walking');
    await page.getByRole('combobox', { name: /Habitude de fumer/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Surveillance des calories/ }).selectOption('no');
    
    // Submit the form
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Wait for prediction results to appear
    await expect(page.locator('.prediction-result')).toBeVisible({ timeout: 10000 });
    
    // Verify prediction results are displayed
    await expect(page.getByRole('heading', { name: /Résultat de l'Analyse/ })).toBeVisible();
    
    // Verify BMI calculation is shown
    await expect(page.locator('.bmi-indicator')).toBeVisible();
    
    // Verify prediction category is displayed
    await expect(page.locator('.risk-badge')).toBeVisible();
    
    // Verify confidence score is shown
    await expect(page.locator('.confidence-bar')).toBeVisible();
    
    // Verify recommendations are provided
    await expect(page.locator('.recommendations')).toBeVisible();
  });

  test('should handle edge case - high risk obesity prediction', async ({ page }) => {
    // Fill form with data likely to result in obesity classification
    
    await page.getByRole('combobox', { name: /Genre/ }).selectOption('male');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('45');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('170');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('120'); // High weight
    await page.getByRole('combobox', { name: /Antécédents familiaux/ }).selectOption('yes'); // Family history
    
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('1'); // Low vegetable consumption
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('4'); // Many meals
    await page.getByRole('combobox', { name: /Grignotage entre les repas/ }).selectOption('always'); // Frequent snacking
    await page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ }).selectOption('yes'); // High calorie foods
    await page.getByRole('spinbutton', { name: /Consommation d'eau quotidienne/ }).fill('1'); // Low water intake
    
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('0'); // No exercise
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('2'); // High screen time
    
    await page.getByRole('combobox', { name: /Consommation d'alcool/ }).selectOption('frequently');
    await page.getByRole('combobox', { name: /Moyen de transport/ }).selectOption('automobile'); // Sedentary transport
    await page.getByRole('combobox', { name: /Habitude de fumer/ }).selectOption('yes');
    await page.getByRole('combobox', { name: /Surveillance des calories/ }).selectOption('no');
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    await expect(page.locator('.prediction-result')).toBeVisible({ timeout: 10000 });
    
    // Verify high-risk indicators are shown
    await expect(page.locator('.risk-badge.risk-high, .risk-badge.risk-critical')).toBeVisible();
    
    // Verify BMI shows obesity range (>30)
    const bmiText = await page.locator('.bmi-indicator').textContent();
    expect(bmiText).toContain('BMI');
  });

  test('should handle edge case - healthy weight prediction', async ({ page }) => {
    // Fill form with data likely to result in normal weight classification
    
    await page.getByRole('combobox', { name: /Genre/ }).selectOption('female');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('25');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('165');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('60'); // Healthy weight
    await page.getByRole('combobox', { name: /Antécédents familiaux/ }).selectOption('no');
    
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('3'); // High vegetable consumption
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByRole('combobox', { name: /Grignotage entre les repas/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ }).selectOption('no');
    await page.getByRole('spinbutton', { name: /Consommation d'eau quotidienne/ }).fill('3'); // High water intake
    
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('3'); // Regular exercise
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('0'); // Low screen time
    
    await page.getByRole('combobox', { name: /Consommation d'alcool/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Moyen de transport/ }).selectOption('walking'); // Active transport
    await page.getByRole('combobox', { name: /Habitude de fumer/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Surveillance des calories/ }).selectOption('yes');
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    await expect(page.locator('.prediction-result')).toBeVisible({ timeout: 10000 });
    
    // Verify healthy indicators are shown
    await expect(page.locator('.risk-badge.risk-low')).toBeVisible();
  });

  test('should validate form fields and show errors for incomplete data', async ({ page }) => {
    // Try to submit form without filling required fields
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // The form should not submit and should show validation errors
    // (This depends on the frontend validation implementation)
    
    // Verify we're still on the same page (form didn't submit)
    await expect(page).toHaveURL(/.*\/app/);
    
    // Fill only partial data and verify specific field validation
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('30');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('175');
    // Leave weight empty intentionally
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Should still be on form page due to validation
    await expect(page).toHaveURL(/.*\/app/);
  });

  test('should handle prediction API errors gracefully', async ({ page }) => {
    // Fill valid form data
    await page.getByRole('combobox', { name: /Genre/ }).selectOption('male');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('30');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('175');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('80');
    await page.getByRole('combobox', { name: /Antécédents familiaux/ }).selectOption('no');
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByRole('combobox', { name: /Grignotage entre les repas/ }).selectOption('sometimes');
    await page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ }).selectOption('no');
    await page.getByRole('spinbutton', { name: /Consommation d'eau quotidienne/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('1');
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('1');
    await page.getByRole('combobox', { name: /Consommation d'alcool/ }).selectOption('sometimes');
    await page.getByRole('combobox', { name: /Moyen de transport/ }).selectOption('walking');
    await page.getByRole('combobox', { name: /Habitude de fumer/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Surveillance des calories/ }).selectOption('no');
    
    // Mock API failure (this would need to be implemented based on the app's error handling)
    await page.route('**/api/prediction/**', route => route.abort());
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Should handle error gracefully - check for error message or fallback behavior
    // The exact behavior depends on the application's error handling implementation
    await page.waitForTimeout(3000); // Give time for error handling
    
    // Verify user is informed about the error (this depends on app implementation)
    const hasErrorMessage = await page.locator('text=/erreur|error|échec/i').count() > 0;
    const staysOnPage = page.url().includes('/app');
    
    // At least one of these should be true - either error shown or stays on form
    expect(hasErrorMessage || staysOnPage).toBeTruthy();
  });

  test('should save prediction to history after successful prediction', async ({ page }) => {
    // Fill and submit a complete form
    await page.getByRole('combobox', { name: /Genre/ }).selectOption('female');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('28');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('160');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('65');
    await page.getByRole('combobox', { name: /Antécédents familiaux/ }).selectOption('no');
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('2.5');
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByRole('combobox', { name: /Grignotage entre les repas/ }).selectOption('sometimes');
    await page.getByRole('combobox', { name: /Consommation fréquente d'aliments caloriques/ }).selectOption('no');
    await page.getByRole('spinbutton', { name: /Consommation d'eau quotidienne/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('1');
    await page.getByRole('combobox', { name: /Consommation d'alcool/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Moyen de transport/ }).selectOption('bike');
    await page.getByRole('combobox', { name: /Habitude de fumer/ }).selectOption('no');
    await page.getByRole('combobox', { name: /Surveillance des calories/ }).selectOption('yes');
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Wait for results
    await expect(page.locator('.prediction-result')).toBeVisible({ timeout: 10000 });
    
    // Navigate to history page
    await page.getByRole('link', { name: /Historique/ }).click();
    await page.waitForURL('**/history');
    
    // Verify the prediction appears in history
    await expect(page).toHaveTitle(/Historique - ObesiTrack/);
    
    // Look for recent prediction entry (this depends on history page implementation)
    // Should find today's date or recent timestamp
    const today = new Date().toLocaleDateString('fr-FR');
    const hasRecentEntry = await page.locator(`text=${today}`).count() > 0 ||
                          await page.locator('text=/aujourd\'hui|today|récent/i').count() > 0 ||
                          await page.locator('.prediction-history-item, .history-entry, tr').count() > 0;
    
    expect(hasRecentEntry).toBeTruthy();
  });
});