import { test, expect } from '@playwright/test';

test('Enhanced intake completes full workflow', async ({ page }) => {
  // Navigate to the enhanced interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_enhanced.yml');
  
  // Wait for page load
  await page.waitForLoadState('networkidle');
  
  // Check title
  await expect(page).toHaveTitle(/Ontario Family Law Common Intake - Enhanced/);
  
  // Continue through introduction
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Emergency check - select no
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
  
  // MIP status - select completed
  await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
  
  // Relationship status - select married
  await page.getByRole('button', { name: /Married/i }).first().click();
  
  // Orders being sought - just continue without selecting any for simplicity
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // User personal info
  await page.fill('input[name*="name.first"]', 'John');
  await page.fill('input[name*="name.last"]', 'Smith');
  await page.fill('input[name*="birthdate"]', '01/01/1980');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // User contact info
  await page.fill('input[name*="address.address"]', '123 Main St');
  await page.fill('input[name*="address.city"]', 'Toronto');
  await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
  await page.fill('input[name*="phone_number"]', '416-555-1234');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Lawyer - select no
  await page.getByRole('button', { name: /No/i }).click();
  
  // Other party info
  await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
  await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Other party contact - just continue (optional fields)
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Other party lawyer - select no
  await page.getByRole('button', { name: /No/i }).click();
  
  // Court info - no existing file
  await page.locator('input[value="False"]').first().check();
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Children - select no
  await page.getByRole('button', { name: /No/i }).click();
  
  // Should reach summary
  await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
  await expect(page.locator('body')).toContainText('John Smith');
  await expect(page.locator('body')).toContainText('Jane Doe');
  await expect(page.locator('body')).toContainText('Self-represented');
  
  console.log('✅ Enhanced intake completed successfully!');
});