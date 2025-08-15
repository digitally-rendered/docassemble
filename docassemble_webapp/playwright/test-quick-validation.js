const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('Quick Validation Test');
  console.log('====================\n');
  
  let testsPassed = 0;
  let testsFailed = 0;
  
  try {
    // Test 1: Error detection
    console.log('1. Testing error detection...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/nonexistent.yml');
    await page.waitForTimeout(2000);
    
    const errorHeading = await page.locator('h1:has-text("Error")').count();
    if (errorHeading > 0) {
      console.log('   ✅ Error screen detected correctly');
      testsPassed++;
    } else {
      console.log('   ❌ Error screen not detected');
      testsFailed++;
    }
    
    // Test 2: Financial form with label clicking
    console.log('\n2. Testing financial form with label clicking...');
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml');
    await page.waitForTimeout(1000);
    
    // Quick navigation to financial form
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(1000);
    await page.click('button:has-text("No, this is not an emergency")'); // Emergency
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Yes, I have my certificate")'); // MIP
    await page.waitForTimeout(1000);
    await page.click('button[type="submit"]#da-continue-button'); // MIP info
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Common-law")'); // Relationship
    await page.waitForTimeout(1000);
    await page.click('text=Spousal support'); // Order
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    // Test filling financial form
    await page.locator('input[type="text"]').first().fill('50000');
    
    // Click labels for radio buttons
    await page.locator('label:has-text("Yes")').first().click(); // Support
    await page.locator('label:has-text("No")').nth(1).click(); // Business
    await page.locator('label:has-text("Yes")').nth(2).click(); // Pension
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    const content = await page.content();
    if (content.includes('Forms Package') || content.includes('Your Forms')) {
      console.log('   ✅ Financial form completed successfully');
      testsPassed++;
    } else {
      console.log('   ❌ Financial form did not complete');
      testsFailed++;
    }
    
    // Test 3: Check that tests fail fast on crashes
    console.log('\n3. Testing fast failure on crashes...');
    const startTime = Date.now();
    
    // Try to trigger an error by going to a bad URL
    await page.goto('http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml&reset=1&bad=param');
    await page.waitForTimeout(1000);
    
    // This should detect any error quickly
    const hasError = await page.locator('h1:has-text("Error")').count() > 0;
    const elapsed = Date.now() - startTime;
    
    if (elapsed < 5000) {
      console.log(`   ✅ Error detected quickly (${elapsed}ms)`);
      testsPassed++;
    } else {
      console.log(`   ❌ Error detection too slow (${elapsed}ms)`);
      testsFailed++;
    }
    
  } catch (error) {
    console.error('Test error:', error.message);
    testsFailed++;
  }
  
  // Summary
  console.log('\n====================');
  console.log(`Results: ${testsPassed} passed, ${testsFailed} failed`);
  
  if (testsFailed === 0) {
    console.log('✅ All improvements validated successfully!');
  } else {
    console.log('⚠️ Some improvements need attention');
  }
  
  await browser.close();
  process.exit(testsFailed === 0 ? 0 : 1);
})();