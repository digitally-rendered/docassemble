const { chromium } = require('playwright');

(async () => {
  console.log('TESTING SIMPLE LAWYER FORM');
  console.log('===========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Loading simple lawyer test...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/test-lawyer-simple.yml');
    await page.waitForTimeout(2000);
    
    // Check for errors
    const errorCount = await page.locator('h1:has-text("Error")').count();
    if (errorCount > 0) {
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('❌ SIMPLE TEST ERROR:', errorMsg);
    } else {
      console.log('✅ Simple test loads');
      
      const content = await page.content();
      if (content.includes('Does the other party have a lawyer?')) {
        console.log('✅ Other party lawyer question found');
        
        // Test the "Yes" button
        await page.click('button:has-text("Yes, they have a lawyer")');
        await page.waitForTimeout(2000);
        
        const afterContent = await page.content();
        if (afterContent.includes('Error')) {
          const errorMsg = await page.locator('blockquote').textContent();
          console.log('❌ LAWYER BUTTON ERROR IN SIMPLE TEST:', errorMsg);
        } else if (afterContent.includes('Other Party\'s Lawyer Information')) {
          console.log('🎉 SUCCESS! Simple lawyer form works!');
          console.log('✅ The issue is not with the lawyer form itself');
          
          // Fill the form to complete test
          await page.fill('input[name="other_lawyer_name"]', 'Test Lawyer');
          await page.fill('input[name="other_lawyer_firm"]', 'Test Firm');
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          const finalContent = await page.content();
          if (finalContent.includes('Test Complete')) {
            console.log('✅ Full simple lawyer flow works perfectly!');
            console.log('🔍 Issue must be in the main wizard integration');
          }
          
        } else {
          console.log('❓ Unexpected result in simple test');
        }
        
      } else {
        console.log('❌ Other party lawyer question not found in simple test');
      }
    }
    
  } catch (error) {
    console.error('❌ Simple test error:', error.message);
  }
  
  await browser.close();
})();