const { chromium } = require('playwright');

(async () => {
  console.log('Debug Wizard Flow');
  console.log('=================\n');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Loading wizard...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(3000);
    
    // Take screenshot and show content
    await page.screenshot({ path: 'debug-wizard-1.png', fullPage: true });
    
    console.log('Page title:', await page.title());
    
    const buttons = await page.locator('button').allTextContents();
    console.log('Available buttons:', buttons);
    
    const content = await page.content();
    console.log('Current page contains:');
    if (content.includes('emergency')) console.log('- emergency content');
    if (content.includes('Emergency')) console.log('- Emergency content');
    if (content.includes('Welcome')) console.log('- Welcome content');
    if (content.includes('Introduction')) console.log('- Introduction content');
    if (content.includes('Continue')) console.log('- Continue button');
    
    // Try clicking continue first
    try {
      await page.click('button[type="submit"]#da-continue-button');
      console.log('✅ Clicked continue button');
      await page.waitForTimeout(2000);
      
      const nextButtons = await page.locator('button').allTextContents();
      console.log('Next screen buttons:', nextButtons);
      
      await page.screenshot({ path: 'debug-wizard-2.png', fullPage: true });
      
    } catch (e) {
      console.log('❌ Could not click continue:', e.message);
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\nScreenshots saved as debug-wizard-1.png and debug-wizard-2.png');
  
  // Keep browser open for debugging
  console.log('Press Ctrl+C to close browser');
  await new Promise(() => {}); // Keep open
  
})();