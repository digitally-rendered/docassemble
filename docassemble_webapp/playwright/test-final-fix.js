const { chromium } = require('playwright');

/**
 * FINAL FIX TEST: Remove Show If Condition Conflict
 * 
 * The issue was that both the mandatory code AND the question had 
 * the same conditional logic, which created a conflict. This test 
 * verifies that removing the redundant "show if" condition fixes 
 * the lawyer form display issue.
 */

(async () => {
  console.log('🔧 FINAL FIX TEST: Remove Show If Conflict');
  console.log('==========================================\n');
  
  const browser = await chromium.launch({ headless: false, slowMo: 200 });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Super quick navigation
    console.log('⚡ Quick navigation to the critical point...');
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
    
    // Fill forms quickly
    const userFields = {
      'dXNlcl9wYXJ0eS5uYW1lLmZpcnN0': 'Quick',
      'dXNlcl9wYXJ0eS5uYW1lLmxhc3Q': 'Test',
      'dXNlcl9wYXJ0eS5iaXJ0aGRhdGU': '1990-01-01',
      'dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI': '4165551000',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M': '100 Quick St',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk': 'Toronto',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnN0YXRl': 'Ontario',
      'dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl': 'M1A1A1'
    };
    
    for (const [name, value] of Object.entries(userFields)) {
      await page.locator(`input[name=\"${name}\"]`).fill(value);
    }
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    const otherFields = {
      'b3RoZXJfcGFydHkubmFtZS5maXJzdA': 'Other',
      'b3RoZXJfcGFydHkubmFtZS5sYXN0': 'Person'
    };
    
    for (const [name, value] of Object.entries(otherFields)) {
      await page.locator(`input[name=\"${name}\"]`).fill(value);
    }
    
    await page.click('button[type=\"submit\"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text(\"No, I am self-represented\")');
    await page.waitForTimeout(1000);
    
    // THE MOMENT OF TRUTH
    console.log('🎯 THE CRITICAL MOMENT - Clicking \"Yes, they have a lawyer\"...');
    
    await page.screenshot({ path: './final-fix-before-click.png' });
    await page.click('button:has-text(\"Yes, they have a lawyer\")');
    await page.waitForTimeout(2000);
    
    const result = await page.locator('h1, h2').first().textContent();
    await page.screenshot({ path: './final-fix-after-click.png' });
    
    console.log(`\\n📋 RESULT: \"${result}\"`);
    
    if (result.includes('Other Party') && result.includes('Lawyer') && result.includes('Information')) {
      console.log('🎉 VICTORY! The lawyer form finally appears!');
      console.log('✅ The \"show if\" conflict was indeed the issue!');
      console.log('🏆 BUG COMPLETELY FIXED!');
      
      // Test that the form actually works
      const inputField = page.locator('input[type=\"text\"]').first();
      await inputField.fill('Success Attorney');
      console.log('✅ Can fill lawyer form fields');
      
      await page.click('button[type=\"submit\"]#da-continue-button');
      await page.waitForTimeout(1500);
      
      const nextScreen = await page.locator('h1, h2').first().textContent();
      console.log(`📋 Next screen: \"${nextScreen}\"`);
      
      if (nextScreen.includes('Court')) {
        console.log('🎯 PERFECT END-TO-END! Advanced to Court Information!');
      }
      
    } else if (result.includes('Court')) {
      console.log('❌ Still skipping - there may be another issue');
      
    } else if (result.includes('Error')) {
      console.log('❌ Error occurred - checking details...');
      
    } else {
      console.log('❓ Unexpected result');
    }
    
  } catch (error) {
    console.error('🚨 Test error:', error.message);
  }
  
  console.log('\\n🏁 FINAL FIX TEST COMPLETE');
  console.log('Press Ctrl+C to close when ready...');
  
  await new Promise((resolve) => {
    process.on('SIGINT', resolve);
  });
  
  await browser.close();
})();