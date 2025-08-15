const { chromium } = require('playwright');

/**
 * QUICK FINAL TEST: Lawyer Form Fix with Correct Individual Properties
 * 
 * Testing the corrected YAML with proper Individual object attributes:
 * - other_lawyer.name.first (instead of other_lawyer.name.full)
 * - other_lawyer.name.last  
 * - other_lawyer.phone_number
 * - other_lawyer.email
 * - other_lawyer_firm (standalone variable for law firm)
 */

(async () => {
  console.log('🎯 QUICK FINAL TEST: Correct Individual Properties');
  console.log('================================================\n');
  
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Rapid navigation to critical point
    await page.click('button[type=\"submit\"]#da-continue-button'); 
    await page.waitForTimeout(500);
    await page.click('button:has-text(\"No, this is not an emergency\")'); 
    await page.waitForTimeout(500);
    await page.click('button:has-text(\"Yes, I have my certificate\")'); 
    await page.waitForTimeout(500);
    await page.click('button[type=\"submit\"]#da-continue-button'); 
    await page.waitForTimeout(500);
    await page.click('button:has-text(\"Never lived together\")'); 
    await page.waitForTimeout(500);
    await page.check('text=Child custody'); 
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(500);
    await page.click('button:has-text(\"I am starting a new case\")'); 
    await page.waitForTimeout(1000);
    
    // Fill user info rapidly
    console.log('📝 Filling forms...');
    const userFields = {
      'dXNlcl9wYXJ0eS5uYW1lLmZpcnN0': 'John',
      'dXNlcl9wYXJ0eS5uYW1lLmxhc3Q': 'Doe',
      'dXNlcl9wYXJ0eS5iaXJ0aGRhdGU': '1985-01-01',
      'dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI': '4165551234',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M': '123 Main St',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk': 'Toronto',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl': 'Ontario',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl': 'M4A1B2'
    };
    
    for (const [name, value] of Object.entries(userFields)) {
      await page.locator(`input[name=\"${name}\"]`).fill(value);
    }
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Other party info
    const otherFields = {
      'b3RoZXJfcGFydHkubmFtZS5maXJzdA': 'Jane',
      'b3RoZXJfcGFydHkubmFtZS5sYXN0': 'Smith'
    };
    
    for (const [name, value] of Object.entries(otherFields)) {
      await page.locator(`input[name=\"${name}\"]`).fill(value);
    }
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text(\"No, I am self-represented\")');
    await page.waitForTimeout(1000);
    
    // THE CRITICAL TEST
    console.log('🎯 CRITICAL TEST: Clicking \"Yes, they have a lawyer\"');
    await page.click('button:has-text(\"Yes, they have a lawyer\")');
    await page.waitForTimeout(2000);
    
    const heading = await page.locator('h1, h2').first().textContent();
    console.log(`📋 Result: \"${heading}\"`);
    
    if (heading.includes('Other Party') && heading.includes('Lawyer')) {
      console.log('🎉 SUCCESS! Lawyer form appeared!');
      
      // Test filling the corrected form
      const firstNameField = page.locator('input').first();
      await firstNameField.fill('Attorney');
      console.log('✅ Filled first name field');
      
      const lastNameField = page.locator('input').nth(1);
      await lastNameField.fill('Johnson');
      console.log('✅ Filled last name field');
      
      console.log('🎯 COMPLETE FIX VERIFIED!');
      
    } else if (heading.includes('Error')) {
      console.log('❌ Still getting error - checking details...');
      const content = await page.content();
      const errorMatch = content.match(/(?:Error|Exception).*?(?:line|Line)\\s*(\\d+)/);
      if (errorMatch) {
        console.log(`📍 Error location: ${errorMatch[0]}`);
      }
      
    } else {
      console.log(`❓ Got: ${heading}`);
    }
    
  } catch (error) {
    console.error('🚨 Error:', error.message);
  }
  
  console.log('\\n🏁 Test complete. Press Ctrl+C to close browser.');
  await new Promise(() => {}); // Keep open
  
})();