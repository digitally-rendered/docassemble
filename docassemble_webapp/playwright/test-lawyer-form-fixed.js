const { chromium } = require('playwright');

/**
 * FIXED VERSION: Lawyer Form Debug Test
 * 
 * ROOT CAUSE IDENTIFIED: User information form wasn't being filled properly,
 * particularly the phone number field, preventing the wizard from advancing.
 * 
 * This test implements the correct field filling strategy and should 
 * successfully reach the lawyer questions.
 */

(async () => {
  console.log('🔧 LAWYER FORM FIX TEST');
  console.log('=======================\n');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 300 
  });
  
  const context = await browser.newContext({
    recordVideo: {
      dir: './test-results/',
      size: { width: 1280, height: 720 }
    }
  });
  
  const page = await context.newPage();
  
  try {
    console.log('🌐 Navigating to wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Navigate through initial screens
    console.log('📍 Step 1: Initial navigation');
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(1000);
    
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(1000);
    
    // CRITICAL: Select "Never lived together" 
    console.log('📍 Step 2: Selecting "Never lived together"');
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(1000);
    
    // CRITICAL: Select child custody
    console.log('📍 Step 3: Selecting child custody');
    await page.check('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Role selection
    console.log('📍 Step 4: Role selection');
    await page.click('button:has-text("I am starting a new case")');
    await page.waitForTimeout(2000);
    
    // FIXED: User Information Form with proper field handling
    console.log('📍 Step 5: User Information (FIXED VERSION)');
    console.log('   🔧 Implementing proper field filling strategy...');
    
    // Fill fields by their base64 encoded names specifically
    const fieldMappings = {
      'dXNlcl9wYXJ0eS5uYW1lLmZpcnN0': 'TestFirstName',      // First name
      'dXNlcl9wYXJ0eS5uYW1lLmxhc3Q': 'TestLastName',        // Last name
      'dXNlcl9wYXJ0eS5iaXJ0aGRhdGU': '1990-01-01',          // Birthdate
      'dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI': '4165550100',       // Phone (this was the issue!)
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M': '123 Test St',  // Address
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk': 'Toronto',          // City
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl': 'Ontario',        // Province
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl': 'M5H2N2' // Postal code
    };
    
    // Fill each field specifically
    for (const [fieldName, value] of Object.entries(fieldMappings)) {
      try {
        const field = page.locator(`input[name="${fieldName}"]`);
        if (await field.count() > 0) {
          await field.fill(value);
          console.log(`   ✓ Filled ${fieldName.split('.').pop()}: ${value}`);
        }
      } catch (error) {
        console.log(`   ⚠️ Could not fill ${fieldName}: ${error.message}`);
      }
    }
    
    await page.screenshot({ path: './debug-fixed-user-form.png' });
    console.log('   🚀 Submitting user information form...');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    // Check if we advanced to Other Party Information
    let content = await page.content();
    let heading = await page.locator('h1, h2').first().textContent();
    console.log(`📍 Step 6: After user form - Current screen: "${heading}"`);
    
    if (content.includes('Other Party')) {
      console.log('   🎉 SUCCESS! Advanced to Other Party Information');
      
      // Fill other party info with the same strategy
      const otherPartyFields = {
        'b3RoZXJfcGFydHkubmFtZS5maXJzdA': 'OtherFirst',
        'b3RoZXJfcGFydHkubmFtZS5sYXN0': 'OtherLast'
      };
      
      for (const [fieldName, value] of Object.entries(otherPartyFields)) {
        try {
          const field = page.locator(`input[name="${fieldName}"]`);
          if (await field.count() > 0) {
            await field.fill(value);
            console.log(`   ✓ Filled other party ${fieldName.split('.').pop()}: ${value}`);
          }
        } catch (error) {
          // Try fallback approach
          const textInputs = await page.locator('input[type="text"]').all();
          if (textInputs.length >= 2) {
            await textInputs[0].fill('OtherFirst');
            await textInputs[1].fill('OtherLast');
            console.log('   ✓ Used fallback method for other party names');
            break;
          }
        }
      }
      
      await page.screenshot({ path: './debug-fixed-other-party.png' });
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(2000);
      
      // Now we should reach the lawyer questions
      content = await page.content();
      heading = await page.locator('h1, h2').first().textContent();
      console.log(`📍 Step 7: After other party - Current screen: "${heading}"`);
      
      if (content.includes('Do you have a lawyer?')) {
        console.log('   🎯 User lawyer question appeared!');
        await page.click('button:has-text("No, I am self-represented")');
        await page.waitForTimeout(2000);
        
        // THE CRITICAL MOMENT: Other party lawyer question
        content = await page.content();
        heading = await page.locator('h1, h2').first().textContent();
        console.log(`📍 Step 8: THE CRITICAL MOMENT - "${heading}"`);
        
        if (content.includes('Does the other party have a lawyer?')) {
          console.log('   🎯 OTHER PARTY LAWYER QUESTION FOUND!');
          console.log('   🔥 This is where the bug was supposed to occur...');
          
          await page.screenshot({ path: './debug-before-critical-click.png' });
          
          console.log('   🔄 Clicking "Yes, they have a lawyer"...');
          await page.click('button:has-text("Yes, they have a lawyer")');
          await page.waitForTimeout(3000);
          
          // Check the result
          content = await page.content();
          heading = await page.locator('h1, h2').first().textContent();
          await page.screenshot({ path: './debug-after-critical-click.png' });
          
          console.log(`📍 Step 9: RESULT - "${heading}"`);
          
          if (content.includes('Other Party') && content.includes('Lawyer') && content.includes('Information')) {
            console.log('   🎉 SUCCESS! Lawyer form appeared correctly!');
            console.log('   ✅ The issue was the form filling, not the YAML logic!');
            
            // Try to fill the lawyer form
            const lawyerNameField = page.locator('input').first();
            await lawyerNameField.fill('Test Lawyer Name');
            console.log('   ✓ Filled lawyer name field');
            
          } else if (content.includes('Court')) {
            console.log('   ❌ BUG STILL EXISTS: Skipped to Court Information');
            console.log('   🔍 The YAML condition may have a logic error');
            
          } else {
            console.log('   ❓ Unexpected result');
            console.log(`   Content preview: ${content.substring(0, 200)}...`);
          }
          
        } else {
          console.log('   ❌ Other party lawyer question not found');
          console.log(`   Found instead: "${heading}"`);
        }
        
      } else {
        console.log('   ❌ User lawyer question not found');
        console.log(`   Found instead: "${heading}"`);
      }
      
    } else {
      console.log('   ❌ Still stuck at user information form');
      console.log('   🔧 Field filling strategy may need further adjustment');
    }
    
  } catch (error) {
    console.error('🚨 Test error:', error);
    await page.screenshot({ path: './debug-error.png' });
  }
  
  console.log('\n📊 TEST COMPLETE');
  console.log('================');
  console.log('📹 Video saved to test-results/');
  console.log('🖼️ Screenshots saved for analysis');
  console.log('\nKeeping browser open for inspection...');
  
  // Keep open for manual inspection
  await new Promise((resolve) => {
    process.on('SIGINT', () => {
      console.log('\n👋 Closing browser...');
      resolve();
    });
  });
  
  await context.close();
  await browser.close();
})();