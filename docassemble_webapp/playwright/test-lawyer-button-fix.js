const { chromium } = require('playwright');

(async () => {
  console.log('Testing Lawyer Button Fix');
  console.log('=========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('1. Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Quick navigation to lawyer question
    console.log('2. Navigating to lawyer question...');
    
    // Welcome
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
    
    // Relationship - Common-law
    await page.click('button:has-text("Common-law")');
    await page.waitForTimeout(1000);
    
    // Orders - Child support
    await page.click('text=Child support');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Fill financial form
    await page.locator('input[type="text"]').first().fill('25000');
    await page.locator('label:has-text("Yes")').first().click();
    await page.locator('label:has-text("No")').nth(1).click();
    await page.locator('label:has-text("No")').nth(2).click();
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Role - Applicant
    await page.click('button:has-text("I am starting a new case (Applicant)")');
    await page.waitForTimeout(1000);
    
    // Fill user info quickly
    await page.fill('input[name="user_party.name.first"]', 'John');
    await page.fill('input[name="user_party.name.last"]', 'Smith');
    await page.fill('input[name="user_party.birthdate"]', '1980-01-01');
    await page.fill('input[name="user_party.phone_number"]', '4165551234');
    await page.fill('input[name="user_party.address.address"]', '123 Main St');
    await page.fill('input[name="user_party.address.city"]', 'Toronto');
    await page.fill('input[name="user_party.address.postal_code"]', 'M5H 2N2');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Fill other party info quickly
    await page.fill('input[name="other_party.name.first"]', 'Jane');
    await page.fill('input[name="other_party.name.last"]', 'Doe');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    console.log('3. Testing user lawyer question...');
    const lawyerContent = await page.content();
    if (lawyerContent.includes('Do you have a lawyer?')) {
      console.log('✅ Reached lawyer question');
      
      // Test "Yes" button
      console.log('4. Testing "Yes, I have a lawyer" button...');
      await page.click('button:has-text("Yes, I have a lawyer")');
      await page.waitForTimeout(2000);
      
      // Should now be at lawyer information form
      const lawyerFormContent = await page.content();
      if (lawyerFormContent.includes('Your Lawyer\'s Information') || lawyerFormContent.includes('Lawyer\'s First Name')) {
        console.log('✅ "Yes" button works - reached lawyer information form');
        
        // Test filling lawyer form
        console.log('5. Testing lawyer form fields...');
        try {
          await page.fill('input[name="user_lawyer.name.first"]', 'Robert');
          await page.fill('input[name="user_lawyer.name.last"]', 'Johnson');
          await page.fill('input[name="user_lawyer.phone_number"]', '4165559999');
          await page.fill('input[name="user_lawyer.email"]', 'robert@lawfirm.com');
          await page.fill('input[name="user_lawyer.address.address"]', '456 Bay Street');
          await page.fill('input[name="user_lawyer.address.city"]', 'Toronto');
          await page.fill('input[name="user_lawyer.address.postal_code"]', 'M5J 2S1');
          
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(2000);
          
          console.log('✅ Lawyer form fields work correctly');
          
          // Should now be at other party lawyer question
          const otherLawyerContent = await page.content();
          if (otherLawyerContent.includes('Does the other party have a lawyer?')) {
            console.log('✅ Reached other party lawyer question after filling lawyer info');
            
            // Test other party lawyer buttons
            await page.click('button:has-text("Yes, they have a lawyer")');
            await page.waitForTimeout(2000);
            
            const otherLawyerFormContent = await page.content();
            if (otherLawyerFormContent.includes('Other Party\'s Lawyer Information')) {
              console.log('✅ Other party lawyer form reached successfully');
              console.log('🎉 ALL LAWYER BUTTONS AND FORMS WORKING CORRECTLY!');
            } else {
              console.log('❌ Other party lawyer form not reached');
            }
            
          } else {
            console.log('❌ Other party lawyer question not reached');
          }
          
        } catch (error) {
          console.error('❌ Error filling lawyer form:', error.message);
        }
        
      } else {
        console.log('❌ "Yes" button failed - did not reach lawyer information form');
        console.log('Current content includes lawyer keywords:', ['lawyer', 'Lawyer', 'name', 'Name'].filter(k => lawyerFormContent.includes(k)));
      }
      
    } else {
      console.log('❌ Did not reach lawyer question');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  await browser.close();
  console.log('\nLawyer button test completed.');
})();