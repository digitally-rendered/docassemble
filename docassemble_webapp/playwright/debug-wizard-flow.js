const { chromium } = require('playwright');

async function debugWizardFlow() {
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const page = await browser.newPage();
  
  try {
    console.log('1. Navigating to wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Check if we have an error
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    if (errorHeading > 0) {
      const errorMessage = await page.locator('blockquote').textContent();
      console.log('ERROR: Wizard failed to load:', errorMessage);
      return;
    }
    
    console.log('2. On welcome screen...');
    await page.screenshot({ path: 'debug-step1-welcome.png' });
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    console.log('3. Emergency question...');
    await page.screenshot({ path: 'debug-step2-emergency.png' });
    // Click "No" for emergency
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    console.log('4. MIP question...');
    await page.screenshot({ path: 'debug-step3-mip.png' });
    // Click "Yes, I have my certificate"
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    
    console.log('5. MIP information screen...');
    await page.screenshot({ path: 'debug-step4-mip-info.png' });
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    console.log('6. Relationship status...');
    await page.screenshot({ path: 'debug-step5-relationship.png' });
    // Click "Common-law"
    await page.click('button:has-text("Common-law")');
    await page.waitForTimeout(1000);
    
    console.log('7. Orders sought...');
    await page.screenshot({ path: 'debug-step6-orders.png' });
    const questionText = await page.locator('#daMainQuestion').textContent();
    console.log('Question text:', questionText);
    
    // Try to click on checkbox for child custody
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    console.log('Found', checkboxes.length, 'checkboxes');
    
    // Click the first checkbox (should be Child custody)
    if (checkboxes.length > 0) {
      await checkboxes[0].click();
      console.log('Clicked first checkbox');
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    console.log('8. Next screen...');
    await page.screenshot({ path: 'debug-step7-next.png' });
    const nextQuestion = await page.locator('#daMainQuestion').textContent();
    console.log('Next question:', nextQuestion);
    
  } catch (error) {
    console.error('Error during debug:', error);
    await page.screenshot({ path: 'debug-error.png' });
  } finally {
    await browser.close();
  }
}

debugWizardFlow().catch(console.error);