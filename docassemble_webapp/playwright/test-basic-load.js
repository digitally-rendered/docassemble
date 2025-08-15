const { chromium } = require('playwright');

(async () => {
  console.log('TESTING BASIC WIZARD LOAD');
  console.log('=========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Get page content
    const content = await page.content();
    const title = await page.title();
    
    console.log('Page title:', title);
    
    // Check for various states
    if (content.includes('Welcome to the Ontario Family Law Forms Wizard')) {
      console.log('✅ WIZARD LOADED SUCCESSFULLY!');
      
    } else if (content.includes('Error')) {
      console.log('❌ ERROR ON LOAD');
      
      // Try to get error message
      try {
        const errorText = await page.locator('blockquote').first().textContent();
        console.log('Error message:', errorText);
      } catch (e) {
        // Try alternative error selectors
        const bodyText = await page.locator('body').textContent();
        const errorMatch = bodyText.match(/Error[^.]*\./);
        if (errorMatch) {
          console.log('Error found:', errorMatch[0]);
        }
      }
      
      // Check for specific error patterns
      if (content.includes('reference to a variable')) {
        const varMatch = content.match(/variable '([^']+)'/);
        if (varMatch) {
          console.log('Undefined variable:', varMatch[1]);
        }
      }
      
    } else {
      console.log('❓ UNEXPECTED CONTENT');
      const headings = await page.locator('h1, h2, h3').allTextContents();
      console.log('Headings:', headings);
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n=========================');
  console.log('Basic load test complete');
})();