const { chromium } = require('playwright');

(async () => {
  console.log('Party Information Integration Test');
  console.log('==================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  let testsPassed = 0;
  let testsFailed = 0;
  
  try {
    console.log('Starting wizard with party information collection...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Check for interview error first
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    if (errorHeading > 0) {
      const errorMessage = await page.locator('blockquote').textContent();
      console.log('❌ Interview crashed:', errorMessage);
      testsFailed++;
      await browser.close();
      process.exit(1);
    }
    
    console.log('✅ Interview loaded successfully');
    testsPassed++;
    
    // Navigate through basic flow to reach party info
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(1000);
    await page.click('button[type="submit"]#da-continue-button'); // MIP info
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("Married")'); // Relationship
    await page.waitForTimeout(1000);
    
    await page.click('text=Divorce'); // Order
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("Uncontested - we agree on everything")');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("No")'); // No children
    await page.waitForTimeout(1000);
    
    // Should now reach role determination
    const content = await page.content();
    if (content.includes('Your Role in the Legal Proceeding') || 
        content.includes('I am starting a new case') || 
        content.includes('Applicant') && content.includes('Respondent')) {
      console.log('✅ Role determination screen reached');
      testsPassed++;
    } else {
      console.log('❌ Role determination screen not found');
      console.log('Current content includes:', content.substring(0, 500));
      testsFailed++;
    }
    
    // Test role selection
    const applicantButton = await page.locator('button:has-text("I am starting a new case")').count();
    if (applicantButton > 0) {
      console.log('✅ Role selection buttons found');
      testsPassed++;
      
      // Click applicant role
      await page.click('button:has-text("I am starting a new case")');
      await page.waitForTimeout(1000);
      
      // Should now have user info form
      const userInfoContent = await page.content();
      if (userInfoContent.includes('Your Information') && 
          userInfoContent.includes('Applicant')) {
        console.log('✅ User information form reached with correct role');
        testsPassed++;
      } else {
        console.log('❌ User information form not reached properly');
        testsFailed++;
      }
      
    } else {
      console.log('❌ Role selection buttons not found');
      testsFailed++;
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
    testsFailed++;
  }
  
  // Summary
  console.log('\n==================================');
  console.log(`Results: ${testsPassed} passed, ${testsFailed} failed`);
  
  if (testsFailed === 0) {
    console.log('✅ Party information integration successful!');
  } else {
    console.log('⚠️ Party information integration needs attention');
  }
  
  await browser.close();
  process.exit(testsFailed === 0 ? 0 : 1);
})();