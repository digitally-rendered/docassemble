import { test, expect } from '@playwright/test';

test('Debug interview flow - find where children question appears', async ({ page }) => {
  console.log('Starting debug test to find children question...');
  
  // Navigate to the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_final.yml');
  await page.waitForLoadState('networkidle');
  
  // Track each page
  let pageNumber = 1;
  
  // Page 1: Introduction
  let pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Page 2: Emergency
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
  
  // Page 3: MIP
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
  await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
  
  // Page 4: Relationship
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
  await page.getByRole('button', { name: /Married/i }).first().click();
  
  // Page 5: What comes next?
  await page.waitForTimeout(1000);
  pageText = await page.locator('#daMainQuestion').textContent();
  console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
  
  // Check if this is orders or children
  if (pageText?.includes('orders')) {
    console.log('⚠️ ISSUE: Orders page appeared immediately after relationship status');
    console.log('⚠️ Children question was SKIPPED!');
    
    // Let's continue to see where children question appears
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Next page
    pageText = await page.locator('#daMainQuestion').textContent();
    console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
    
    // Continue through personal info
    if (pageText?.includes('Personal Information')) {
      const inputs = page.locator('input[type="text"]');
      await inputs.nth(0).fill('Test');
      await inputs.nth(2).fill('User');  
      await inputs.nth(3).fill('01/01/1980');
      await page.getByRole('button', { name: /Continue/i }).click();
      
      pageText = await page.locator('#daMainQuestion').textContent();
      console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
    }
    
    // Continue through contact
    if (pageText?.includes('Contact Information')) {
      const inputs = page.locator('input[type="text"]:visible');
      await inputs.nth(0).fill('123 Main St');
      await inputs.nth(2).fill('Toronto');
      await inputs.nth(4).fill('M5H2N2');
      await inputs.nth(5).fill('4165551234');
      await page.getByRole('button', { name: /Continue/i }).click();
      
      pageText = await page.locator('#daMainQuestion').textContent();
      console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
    }
    
    // Continue for next 5 pages to find children
    for (let i = 0; i < 5; i++) {
      if (pageText?.includes('children')) {
        console.log(`✅ FOUND IT! Children question appears at page ${pageNumber - 1}`);
        break;
      }
      
      // Try to continue
      const hasNoButton = await page.getByRole('button', { name: /^No$/i }).isVisible().catch(() => false);
      const hasContinueButton = await page.getByRole('button', { name: /Continue/i }).isVisible().catch(() => false);
      
      if (hasNoButton) {
        await page.getByRole('button', { name: /^No$/i }).click();
      } else if (hasContinueButton) {
        await page.getByRole('button', { name: /Continue/i }).click();
      } else {
        console.log('No buttons found to continue');
        break;
      }
      
      await page.waitForTimeout(500);
      pageText = await page.locator('#daMainQuestion').textContent();
      console.log(`Page ${pageNumber++}: ${pageText?.substring(0, 50)}...`);
    }
  } else if (pageText?.includes('children')) {
    console.log('✅ SUCCESS: Children question appeared right after relationship status as expected!');
  }
});