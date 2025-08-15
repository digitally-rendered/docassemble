const { chromium } = require('playwright');

/**
 * FINAL TEST: Lawyer Form Fix Verification
 * 
 * After fixing the YAML variable naming inconsistency, this test verifies:
 * 1. User information form fills correctly
 * 2. Other party information form advances properly  
 * 3. User lawyer question appears and responds correctly
 * 4. Other party lawyer question appears  
 * 5. CRITICAL: Other party lawyer form appears when clicking "Yes"
 * 6. Lawyer form fields can be filled without errors
 */

(async () => {
  console.log('🎯 FINAL LAWYER FORM FIX TEST');
  console.log('=============================\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 200
  });
  
  const context = await browser.newContext({
    recordVideo: {
      dir: './test-results/',
      size: { width: 1280, height: 720 }
    }
  });
  
  const page = await context.newPage();
  
  try {
    console.log('🌐 Starting final verification test...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Quick navigation to the critical point
    console.log('🚀 Quick navigation through initial screens...');
    
    await page.click('button[type=\"submit\"]#da-continue-button'); // Welcome
    await page.waitForTimeout(800);
    
    await page.click('button:has-text(\"No, this is not an emergency\")'); // Emergency  
    await page.waitForTimeout(800);
    
    await page.click('button:has-text(\"Yes, I have my certificate\")'); // MIP
    await page.waitForTimeout(800);
    
    await page.click('button[type=\"submit\"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(800);
    
    await page.click('button:has-text(\"Never lived together\")'); // Relationship
    await page.waitForTimeout(800);
    
    await page.check('text=Child custody'); // Orders
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(800);
    
    await page.click('button:has-text(\"I am starting a new case\")'); // Role
    await page.waitForTimeout(1500);
    
    // Fill user information with the proven strategy
    console.log('📝 Filling user information...');
    
    const userFields = {
      'dXNlcl9wYXJ0eS5uYW1lLmZpcnN0': 'John',
      'dXNlcl9wYXJ0eS5uYW1lLmxhc3Q': 'Doe', 
      'dXNlcl9wYXJ0eS5iaXJ0aGRhdGU': '1985-03-15',
      'dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI': '4165551234',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M': '456 Main St',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk': 'Toronto',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl': 'Ontario',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl': 'M4A1B2'
    };
    
    for (const [name, value] of Object.entries(userFields)) {
      const field = page.locator(`input[name=\"${name}\"]`);
      if (await field.count() > 0) {
        await field.fill(value);
      }
    }
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    // Fill other party information  
    console.log('📝 Filling other party information...');
    
    const otherFields = {
      'b3RoZXJfcGFydHkubmFtZS5maXJzdA': 'Jane',
      'b3RoZXJfcGFydHkubmFtZS5sYXN0': 'Smith'
    };
    
    for (const [name, value] of Object.entries(otherFields)) {
      const field = page.locator(`input[name=\"${name}\"]`);
      if (await field.count() > 0) {
        await field.fill(value);
      }
    }
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    // User lawyer question
    console.log('⚖️ Handling user lawyer question...');
    await page.click('button:has-text(\"No, I am self-represented\")');
    await page.waitForTimeout(1500);
    
    // THE CRITICAL MOMENT: Other party lawyer question
    console.log('🎯 THE CRITICAL TEST: Other party lawyer question');
    
    let content = await page.content();
    if (content.includes('Does the other party have a lawyer?')) {
      console.log('   ✅ Other party lawyer question found');
      
      await page.screenshot({ path: './final-test-before-click.png' });
      console.log('   🔄 Clicking \"Yes, they have a lawyer\"...');
      
      await page.click('button:has-text(\"Yes, they have a lawyer\")');
      await page.waitForTimeout(2000);
      
      // Check the result
      content = await page.content();
      const heading = await page.locator('h1, h2').first().textContent();
      await page.screenshot({ path: './final-test-after-click.png' });
      
      console.log(`   📋 Result: \"${heading}\"`);
      
      if (content.includes('Other Party') && content.includes('Lawyer') && content.includes('Information')) {
        console.log('   🎉 SUCCESS! Other party lawyer form appeared!');
        console.log('   ✅ The YAML fix worked correctly!');
        
        // Test filling the lawyer form
        console.log('   📝 Testing lawyer form fields...');
        
        try {
          // Look for lawyer name field
          const lawyerFields = await page.locator('input[type=\"text\"]').all();
          if (lawyerFields.length > 0) {
            await lawyerFields[0].fill('Attorney Smith');
            console.log('   ✅ Filled lawyer name successfully');
            
            if (lawyerFields.length > 1) {
              await lawyerFields[1].fill('Smith & Associates');
              console.log('   ✅ Filled law firm successfully'); 
            }
            
            // Try to continue 
            await page.click('button[type=\"submit\"]#da-continue-button');
            await page.waitForTimeout(2000);
            
            const nextHeading = await page.locator('h1, h2').first().textContent();
            console.log(`   ➡️ Advanced to: \"${nextHeading}\"`);
            
            if (nextHeading.includes('Court')) {
              console.log('   🎯 COMPLETE SUCCESS! Advanced to Court Information as expected!');
            }
            
          } else {
            console.log('   ⚠️ No text fields found in lawyer form');
          }
        } catch (error) {
          console.log(`   ⚠️ Error filling lawyer form: ${error.message}`);
        }
        
      } else if (content.includes('Court')) {
        console.log('   ❌ STILL BROKEN: Skipped directly to Court Information');
        console.log('   🔍 The YAML fix may not be complete or there is another issue');
        
      } else if (content.includes('Error')) {
        console.log('   ❌ ERROR: An error occurred after clicking Yes');
        const errorPreview = content.substring(content.indexOf('Error'), content.indexOf('Error') + 200);
        console.log(`   📄 Error preview: ${errorPreview}`);
        
      } else {
        console.log('   ❓ UNEXPECTED: Unknown screen after clicking Yes');
        console.log(`   📄 Content preview: ${content.substring(0, 300)}`);
      }
      
    } else {
      console.log('   ❌ FAILURE: Other party lawyer question not found');
      const currentHeading = await page.locator('h1, h2').first().textContent();
      console.log(`   📋 Current screen: \"${currentHeading}\"`);
    }
    
  } catch (error) {
    console.error('🚨 Test failed:', error);
    await page.screenshot({ path: './final-test-error.png' });
  }
  
  console.log('\n🏁 FINAL TEST COMPLETE');
  console.log('=======================');
  console.log('📹 Video: test-results/');
  console.log('🖼️ Screenshots: ./final-test-*.png');
  console.log('\nBrowser will stay open for inspection...');
  
  // Keep open for examination
  await new Promise((resolve) => {
    process.on('SIGINT', resolve);
  });
  
  await context.close();  
  await browser.close();
})();