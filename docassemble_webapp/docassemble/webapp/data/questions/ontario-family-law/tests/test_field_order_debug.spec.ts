import { test, expect } from '@playwright/test';

test('Debug contact form field order', async ({ page }) => {
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
  console.log('✅ On contact info page\n');
  
  // Get ALL inputs on the page (not just text)
  const allInputs = page.locator('input:visible');
  const inputCount = await allInputs.count();
  
  console.log(`Total visible inputs: ${inputCount}\n`);
  
  // Check each input
  for (let i = 0; i < inputCount; i++) {
    const input = allInputs.nth(i);
    const inputType = await input.getAttribute('type');
    const inputId = await input.getAttribute('id');
    const inputName = await input.getAttribute('name');
    const inputPlaceholder = await input.getAttribute('placeholder');
    
    // Try to find the label
    let label = '';
    try {
      // Try to find label by for attribute
      if (inputId) {
        const labelElement = page.locator(`label[for="${inputId}"]`);
        if (await labelElement.count() > 0) {
          label = await labelElement.textContent() || '';
        }
      }
      // Also check if there's a label wrapping the input
      if (!label) {
        const parentLabel = await input.locator('xpath=ancestor::label[1]').textContent().catch(() => '');
        if (parentLabel) label = parentLabel;
      }
    } catch (e) {}
    
    console.log(`Input ${i}:`);
    console.log(`  Type: ${inputType}`);
    console.log(`  ID: ${inputId || 'none'}`);
    console.log(`  Name: ${inputName || 'none'}`);
    console.log(`  Placeholder: ${inputPlaceholder || 'none'}`);
    console.log(`  Label: ${label.trim() || 'not found'}`);
    console.log('');
  }
  
  // Also check for select dropdowns
  const selects = page.locator('select:visible');
  const selectCount = await selects.count();
  
  if (selectCount > 0) {
    console.log(`\nFound ${selectCount} select dropdown(s):\n`);
    for (let i = 0; i < selectCount; i++) {
      const select = selects.nth(i);
      const selectId = await select.getAttribute('id');
      const selectName = await select.getAttribute('name');
      
      console.log(`Select ${i}:`);
      console.log(`  ID: ${selectId || 'none'}`);
      console.log(`  Name: ${selectName || 'none'}`);
      
      // Get selected value
      const selectedValue = await select.inputValue();
      console.log(`  Selected: ${selectedValue}`);
      console.log('');
    }
  }
  
  console.log('\n--- Now testing field entry ---\n');
  
  // Test entering values in text inputs only
  const textOnlyInputs = page.locator('input[type="text"]:visible');
  const textInputCount = await textOnlyInputs.count();
  
  console.log(`Found ${textInputCount} text inputs\n`);
  
  // Enter test values
  console.log('Entering test values:');
  await textOnlyInputs.nth(0).fill('123 Main Street');
  console.log('  Input 0 (text): 123 Main Street');
  
  if (textInputCount > 1) {
    await textOnlyInputs.nth(1).fill('Apt 5');
    console.log('  Input 1 (text): Apt 5');
  }
  
  if (textInputCount > 2) {
    await textOnlyInputs.nth(2).fill('Toronto');
    console.log('  Input 2 (text): Toronto');
  }
  
  if (textInputCount > 3) {
    await textOnlyInputs.nth(3).fill('M5H2N2');
    console.log('  Input 3 (text): M5H2N2 (hoping this is postal code)');
  }
  
  if (textInputCount > 4) {
    await textOnlyInputs.nth(4).fill('4165551234');
    console.log('  Input 4 (text): 4165551234 (hoping this is phone)');
  }
  
  if (textInputCount > 5) {
    await textOnlyInputs.nth(5).fill('Extra field value');
    console.log('  Input 5 (text): Extra field value');
  }
  
  // Take screenshot to see what was filled
  await page.screenshot({ path: 'contact-form-filled.png', fullPage: true });
  console.log('\nScreenshot saved as contact-form-filled.png');
});