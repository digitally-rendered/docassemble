const { chromium } = require('playwright');

(async () => {
  console.log('Debug Party Integration');
  console.log('=======================\n');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('1. Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    // Check for errors immediately
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    if (errorHeading > 0) {
      const errorMessage = await page.locator('blockquote').textContent();
      console.log('❌ Interview crashed at start:', errorMessage);
      
      // Try without the party info include
      console.log('\n2. Testing without party info include...');
      await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml&reset=1');
      await page.waitForTimeout(2000);
      
      const stillError = await page.locator('h1:has-text("Error")').count();
      if (stillError > 0) {
        console.log('❌ Error persists without party info');
      } else {
        console.log('✅ Works without party info - integration issue');
      }
      
      await browser.close();
      return;
    }
    
    console.log('✅ Interview loaded successfully');
    
    // Navigate through to party info section
    console.log('\n2. Navigating to party info section...');
    
    // Continue through introduction
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Handle emergency
    await page.click('button:has-text("No, this is not an emergency")');
    await page.waitForTimeout(1000);
    
    // Handle MIP
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.waitForTimeout(1000);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Select married
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(1000);
    
    // Select divorce only
    await page.click('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1000);
    
    // Uncontested
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(1000);
    
    // No children
    await page.click('button:has-text("No")');
    await page.waitForTimeout(2000);
    
    // Should now be at role determination
    const content = await page.content();
    
    console.log('\n3. Current page analysis:');
    console.log('- URL:', page.url());
    
    if (content.includes('Your Role in the Legal Proceeding')) {
      console.log('✅ Role determination screen reached');
    } else if (content.includes('Error')) {
      const errorMsg = await page.locator('blockquote').textContent();
      console.log('❌ Error occurred:', errorMsg);
    } else {
      console.log('❓ Current content keywords:');
      ['form', 'Form', 'role', 'Role', 'applicant', 'Applicant', 'party', 'Party'].forEach(keyword => {
        if (content.includes(keyword)) {
          console.log(`  - Contains "${keyword}"`);
        }
      });
      
      // Show available buttons
      const buttons = await page.locator('button').allTextContents();
      console.log('Available buttons:', buttons.filter(b => b.trim()));
    }
    
    await page.screenshot({ path: 'debug-party-current.png', fullPage: true });
    console.log('\nScreenshot saved as debug-party-current.png');
    
  } catch (error) {
    console.error('❌ Error during test:', error.message);
  }
  
  console.log('\nPress Ctrl+C to close browser');
  await new Promise(() => {}); // Keep open
  
})();