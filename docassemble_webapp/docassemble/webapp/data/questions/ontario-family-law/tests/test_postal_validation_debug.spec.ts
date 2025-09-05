import { test, expect } from '@playwright/test';

test('Debug postal code validation', async ({ page }) => {
  // Navigate to the interview
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_final.yml');
  await page.waitForLoadState('networkidle');
  
  // Quick navigation to contact info page
  await page.getByRole('button', { name: /Continue/i }).click(); // Introduction
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click(); // Emergency
  await page.getByRole('button', { name: /Yes, I have my certificate/i }).click(); // MIP
  await page.getByRole('button', { name: /Married/i }).first().click(); // Relationship
  await page.getByRole('button', { name: /Continue/i }).click(); // Skip orders
  
  // Personal info
  const textInputs = page.locator('input[type="text"]:visible');
  await textInputs.nth(0).fill('Test');
  await textInputs.nth(2).fill('User');
  const dateInput = page.locator('input[type="date"]');
  await dateInput.fill('1990-01-01');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Now on contact info page
  await expect(page.locator('#daMainQuestion')).toContainText('Your Contact Information');
  console.log('✅ On contact info page');
  
  // Fill required fields except postal code
  const contactInputs = page.locator('input[type="text"]:visible');
  await contactInputs.nth(0).fill('123 Main Street'); // Street
  await contactInputs.nth(2).fill('Toronto'); // City
  await contactInputs.nth(5).fill('4165551234'); // Phone
  
  // Test various invalid postal codes
  const postalCodeField = contactInputs.nth(4);
  
  console.log('\nTesting postal code validation:');
  
  // Test 1: Empty postal code (should be required)
  console.log('1. Testing empty postal code...');
  await postalCodeField.clear();
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForTimeout(500);
  
  let currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('Contact')) {
    console.log('   ❌ Empty postal code blocked (still on contact page)');
    // Look for error message
    const errors = await page.locator('.da-has-error, .text-danger, [role="alert"]').allTextContents();
    console.log('   Error messages:', errors);
  } else {
    console.log('   ⚠️ Empty postal code allowed (moved to next page)');
  }
  
  // Test 2: Invalid format "INVALID"
  console.log('2. Testing "INVALID"...');
  await postalCodeField.clear();
  await postalCodeField.fill('INVALID');
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForTimeout(500);
  
  currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('Contact')) {
    console.log('   ❌ "INVALID" blocked (still on contact page)');
    const errors = await page.locator('.da-has-error, .text-danger, [role="alert"]').allTextContents();
    console.log('   Error messages:', errors);
  } else {
    console.log('   ⚠️ "INVALID" allowed (moved to next page)');
  }
  
  // Test 3: US ZIP code
  console.log('3. Testing US ZIP "12345"...');
  await postalCodeField.clear();
  await postalCodeField.fill('12345');
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForTimeout(500);
  
  currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('Contact')) {
    console.log('   ❌ US ZIP blocked (still on contact page)');
    const errors = await page.locator('.da-has-error, .text-danger, [role="alert"]').allTextContents();
    console.log('   Error messages:', errors);
  } else {
    console.log('   ⚠️ US ZIP allowed (moved to next page)');
  }
  
  // Test 4: Invalid Canadian format
  console.log('4. Testing invalid Canadian "A1A1A"...');
  await postalCodeField.clear();
  await postalCodeField.fill('A1A1A');
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForTimeout(500);
  
  currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('Contact')) {
    console.log('   ❌ Invalid format blocked (still on contact page)');
    const errors = await page.locator('.da-has-error, .text-danger, [role="alert"]').allTextContents();
    console.log('   Error messages:', errors);
  } else {
    console.log('   ⚠️ Invalid format allowed (moved to next page)');
  }
  
  // Test 5: Valid without space
  console.log('5. Testing valid "M5H2N2" (no space)...');
  await postalCodeField.clear();
  await postalCodeField.fill('M5H2N2');
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForTimeout(1000);
  
  currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('lawyer')) {
    console.log('   ✅ Valid postal code accepted (moved to lawyer question)');
    
    // Go to summary to check formatting
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    
    // Other party info
    await page.locator('input[type="text"]:visible').nth(0).fill('Other');
    await page.locator('input[type="text"]:visible').nth(2).fill('Party');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    
    // Court
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should be at summary
    const summaryText = await page.locator('body').textContent();
    if (summaryText?.includes('M5H 2N2')) {
      console.log('   ✅ Postal code formatted with space: M5H 2N2');
    } else if (summaryText?.includes('M5H2N2')) {
      console.log('   ⚠️ Postal code not formatted: M5H2N2');
    }
  } else {
    console.log('   ❌ Valid postal code not accepted');
  }
  
  console.log('\n✅ Postal code validation testing complete');
});