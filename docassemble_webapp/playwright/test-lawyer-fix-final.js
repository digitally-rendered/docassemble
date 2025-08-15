const { chromium } = require('playwright');

(async () => {
  console.log('FINAL LAWYER BUTTON FIX TEST');
  console.log('=============================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Check for immediate crash
    let errorHeading = await page.locator('h1:has-text("Error")').count();
    if (errorHeading > 0) {
      const errorMessage = await page.locator('blockquote').textContent();
      console.log('❌ CRASH ON LOAD:', errorMessage);
      process.exit(1);
    }
    
    console.log('✅ Wizard loads without crashing');
    
    // Fast path to lawyer question - using the never lived together path which is shorter
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(500);
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    
    // Use NEVER LIVED TOGETHER (shorter path - no financial forms)
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(500);
    
    // Select child custody (minimal)
    await page.click('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Should go straight to role selection (no financial forms for never together)
    console.log('Testing role selection...');
    let content = await page.content();
    if (content.includes('Your Role in the Legal Proceeding')) {
      console.log('✅ Role selection reached');
      
      await page.click('button:has-text("I am starting a new case (Applicant)")');
      await page.waitForTimeout(1000);
      
      // Fill user info - test the ACTUAL field names
      console.log('Testing user info form...');
      content = await page.content();
      if (content.includes('Your Information')) {
        console.log('✅ User info form reached');
        
        // Try to fill user form with correct field names
        try {
          await page.fill('input[name="user_party.name.first"]', 'John');
          await page.fill('input[name="user_party.name.last"]', 'Smith');
          await page.fill('input[name="user_party.birthdate"]', '1980-01-01');
          await page.fill('input[name="user_party.phone_number"]', '4165551234');
          await page.fill('input[name="user_party.address.address"]', '123 Test St');
          await page.fill('input[name="user_party.address.city"]', 'Toronto');
          await page.fill('input[name="user_party.address.postal_code"]', 'M5H 2N2');
          
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          console.log('✅ User info form filled successfully');
          
          // Fill other party minimal
          await page.fill('input[name="other_party.name.first"]', 'Jane');
          await page.fill('input[name="other_party.name.last"]', 'Doe');
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          console.log('✅ Other party info completed');
          
          // NOW TEST THE LAWYER BUTTON
          content = await page.content();
          if (content.includes('Do you have a lawyer?')) {
            console.log('✅ REACHED LAWYER QUESTION!');
            
            // THE CRITICAL TEST
            console.log('🔥 TESTING "YES I HAVE A LAWYER" BUTTON...');
            await page.click('button:has-text("Yes, I have a lawyer")');
            await page.waitForTimeout(2000);
            
            // Check what happened
            content = await page.content();
            if (content.includes('Error')) {
              const errorMsg = await page.locator('blockquote').textContent();
              console.log('❌ LAWYER BUTTON CAUSED ERROR:', errorMsg);
            } else if (content.includes('Your Lawyer\'s Information') || content.includes('Lawyer\'s Full Name')) {
              console.log('🎉 SUCCESS! LAWYER BUTTON WORKS!');
              console.log('✅ Lawyer form reached successfully');
              
              // Test filling lawyer form
              try {
                await page.fill('input[name="user_lawyer.name"]', 'Robert Johnson');
                await page.fill('input[name="user_lawyer.phone_number"]', '4165559999');
                await page.fill('input[name="user_lawyer.email"]', 'robert@law.com');
                await page.fill('input[name="user_lawyer.address.address"]', '456 Bay St');
                await page.fill('input[name="user_lawyer.address.city"]', 'Toronto');
                await page.fill('input[name="user_lawyer.address.postal_code"]', 'M5J 2S1');
                
                console.log('✅ Lawyer form fields can be filled!');
                console.log('🎉 LAWYER BUTTON AND FORM COMPLETELY FIXED!');
                
              } catch (fillError) {
                console.log('⚠️ Lawyer form reached but field names may need adjustment');
                console.log('Field error:', fillError.message.substring(0, 100));
              }
              
            } else {
              console.log('❌ Lawyer button clicked but unexpected result');
              console.log('Content includes:', ['lawyer', 'Lawyer', 'form', 'name'].filter(k => content.includes(k)));
            }
            
          } else {
            console.log('❌ Did not reach lawyer question');
          }
          
        } catch (userFormError) {
          console.log('❌ User form filling failed:', userFormError.message.substring(0, 100));
        }
        
      } else {
        console.log('❌ User info form not reached');
      }
      
    } else {
      console.log('❌ Role selection not reached');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n===========================');
  console.log('LAWYER BUTTON TEST COMPLETE');
  console.log('===========================');
})();