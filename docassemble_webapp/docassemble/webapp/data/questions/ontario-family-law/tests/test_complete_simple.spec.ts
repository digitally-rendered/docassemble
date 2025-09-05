import { test, expect } from '@playwright/test';

test('should load complete intake interview', async ({ page }) => {
  // Navigate to the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_complete.yml');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Check for the title
  await expect(page).toHaveTitle(/Ontario Family Law/);
  
  // Look for the introduction text
  await expect(page.locator('body')).toContainText('Ontario Family Law Common Intake');
  await expect(page.locator('body')).toContainText('collects information commonly needed');
  
  // Verify continue button exists
  await expect(page.getByRole('button', { name: /Continue/i })).toBeVisible();
});