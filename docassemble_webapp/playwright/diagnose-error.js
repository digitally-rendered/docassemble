const { chromium } = require('playwright');

/**
 * Error Diagnostic Test
 * 
 * This test captures the exact error message when clicking "Yes, they have a lawyer"
 * to understand what's causing the YAML to fail.
 */

(async () => {
  console.log('🔍 ERROR DIAGNOSTIC TEST');
  console.log('========================\n');
  
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForLoadState('networkidle');
    
    // Rapid navigation
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
    
    // Capture state before critical click
    const beforeContent = await page.content();
    console.log('📍 State before clicking "Yes":');
    console.log(`   URL: ${page.url()}`);
    
    const beforeHeading = await page.locator('h1, h2').first().textContent();
    console.log(`   Heading: "${beforeHeading}"`);
    
    // The critical click that causes the error
    console.log('🎯 Clicking "Yes, they have a lawyer"...');
    await page.click('button:has-text(\"Yes, they have a lawyer\")');
    await page.waitForTimeout(3000);
    
    // Capture full error details
    const afterContent = await page.content();
    const afterHeading = await page.locator('h1, h2').first().textContent();
    
    console.log('\\n📍 State after clicking "Yes":');
    console.log(`   URL: ${page.url()}`);
    console.log(`   Heading: "${afterHeading}"`);
    
    if (afterContent.includes('Error') || afterContent.includes('Exception')) {
      console.log('\\n🚨 ERROR DETAILS:');
      
      // Extract error message
      const errorSection = afterContent.match(/<div[^>]*class[^>]*error[^>]*>([\\s\\S]*?)<\/div>/gi);
      if (errorSection) {
        console.log('Error section found:', errorSection[0].replace(/<[^>]*>/g, '').trim());
      }
      
      // Look for Python traceback
      const tracebackMatch = afterContent.match(/Traceback[\\s\\S]*?(?=<\/|$)/);
      if (tracebackMatch) {
        console.log('Traceback:', tracebackMatch[0]);
      }
      
      // Look for line numbers
      const lineMatch = afterContent.match(/line \\d+/gi);
      if (lineMatch) {
        console.log('Line references:', lineMatch);
      }
      
      // Look for specific error messages
      const specificErrors = afterContent.match(/(NameError|AttributeError|TypeError|ValueError|SyntaxError|KeyError)[^<\\n]*/gi);
      if (specificErrors) {
        console.log('Specific errors:', specificErrors);
      }
      
      // Save full error content for analysis
      const fs = require('fs');
      fs.writeFileSync('./error-page.html', afterContent);
      console.log('\\n💾 Full error page saved to ./error-page.html');
      
    } else {
      console.log('\\n✅ No error detected');
      console.log(`Content preview: ${afterContent.substring(0, 200)}...`);
    }
    
  } catch (error) {
    console.error('🚨 Test error:', error.message);
  }
  
  console.log('\\n🏁 Diagnostic complete. Press Ctrl+C to close.');
  await new Promise(() => {}); // Keep open
  
})();