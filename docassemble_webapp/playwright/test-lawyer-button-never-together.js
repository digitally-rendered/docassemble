const { chromium } = require('playwright');

(async () => {
  console.log('TESTING LAWYER BUTTON IN NEVER TOGETHER FLOW');
  console.log('==============================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Quick navigation to party section
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
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
    await page.check('text=Child custody'); // Orders
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Skip financial if it appears
    let content = await page.content();
    if (content.includes('financial situation')) {
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
    }
    
    // Select applicant role
    console.log('1. Selecting Applicant role...');
    await page.click('button:has-text("I am starting a new case")');
    await page.waitForTimeout(1000);
    
    // Fill minimal user info
    console.log('2. Filling user information...');
    await page.fill('input[name*="first"]', 'Test');
    await page.fill('input[name*="last"]', 'User');
    
    // Find and fill the date field
    const dateInputs = await page.locator('input[type="date"], input[type="text"][placeholder*="yyyy"]').all();
    if (dateInputs.length > 0) {
      await dateInputs[0].fill('1990-01-01');
    }
    
    // Fill phone
    const phoneInputs = await page.locator('input[type="tel"], input[type="text"][placeholder*="phone"]').all();
    if (phoneInputs.length > 0) {
      await phoneInputs[0].fill('4165550100');
    }
    
    // Fill address fields
    const textInputs = await page.locator('input[type="text"]').all();
    for (const input of textInputs) {
      const name = await input.getAttribute('name');
      if (name) {
        if (name.includes('address') && !name.includes('email')) {
          await input.fill('123 Test St');
        } else if (name.includes('city')) {
          await input.fill('Toronto');
        } else if (name.includes('postal')) {
          await input.fill('M5H 2N2');
        }
      }
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Fill other party info
    console.log('3. Filling other party information...');
    await page.fill('input[name*="first"]', 'Other');
    await page.fill('input[name*="last"]', 'Party');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // User lawyer question
    console.log('4. User has no lawyer...');
    content = await page.content();
    if (content.includes('Do you have a lawyer?')) {
      await page.click('button:has-text("No, I am self-represented")');
      await page.waitForTimeout(1000);
    }
    
    // OTHER PARTY LAWYER - THE PROBLEMATIC QUESTION
    content = await page.content();
    if (content.includes('Does the other party have a lawyer?')) {
      console.log('5. TESTING THE PROBLEMATIC BUTTON...');
      console.log('   Clicking "Yes, they have a lawyer"...');
      
      await page.click('button:has-text("Yes, they have a lawyer")');
      await page.waitForTimeout(2000);
      
      // Check what happens
      content = await page.content();
      
      if (content.includes('Other Party\'s Lawyer Information') || 
          content.includes("Other Party's Lawyer Information")) {
        console.log('✅ SUCCESS! Lawyer form displayed!');
        console.log('THE LAWYER BUTTON WORKS!');
        
        // Try to fill it
        console.log('6. Filling lawyer information...');
        const lawyerInputs = await page.locator('input[type="text"]').all();
        if (lawyerInputs.length > 0) {
          await lawyerInputs[0].fill('Test Lawyer');
        }
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        content = await page.content();
        if (content.includes('Court Information')) {
          console.log('✅ Moved to Court Information - full flow works!');
        }
        
      } else if (content.includes('Court Information')) {
        console.log('⚠️ SKIPPED lawyer form - went straight to court');
        console.log('The conditional "show if" may not be working');
        
      } else if (content.includes('Error')) {
        console.log('❌ ERROR after clicking lawyer button');
        try {
          const errorMsg = await page.locator('blockquote').textContent();
          console.log('Error message:', errorMsg);
        } catch (e) {
          console.log('Could not extract error');
        }
        
      } else {
        console.log('❓ Unexpected result');
        const heading = await page.locator('h1, h2').first().textContent();
        console.log('Current screen:', heading);
      }
      
    } else {
      console.log('❌ Never reached other party lawyer question');
      const heading = await page.locator('h1, h2').first().textContent();
      console.log('Stuck at:', heading);
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n==============================================');
  console.log('Lawyer button test complete');
})();