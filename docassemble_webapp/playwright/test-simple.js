const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    console.log('Step 1: Navigating to wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForSelector('#daMainQuestion', { timeout: 10000 });
    console.log('✓ Welcome page loaded');
    
    console.log('Step 2: Clicking Continue on welcome page...');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    console.log('✓ Moved to emergency question');
    
    console.log('Step 3: Selecting "No, this is not an emergency"...');
    await page.click('button[type="submit"]:has-text("No, this is not an emergency")');
    await page.waitForTimeout(2000);
    console.log('✓ Emergency question answered');
    
    console.log('Step 4: Handling MIP question...');
    const mipQuestion = await page.textContent('#daMainQuestion');
    console.log('MIP question:', mipQuestion);
    
    // Click "Yes, I have my certificate"
    await page.click('button[type="submit"]:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(2000);
    console.log('✓ MIP status selected');
    
    console.log('Step 5: Handling MIP information screen...');
    // Click Continue on MIP information screen
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    console.log('✓ MIP information acknowledged');
    
    console.log('Step 6: Selecting relationship status...');
    const relationshipQuestion = await page.textContent('#daMainQuestion');
    console.log('Relationship question:', relationshipQuestion);
    
    // Click "Common-law"
    await page.click('button[type="submit"]:has-text("Common-law")');
    await page.waitForTimeout(2000);
    console.log('✓ Relationship status selected');
    
    console.log('Step 7: Selecting orders sought...');
    const ordersQuestion = await page.textContent('#daMainQuestion');
    console.log('Orders question:', ordersQuestion);
    
    // Check "Child custody" checkbox by clicking the label
    await page.click('text=Child custody');
    console.log('✓ Custody checkbox checked');
    
    // Click Continue
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    console.log('Step 8: Checking if we reached recommendations...');
    const finalQuestion = await page.textContent('#daMainQuestion');
    console.log('Final screen:', finalQuestion);
    
    if (finalQuestion.includes('Personalized Forms Package') || finalQuestion.includes('Financial')) {
      console.log('✅ SUCCESS: Reached recommendations or financial questions!');
    } else {
      console.log('⚠️  Unexpected screen:', finalQuestion);
    }
    
  } catch (error) {
    console.error('❌ ERROR:', error.message);
    
    // Try to get current question for debugging
    try {
      const currentQuestion = await page.textContent('#daMainQuestion');
      console.log('Current question when error occurred:', currentQuestion);
    } catch (e) {
      console.log('Could not get current question');
    }
  }
  
  await browser.close();
})();