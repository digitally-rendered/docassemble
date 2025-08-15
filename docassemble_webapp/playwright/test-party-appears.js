const { chromium } = require('playwright');

(async () => {
  console.log('TESTING IF PARTY INFO APPEARS IN NEVER TOGETHER FLOW');
  console.log('=====================================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Starting wizard flow...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Quick navigation through initial screens
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(500);
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    
    // Select never lived together
    console.log('Selecting "Never lived together"...');
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(1000);
    
    // Select child custody (simplest option)
    console.log('Selecting child custody...');
    await page.check('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Handle financial form if it appears
    let content = await page.content();
    if (content.includes('financial situation')) {
      console.log('Financial form appeared - filling minimal data...');
      
      // Just fill the first text input with a value
      const inputs = await page.locator('input[type="text"]').all();
      if (inputs.length > 0) {
        await inputs[0].fill('10000');
      }
      
      // Click first available radio button for each group
      const radioGroups = ['support_involved', 'business_owner', 'pension_involved'];
      for (let i = 0; i < radioGroups.length; i++) {
        try {
          await page.locator(`input[type="radio"][value="False"]`).nth(i).click();
        } catch (e) {
          // Skip if not found
        }
      }
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
    }
    
    // Now check what screen we're on
    content = await page.content();
    
    if (content.includes('Your Role in the Legal Proceeding')) {
      console.log('✅ SUCCESS! Party information collection started!');
      console.log('The never lived together flow DOES use party information.');
      
      // Test continuing
      await page.click('button:has-text("I am starting a new case")');
      await page.waitForTimeout(1000);
      
      const afterRole = await page.content();
      if (afterRole.includes('Your Information')) {
        console.log('✅ User information form also works!');
      }
      
    } else if (content.includes('Error')) {
      console.log('❌ Error before reaching party info');
      try {
        const errorText = await page.locator('blockquote').textContent();
        console.log('Error:', errorText);
        
        // Check for undefined variable errors
        if (errorText.includes('reference to a variable')) {
          const varMatch = errorText.match(/variable '([^']+)'/);
          if (varMatch) {
            console.log('Undefined variable:', varMatch[1]);
          }
        }
      } catch (e) {
        console.log('Could not extract error details');
      }
    } else {
      console.log('❓ Unexpected screen after orders');
      const heading = await page.locator('h1, h2').first().textContent();
      console.log('Current screen:', heading);
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n=====================================================');
  console.log('Party info test complete');
})();