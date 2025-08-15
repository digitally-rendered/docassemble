const { chromium } = require('playwright');

(async () => {
  console.log('CHECKING MAIN PAGE ERROR WITH DEBUG');
  console.log('=====================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard with debug features...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    // Check for debug error display
    const content = await page.content();
    
    if (content.includes('Technical Issue Detected')) {
      console.log('⚠️ DEBUG ERROR DETECTED ON MAIN PAGE');
      
      // Extract error details
      const errorDisplay = await page.locator('.error-display, .debug-error, pre, code').allTextContents();
      console.log('\n📋 ERROR DETAILS:');
      errorDisplay.forEach(detail => {
        if (detail.trim()) {
          console.log(detail.substring(0, 500));
        }
      });
      
      // Look for specific error types
      if (content.includes('ModuleNotFoundError')) {
        console.log('\n🔴 MODULE NOT FOUND ERROR');
        const moduleMatch = content.match(/No module named '([^']+)'/);
        if (moduleMatch) {
          console.log(`Missing module: ${moduleMatch[1]}`);
        }
      }
      
      if (content.includes('NameError')) {
        const nameMatch = content.match(/name '([^']+)' is not defined/);
        if (nameMatch) {
          console.log(`\n🔴 UNDEFINED VARIABLE: ${nameMatch[1]}`);
        }
      }
      
      if (content.includes('AttributeError')) {
        console.log('\n🔴 ATTRIBUTE ERROR FOUND');
      }
      
      if (content.includes('line')) {
        const lineMatch = content.match(/line (\d+)/);
        if (lineMatch) {
          console.log(`📍 Error at line ${lineMatch[1]}`);
        }
      }
      
    } else if (content.includes('Error')) {
      console.log('❌ Standard error screen (not debug)');
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('Error message:', errorMsg);
      
    } else if (content.includes('Welcome to the Ontario Family Law')) {
      console.log('✅ Wizard loaded successfully!');
      console.log('The main page is working');
      
    } else {
      console.log('❓ Unexpected content on main page');
      console.log('Page title:', await page.title());
      
      // Check what's on the page
      const headings = await page.locator('h1, h2').allTextContents();
      if (headings.length > 0) {
        console.log('Headings found:', headings);
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n=====================================');
  console.log('Main page error check complete');
})();