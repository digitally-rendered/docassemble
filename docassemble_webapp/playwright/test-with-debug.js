const { chromium } = require('playwright');

(async () => {
  console.log('TESTING WIZARD WITH DEBUG FEATURES');
  console.log('===================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('1. Loading wizard with debug enabled...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    // Check for initial errors
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    const technicalIssue = await page.locator('text=Technical Issue Detected').count();
    
    if (errorHeading > 0) {
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('❌ Initial error:', errorMsg);
      
      // Look for debug details
      const debugInfo = await page.locator('.debug-info, .traceback, pre').allTextContents();
      if (debugInfo.length > 0) {
        console.log('\n📋 DEBUG DETAILS:');
        debugInfo.forEach(info => {
          if (info.trim()) console.log(info.substring(0, 200));
        });
      }
    } else if (technicalIssue > 0) {
      console.log('⚠️ Technical issue detected by debug helper');
      
      // Get the error display content
      const errorDisplay = await page.locator('[class*="error"], [class*="debug"]').allTextContents();
      console.log('Error details:', errorDisplay);
      
    } else {
      console.log('✅ Wizard loads without errors');
      
      // Navigate to the lawyer section to test debug features
      console.log('\n2. Navigating to lawyer section...');
      
      // Quick navigation
      await page.click('button[type="submit"]#da-continue-button'); // Welcome
      await page.waitForTimeout(500);
      await page.click('button:has-text("No, this is not an emergency")'); // Emergency
      await page.waitForTimeout(500);
      await page.click('button:has-text("Yes, I have my certificate")'); // MIP
      await page.waitForTimeout(500);
      await page.click('button[type="submit"]#da-continue-button'); // MIP continue
      await page.waitForTimeout(500);
      await page.click('button:has-text("Never lived together")'); // Relationship
      await page.waitForTimeout(500);
      await page.click('text=Child custody'); // Orders
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
      
      // Check if we get any debug errors at this point
      const partyError = await page.locator('text=Technical Issue Detected').count();
      if (partyError > 0) {
        console.log('⚠️ Party collection error detected');
        
        // Get the error details from debug helper
        const errorContent = await page.content();
        if (errorContent.includes('NameError')) {
          console.log('📍 NameError found - variable not defined');
        }
        if (errorContent.includes('AttributeError')) {
          console.log('📍 AttributeError found - object issue');
        }
        if (errorContent.includes('line')) {
          const lineMatch = errorContent.match(/line (\d+)/);
          if (lineMatch) {
            console.log(`📍 Error at line ${lineMatch[1]}`);
          }
        }
        
        // Try to continue anyway
        const continueBtn = await page.locator('button:has-text("Continue anyway")').count();
        if (continueBtn > 0) {
          console.log('Clicking "Continue anyway" to proceed...');
          await page.click('button:has-text("Continue anyway")');
          await page.waitForTimeout(1000);
        }
      }
      
      // Continue to role selection
      await page.click('button:has-text("I am starting a new case (Applicant)")'); // Role
      await page.waitForTimeout(1000);
      
      console.log('\n3. Checking for debug output in party forms...');
      
      const currentContent = await page.content();
      if (currentContent.includes('Technical Issue') || currentContent.includes('error_display')) {
        console.log('⚠️ Debug error display found');
        
        // Extract specific error information
        const errorTypes = ['NameError', 'AttributeError', 'TypeError', 'KeyError'];
        errorTypes.forEach(errorType => {
          if (currentContent.includes(errorType)) {
            console.log(`📍 ${errorType} detected in the flow`);
          }
        });
      } else if (currentContent.includes('Your Information')) {
        console.log('✅ User information form reached without debug errors');
      }
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n===================================');
  console.log('Debug feature test complete');
  console.log('The debug helpers will show detailed error info if issues occur');
})();