const { test, expect } = require('@playwright/test');

test('Simple wizard flow test', async ({ page }) => {
  // Navigate to wizard
  await page.goto('/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
  
  // Wait for welcome screen
  await expect(page.locator('h1')).toContainText('Welcome', { timeout: 10000 });
  
  // Click continue on welcome
  await page.click('button:has-text("Continue")');
  
  // Handle emergency question
  await page.waitForSelector('button:has-text("No")', { timeout: 10000 });
  await page.click('button:has-text("No")');
  
  // Handle MIP question
  await page.waitForSelector('button:has-text("Unsure")', { timeout: 10000 });
  await page.click('button:has-text("Unsure")');
  
  // Handle MIP continue
  await page.click('button:has-text("Continue")');
  
  // Handle relationship status
  await page.waitForSelector('button:has-text("Common-law")', { timeout: 10000 });
  await page.click('button:has-text("Common-law")');
  
  // Wait for orders question
  await page.waitForSelector('h1:has-text("orders")', { timeout: 10000 });
  
  // Select custody checkbox
  await page.click('label:has-text("Child custody")');
  
  // Click continue
  await page.click('button:has-text("Continue")');
  
  // Wait for completion
  await page.waitForSelector('h1:has-text("Information Collection Complete")', { timeout: 10000 });
  
  console.log('Test completed successfully!');
});