const { test, expect } = require('@playwright/test');

test('Debug wizard flow', async ({ page }) => {
  // Enable console logging
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  
  // Navigate to wizard
  await page.goto('/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
  
  // Wait for welcome screen - use more specific selector
  await expect(page.locator('h1#daMainQuestion')).toContainText('Welcome', { timeout: 10000 });
  console.log('✓ Welcome screen loaded');
  
  // Click continue on welcome
  await page.click('button:has-text("Continue")');
  
  // Handle emergency question
  await page.waitForSelector('button:has-text("No")', { timeout: 10000 });
  console.log('✓ Emergency question appeared');
  await page.click('button:has-text("No")');
  
  // Handle MIP question
  await page.waitForSelector('button:has-text("not sure")', { timeout: 10000 });
  console.log('✓ MIP question appeared');
  await page.click('button:has-text("not sure")');
  
  // Handle MIP continue
  await page.waitForSelector('button:has-text("Continue")', { timeout: 10000 });
  console.log('✓ MIP info screen appeared');
  await page.click('button:has-text("Continue")');
  
  // Handle relationship status
  await page.waitForSelector('button:has-text("Common-law")', { timeout: 10000 });
  console.log('✓ Relationship status question appeared');
  await page.click('button:has-text("Common-law")');
  
  // Wait for orders question to load
  await page.waitForTimeout(2000);
  
  // Check what's on screen
  const h1Text = await page.locator('h1#daMainQuestion').textContent();
  console.log('Current H1:', h1Text);
  
  // Check if we're on orders question
  if (h1Text.includes('orders')) {
    console.log('✓ Orders question appeared');
    
    // Take screenshot before clicking
    await page.screenshot({ path: 'debug-before-checkbox.png' });
    
    // Try to select custody checkbox
    const checkboxLabel = page.locator('label:has-text("Child custody")');
    if (await checkboxLabel.isVisible()) {
      console.log('Found custody checkbox label');
      await checkboxLabel.click();
      console.log('✓ Clicked custody checkbox');
    } else {
      console.log('❌ Could not find custody checkbox');
    }
    
    // Take screenshot after clicking checkbox
    await page.screenshot({ path: 'debug-after-checkbox.png' });
    
    // Click continue
    await page.click('button:has-text("Continue")');
    console.log('✓ Clicked continue after orders');
    
    // Wait and see what happens next
    await page.waitForTimeout(3000);
    
    // Check what screen we're on now
    const nextH1 = await page.locator('h1#daMainQuestion').textContent();
    console.log('Next screen H1:', nextH1);
    
    // Take screenshot of next screen
    await page.screenshot({ path: 'debug-next-screen.png' });
    
    // Check if there's an error message
    const errorMessage = page.locator('.da-has-error, .error-message, .alert-danger');
    if (await errorMessage.count() > 0) {
      const errorText = await errorMessage.textContent();
      console.log('ERROR FOUND:', errorText);
    }
  } else {
    console.log('❌ Not on orders question, got:', h1Text);
  }
});