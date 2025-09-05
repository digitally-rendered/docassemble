import { test, expect } from '@playwright/test';

test('Enhanced intake loads and shows emergency check', async ({ page }) => {
  // Navigate to the enhanced interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_enhanced.yml');
  
  // Wait for page load
  await page.waitForLoadState('networkidle');
  
  // Check title
  await expect(page).toHaveTitle(/Ontario Family Law Common Intake - Enhanced/);
  
  // Look for introduction content
  await expect(page.locator('body')).toContainText('comprehensive intake form');
  await expect(page.locator('body')).toContainText('Emergency situations');
  await expect(page.locator('body')).toContainText('Mandatory Information Program');
  
  // Continue to emergency check
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Should be on emergency check page
  await expect(page.locator('#daMainQuestion')).toContainText('Is this an emergency situation?');
  await expect(page.locator('body')).toContainText('Immediate physical danger');
  
  // Select no emergency
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
  
  // Should proceed to MIP check
  await expect(page.locator('#daMainQuestion')).toContainText('Mandatory Information Program');
  await expect(page.locator('body')).toContainText('free 2-hour session');
});

test('Enhanced intake handles emergency flow', async ({ page }) => {
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_enhanced.yml');
  await page.waitForLoadState('networkidle');
  
  // Continue past intro
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Select emergency
  await page.getByRole('button', { name: /Yes, this is an emergency/i }).click();
  
  // Should show emergency warning
  await expect(page.locator('#daMainQuestion')).toContainText('URGENT: Emergency Filing Required');
  await expect(page.locator('body')).toContainText('Form 8 - Application');
  await expect(page.locator('body')).toContainText('911');
  await expect(page.locator('body')).toContainText('1-866-863-0511');
  
  // Can continue
  await page.getByRole('button', { name: /Continue.*understand/i }).click();
  
  // Should still proceed to MIP
  await expect(page.locator('#daMainQuestion')).toContainText('Mandatory Information Program');
});

test('Enhanced intake collects relationship and orders', async ({ page }) => {
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_enhanced.yml');
  await page.waitForLoadState('networkidle');
  
  // Navigate through initial screens
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
  await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
  
  // Should be on relationship status
  await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
  
  // Select married
  await page.getByRole('button', { name: /Married/i }).click();
  
  // Should show orders page
  await expect(page.locator('#daMainQuestion')).toContainText('What orders are you seeking');
  
  // Should show divorce option for married
  await expect(page.locator('body')).toContainText('Divorce');
  
  // Select some orders
  await page.locator('input[type="checkbox"]').first().check(); // Divorce
  await page.getByLabel(/Child custody/).check();
  await page.getByLabel(/Child support/).check();
  
  // Continue
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Should ask for financial information since support was selected
  await expect(page.locator('#daMainQuestion')).toContainText('Financial Information');
});