const { chromium } = require('playwright');

(async () => {
  console.log('LAWYER BUTTON DEBUG TEST');
  console.log('========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading debug test interview...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-lawyer-debug.yml');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    
    if (content.includes('Does the other party have a lawyer?')) {
      console.log('✅ Lawyer question loaded');
      
      console.log('Clicking "Yes, they have a lawyer"...');
      await page.click('button:has-text("Yes, they have a lawyer")');
      await page.waitForTimeout(3000);
      
      const afterClick = await page.content();
      
      if (afterClick.includes('Debug Error Detected')) {
        console.log('⚠️ DEBUG ERROR CAUGHT!');
        
        // Extract error details
        const errorDetails = await page.locator('pre, code, .error-message').allTextContents();
        console.log('\n📋 ERROR DETAILS:');
        errorDetails.forEach(detail => {
          if (detail.trim()) {
            console.log(detail.substring(0, 500));
          }
        });
        
        // Look for specific error types
        if (afterClick.includes('NameError')) {
          const nameErrorMatch = afterClick.match(/NameError: name '([^']+)' is not defined/);
          if (nameErrorMatch) {
            console.log(`\n🔴 VARIABLE NOT DEFINED: ${nameErrorMatch[1]}`);
          }
        }
        
        if (afterClick.includes('line')) {
          const lineMatch = afterClick.match(/line (\d+)/);
          if (lineMatch) {
            console.log(`📍 Error at line ${lineMatch[1]}`);
          }
        }
        
      } else if (afterClick.includes('Other Party\'s Lawyer Information')) {
        console.log('✅ Lawyer form displayed successfully!');
        
        // Fill and submit
        await page.fill('input[name="other_lawyer_name"]', 'Test Lawyer');
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        const final = await page.content();
        if (final.includes('Test Complete')) {
          console.log('🎉 LAWYER BUTTON WORKS IN DEBUG TEST!');
        }
        
      } else {
        console.log('❓ Unexpected result after clicking lawyer button');
      }
      
    } else if (content.includes('Debug Error Detected')) {
      console.log('❌ Immediate error on load');
      const errorText = await page.locator('body').textContent();
      console.log('Error:', errorText.substring(0, 500));
    } else {
      console.log('❌ Test interview did not load properly');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n========================');
  console.log('Debug test complete');
})();