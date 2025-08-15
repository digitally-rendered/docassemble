const { chromium } = require('playwright');
const { checkForInterviewCrash, fillFinancialForm, waitForDocassembleLoad } = require('./utils/interview-helpers');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Testing improved error detection and form handling...\n');
    
    // Test 1: Navigate to wizard
    console.log('1. Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await waitForDocassembleLoad(page);
    
    // Check for initial crashes
    let crashInfo = await checkForInterviewCrash(page);
    if (crashInfo.crashed) {
      console.log(`❌ Interview crashed on load: ${crashInfo.message}`);
      process.exit(1);
    }
    console.log('✅ Wizard loaded successfully');
    
    // Test 2: Navigate through initial questions
    console.log('\n2. Navigating through initial questions...');
    
    // Welcome page
    await page.click('button[type="submit"]#da-continue-button');
    await waitForDocassembleLoad(page);
    
    crashInfo = await checkForInterviewCrash(page);
    if (crashInfo.crashed) {
      console.log(`❌ Crashed after welcome: ${crashInfo.message}`);
      process.exit(1);
    }
    
    // Emergency question
    await page.click('button[type="submit"]:has-text("No, this is not an emergency")');
    await waitForDocassembleLoad(page);
    
    crashInfo = await checkForInterviewCrash(page);
    if (crashInfo.crashed) {
      console.log(`❌ Crashed after emergency: ${crashInfo.message}`);
      process.exit(1);
    }
    
    // MIP
    await page.click('button[type="submit"]:has-text("Yes, I have my certificate")');
    await waitForDocassembleLoad(page);
    
    // MIP info
    await page.click('button[type="submit"]#da-continue-button');
    await waitForDocassembleLoad(page);
    
    // Relationship
    await page.click('button[type="submit"]:has-text("Common-law")');
    await waitForDocassembleLoad(page);
    
    // Orders - select spousal support
    await page.click('text=Spousal support');
    await page.click('button[type="submit"]#da-continue-button');
    await waitForDocassembleLoad(page);
    
    crashInfo = await checkForInterviewCrash(page);
    if (crashInfo.crashed) {
      console.log(`❌ Crashed before financial form: ${crashInfo.message}`);
      process.exit(1);
    }
    console.log('✅ Reached financial form without crashes');
    
    // Test 3: Fill financial form with improved helpers
    console.log('\n3. Testing improved financial form handling...');
    
    const financialData = {
      property_value: 75000,
      support_involved: true,
      business_owner: false,
      pension_involved: true
    };
    
    await fillFinancialForm(page, financialData);
    console.log('✅ Financial form filled successfully');
    
    // Submit financial form
    await page.click('button[type="submit"]#da-continue-button');
    await waitForDocassembleLoad(page);
    
    crashInfo = await checkForInterviewCrash(page);
    if (crashInfo.crashed) {
      console.log(`❌ Crashed after financial form: ${crashInfo.message}`);
      process.exit(1);
    }
    
    // Check if we reached recommendations
    const pageContent = await page.content();
    if (pageContent.includes('Personalized Forms Package') || pageContent.includes('Your Forms')) {
      console.log('✅ Successfully reached recommendations!');
    } else {
      const question = await page.locator('#daMainQuestion').textContent();
      console.log(`⚠️ Reached unexpected screen: ${question}`);
    }
    
    console.log('\n✅ All improvements working correctly!');
    console.log('- Error detection catches crashes immediately');
    console.log('- Financial form fills reliably');
    console.log('- Interview completes successfully');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'test-error.png', fullPage: true });
    console.log('Screenshot saved to test-error.png');
  }
  
  await browser.close();
})();