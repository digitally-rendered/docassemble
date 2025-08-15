const { chromium } = require('playwright');

(async () => {
  console.log('CHECKING ERROR DETAILS');
  console.log('======================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard...');
    const response = await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    console.log('Response status:', response.status());
    
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    const title = await page.title();
    
    console.log('Page title:', title);
    
    if (content.includes('Error')) {
      console.log('\n❌ ERROR DETECTED\n');
      
      // Try to get error details
      const bodyText = await page.locator('body').textContent();
      
      // Look for specific error patterns
      if (bodyText.includes('NameError')) {
        const nameMatch = bodyText.match(/NameError[^.]*name '([^']+)'/);
        if (nameMatch) {
          console.log('Undefined name:', nameMatch[1]);
        }
      }
      
      if (bodyText.includes('not defined')) {
        const notDefinedMatch = bodyText.match(/'([^']+)' is not defined/);
        if (notDefinedMatch) {
          console.log('Not defined:', notDefinedMatch[1]);
        }
      }
      
      if (bodyText.includes('province_list')) {
        console.log('⚠️ province_list function not found');
        console.log('Need to define or import province_list()');
      }
      
      if (bodyText.includes('countries_list')) {
        console.log('⚠️ countries_list function not found');
        console.log('Need to define or import countries_list()');
      }
      
      if (bodyText.includes('validate_legal_date')) {
        console.log('⚠️ validate_legal_date function not found');
        console.log('Need to import from ontario-family-law-common.yml');
      }
      
      if (bodyText.includes('validation_error')) {
        console.log('⚠️ validation_error function issue');
      }
      
      // Check for line number
      if (bodyText.includes('line')) {
        const lineMatch = bodyText.match(/line (\d+)/);
        if (lineMatch) {
          console.log('Error at line:', lineMatch[1]);
        }
      }
      
      // Try to find the actual error message
      const errorBlock = await page.locator('blockquote, .alert, .error-message').first();
      if (await errorBlock.count() > 0) {
        const errorText = await errorBlock.textContent();
        console.log('\nFull error message:');
        console.log(errorText);
      }
      
    } else if (content.includes('Welcome')) {
      console.log('✅ Wizard loaded without errors');
    } else {
      console.log('❓ Unexpected content');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n======================');
  console.log('Error check complete');
})();