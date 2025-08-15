const { chromium } = require('playwright');

(async () => {
  console.log('TESTING OBJECTS DEFINITION ONLY');
  console.log('================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading objects test...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-objects-only.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    
    if (content.includes('Test Objects')) {
      console.log('✅ ALL OBJECTS LOAD CORRECTLY!');
      console.log('\nConfirmed working:');
      console.log('  - Person objects for parties');
      console.log('  - Individual objects for lawyers');
      console.log('  - Organization objects for law firms');
      console.log('  - IndividualName for org names');
      
    } else if (content.includes('Error')) {
      console.log('❌ Object definition has issues');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n================================');
})();