const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('Navigating to wizard...');
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
  
  console.log('Waiting for Welcome page...');
  await page.waitForSelector('#daMainQuestion', { timeout: 10000 });
  
  const welcomeText = await page.textContent('#daMainQuestion');
  console.log('Welcome text:', welcomeText);
  
  console.log('Looking for Continue button...');
  const continueButton = await page.$('button[type="submit"]#da-continue-button');
  if (continueButton) {
    console.log('Found continue button, clicking...');
    await continueButton.click();
    
    console.log('Waiting for next page...');
    await page.waitForTimeout(3000);
    
    const nextQuestion = await page.textContent('#daMainQuestion');
    console.log('Next question:', nextQuestion);
    
    // Check what buttons are available
    const buttons = await page.$$eval('button[type="submit"]', buttons => 
      buttons.map(b => ({ text: b.textContent, value: b.value, name: b.name }))
    );
    console.log('Available buttons:', buttons);
  } else {
    console.log('Continue button not found');
  }
  
  await page.waitForTimeout(60000); // Keep browser open for 1 minute
  await browser.close();
})();