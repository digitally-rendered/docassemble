const { chromium } = require('playwright');

(async () => {
  console.log('MINIMAL LAWYER BUTTON TEST');
  console.log('===========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Navigate quickly to party section
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Click through initial screens
    const clickSequence = [
      'button[type="submit"]#da-continue-button', // Welcome
      'button:has-text("No, this is not an emergency")', // Emergency
      'button:has-text("Yes, I have my certificate")', // MIP
      'button[type="submit"]#da-continue-button', // MIP continue
      'button:has-text("Never lived together")' // Relationship
    ];
    
    for (const selector of clickSequence) {
      await page.click(selector);
      await page.waitForTimeout(500);
    }
    
    // Select child custody
    await page.check('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Skip financial if present
    if ((await page.content()).includes('financial situation')) {
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
    }
    
    // Select applicant
    console.log('Selecting Applicant role...');
    await page.click('button:has-text("I am starting a new case")');
    await page.waitForTimeout(1000);
    
    // Fill user info - use the actual encoded field names
    console.log('Filling user information...');
    const userInputs = await page.locator('input[type="text"], input[type="date"], input[type="tel"]').all();
    
    // Fill required fields with test data
    let fieldsFilled = 0;
    for (const input of userInputs) {
      const isRequired = await input.getAttribute('required');
      if (isRequired !== null) {
        const type = await input.getAttribute('type');
        if (type === 'date') {
          await input.fill('1990-01-01');
        } else {
          // Fill text fields based on position
          if (fieldsFilled === 0) await input.fill('Test'); // First name
          else if (fieldsFilled === 1) await input.fill('User'); // Last name
          else if (fieldsFilled === 2) await input.fill('4165550100'); // Phone
          else if (fieldsFilled === 3) await input.fill('123 Test St'); // Address
          else if (fieldsFilled === 4) await input.fill('Toronto'); // City
          else if (fieldsFilled === 5) await input.fill('M5H 2N2'); // Postal
        }
        fieldsFilled++;
      }
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Fill other party info - minimal
    console.log('Filling other party information...');
    const otherInputs = await page.locator('input[type="text"]').all();
    if (otherInputs.length >= 2) {
      await otherInputs[0].fill('Other'); // First name
      await otherInputs[1].fill('Party'); // Last name
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // User lawyer
    console.log('User has no lawyer...');
    if ((await page.content()).includes('Do you have a lawyer?')) {
      await page.click('button:has-text("No, I am self-represented")');
      await page.waitForTimeout(1000);
    }
    
    // THE KEY TEST - Other party lawyer
    const content = await page.content();
    if (content.includes('Does the other party have a lawyer?')) {
      console.log('\n🎯 LAWYER QUESTION REACHED!');
      console.log('Clicking "Yes, they have a lawyer"...\n');
      
      await page.click('button:has-text("Yes, they have a lawyer")');
      await page.waitForTimeout(3000);
      
      // Check result
      const afterClick = await page.content();
      
      if (afterClick.includes('Lawyer') && afterClick.includes('Information')) {
        console.log('✅ LAWYER FORM DISPLAYED!');
        
        // Fill it
        const lawyerInputs = await page.locator('input[type="text"]').all();
        if (lawyerInputs.length > 0) {
          await lawyerInputs[0].fill('Test Lawyer');
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          if ((await page.content()).includes('Court')) {
            console.log('✅ COMPLETE SUCCESS - Reached Court Information!');
          }
        }
        
      } else if (afterClick.includes('Court Information')) {
        console.log('⚠️ SKIPPED - Went straight to Court Information');
        console.log('The show if condition may not be working correctly');
        
      } else if (afterClick.includes('Error')) {
        console.log('❌ ERROR OCCURRED');
        try {
          const errorText = await page.locator('blockquote, .alert').first().textContent();
          console.log('Error:', errorText.substring(0, 200));
        } catch (e) {}
        
      } else {
        console.log('❓ UNEXPECTED RESULT');
        const heading = await page.locator('h1, h2').first().textContent();
        console.log('Current screen:', heading);
      }
      
    } else {
      console.log('❌ Never reached lawyer question');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n===========================');
  console.log('Test complete');
})();