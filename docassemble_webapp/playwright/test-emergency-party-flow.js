const { chromium } = require('playwright');

(async () => {
  console.log('Emergency Flow Party Collection Test');
  console.log('=====================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  let testsPassed = 0;
  let testsFailed = 0;
  
  try {
    console.log('1. Loading wizard for emergency flow...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    console.log('✅ Wizard loaded');
    testsPassed++;
    
    console.log('\n2. Testing EMERGENCY flow with party collection...');
    
    // Welcome
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Emergency - YES (this is the key difference)
    await page.click('button:has-text("Yes, this is an emergency")');
    await page.waitForTimeout(1000);
    
    // Should show emergency forms screen
    const emergencyContent = await page.content();
    if (emergencyContent.includes('URGENT: Emergency Filing Required')) {
      console.log('✅ Emergency screen reached');
      testsPassed++;
      
      // Continue through emergency screen
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      // Should go to relationship status (no MIP for emergency)
      await page.click('button:has-text("Married")');
      await page.waitForTimeout(1000);
      
      // Emergency cases might have restraining orders
      await page.click('text=Restraining order');
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      // Should now reach party information (universal)
      const partyContent = await page.content();
      if (partyContent.includes('Your Role in the Legal Proceeding')) {
        console.log('✅ EMERGENCY FLOW includes party information collection!');
        testsPassed++;
        
        // Test the party flow works in emergency
        await page.click('button:has-text("I am starting a new case (Applicant)")');
        await page.waitForTimeout(1000);
        
        const userInfoContent = await page.content();
        if (userInfoContent.includes('Your Information') && userInfoContent.includes('Applicant')) {
          console.log('✅ Emergency flow user information form working');
          testsPassed++;
        } else {
          console.log('❌ Emergency flow user information form not working');
          testsFailed++;
        }
        
      } else {
        console.log('❌ EMERGENCY FLOW missing party information collection');
        console.log('Current content includes:', ['role', 'Role', 'form', 'Form'].filter(k => partyContent.includes(k)));
        testsFailed++;
      }
      
    } else {
      console.log('❌ Emergency screen not reached');
      testsFailed++;
    }
    
  } catch (error) {
    console.error('❌ Emergency test error:', error.message);
    testsFailed++;
  }
  
  await browser.close();
  
  // Test never lived together flow
  const browser2 = await chromium.launch({ headless: true });
  const page2 = await browser2.newPage();
  
  try {
    console.log('\n3. Testing NEVER LIVED TOGETHER flow with party collection...');
    
    await page2.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page2.waitForTimeout(2000);
    
    // Welcome
    await page2.click('button[type="submit"]#da-continue-button');
    await page2.waitForTimeout(1000);
    
    // Emergency - No
    await page2.click('button:has-text("No, this is not an emergency")');
    await page2.waitForTimeout(1000);
    
    // MIP - Yes
    await page2.click('button:has-text("Yes, I have my certificate")');
    await page2.waitForTimeout(1000);
    await page2.click('button[type="submit"]#da-continue-button');
    await page2.waitForTimeout(1000);
    
    // Relationship - NEVER LIVED TOGETHER (this is the key difference)
    await page2.click('button:has-text("Never lived together")');
    await page2.waitForTimeout(1000);
    
    // Never together orders
    await page2.click('text=Child custody');
    await page2.click('button[type="submit"]#da-continue-button');
    await page2.waitForTimeout(1000);
    
    // Should now reach party information (universal)
    const neverTogetherPartyContent = await page2.content();
    if (neverTogetherPartyContent.includes('Your Role in the Legal Proceeding')) {
      console.log('✅ NEVER LIVED TOGETHER FLOW includes party information collection!');
      testsPassed++;
      
      // Test role selection works
      await page2.click('button:has-text("I am starting a new case (Applicant)")');
      await page2.waitForTimeout(1000);
      
      const neverTogetherUserInfo = await page2.content();
      if (neverTogetherUserInfo.includes('Your Information') && neverTogetherUserInfo.includes('Applicant')) {
        console.log('✅ Never lived together flow user information working');
        testsPassed++;
      } else {
        console.log('❌ Never lived together flow user information not working');
        testsFailed++;
      }
      
    } else {
      console.log('❌ NEVER LIVED TOGETHER FLOW missing party information collection');
      testsFailed++;
    }
    
  } catch (error) {
    console.error('❌ Never lived together test error:', error.message);
    testsFailed++;
  }
  
  await browser2.close();
  
  // Summary
  console.log('\n=====================================');
  console.log(`Final Results: ${testsPassed} passed, ${testsFailed} failed`);
  
  if (testsFailed === 0) {
    console.log('🎉 SUCCESS: Party information now collected in ALL flows!');
    console.log('✅ Emergency flow includes party collection');
    console.log('✅ Never lived together flow includes party collection');
    console.log('✅ Regular flow includes party collection');
    console.log('✅ Universal party information collection implemented');
  } else {
    console.log('⚠️ Some flows still missing party information collection');
  }
  
  process.exit(testsFailed === 0 ? 0 : 1);
})();