const { chromium } = require('playwright');

(async () => {
  console.log('TESTING SIMPLE WIZARD');
  console.log('=====================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading simple test wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-simple-wizard.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    
    if (content.includes('Test Wizard')) {
      console.log('✅ Simple wizard loads successfully!');
      console.log('Individual objects work fine.\n');
      
      // Try to proceed
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const afterContinue = await page.content();
      if (afterContinue.includes('Your Name')) {
        console.log('✅ Form with Individual fields works!');
      }
      
    } else if (content.includes('Error')) {
      console.log('❌ Even simple wizard has error');
      try {
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('Error:', errorMsg);
      } catch (e) {
        console.log('Could not get error details');
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n=====================');
  console.log('Simple test complete');
})();