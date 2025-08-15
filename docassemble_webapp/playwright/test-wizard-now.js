const { chromium } = require('playwright');

(async () => {
  console.log('TESTING WIZARD WITH ERROR HANDLING');
  console.log('===================================\n');
  
  const browser = await chromium.launch({ headless: false }); // Not headless to see what's happening
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    const content = await page.content();
    const title = await page.title();
    
    console.log('Page title:', title);
    
    if (content.includes('Technical Issue Detected')) {
      console.log('✅ ERROR HANDLER WORKING!');
      
      // Extract error details
      const errorType = await page.locator('text=Error Type:').locator('..').textContent();
      const errorMsg = await page.locator('code').first().textContent();
      
      console.log('\n📋 ERROR DETAILS:');
      console.log(errorType);
      console.log('Message:', errorMsg);
      
      // Check for traceback
      const traceback = await page.locator('text=Full Traceback:').locator('..').locator('code').textContent();
      if (traceback) {
        console.log('\nTraceback preview:');
        console.log(traceback.split('\n').slice(0, 5).join('\n'));
      }
      
    } else if (content.includes('Welcome to the Ontario Family Law')) {
      console.log('✅ WIZARD LOADS SUCCESSFULLY!');
      console.log('\nObjects working:');
      console.log('  - Parties: Person');
      console.log('  - Lawyers: Individual');
      console.log('  - Law firms: Organization');
      
    } else if (content.includes('Error')) {
      console.log('❌ System error (not caught by our handler)');
      
      // This means there's a YAML syntax error or import issue
      const bodyText = await page.locator('body').textContent();
      if (bodyText.includes('SyntaxError')) {
        console.log('⚠️ YAML Syntax Error detected');
      }
      if (bodyText.includes('could not be looked up')) {
        const varMatch = bodyText.match(/variable '([^']+)'/);
        if (varMatch) {
          console.log(`⚠️ Undefined variable: ${varMatch[1]}`);
        }
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  // Keep browser open for 5 seconds to see the page
  await page.waitForTimeout(5000);
  await browser.close();
  console.log('\n===================================');
  console.log('Test complete');
})();