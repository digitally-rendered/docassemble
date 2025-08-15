const { chromium } = require('playwright');

/**
 * CONDITION FIX TEST: Simplify Boolean Check
 * 
 * Changed from "if other_party_has_lawyer is True:" to "if other_party_has_lawyer:"
 * This might fix the issue if Docassemble has problems with explicit boolean comparison.
 */

(async () => {
  console.log('🎯 CONDITION FIX TEST');
  console.log('=====================\n');
  
  const browser = await chromium.launch({ headless: false, slowMo: 150 });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Lightning-fast navigation
    await page.click('button[type=\"submit\"]#da-continue-button'); 
    await page.waitForTimeout(300);
    await page.click('button:has-text(\"No, this is not an emergency\")'); 
    await page.waitForTimeout(300);
    await page.click('button:has-text(\"Yes, I have my certificate\")'); 
    await page.waitForTimeout(300);
    await page.click('button[type=\"submit\"]#da-continue-button'); 
    await page.waitForTimeout(300);
    await page.click('button:has-text(\"Never lived together\")'); 
    await page.waitForTimeout(300);
    await page.check('text=Child custody'); 
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(300);
    await page.click('button:has-text(\"I am starting a new case\")'); 
    await page.waitForTimeout(800);
    
    console.log('⚡ Filling forms...');
    
    // User fields
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5uYW1lLmZpcnN0\"]').fill('Test');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5uYW1lLmxhc3Q\"]').fill('User');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5iaXJ0aGRhdGU\"]').fill('1990-01-01');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI\"]').fill('4165551000');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M\"]').fill('123 Test St');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk\"]').fill('Toronto');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl\"]').fill('Ontario');
    await page.locator('input[name=\"dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl\"]').fill('M1A1A1');
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(800);
    
    // Other party fields
    await page.locator('input[name=\"b3RoZXJfcGFydHkubmFtZS5maXJzdA\"]').fill('Other');
    await page.locator('input[name=\"b3RoZXJfcGFydHkubmFtZS5sYXN0\"]').fill('Party');
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(800);
    
    await page.click('button:has-text(\"No, I am self-represented\")');
    await page.waitForTimeout(800);
    
    console.log('🎯 CRITICAL TEST: Clicking \"Yes, they have a lawyer\"');
    console.log('   (Testing simplified condition: if other_party_has_lawyer:)');
    
    await page.click('button:has-text(\"Yes, they have a lawyer\")');
    await page.waitForTimeout(1500);
    
    const heading = await page.locator('h1, h2').first().textContent();
    console.log(`\\n📋 RESULT: \"${heading}\"`);
    
    if (heading && heading.includes('Other Party') && heading.includes('Lawyer') && heading.includes('Information')) {
      console.log('🎉 SUCCESS! The condition fix worked!');
      console.log('✅ Lawyer form is now appearing correctly!');
      console.log('🏆 COMPLETE BUG FIX ACHIEVED!');
      
    } else if (heading && heading.includes('Court')) {
      console.log('❌ Still skipping to Court - need to investigate further');
      
    } else if (heading && heading.includes('Error')) {
      console.log('❌ Error occurred');
      
    } else {
      console.log(`❓ Unexpected result: ${heading || 'No heading found'}`);
    }
    
  } catch (error) {
    console.error('🚨 Test failed:', error.message);
  }
  
  console.log('\\n🏁 Test complete - press Ctrl+C when ready');
  await new Promise(() => {});
  
})();