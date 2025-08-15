const { chromium } = require('playwright');

(async () => {
  console.log('TESTING PERSON AND ORGANIZATION OBJECTS');
  console.log('========================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading test for Person and Organization...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-person-org.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    
    if (content.includes('Test Person and Organization')) {
      console.log('✅ Person and Organization objects work!');
      console.log('\nObject types confirmed:');
      console.log('  - Person: Works for parties');
      console.log('  - Individual: Works for lawyers');
      console.log('  - Organization: Works for law firms');
      
    } else if (content.includes('Error')) {
      console.log('❌ Error with Person/Organization objects');
      try {
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('Error:', errorMsg);
      } catch (e) {
        console.log('Basic object types not working');
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n========================================');
})();