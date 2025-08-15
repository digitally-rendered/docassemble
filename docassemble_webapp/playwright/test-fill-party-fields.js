const { chromium } = require('playwright');

(async () => {
  console.log('TESTING PARTY FIELD FILLING');
  console.log('============================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Navigate to wizard
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Quick navigation to party section
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
    
    console.log('At User Information form...\n');
    
    // Get all input fields and their attributes
    const inputs = await page.locator('input').all();
    console.log(`Found ${inputs.length} input fields:`);
    
    for (let i = 0; i < inputs.length; i++) {
      const input = inputs[i];
      const name = await input.getAttribute('name');
      const type = await input.getAttribute('type');
      const required = await input.getAttribute('required');
      const placeholder = await input.getAttribute('placeholder');
      
      console.log(`Field ${i}: name="${name}" type="${type}" required="${required !== null}" placeholder="${placeholder}"`);
      
      // Try to fill based on the encoded field name patterns
      if (name) {
        try {
          // Docassemble uses base64 encoded field names
          // Look for patterns in the name
          if (type === 'text' || type === 'tel') {
            if (i === 0 || name.includes('first')) {
              await input.fill('TestFirst');
              console.log('  -> Filled with: TestFirst');
            } else if (i === 2 || name.includes('last')) {
              await input.fill('TestLast');
              console.log('  -> Filled with: TestLast');
            } else if (type === 'tel' || placeholder?.includes('phone')) {
              await input.fill('4165550100');
              console.log('  -> Filled with: 4165550100');
            } else if (i === 7 || placeholder?.includes('address')) {
              await input.fill('123 Test Street');
              console.log('  -> Filled with: 123 Test Street');
            } else if (i === 9 || placeholder?.includes('city')) {
              await input.fill('Toronto');
              console.log('  -> Filled with: Toronto');
            } else if (i === 11 || placeholder?.includes('postal')) {
              await input.fill('M5H 2N2');
              console.log('  -> Filled with: M5H 2N2');
            }
          } else if (type === 'date') {
            await input.fill('1990-01-01');
            console.log('  -> Filled with: 1990-01-01');
          } else if (type === 'email') {
            await input.fill('test@example.com');
            console.log('  -> Filled with: test@example.com');
          }
        } catch (e) {
          console.log(`  -> Could not fill: ${e.message}`);
        }
      }
    }
    
    console.log('\nSubmitting form...');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    // Check where we are now
    const content = await page.content();
    const heading = await page.locator('h1, h2').first().textContent();
    
    if (content.includes('Other Party')) {
      console.log('✅ Successfully moved to Other Party Information!');
      
      // Fill other party minimally
      const otherInputs = await page.locator('input[type="text"]').all();
      if (otherInputs.length >= 2) {
        await otherInputs[0].fill('OtherFirst');
        await otherInputs[1].fill('OtherLast');
      }
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      // Check for lawyer questions
      const afterOther = await page.content();
      if (afterOther.includes('Do you have a lawyer?')) {
        console.log('✅ Reached user lawyer question!');
        
        await page.click('button:has-text("No, I am self-represented")');
        await page.waitForTimeout(1000);
        
        const afterUserLawyer = await page.content();
        if (afterUserLawyer.includes('Does the other party have a lawyer?')) {
          console.log('✅ REACHED OTHER PARTY LAWYER QUESTION!');
          
          console.log('\nTESTING THE PROBLEMATIC BUTTON...');
          await page.click('button:has-text("Yes, they have a lawyer")');
          await page.waitForTimeout(2000);
          
          const final = await page.content();
          if (final.includes('Lawyer') && final.includes('Information')) {
            console.log('🎉 SUCCESS! LAWYER FORM DISPLAYED!');
          } else if (final.includes('Court')) {
            console.log('⚠️ Skipped to Court Information');
          } else {
            const finalHeading = await page.locator('h1, h2').first().textContent();
            console.log(`Result: ${finalHeading}`);
          }
        }
      }
      
    } else {
      console.log(`Still on: ${heading}`);
      
      // Check for validation errors
      const errors = await page.locator('.alert-danger, .text-danger, .invalid-feedback').allTextContents();
      if (errors.length > 0) {
        console.log('\nValidation errors found:');
        errors.forEach(err => {
          if (err.trim()) console.log(`  - ${err}`);
        });
      }
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n============================');
  console.log('Field filling test complete');
})();