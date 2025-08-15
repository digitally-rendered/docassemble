const { chromium } = require('playwright');

(async () => {
  console.log('TESTING ENHANCED PARTY AND LAWYER OBJECTS');
  console.log('==========================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('1. Loading wizard with enhanced objects...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    // Check if wizard loads
    const content = await page.content();
    
    if (content.includes('Welcome to the Ontario Family Law Forms Wizard')) {
      console.log('✅ Wizard loaded successfully\n');
      
      // Navigate through initial screens
      console.log('2. Navigating to party information...');
      await page.click('button[type="submit"]#da-continue-button'); // Welcome
      await page.waitForTimeout(500);
      await page.click('button:has-text("No, this is not an emergency")'); // Emergency
      await page.waitForTimeout(500);
      await page.click('button:has-text("Yes, I have my certificate")'); // MIP
      await page.waitForTimeout(500);
      await page.click('button[type="submit"]#da-continue-button'); // MIP continue
      await page.waitForTimeout(500);
      await page.click('button:has-text("Married")'); // Relationship - testing married for more fields
      await page.waitForTimeout(500);
      
      // Select multiple orders to test financial forms
      console.log('3. Selecting orders (divorce, custody, support)...');
      await page.check('text=Divorce');
      await page.check('text=Child custody');
      await page.check('text=Child support');
      await page.check('text=Spousal support');
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
      
      // Divorce complexity
      await page.click('button:has-text("Contested")');
      await page.waitForTimeout(500);
      
      // Financial complexity
      const financialContent = await page.content();
      if (financialContent.includes('financial situation')) {
        console.log('4. Filling enhanced financial information...');
        
        // Try to fill the financial form fields
        const inputs = await page.locator('input[type="text"], input[type="number"]').all();
        if (inputs.length > 0) {
          // Fill property value
          for (const input of inputs) {
            const name = await input.getAttribute('name');
            if (name && name.includes('property')) {
              await input.fill('150000');
              break;
            }
          }
        }
        
        // Select radio buttons
        const radioButtons = await page.locator('input[type="radio"]').all();
        for (let i = 0; i < Math.min(4, radioButtons.length); i++) {
          if (i % 2 === 0) {
            await radioButtons[i].click(); // Click every other radio
          }
        }
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
      }
      
      // Check for role selection
      const roleContent = await page.content();
      if (roleContent.includes('Your Role in the Legal Proceeding')) {
        console.log('5. Selecting Applicant role...');
        await page.click('button:has-text("I am starting a new case")');
        await page.waitForTimeout(1500);
      }
      
      // Check for enhanced user information form
      const userContent = await page.content();
      if (userContent.includes('Your Information')) {
        console.log('✅ ENHANCED USER FORM LOADED!\n');
        
        // Check for new Individual fields
        const hasGenderField = userContent.includes('Gender');
        const hasOtherNamesField = userContent.includes('Any other names used');
        const hasAlternativePhone = userContent.includes('Phone Number (Alternative)');
        const hasCountryField = userContent.includes('Country');
        
        console.log('Enhanced Individual fields detected:');
        console.log(`  - Gender field: ${hasGenderField ? '✅' : '❌'}`);
        console.log(`  - Other names field: ${hasOtherNamesField ? '✅' : '❌'}`);
        console.log(`  - Alternative phone: ${hasAlternativePhone ? '✅' : '❌'}`);
        console.log(`  - Country field: ${hasCountryField ? '✅' : '❌'}`);
        
        // Fill the enhanced form
        console.log('\n6. Filling enhanced user information...');
        
        // Fill by field names (base64 encoded)
        const allInputs = await page.locator('input').all();
        let fieldsFilled = 0;
        
        for (const input of allInputs) {
          const name = await input.getAttribute('name');
          const type = await input.getAttribute('type');
          
          if (name && type !== 'hidden') {
            // First name
            if (name.includes('Zmlyc3Q')) {
              await input.fill('John');
              fieldsFilled++;
            }
            // Last name  
            else if (name.includes('bGFzdA')) {
              await input.fill('Smith');
              fieldsFilled++;
            }
            // Birthdate
            else if (type === 'date') {
              await input.fill('1985-06-15');
              fieldsFilled++;
            }
            // Phone
            else if (name.includes('waG9uZQ') && type !== 'hidden') {
              await input.fill('4165551234');
              fieldsFilled++;
            }
            // Email
            else if (type === 'email') {
              await input.fill('john.smith@example.com');
              fieldsFilled++;
            }
            // Address
            else if (name.includes('YWRkcmVzcw') && name.includes('YWRkcmVzcw')) {
              await input.fill('123 King Street West');
              fieldsFilled++;
            }
            // City
            else if (name.includes('Y2l0eQ')) {
              await input.fill('Toronto');
              fieldsFilled++;
            }
            // Postal code
            else if (name.includes('cG9zdGFs')) {
              await input.fill('M5H 2N2');
              fieldsFilled++;
            }
          }
        }
        
        console.log(`  Filled ${fieldsFilled} fields`);
        
        // Select gender if present
        const genderSelects = await page.locator('select').all();
        for (const select of genderSelects) {
          const name = await select.getAttribute('name');
          if (name && name.includes('gender')) {
            await select.selectOption('male');
            console.log('  Selected gender: Male');
          }
        }
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1500);
        
        // Check if we moved to other party
        const afterUser = await page.content();
        if (afterUser.includes('Other Party')) {
          console.log('\n✅ User form accepted - moved to Other Party!');
          
          // Check for enhanced other party fields
          const hasOtherGender = afterUser.includes('Gender');
          const hasOtherAlternative = afterUser.includes('Alternative');
          
          console.log('Enhanced Other Party fields:');
          console.log(`  - Gender field: ${hasOtherGender ? '✅' : '❌'}`);
          console.log(`  - Alternative contacts: ${hasOtherAlternative ? '✅' : '❌'}`);
          
        } else if (afterUser.includes('Error')) {
          console.log('\n❌ Validation error occurred');
          const errors = await page.locator('.alert-danger, .text-danger').allTextContents();
          errors.forEach(err => {
            if (err.trim()) console.log(`  Error: ${err.trim()}`);
          });
        } else {
          console.log('\n❓ Still on user form - may have validation issues');
        }
        
      } else {
        console.log('❌ Enhanced user form did not appear');
        const heading = await page.locator('h1, h2').first().textContent();
        console.log(`Current screen: ${heading}`);
      }
      
    } else if (content.includes('Error')) {
      console.log('❌ Error on load');
      try {
        const errorMsg = await page.locator('blockquote').textContent();
        console.log('Error:', errorMsg);
        
        // Check for specific validation or object errors
        if (errorMsg.includes('validate_')) {
          console.log('⚠️ Validation function error - may need to import from common file');
        }
        if (errorMsg.includes('province_list') || errorMsg.includes('countries_list')) {
          console.log('⚠️ Helper function error - may need to define these functions');
        }
      } catch (e) {
        console.log('Could not extract error details');
      }
    } else {
      console.log('❓ Unexpected content');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n==========================================');
  console.log('Enhanced objects test complete');
})();