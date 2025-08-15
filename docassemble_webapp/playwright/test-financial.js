const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Testing financial forms flow...');
    
    // Navigate through to financial questions
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForSelector('#daMainQuestion', { timeout: 10000 });
    
    // Welcome page
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Emergency question - No
    await page.click('button[type="submit"]:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    // MIP - Yes
    await page.click('button[type="submit"]:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    
    // MIP info - Continue
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Relationship - Common-law
    await page.click('button[type="submit"]:has-text("Common-law")');
    await page.waitForTimeout(1000);
    
    // Orders - Select spousal support (which requires financial forms)
    await page.click('text=Spousal support');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    // Check if we hit an error or reached financial questions
    const pageContent = await page.content();
    
    if (pageContent.includes('Error')) {
      console.log('❌ ERROR: Interview crashed');
      const errorText = await page.textContent('blockquote');
      console.log('Error message:', errorText);
    } else {
      const question = await page.textContent('#daMainQuestion');
      console.log('✅ SUCCESS: Reached question:', question);
      
      // Check if it's the financial situation question
      if (question.includes('financial situation')) {
        console.log('✅ Financial question is now working!');
        
        // Fill in the financial form
        await page.fill('input[type="text"]', '50000'); // Property value
        await page.click('input[value="True"]'); // Support involved
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const nextQuestion = await page.textContent('#daMainQuestion');
        console.log('Next screen:', nextQuestion);
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
})();