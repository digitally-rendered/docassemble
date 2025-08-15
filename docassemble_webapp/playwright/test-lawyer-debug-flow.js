const { chromium } = require('playwright');

(async () => {
  console.log('DEBUGGING LAWYER FLOW');
  console.log('=====================\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Navigate to wizard
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Navigate through initial screens
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
    
    // Select child custody
    await page.check('text=Child custody');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Skip financial if present
    if ((await page.content()).includes('financial situation')) {
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(500);
    }
    
    // Select applicant
    console.log('1. At role selection...');
    await page.click('button:has-text("I am starting a new case")');
    await page.waitForTimeout(1000);
    
    // Fill user info minimally
    console.log('2. At user information...');
    const allInputs = await page.locator('input').all();
    console.log(`   Found ${allInputs.length} input fields`);
    
    // Just fill the absolutely required fields
    for (let i = 0; i < allInputs.length && i < 10; i++) {
      const input = allInputs[i];
      const type = await input.getAttribute('type');
      const required = await input.getAttribute('required');
      
      if (required !== null) {
        if (type === 'text') {
          if (i === 0) await input.fill('Test');
          else if (i === 2) await input.fill('User');
          else await input.fill('TestData');
        } else if (type === 'date') {
          await input.fill('1990-01-01');
        } else if (type === 'tel') {
          await input.fill('4165550100');
        }
      }
    }
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Check what screen we're on
    let content = await page.content();
    let heading = await page.locator('h1, h2').first().textContent();
    console.log(`3. After user info, screen shows: "${heading}"`);
    
    // Fill other party info minimally
    if (content.includes('Other Party')) {
      console.log('4. At other party information...');
      const inputs = await page.locator('input[type="text"]').all();
      if (inputs.length >= 2) {
        await inputs[0].fill('Other');
        await inputs[1].fill('Party');
      }
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
    }
    
    // Check what screen we're on now
    content = await page.content();
    heading = await page.locator('h1, h2').first().textContent();
    console.log(`5. After other party, screen shows: "${heading}"`);
    
    // Handle user lawyer question
    if (content.includes('Do you have a lawyer?')) {
      console.log('6. User lawyer question appeared');
      await page.click('button:has-text("No, I am self-represented")');
      await page.waitForTimeout(1000);
      
      // Check what comes next
      content = await page.content();
      heading = await page.locator('h1, h2').first().textContent();
      console.log(`7. After user lawyer, screen shows: "${heading}"`);
      
      // Look for other party lawyer question
      if (content.includes('Does the other party have a lawyer?')) {
        console.log('8. ✅ OTHER PARTY LAWYER QUESTION FOUND!');
        
        // Get all buttons
        const buttons = await page.locator('button').allTextContents();
        console.log('   Available buttons:', buttons);
        
        console.log('9. Clicking "Yes, they have a lawyer"...');
        await page.click('button:has-text("Yes, they have a lawyer")');
        await page.waitForTimeout(2000);
        
        // Final check
        content = await page.content();
        heading = await page.locator('h1, h2').first().textContent();
        console.log(`10. After clicking Yes, screen shows: "${heading}"`);
        
        if (content.includes('Lawyer') && content.includes('Information')) {
          console.log('🎉 SUCCESS! Lawyer form is displayed!');
        } else if (content.includes('Court')) {
          console.log('⚠️ Skipped to Court Information');
        } else if (content.includes('Error')) {
          console.log('❌ Error occurred');
        }
        
      } else if (content.includes('Court Information')) {
        console.log('⚠️ SKIPPED OTHER PARTY LAWYER - went to Court');
      }
      
    } else if (content.includes('Court Information')) {
      console.log('⚠️ SKIPPED BOTH LAWYER QUESTIONS - went to Court');
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
  }
  
  await browser.close();
  console.log('\n=====================');
  console.log('Debug flow complete');
})();