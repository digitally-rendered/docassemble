const { chromium } = require('playwright');

(async () => {
  console.log('TESTING BOTH LAWYER BUTTONS');
  console.log('=============================\n');
  
  const browser = await chromium.launch({ headless: false }); // Visual to see what's happening
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(2000);
    
    console.log('1. Quick navigation to party info...');
    
    // Quick navigation
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
    
    console.log('2. Filling user party info...');
    
    // Fill user form (using encoded names)
    await page.fill('input[name="dXNlcl9wYXJ0eS5uYW1lLmZpcnN0"]', 'John');
    await page.fill('input[name="dXNlcl9wYXJ0eS5uYW1lLmxhc3Q"]', 'Smith');
    await page.fill('input[name="dXNlcl9wYXJ0eS5iaXJ0aGRhdGU"]', '1980-01-01');
    await page.fill('input[name="dXNlcl9wYXJ0eS5waG9uZV9udW1iZXI"]', '4165551234');
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLmFkZHJlc3M"]', '123 Test St');
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLmNpdHk"]', 'Toronto');
    await page.fill('input[name="dXNlcl9wYXJ0eS5hZGRyZXNzLnBvc3RhbF9jb2Rl"]', 'M5H 2N2');
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    console.log('3. Filling other party info...');
    
    // Fill other party (try to find any name fields)
    const otherFirstInput = await page.locator('input').first();
    const firstName = await otherFirstInput.getAttribute('name');
    console.log('First input field name:', firstName);
    
    // Fill minimal other party info
    await page.fill('input[name*="name"][name*="first"], input[name*="first_name"]', 'Jane');
    await page.fill('input[name*="name"][name*="last"], input[name*="last_name"]', 'Doe');
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
    
    console.log('4. Testing FIRST lawyer question (user)...');
    
    let content = await page.content();
    if (content.includes('Do you have a lawyer?')) {
      console.log('✅ First lawyer question found');
      
      // Test saying NO first to skip user lawyer form
      await page.click('button:has-text("No, I am self-represented")');
      await page.waitForTimeout(1500);
      
      console.log('5. Testing SECOND lawyer question (other party)...');
      
      content = await page.content();
      if (content.includes('Does the other party have a lawyer?')) {
        console.log('✅ Second lawyer question found');
        
        // Show available buttons
        const buttons = await page.locator('button').allTextContents();
        console.log('Available buttons:', buttons.filter(b => b.trim()));
        
        // THE CRITICAL TEST - Click "Yes, they have a lawyer"
        console.log('🔥 CLICKING "Yes, they have a lawyer"...');
        
        await page.click('button:has-text("Yes, they have a lawyer")');
        await page.waitForTimeout(3000);
        
        // Check result
        content = await page.content();
        if (content.includes('Error')) {
          const errorMsg = await page.locator('blockquote').textContent();
          console.log('❌ OTHER PARTY LAWYER BUTTON ERROR:', errorMsg);
        } else if (content.includes('Other Party\'s Lawyer Information')) {
          console.log('🎉 SUCCESS! Other party lawyer form reached!');
        } else {
          console.log('❓ Unexpected result. Content contains:');
          console.log(['lawyer', 'Lawyer', 'information', 'form', 'court'].filter(k => content.includes(k)));
        }
        
      } else {
        console.log('❌ Second lawyer question not found');
      }
      
    } else {
      console.log('❌ First lawyer question not found');
    }
    
    console.log('\nPress Ctrl+C when done examining');
    await new Promise(() => {}); // Keep open for inspection
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  await browser.close();
})();