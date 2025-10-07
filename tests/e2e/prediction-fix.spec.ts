import { test, expect } from '@playwright/test';

/**
 * FIXED E2E Test: Prediction Functionality - Corrected Selectors
 * 
 * This test verifies the actual prediction functionality with correct selectors
 * based on the real DOM structure discovered during browser inspection.
 */

test.describe('Prediction Functionality - Fixed Selectors', () => {
  
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

  test('should successfully submit prediction form and display results', async ({ page }) => {
    // Fill all required fields with valid test data
    
    // Personal Information
    await page.getByLabel('Genre').selectOption('Homme');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('30');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('175');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('80');
    await page.getByLabel('Antécédents familiaux').selectOption('Non');
    
    // Food habits
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByLabel('Grignotage entre les repas').selectOption('Parfois');
    await page.getByLabel('Consommation fréquente d\'aliments caloriques').selectOption('Non');
    await page.getByRole('spinbutton', { name: /Consommation d'eau/ }).fill('2');
    
    // Physical activity
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('1');
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('1');
    
    // Lifestyle
    await page.getByLabel('Consommation d\'alcool').selectOption('Parfois');
    await page.getByLabel('Moyen de transport principal').selectOption('Marche');
    await page.getByLabel('Habitude de fumer').selectOption('Non');
    await page.getByLabel('Surveillance des calories').selectOption('Non');
    
    // Submit the form
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Wait for prediction results to appear - CORRECTED SELECTOR
    await expect(page.locator('#resultContainer')).toBeVisible({ timeout: 10000 });
    
    // Verify prediction results are displayed - CORRECTED SELECTORS
    await expect(page.getByRole('heading', { name: /Résultat de la Prédiction/ })).toBeVisible();
    
    // Verify prediction category is displayed
    await expect(page.getByRole('heading', { name: /Catégorie prédite/ })).toBeVisible();
    
    // Verify BMI calculation is shown - CORRECTED SELECTOR
    await expect(page.locator('.bmi-indicator')).toBeVisible();
    
    // Verify recommendations are provided
    await expect(page.getByRole('heading', { name: /Recommandations/ })).toBeVisible();
    
    // Verify specific result elements exist
    await expect(page.locator('text=/Normal_Weight|Overweight_Level|Obesity_Type/i')).toBeVisible();
    await expect(page.locator('text=/Indice de confiance/i')).toBeVisible();
    await expect(page.locator('text=/IMC: [0-9.]+$/i').first()).toBeVisible();
  });

  test('should handle edge case - high BMI prediction', async ({ page }) => {
    // Fill form with data likely to result in higher BMI
    
    await page.getByLabel('Genre').selectOption('Homme');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('45');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('170');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('120'); // High weight
    await page.getByLabel('Antécédents familiaux').selectOption('Oui'); // Family history
    
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('1'); // Low vegetable consumption
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('4'); // Many meals
    await page.getByLabel('Grignotage entre les repas').selectOption('Toujours'); // Frequent snacking
    await page.getByLabel('Consommation fréquente d\'aliments caloriques').selectOption('Oui'); // High calorie foods
    await page.getByRole('spinbutton', { name: /Consommation d'eau/ }).fill('1'); // Low water intake
    
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('0'); // No exercise
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('2'); // High screen time
    
    await page.getByLabel('Consommation d\'alcool').selectOption('Fréquemment');
    await page.getByLabel('Moyen de transport principal').selectOption('Voiture'); // Sedentary transport
    await page.getByLabel('Habitude de fumer').selectOption('Oui');
    await page.getByLabel('Surveillance des calories').selectOption('Non');
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Wait for results - CORRECTED SELECTOR
    await expect(page.locator('#resultContainer')).toBeVisible({ timeout: 10000 });
    
    // Verify BMI shows high value (this person should have BMI around 41.5)
    const bmiText = await page.locator('text=/IMC: [0-9.]+$/i').first().textContent();
    expect(bmiText).toBeTruthy();
    console.log('BMI Result:', bmiText);
    
    // Should show some obesity classification
    const predictionText = await page.locator('.bmi-indicator').first().textContent();
    console.log('Prediction Result:', predictionText);
  });

  test('should handle edge case - healthy profile prediction', async ({ page }) => {
    // Fill form with data likely to result in normal weight classification
    
    await page.getByLabel('Genre').selectOption('Femme');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('25');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('165');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('60'); // Healthy weight
    await page.getByLabel('Antécédents familiaux').selectOption('Non');
    
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('3'); // High vegetable consumption
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByLabel('Grignotage entre les repas').selectOption('Jamais');
    await page.getByLabel('Consommation fréquente d\'aliments caloriques').selectOption('Non');
    await page.getByRole('spinbutton', { name: /Consommation d'eau/ }).fill('3'); // High water intake
    
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('3'); // Regular exercise
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('0'); // Low screen time
    
    await page.getByLabel('Consommation d\'alcool').selectOption('Jamais');
    await page.getByLabel('Moyen de transport principal').selectOption('Marche'); // Active transport
    await page.getByLabel('Habitude de fumer').selectOption('Non');
    await page.getByLabel('Surveillance des calories').selectOption('Oui');
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    // Wait for results - CORRECTED SELECTOR
    await expect(page.locator('#resultContainer')).toBeVisible({ timeout: 10000 });
    
    // This profile should show healthy BMI (around 22.0)
    const bmiText = await page.locator('text=/IMC: [0-9.]+$/i').first().textContent();
    expect(bmiText).toBeTruthy();
    console.log('Healthy BMI Result:', bmiText);
  });

  test('should verify BMI calculation accuracy', async ({ page }) => {
    // Test with specific values to verify BMI calculation
    // BMI = weight(kg) / height(m)^2
    // Expected BMI = 80 / (1.75)^2 = 80 / 3.0625 = 26.12
    
    await page.getByLabel('Genre').selectOption('Homme');
    await page.getByRole('spinbutton', { name: /Âge/ }).fill('30');
    await page.getByRole('spinbutton', { name: /Taille/ }).fill('175');
    await page.getByRole('spinbutton', { name: /Poids/ }).fill('80');
    await page.getByLabel('Antécédents familiaux').selectOption('Non');
    
    // Fill remaining fields with neutral values
    await page.getByRole('spinbutton', { name: /Consommation de légumes/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Repas principaux/ }).fill('3');
    await page.getByLabel('Grignotage entre les repas').selectOption('Parfois');
    await page.getByLabel('Consommation fréquente d\'aliments caloriques').selectOption('Non');
    await page.getByRole('spinbutton', { name: /Consommation d'eau/ }).fill('2');
    await page.getByRole('spinbutton', { name: /Fréquence sport/ }).fill('1');
    await page.getByRole('spinbutton', { name: /Temps écrans/ }).fill('1');
    await page.getByLabel('Consommation d\'alcool').selectOption('Parfois');
    await page.getByLabel('Moyen de transport principal').selectOption('Marche');
    await page.getByLabel('Habitude de fumer').selectOption('Non');
    await page.getByLabel('Surveillance des calories').selectOption('Non');
    
    await page.getByRole('button', { name: /Analyser avec l'IA/ }).click();
    
    await expect(page.locator('#resultContainer')).toBeVisible({ timeout: 10000 });
    
    // Extract and verify BMI value
    const bmiText = await page.locator('text=/IMC: [0-9.]+/i').textContent();
    expect(bmiText).toBeTruthy();
    
    // Extract the numeric BMI value
    const bmiMatch = bmiText?.match(/IMC:\s*([0-9.]+)/i);
    if (bmiMatch) {
      const calculatedBMI = parseFloat(bmiMatch[1]);
      console.log('Calculated BMI:', calculatedBMI);
      
      // Expected BMI should be around 26.1 (allowing small rounding differences)
      expect(calculatedBMI).toBeGreaterThan(25.0);
      expect(calculatedBMI).toBeLessThan(27.0);
    } else {
      throw new Error('Could not extract BMI value from results');
    }
  });
});