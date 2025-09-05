import { test, expect } from '@playwright/test';

test('should load common intake working interview', async ({ page }) => {
  // Navigate to the interview using the correct package URL
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_working.yml');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Check for the title
  await expect(page).toHaveTitle(/Ontario Family Law/);
  
  // Look for the introduction text
  await expect(page.locator('body')).toContainText('Ontario Family Law Common Intake');
  await expect(page.locator('body')).toContainText('This interview will collect information');
  
  // Click continue to start the interview
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Verify we're on the personal information page
  await expect(page.locator('h1')).toContainText('Your Personal Information');
  
  // Fill in basic required fields
  await page.fill('input[name*="name.first"]', 'John');
  await page.fill('input[name*="name.last"]', 'Smith');
  
  // Continue to contact information
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Verify we're on contact information page
  await expect(page.locator('h1')).toContainText('Your Contact Information');
  
  // Fill in required address fields
  await page.fill('input[name*="address.address"]', '123 Main Street');
  await page.fill('input[name*="address.city"]', 'Toronto');
  await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
  
  // Continue to legal representation
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Verify we're on legal representation page
  await expect(page.locator('h1')).toContainText('Legal Representation');
  
  // Select no lawyer
  await page.getByRole('button', { name: /No/i }).click();
  
  // Continue to opposing party
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Fill in opposing party info
  await expect(page.locator('h1')).toContainText("Other Party's Information");
  await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
  await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
  
  // Continue to opposing party's legal representation
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Select no lawyer for opposing party
  await expect(page.locator('h1')).toContainText("Other Party's Legal Representation");
  await page.getByLabel('They have a lawyer').check();
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Skip opposing lawyer info (all fields optional)
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Court information
  await expect(page.locator('h1')).toContainText('Court Information');
  await page.getByLabel('Is there an existing court file?').first().check(); // Yes
  
  // Fill court details
  await page.selectOption('select[name*="court.name"]', 'Superior Court of Justice');
  await page.fill('input[name*="court.location"]', 'Toronto');
  await page.fill('input[name*="court.file_number"]', 'CV-2024-123456');
  
  // Continue to summary
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Verify we're on the summary page
  await expect(page.locator('h1')).toContainText('Information Collected');
  await expect(page.locator('body')).toContainText('John Smith');
  await expect(page.locator('body')).toContainText('123 Main Street');
  await expect(page.locator('body')).toContainText('Toronto');
  await expect(page.locator('body')).toContainText('Self-represented');
  await expect(page.locator('body')).toContainText('Jane Doe');
  await expect(page.locator('body')).toContainText('Superior Court of Justice');
  await expect(page.locator('body')).toContainText('CV-2024-123456');
});

test('should handle validation in working interview', async ({ page }) => {
  // Navigate to the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_working.yml');
  
  await page.waitForLoadState('networkidle');
  
  // Click continue to get to personal info
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Try to continue without filling required fields
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Should show validation errors
  await expect(page.locator('body')).toContainText(/required|Please/i);
});