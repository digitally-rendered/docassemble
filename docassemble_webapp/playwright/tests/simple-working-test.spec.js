const { test, expect } = require('@playwright/test');

test('Simplified wizard flow - common law custody', async ({ page }) => {
  // Navigate to wizard
  await page.goto('/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
  
  // Welcome screen
  await page.waitForSelector('h1#daMainQuestion', { timeout: 10000 });
  await page.click('button:has-text("Continue")');
  
  // Emergency question - select No
  await page.waitForSelector('button:has-text("No, this is not an emergency")', { timeout: 10000 });
  await page.click('button:has-text("No, this is not an emergency")');
  
  // MIP question - select "not sure"
  await page.waitForSelector('button:has-text("not sure")', { timeout: 10000 });
  await page.click('button:has-text("not sure")');
  
  // MIP info screen - Continue
  await page.waitForSelector('h1:has-text("MIP Session Information")', { timeout: 10000 });
  await page.click('button:has-text("Continue")');
  
  // Relationship status - select Common-law
  await page.waitForSelector('button:has-text("Common-law")', { timeout: 10000 });
  await page.click('button:has-text("Common-law")');
  
  // Orders question - select custody
  await page.waitForSelector('h1:has-text("orders")', { timeout: 10000 });
  await page.click('label:has-text("Child custody")');
  await page.click('button:has-text("Continue")');
  
  // Verify completion
  await page.waitForSelector('h1:has-text("Information Collection Complete")', { timeout: 10000 });
  
  // Verify summary content
  const pageContent = await page.textContent('body');
  expect(pageContent).toContain('Common-law');
  expect(pageContent).toContain('Child custody');
  
  console.log('✓ Test passed - wizard completed successfully');
});