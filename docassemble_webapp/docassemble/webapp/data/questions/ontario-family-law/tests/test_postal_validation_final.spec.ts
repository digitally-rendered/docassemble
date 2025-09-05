import { test, expect } from '@playwright/test';

test('Test postal code validation thoroughly', async ({ page }) => {
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
  console.log('On contact info page\n');
  
  // Fill all required fields properly
  const contactInputs = page.locator('input[type="text"]:visible');
  
  // Log what we're filling
  console.log('Filling contact form:');
  console.log('  Field 0 (Street): 123 Main Street');
  await contactInputs.nth(0).fill('123 Main Street');
  
  console.log('  Field 1 (Unit): Skipping');
  
  console.log('  Field 2 (City): Toronto');
  await contactInputs.nth(2).fill('Toronto');
  
  console.log('  Field 3 (Postal): Testing various values...');
  console.log('  Field 4 (Phone): 4165551234');
  await contactInputs.nth(4).fill('4165551234');
  
  // Test 1: Invalid format "INVALID"
  console.log('\nTest 1: Entering "INVALID" in postal code field');
  await contactInputs.nth(3).clear();
  await contactInputs.nth(3).fill('INVALID');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Wait and check if we moved forward or stayed
  await page.waitForTimeout(1000);
  let currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('Contact')) {
    console.log('  ✅ Stayed on contact page (validation worked)');
    
    // Look for any error messages
    const errorElements = await page.locator('.da-has-error, .text-danger, [role="alert"], .da-field-error').allTextContents();
    if (errorElements.length > 0) {
      console.log('  Error messages found:', errorElements.filter(e => e.trim()));
    }
  } else {
    console.log('  ❌ Moved to next page (validation failed - accepted invalid code)');
    console.log('  Current page:', currentPage?.substring(0, 50));
    // Go back to test more
    await page.goBack();
    await page.waitForTimeout(500);
  }
  
  // Test 2: US ZIP code
  console.log('\nTest 2: Entering US ZIP "12345"');
  await contactInputs.nth(3).clear();
  await contactInputs.nth(3).fill('12345');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  await page.waitForTimeout(1000);
  currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('Contact')) {
    console.log('  ✅ Stayed on contact page (validation worked)');
  } else {
    console.log('  ❌ Moved to next page (accepted US ZIP)');
    await page.goBack();
    await page.waitForTimeout(500);
  }
  
  // Test 3: Valid Canadian postal code without space
  console.log('\nTest 3: Entering valid "M5H2N2" (no space)');
  await contactInputs.nth(3).clear();
  await contactInputs.nth(3).fill('M5H2N2');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  await page.waitForTimeout(1500);
  currentPage = await page.locator('#daMainQuestion').textContent();
  if (currentPage?.includes('lawyer')) {
    console.log('  ✅ Moved to lawyer question (valid code accepted!)');
    
    // Continue to summary to check formatting
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    
    // Other party
    const partyInputs = page.locator('input[type="text"]:visible');
    await partyInputs.nth(0).fill('Other');
    await partyInputs.nth(2).fill('Party');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Skip other party contact
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // No lawyer for other party
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Court - no existing file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Check summary
    await page.waitForTimeout(500);
    const summaryText = await page.locator('body').textContent();
    if (summaryText?.includes('M5H 2N2')) {
      console.log('  ✅ Postal code formatted with space in summary: M5H 2N2');
    } else if (summaryText?.includes('M5H2N2')) {
      console.log('  ⚠️ Postal code not formatted in summary: M5H2N2');
    } else {
      console.log('  ❓ Could not find postal code in summary');
    }
  } else if (currentPage?.includes('Contact')) {
    console.log('  ❌ Valid code was rejected (still on contact page)');
    
    // Check for error messages
    const errors = await page.locator('.da-has-error, .text-danger').allTextContents();
    console.log('  Error messages:', errors.filter(e => e.trim()));
  } else {
    console.log('  ❓ Unexpected page:', currentPage?.substring(0, 50));
  }
  
  console.log('\n✅ Postal code validation test complete');
});