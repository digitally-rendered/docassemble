const { chromium } = require('playwright');

(async () => {
  console.log('TESTING DEBUG WIZARD');
  console.log('====================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading debug wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-wizard-debug.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    
    if (content.includes('Welcome to the Ontario Family Law')) {
      console.log('✅ Debug wizard loads!');
      
      // Try to proceed
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const after = await page.content();
      if (after.includes('emergency situation')) {
        console.log('✅ Reached emergency question');
      }
      
    } else if (content.includes('Debug: Error Detected')) {
      console.log('⚠️ Error caught by debug handler!');
      
      // Extract error details
      const errorType = await page.locator('text=Error Type:').locator('..').textContent();
      const errorMsg = await page.locator('code, pre').first().textContent();
      
      console.log('\nError details:');
      console.log(errorType);
      console.log('Message:', errorMsg);
      
    } else if (content.includes('Error')) {
      console.log('❌ System error (not caught by handler)');
      try {
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('System error:', errorMsg);
      } catch (e) {
        console.log('Could not extract error');
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n====================');
  console.log('Debug test complete');
})();