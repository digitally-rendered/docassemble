const { chromium } = require('playwright');

(async () => {
  console.log('Quick Lawyer Button Test');
  console.log('========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    console.log('✅ Wizard loaded');
    
    // The key test: Can we reach the lawyer question without errors?
    console.log('Testing if lawyer question is reachable...');
    
    // Quick path to lawyer question
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(500);
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    await page.click('button:has-text("Common-law")'); // Relationship
    await page.waitForTimeout(500);
    await page.click('text=Child support'); // Order - triggers party collection
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Fill financial quickly with minimal fields
    await page.locator('input[type="text"]').first().fill('25000');
    await page.locator('label:has-text("Yes")').first().click();
    await page.locator('label:has-text("No")').nth(1).click(); 
    await page.locator('label:has-text("No")').nth(2).click();
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Role
    await page.click('button:has-text("I am starting a new case (Applicant)")');
    await page.waitForTimeout(500);
    
    // Fill minimal user info to get to next step
    await page.fill('input[name="user_party.name.first"]', 'Test');
    await page.fill('input[name="user_party.name.last"]', 'User');  
    await page.fill('input[name="user_party.birthdate"]', '1980-01-01');
    await page.fill('input[name="user_party.phone_number"]', '4165551234');
    await page.fill('input[name="user_party.address.address"]', '123 Test St');
    await page.fill('input[name="user_party.address.city"]', 'Toronto');
    await page.fill('input[name="user_party.address.postal_code"]', 'M5H 2N2');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Fill minimal other party info
    await page.fill('input[name="other_party.name.first"]', 'Other');
    await page.fill('input[name="other_party.name.last"]', 'Party');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Should now be at lawyer question
    const content = await page.content();
    if (content.includes('Do you have a lawyer?')) {
      console.log('✅ Reached lawyer question successfully');
      
      // Test the "Yes" button
      await page.click('button:has-text("Yes, I have a lawyer")');
      await page.waitForTimeout(1000);
      
      const lawyerFormContent = await page.content();
      if (lawyerFormContent.includes('Lawyer\'s First Name') || lawyerFormContent.includes('Your Lawyer\'s Information')) {
        console.log('✅ "Yes, I have a lawyer" button works - reached lawyer form');
        console.log('🎉 LAWYER BUTTON ISSUE IS FIXED!');
      } else {
        console.log('❌ Lawyer button clicked but form not reached');
      }
      
    } else {
      console.log('❌ Did not reach lawyer question');
      // Show what we did reach
      if (content.includes('Error')) {
        const errorMsg = await page.locator('blockquote').textContent().catch(() => 'Unknown error');
        console.log('Error occurred:', errorMsg);
      } else {
        console.log('Current page contains:', ['form', 'Form', 'information', 'party', 'lawyer'].filter(k => content.includes(k)));
      }
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  await browser.close();
  console.log('\nLawyer button test completed.');
})();