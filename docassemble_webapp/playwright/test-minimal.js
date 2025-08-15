const { chromium } = require('playwright');

(async () => {
  console.log('TESTING MINIMAL WIZARD');
  console.log('======================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading minimal wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-wizard-minimal.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    
    if (content.includes('Welcome to the Ontario Family Law')) {
      console.log('✅ Minimal wizard loads!');
      console.log('The issue is in the complex validation or includes\n');
    } else if (content.includes('Error')) {
      console.log('❌ Even minimal wizard fails');
      const bodyText = await page.locator('body').textContent();
      if (bodyText.includes('not found')) {
        console.log('File not found error');
      } else {
        console.log('Other error');
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('======================');
})();