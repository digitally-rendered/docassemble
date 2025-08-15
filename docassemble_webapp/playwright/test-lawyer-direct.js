const { chromium } = require('playwright');

(async () => {
  console.log('DIRECT LAWYER BUTTON TEST');
  console.log('==========================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    console.log('Quick path to lawyer question...');
    
    // Navigate quickly
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
    await page.click('text=Child custody'); // Orders
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    await page.click('button:has-text("I am starting a new case (Applicant)")'); // Role
    await page.waitForTimeout(1000);
    
    // Fill user form using the base64-encoded field names (as they actually appear)
    console.log('Filling user form with correct field names...');
    await page.fill('input[name="dXNlcl9wYXJ0eS5uYW1lLmZpcnN0"]', 'John'); // user_party.name.first
    await page.fill('input[name="dXNlcl9wYXJ0eS5uYW1lLmxhc3Q"]', 'Smith'); // user_party.name.last
    await page.fill('input[name="dXNlcl9wYXJ0eS5iaXJ0aGRhdGU"]', '1980-01-01'); // user_party.birthdate
    await page.fill('input[name="dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI"]', '4165551234'); // user_party.phone_number
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M"]', '123 Test St'); // user_party.address.address
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk"]', 'Toronto'); // user_party.address.city
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl"]', 'M5H 2N2'); // user_party.address.postal_code
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    console.log('✅ User form completed, filling other party...');
    
    // Fill other party - get field names first
    const otherInputs = await page.locator('input[name*="other_party"]').all();
    if (otherInputs.length > 0) {
      // Fill with base64 encoded names for other_party
      await page.fill('input[name*="other_party"][name*="first"]', 'Jane');
      await page.fill('input[name*="other_party"][name*="last"]', 'Doe');
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      console.log('✅ Other party completed, should be at lawyer question...');
      
      // CHECK FOR LAWYER QUESTION
      const content = await page.content();
      if (content.includes('Do you have a lawyer?')) {
        console.log('🎯 FOUND LAWYER QUESTION!');
        
        // Show available buttons
        const buttons = await page.locator('button').allTextContents();
        console.log('Available buttons:', buttons.filter(b => b.trim()));
        
        // THE CRITICAL TEST - Try clicking "Yes, I have a lawyer"
        console.log('\n🔥 TESTING LAWYER BUTTON CLICK...');
        
        try {
          await page.click('button:has-text("Yes, I have a lawyer")');
          await page.waitForTimeout(3000); // Give it time
          
          // Check what happened after clicking
          const afterClickContent = await page.content();
          
          if (afterClickContent.includes('Error')) {
            const errorMsg = await page.locator('blockquote').textContent();
            console.log('❌ LAWYER BUTTON ERROR:', errorMsg);
          } else if (afterClickContent.includes('Your Lawyer') || afterClickContent.includes('Lawyer\'s Name')) {
            console.log('🎉 SUCCESS! LAWYER BUTTON WORKS!');
            console.log('✅ Lawyer form loaded successfully');
            
            // Show what fields are in lawyer form
            const lawyerInputs = await page.locator('input').all();
            console.log('\nLawyer form fields:');
            for (let input of lawyerInputs) {
              const name = await input.getAttribute('name');
              if (name && !name.includes('csrf') && !name.includes('_back')) {
                console.log(`  - ${name}`);
              }
            }
            
          } else {
            console.log('❓ UNEXPECTED RESULT after clicking lawyer button');
            console.log('Content keywords:', ['lawyer', 'Lawyer', 'form', 'name', 'phone'].filter(k => afterClickContent.includes(k)));
          }
          
        } catch (clickError) {
          console.log('❌ LAWYER BUTTON CLICK FAILED:', clickError.message);
        }
        
      } else {
        console.log('❌ Lawyer question not found');
        console.log('Page contains:', ['lawyer', 'Lawyer', 'legal', 'representation'].filter(k => content.includes(k)));
      }
      
    } else {
      console.log('❌ Other party form not found');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n========================');
  console.log('LAWYER BUTTON TEST DONE');
  console.log('========================');
})();