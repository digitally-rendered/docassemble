const { chromium } = require('playwright');

(async () => {
  console.log('TESTING NEVER LIVED TOGETHER FLOW');
  console.log('==================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('1. Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Welcome screen
    console.log('2. Clicking continue on welcome...');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Emergency check
    console.log('3. Not an emergency...');
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(500);
    
    // MIP
    console.log('4. MIP completed...');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Relationship status - NEVER LIVED TOGETHER
    console.log('5. Selecting "Never lived together"...');
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(1000);
    
    // Check what appears next
    const content = await page.content();
    
    if (content.includes('What orders are you seeking?')) {
      console.log('✅ Orders question appeared for never_together');
      
      // Select some orders
      console.log('6. Selecting child custody and support...');
      await page.check('text=Child custody');
      await page.check('text=Child support');
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      // Check where we are now
      const afterOrders = await page.content();
      
      if (afterOrders.includes('Your Role in the Legal Proceeding')) {
        console.log('✅ Party information collection started!');
        
        // Select applicant
        console.log('7. Selecting Applicant role...');
        await page.click('button:has-text("I am starting a new case (Applicant)")');
        await page.waitForTimeout(1000);
        
        const afterRole = await page.content();
        if (afterRole.includes('Your Information')) {
          console.log('✅ User information form reached!');
          console.log('NEVER LIVED TOGETHER FLOW WORKS WITH PARTY INFO!');
        }
        
      } else if (afterOrders.includes('financial situation')) {
        console.log('📊 Financial complexity question appeared');
      } else if (afterOrders.includes('Error')) {
        console.log('❌ Error after orders selection');
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('Error:', errorMsg);
      } else {
        console.log('❓ Unexpected screen after orders');
        const headings = await page.locator('h1, h2').first().textContent();
        console.log('Current screen:', headings);
      }
      
    } else if (content.includes('Error')) {
      console.log('❌ Error after selecting never_together');
      try {
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('Error message:', errorMsg);
      } catch (e) {
        console.log('Could not extract error message');
      }
    } else {
      console.log('❓ Unexpected content after never_together');
      const headings = await page.locator('h1, h2').allTextContents();
      console.log('Headings found:', headings);
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n==================================');
  console.log('Never lived together flow test complete');
})();