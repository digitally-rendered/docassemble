const { chromium } = require('playwright');

(async () => {
  console.log('TESTING PARTY FIELDS WITH CORRECT NAMES');
  console.log('========================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Navigate to wizard
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Quick navigation
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency  
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.click('button:has-text("Never lived together")'); // Relationship
    await page.check('text=Child custody'); // Orders
    await page.click('button[type="submit"]#da-continue-button');
    
    // Skip financial if present
    await page.waitForTimeout(500);
    if ((await page.content()).includes('financial situation')) {
      await page.click('button[type="submit"]#da-continue-button');
    }
    
    // Select applicant
    await page.click('button:has-text("I am starting a new case")');
    await page.waitForTimeout(1000);
    
    console.log('Filling User Information form...\n');
    
    // Fill fields by their base64 encoded names
    // dXNlcl9wYXJ0eS5uYW1lLmZpcnN0 = user_party.name.first
    await page.fill('input[name="dXNlcl9wYXJ0eS5uYW1lLmZpcnN0"]', 'John');
    
    // dXNlcl9wYXJ0eS5uYW1lLmxhc3Q = user_party.name.last
    await page.fill('input[name="dXNlcl9wYXJ0eS5uYW1lLmxhc3Q"]', 'Smith');
    
    // dXNlcl9wYXJ0eS5iaXJ0aGRhdGU = user_party.birthdate
    await page.fill('input[name="dXNlcl9wYXJ0eS5iaXJ0aGRhdGU"]', '1990-01-01');
    
    // dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI = user_party.phone_number
    await page.fill('input[name="dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI"]', '4165550100');
    
    // dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M = user_party.address.address
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M"]', '123 Test Street');
    
    // dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk = user_party.address.city
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk"]', 'Toronto');
    
    // dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl = user_party.address.state (Province)
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl"]', 'Ontario');
    
    // dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl = user_party.address.postal_code
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl"]', 'M5H 2N2');
    
    console.log('Submitting user information...');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    // Check if we moved to other party
    const content = await page.content();
    if (content.includes('Other Party')) {
      console.log('✅ Moved to Other Party Information!\n');
      
      // Fill other party fields
      console.log('Filling Other Party Information...');
      
      // other_party.name.first
      await page.fill('input[name="b3RoZXJfcGFydHkubmFtZS5maXJzdA"]', 'Jane');
      
      // other_party.name.last
      await page.fill('input[name="b3RoZXJfcGFydHkubmFtZS5sYXN0"]', 'Doe');
      
      console.log('Submitting other party information...');
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1500);
      
      // Check for lawyer question
      const afterOther = await page.content();
      if (afterOther.includes('Do you have a lawyer?')) {
        console.log('✅ Reached User Lawyer Question!\n');
        
        console.log('Selecting "No, I am self-represented"...');
        await page.click('button:has-text("No, I am self-represented")');
        await page.waitForTimeout(1500);
        
        // Check for other party lawyer
        const afterUserLawyer = await page.content();
        if (afterUserLawyer.includes('Does the other party have a lawyer?')) {
          console.log('✅ REACHED OTHER PARTY LAWYER QUESTION!\n');
          
          console.log('🎯 CLICKING "YES, THEY HAVE A LAWYER"...');
          await page.click('button:has-text("Yes, they have a lawyer")');
          await page.waitForTimeout(2000);
          
          // Check result
          const final = await page.content();
          const heading = await page.locator('h1, h2').first().textContent();
          
          if (final.includes('Lawyer') && (final.includes('Information') || final.includes('information'))) {
            console.log('🎉 SUCCESS! LAWYER FORM IS DISPLAYED!');
            console.log(`Screen shows: "${heading}"`);
            
            // Try to fill the lawyer form
            console.log('\nFilling lawyer information...');
            const lawyerInputs = await page.locator('input[type="text"]').all();
            if (lawyerInputs.length > 0) {
              await lawyerInputs[0].fill('John Lawyer');
              console.log('Filled lawyer name');
              
              await page.click('button[type="submit"]#da-continue-button');
              await page.waitForTimeout(1000);
              
              const afterLawyer = await page.content();
              if (afterLawyer.includes('Court')) {
                console.log('✅ Successfully continued to Court Information!');
              }
            }
            
          } else if (final.includes('Court Information')) {
            console.log('⚠️ PROBLEM: Skipped lawyer form, went to Court Information');
            console.log('The "show if" condition may not be working');
            
          } else if (final.includes('Error')) {
            console.log('❌ ERROR after clicking lawyer button');
            const errorMsg = await page.locator('blockquote').textContent();
            console.log('Error:', errorMsg);
            
          } else {
            console.log(`❓ Unexpected screen: "${heading}"`);
          }
          
        } else {
          console.log('❌ Other party lawyer question did not appear');
          const heading = await page.locator('h1, h2').first().textContent();
          console.log(`Current screen: "${heading}"`);
        }
        
      } else {
        console.log('❌ User lawyer question did not appear');
      }
      
    } else {
      console.log('❌ Failed to move from User Information');
      
      // Check for errors
      const errors = await page.locator('.alert-danger, .text-danger').allTextContents();
      if (errors.length > 0) {
        console.log('Validation errors:');
        errors.forEach(err => {
          if (err.trim()) console.log(`  - ${err}`);
        });
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n========================================');
  console.log('Test complete');
})();