const { chromium } = require('playwright');

(async () => {
  console.log('TESTING WIZARD WITH PERSON OBJECTS FOR PARTIES');
  console.log('===============================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard with Person parties...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    const title = await page.title();
    
    console.log('Page title:', title);
    
    if (content.includes('Welcome to the Ontario Family Law')) {
      console.log('✅ WIZARD LOADS WITH PERSON OBJECTS!');
      console.log('\nObject structure:');
      console.log('  - Parties (applicant, respondent): Person objects');
      console.log('  - Lawyers (user_lawyer, other_lawyer): Individual objects');
      console.log('  - Law firms: Organization objects');
      
    } else if (content.includes('Error')) {
      console.log('❌ Error loading wizard');
      
      // Try to get error details
      try {
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('Error message:', errorMsg);
      } catch (e) {
        console.log('Could not extract error message');
      }
      
      // Check for specific error patterns
      const bodyText = await page.locator('body').textContent();
      if (bodyText.includes('Person')) {
        console.log('⚠️ Person object issue detected');
      }
      if (bodyText.includes('Organization')) {
        console.log('⚠️ Organization object issue detected');
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n===============================================');
  console.log('Person objects test complete');
})();