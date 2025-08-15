const { chromium } = require('playwright');

(async () => {
  console.log('TESTING WIZARD WITHOUT VALIDATION');
  console.log('==================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard without validation...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard-no-validation.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    const title = await page.title();
    
    console.log('Page title:', title);
    
    if (content.includes('Welcome to the Ontario Family Law')) {
      console.log('✅ WIZARD LOADS WITHOUT VALIDATION!');
      console.log('\nThe validation code is causing the issue.');
    } else if (content.includes('Error')) {
      console.log('❌ Still has error even without validation');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n==================================');
})();