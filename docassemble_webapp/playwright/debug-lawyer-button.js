const { chromium } = require('playwright');

(async () => {
  console.log('DEBUG LAWYER BUTTON ISSUE');
  console.log('==========================\n');
  
  const browser = await chromium.launch({ headless: false }); // Visual debugging
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    // Check if it loads properly
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check for immediate errors
    const errorCount = await page.locator('h1:has-text("Error")').count();
    if (errorCount > 0) {
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('❌ IMMEDIATE ERROR:', errorMsg);
      await browser.close();
      return;
    }
    
    console.log('✅ Wizard loaded, navigating manually...');
    
    // Navigate step by step with visual confirmation
    console.log('Step 1: Welcome screen - look for Continue button');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'debug-step1.png' });
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    console.log('Step 2: Emergency question');
    await page.screenshot({ path: 'debug-step2.png' });
    
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(2000);
    
    console.log('Step 3: MIP question');
    await page.screenshot({ path: 'debug-step3.png' });
    
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    console.log('Step 4: Relationship status');
    await page.screenshot({ path: 'debug-step4.png' });
    
    // Use never lived together for shortest path
    await page.click('button:has-text("Never lived together")');
    await page.waitForTimeout(2000);
    
    console.log('Step 5: Never together orders');
    await page.screenshot({ path: 'debug-step5.png' });
    
    await page.click('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    console.log('Step 6: Should be at role selection');
    await page.screenshot({ path: 'debug-step6.png' });
    
    const roleContent = await page.content();
    if (roleContent.includes('Your Role in the Legal Proceeding')) {
      console.log('✅ At role selection');
      
      await page.click('button:has-text("I am starting a new case (Applicant)")');
      await page.waitForTimeout(2000);
      
      console.log('Step 7: User information - checking field names');
      await page.screenshot({ path: 'debug-step7.png' });
      
      // Check what input fields exist
      const inputs = await page.locator('input').all();
      console.log('Available input fields:');
      for (let i = 0; i < inputs.length; i++) {
        const name = await inputs[i].getAttribute('name');
        if (name) console.log(`  - ${name}`);
      }
      
      console.log('\nThis will help us see the actual field names.');
      console.log('Screenshots saved as debug-step1.png through debug-step7.png');
      console.log('Press Ctrl+C to close when done examining');
      
      // Keep browser open for inspection
      await new Promise(() => {});
      
    } else {
      console.log('❌ Not at role selection. Current page contains:');
      console.log(['role', 'Role', 'applicant', 'Applicant', 'party', 'Party'].filter(k => roleContent.includes(k)));
    }
    
  } catch (error) {
    console.error('Error during debug:', error.message);
  }
  
  await browser.close();
})();