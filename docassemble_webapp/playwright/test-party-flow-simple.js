const { chromium } = require('playwright');

(async () => {
  console.log('Simple Party Flow Test');
  console.log('======================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  let testsPassed = 0;
  let testsFailed = 0;
  
  try {
    console.log('Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Check for crash
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    if (errorHeading > 0) {
      const errorMessage = await page.locator('blockquote').textContent();
      console.log('❌ Interview crashed:', errorMessage);
      testsFailed++;
    } else {
      console.log('✅ Interview loaded successfully');
      testsPassed++;
    }
    
    // Navigate through basic flow
    console.log('\nNavigating to party info section...');
    
    // Welcome screen
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Emergency - No
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    // MIP - Yes
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Relationship - Married
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(1000);
    
    // Orders - Just divorce
    await page.click('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Divorce type - try both possible button texts
    let divorceClicked = false;
    try {
      await page.click('button:has-text("Uncontested - we agree")', { timeout: 2000 });
      divorceClicked = true;
    } catch (e) {
      try {
        await page.click('button:has-text("Uncontested")', { timeout: 2000 });
        divorceClicked = true;
      } catch (e2) {
        console.log('Available buttons:', await page.locator('button').allTextContents());
      }
    }
    
    if (divorceClicked) {
      await page.waitForTimeout(1000);
      
      // Children - No
      await page.click('button:has-text("No")');
      await page.waitForTimeout(2000);
      
      // Should now be at role determination
      const content = await page.content();
      if (content.includes('Your Role in the Legal Proceeding')) {
        console.log('✅ Reached role determination screen');
        testsPassed++;
        
        // Test role selection
        await page.click('button:has-text("I am starting a new case (Applicant)")');
        await page.waitForTimeout(1000);
        
        // Should now be at user information
        const userInfoContent = await page.content();
        if (userInfoContent.includes('Your Information') && userInfoContent.includes('Applicant')) {
          console.log('✅ Reached user information screen with correct role');
          testsPassed++;
          
          // Fill some basic info
          await page.fill('input[name="user_party.name.first"]', 'John');
          await page.fill('input[name="user_party.name.last"]', 'Smith');
          await page.fill('input[name="user_party.birthdate"]', '1980-01-01');
          await page.fill('input[name="user_party.phone_number"]', '4165551234');
          await page.fill('input[name="user_party.address.address"]', '123 Main St');
          await page.fill('input[name="user_party.address.city"]', 'Toronto');
          await page.fill('input[name="user_party.address.postal_code"]', 'M5H 2N2');
          
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          // Should now be at other party info
          const otherPartyContent = await page.content();
          if (otherPartyContent.includes('Other Party') && otherPartyContent.includes('Respondent')) {
            console.log('✅ Reached other party information screen');
            testsPassed++;
          } else {
            console.log('❌ Did not reach other party information screen');
            testsFailed++;
          }
          
        } else {
          console.log('❌ Did not reach user information screen properly');
          testsFailed++;
        }
        
      } else {
        console.log('❌ Did not reach role determination screen');
        console.log('Current page keywords:', ['role', 'Role', 'applicant', 'Applicant'].filter(k => content.includes(k)));
        testsFailed++;
      }
      
    } else {
      console.log('❌ Could not click divorce complexity button');
      testsFailed++;
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
    testsFailed++;
  }
  
  // Summary
  console.log('\n======================');
  console.log(`Results: ${testsPassed} passed, ${testsFailed} failed`);
  
  if (testsFailed === 0) {
    console.log('✅ Party information collection working!');
  } else {
    console.log('⚠️ Some party information features need attention');
  }
  
  await browser.close();
  process.exit(testsFailed === 0 ? 0 : 1);
})();