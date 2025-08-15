const { chromium } = require('playwright');

(async () => {
  console.log('LAWYER BUTTON STATUS CHECK');
  console.log('==========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    const errorCount = await page.locator('h1:has-text("Error")').count();
    if (errorCount > 0) {
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('❌ WIZARD LOAD ERROR:', errorMsg);
      console.log('\nThe lawyer form changes may have introduced a syntax error.');
      console.log('Need to revert to working version and fix the lawyer issue differently.');
    } else {
      console.log('✅ Wizard loads successfully');
      console.log('Lawyer button issue may be fixed - would need full test to confirm');
    }
    
  } catch (error) {
    console.error('❌ Status check error:', error.message);
  }
  
  await browser.close();
})();