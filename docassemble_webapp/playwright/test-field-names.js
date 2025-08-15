const { chromium } = require('playwright');

(async () => {
  console.log('Testing Field Names');
  console.log('===================\n');
  
  const browser = await chromium.launch({ headless: false }); // Visual debugging
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Navigate to user info form quickly
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(1000);
    await page.click('button[type="submit"]#da-continue-button'); // MIP info
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Common-law")'); // Relationship
    await page.waitForTimeout(1000);
    await page.click('text=Child support'); // Order
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Skip financial form quickly
    await page.locator('input[type="text"]').first().fill('25000');
    await page.locator('label:has-text("Yes")').first().click();
    await page.locator('label:has-text("No")').nth(1).click();
    await page.locator('label:has-text("No")').nth(2).click();
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Select role
    await page.click('button:has-text("I am starting a new case (Applicant)")');
    await page.waitForTimeout(2000);
    
    console.log('At user info form. Available input fields:');
    const inputs = await page.locator('input').all();
    for (let input of inputs) {
      const name = await input.getAttribute('name');
      const type = await input.getAttribute('type');
      if (name) {
        console.log(`- ${name} (${type})`);
      }
    }
    
    console.log('\nPress Ctrl+C when done examining the form');
    await new Promise(() => {}); // Keep open
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  await browser.close();
})();