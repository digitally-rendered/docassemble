import { test, expect } from '@playwright/test';

test('should load common intake interview', async ({ page }) => {
  // Try to load the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/common_intake.yml');
  
  // Take screenshot for debugging
  await page.screenshot({ path: 'interview-load.png', fullPage: true });
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Check if we have the expected content
  const title = await page.title();
  console.log('Page title:', title);
  
  const bodyText = await page.textContent('body');
  console.log('Page contains text:', bodyText?.substring(0, 500));
  
  // Look for the introduction text
  await expect(page.locator('body')).toContainText('Ontario Family Law');
});