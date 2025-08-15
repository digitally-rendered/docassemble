const { chromium } = require('playwright');

(async () => {
  console.log('TESTING COMPLETE NEVER LIVED TOGETHER FLOW');
  console.log('===========================================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('1. Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Welcome screen
    console.log('2. Welcome screen...');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Emergency check
    console.log('3. Not an emergency...');
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(500);
    
    // MIP
    console.log('4. MIP completed...');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Relationship status - NEVER LIVED TOGETHER
    console.log('5. Never lived together...');
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(1000);
    
    // Orders
    console.log('6. Selecting child custody and support...');
    await page.check('text=Child custody');
    await page.check('text=Child support');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Financial complexity (if appears)
    const content1 = await page.content();
    if (content1.includes('financial situation')) {
      console.log('7. Filling financial information...');
      
      // Find the property value field - Docassemble uses encoded field names
      const propertyInput = await page.locator('input[type="text"]').filter({ has: page.locator('[data-testid="property-value-field"]') }).first();
      if (await propertyInput.count() > 0) {
        await propertyInput.fill('50000');
      } else {
        // Try alternative selector
        await page.fill('input[type="text"]', '50000');
      }
      
      // Click radio buttons for other fields
      const radioButtons = await page.locator('input[type="radio"][value="True"]');
      if (await radioButtons.count() > 0) {
        await radioButtons.first().click(); // support_involved = True
      }
      
      // Click No for business and pension
      await page.locator('input[type="radio"][value="False"]').nth(1).click(); // business_owner = False
      await page.locator('input[type="radio"][value="False"]').nth(3).click(); // pension_involved = False
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
    }
    
    // Check for party information
    const content2 = await page.content();
    
    if (content2.includes('Your Role in the Legal Proceeding')) {
      console.log('✅ PARTY INFORMATION SECTION REACHED!');
      
      // Select applicant
      console.log('8. Selecting Applicant role...');
      await page.click('button:has-text("I am starting a new case (Applicant)")');
      await page.waitForTimeout(1000);
      
      // Fill user information
      const content3 = await page.content();
      if (content3.includes('Your Information')) {
        console.log('✅ User information form displayed');
        
        console.log('9. Filling user information...');
        await page.fill('input[name*="name.first"]', 'Test');
        await page.fill('input[name*="name.last"]', 'User');
        await page.fill('input[name*="birthdate"]', '1990-01-01');
        await page.fill('input[name*="phone_number"]', '416-555-0100');
        await page.fill('input[name*="address.address"]', '123 Test St');
        await page.fill('input[name*="address.city"]', 'Toronto');
        await page.fill('input[name*="postal_code"]', 'M5H 2N2');
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        // Other party information
        const content4 = await page.content();
        if (content4.includes('Other Party')) {
          console.log('✅ Other party information form displayed');
          
          console.log('10. Filling other party information...');
          await page.fill('input[name*="name.first"]', 'Other');
          await page.fill('input[name*="name.last"]', 'Party');
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          // Check for lawyer question
          const content5 = await page.content();
          if (content5.includes('Do you have a lawyer?')) {
            console.log('✅ Lawyer question reached');
            
            console.log('11. Self-represented...');
            await page.click('button:has-text("No, I am self-represented")');
            await page.waitForTimeout(1000);
            
            // Other party lawyer
            const content6 = await page.content();
            if (content6.includes('Does the other party have a lawyer?')) {
              console.log('✅ Other party lawyer question');
              
              console.log('12. Testing problematic "Yes" button...');
              await page.click('button:has-text("Yes, they have a lawyer")');
              await page.waitForTimeout(2000);
              
              // Check what happens
              const content7 = await page.content();
              if (content7.includes('Other Party\'s Lawyer Information')) {
                console.log('🎉 SUCCESS! LAWYER FORM DISPLAYED!');
                console.log('THE LAWYER BUTTON WORKS IN NEVER TOGETHER FLOW!');
              } else if (content7.includes('Error')) {
                console.log('❌ Error after clicking lawyer button');
                try {
                  const errorMsg = await page.locator('blockquote').textContent();
                  console.log('Error:', errorMsg);
                } catch (e) {
                  console.log('Could not get error details');
                }
              } else if (content7.includes('Court Information')) {
                console.log('⚠️ Skipped to court info (lawyer form not shown)');
              } else {
                console.log('❓ Unexpected result after lawyer button');
                const heading = await page.locator('h1, h2').first().textContent();
                console.log('Current screen:', heading);
              }
            }
          }
        }
      }
      
    } else if (content2.includes('Error')) {
      console.log('❌ Error reaching party information');
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('Error:', errorMsg);
    } else {
      console.log('❓ Unexpected screen');
      const heading = await page.locator('h1, h2').first().textContent();
      console.log('Current screen:', heading);
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n===========================================');
  console.log('Never lived together flow test complete');
})();