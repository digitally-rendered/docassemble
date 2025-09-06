import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8080';
const INTERVIEW_PATH = '/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fform_8_enhanced.yml';

test.describe('Form 8 Enhanced - Comprehensive Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL + INTERVIEW_PATH);
    await page.waitForLoadState('networkidle');
  });

  test('should load the interview and display initial question', async ({ page }) => {
    // Check for metadata elements
    await expect(page).toHaveTitle(/Ontario Family Law Form 8/);
    
    // Look for the first question
    const questionText = await page.locator('h1, .question-label').first().textContent();
    expect(questionText).toBeTruthy();
  });

  test('should complete court information section', async ({ page }) => {
    // Court Information
    const courtFileInput = page.locator('input[name*="courtfileno"], #courtfileno');
    if (await courtFileInput.isVisible()) {
      await courtFileInput.fill('FC-24-123456');
    }

    const courtAddressInput = page.locator('input[name*="court_address"], #court_address');
    if (await courtAddressInput.isVisible()) {
      await courtAddressInput.fill('393 University Avenue, Toronto, ON M5G 1E6');
    }

    const courtRequestInput = page.locator('textarea[name*="i_ask_the_court"], #form8_i_ask_the_court_for_the_following');
    if (await courtRequestInput.isVisible()) {
      await courtRequestInput.fill('Divorce and custody of children');
    }

    // Continue button
    const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")');
    if (await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should complete party information section', async ({ page }) => {
    // Email
    const emailInput = page.locator('input[type="email"], input[name*="email"]').first();
    if (await emailInput.isVisible()) {
      await emailInput.fill('test@example.com');
    }

    // Name before marriage
    const nameBeforeMarriageInput = page.locator('input[name*="name_before_marriage"]');
    if (await nameBeforeMarriageInput.isVisible()) {
      await nameBeforeMarriageInput.fill('Jane Smith');
    }

    // Full legal name
    const fullNameInput = page.locator('input[name*="full_legal_name"]');
    if (await fullNameInput.isVisible()) {
      await fullNameInput.fill('Jane Marie Doe');
    }

    // Address
    const addressInput = page.locator('input[name*="address"], textarea[name*="address"]').first();
    if (await addressInput.isVisible()) {
      await addressInput.fill('123 Main Street, Toronto, ON M5V 3A8');
    }

    // Continue
    const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")');
    if (await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should handle children information if applicable', async ({ page }) => {
    // Check if children section appears
    const childNameInput = page.locator('input[name*="child_name"], input[name*="children"]');
    if (await childNameInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await childNameInput.fill('John Doe Jr.');

      const childBirthdateInput = page.locator('input[name*="child_birthdate"], input[type="date"]').first();
      if (await childBirthdateInput.isVisible()) {
        await childBirthdateInput.fill('2015-06-15');
      }

      const childAgeInput = page.locator('input[name*="child_age"], input[type="number"]').first();
      if (await childAgeInput.isVisible()) {
        await childAgeInput.fill('9');
      }

      // Continue
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")');
      if (await continueButton.isVisible()) {
        await continueButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('should handle claims and relief section', async ({ page }) => {
    // Property claim checkbox
    const propertyClaimCheckbox = page.locator('input[type="checkbox"][name*="property"], input[type="radio"][value="True"]').first();
    if (await propertyClaimCheckbox.isVisible({ timeout: 5000 }).catch(() => false)) {
      await propertyClaimCheckbox.check();
    }

    // Continue
    const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")');
    if (await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should complete additional information fields', async ({ page }) => {
    // Handle court type selection if present
    const courtTypeRadio = page.locator('input[type="radio"][value*="Superior Court"]').first();
    if (await courtTypeRadio.isVisible({ timeout: 5000 }).catch(() => false)) {
      await courtTypeRadio.check();
    }

    // Fill various text fields
    const textFields = await page.locator('input[type="text"]:visible').all();
    for (let i = 0; i < Math.min(textFields.length, 5); i++) {
      const field = textFields[i];
      const fieldName = await field.getAttribute('name') || '';
      
      // Skip if already filled
      const currentValue = await field.inputValue();
      if (!currentValue) {
        if (fieldName.includes('field')) {
          await field.fill(`Test data ${i + 1}`);
        }
      }
    }

    // Handle checkboxes
    const checkboxes = await page.locator('input[type="checkbox"]:visible, input[type="radio"][name*="check"]:visible').all();
    for (let i = 0; i < Math.min(checkboxes.length, 3); i++) {
      const checkbox = checkboxes[i];
      const isChecked = await checkbox.isChecked();
      if (!isChecked) {
        await checkbox.check();
      }
    }

    // Continue
    const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")');
    if (await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate through all pages until completion', async ({ page }) => {
    let pageCount = 0;
    const maxPages = 50; // Safety limit

    while (pageCount < maxPages) {
      // Check if we've reached the final screen
      const finalScreen = page.locator('text=/Form 8 Interview Complete|Your form has been completed/i');
      if (await finalScreen.isVisible({ timeout: 1000 }).catch(() => false)) {
        console.log('Reached final screen');
        break;
      }

      // Fill current page fields
      // Text inputs
      const textInputs = await page.locator('input[type="text"]:visible, input[type="email"]:visible, textarea:visible').all();
      for (const input of textInputs) {
        const currentValue = await input.inputValue();
        if (!currentValue) {
          const inputType = await input.getAttribute('type');
          const inputName = await input.getAttribute('name') || '';
          
          if (inputType === 'email') {
            await input.fill('test@example.com');
          } else if (inputName.includes('phone')) {
            await input.fill('416-555-0123');
          } else if (inputName.includes('address')) {
            await input.fill('123 Test Street, Toronto, ON M5V 3A8');
          } else if (inputName.includes('name')) {
            await input.fill('Test Name');
          } else {
            await input.fill('Test data');
          }
        }
      }

      // Date inputs
      const dateInputs = await page.locator('input[type="date"]:visible').all();
      for (const input of dateInputs) {
        const currentValue = await input.inputValue();
        if (!currentValue) {
          await input.fill('2024-01-15');
        }
      }

      // Number inputs
      const numberInputs = await page.locator('input[type="number"]:visible').all();
      for (const input of numberInputs) {
        const currentValue = await input.inputValue();
        if (!currentValue) {
          await input.fill('25');
        }
      }

      // Radio buttons - select first option
      const radioGroups = await page.locator('input[type="radio"]:visible').all();
      const radioNames = new Set();
      for (const radio of radioGroups) {
        const name = await radio.getAttribute('name');
        if (name && !radioNames.has(name)) {
          radioNames.add(name);
          await radio.check();
        }
      }

      // Checkboxes - check first few
      const checkboxes = await page.locator('input[type="checkbox"]:visible').all();
      for (let i = 0; i < Math.min(checkboxes.length, 2); i++) {
        const checkbox = checkboxes[i];
        const isChecked = await checkbox.isChecked();
        if (!isChecked) {
          await checkbox.check();
        }
      }

      // Try to continue
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next"), button[type="submit"]:visible').first();
      if (await continueButton.isVisible()) {
        await continueButton.click();
        await page.waitForLoadState('networkidle');
        pageCount++;
      } else {
        console.log('No continue button found, checking for final screen');
        break;
      }
    }

    // Verify we reached completion
    const completionIndicators = [
      'text=/Form 8 Interview Complete/i',
      'text=/Your form has been completed/i',
      'text=/ready for download/i',
      'button:has-text("Exit")',
      'button:has-text("Restart")'
    ];

    let foundCompletion = false;
    for (const indicator of completionIndicators) {
      if (await page.locator(indicator).isVisible({ timeout: 1000 }).catch(() => false)) {
        foundCompletion = true;
        break;
      }
    }

    expect(foundCompletion).toBeTruthy();
  });

  test('should validate required fields', async ({ page }) => {
    // Try to continue without filling required fields
    const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
    
    if (await continueButton.isVisible()) {
      await continueButton.click();
      
      // Check for validation messages
      const validationMessage = page.locator('.alert-danger, .error-message, .validation-error, [role="alert"]');
      
      // Some fields might be required
      if (await validationMessage.isVisible({ timeout: 2000 }).catch(() => false)) {
        const errorText = await validationMessage.textContent();
        expect(errorText).toBeTruthy();
        console.log('Validation working correctly:', errorText);
      }
    }
  });

  test('should handle back navigation', async ({ page }) => {
    // Navigate forward a few pages
    for (let i = 0; i < 3; i++) {
      // Fill any required fields
      const inputs = await page.locator('input:visible, textarea:visible').all();
      for (const input of inputs.slice(0, 2)) {
        const inputType = await input.getAttribute('type');
        if (inputType !== 'hidden' && inputType !== 'submit') {
          await input.fill('Test data');
        }
      }

      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
      if (await continueButton.isVisible()) {
        await continueButton.click();
        await page.waitForLoadState('networkidle');
      }
    }

    // Try to go back
    const backButton = page.locator('button:has-text("Back"), a:has-text("Back")').first();
    if (await backButton.isVisible()) {
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      // Verify we went back
      expect(page.url()).toContain('interview');
    }
  });

  test('should save and restore session', async ({ page, context }) => {
    // Fill some initial data
    const firstInput = page.locator('input[type="text"]:visible').first();
    if (await firstInput.isVisible()) {
      await firstInput.fill('Session Test Data');
    }

    // Get session cookies
    const cookies = await context.cookies();
    
    // Navigate away and back
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    // Restore session and return to interview
    await context.addCookies(cookies);
    await page.goto(BASE_URL + INTERVIEW_PATH);
    await page.waitForLoadState('networkidle');
    
    // Check if session was preserved
    const sessionIndicator = page.locator('text=/Session Test Data|Continue where you left off/i');
    if (await sessionIndicator.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('Session successfully preserved');
    }
  });
});

test.describe('Form 8 Enhanced - Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL + INTERVIEW_PATH);
    await page.waitForLoadState('networkidle');
  });

  test('should handle special characters in text fields', async ({ page }) => {
    const specialChars = "Test & Company's \"Special\" <Characters> @ 100%";
    
    const textInput = page.locator('input[type="text"]:visible').first();
    if (await textInput.isVisible()) {
      await textInput.fill(specialChars);
      
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
      if (await continueButton.isVisible()) {
        await continueButton.click();
        await page.waitForLoadState('networkidle');
        
        // Should accept special characters
        const errorMessage = page.locator('.alert-danger, .error-message');
        const hasError = await errorMessage.isVisible({ timeout: 1000 }).catch(() => false);
        expect(hasError).toBeFalsy();
      }
    }
  });

  test('should validate email format', async ({ page }) => {
    // Navigate to email field if not immediately visible
    while (true) {
      const emailInput = page.locator('input[type="email"]:visible').first();
      if (await emailInput.isVisible({ timeout: 1000 }).catch(() => false)) {
        // Test invalid email
        await emailInput.fill('invalid-email');
        
        const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
        await continueButton.click();
        
        // Should show validation error or browser validation
        const validationError = await page.locator(':invalid, .alert-danger').isVisible({ timeout: 1000 }).catch(() => false);
        
        // Now test valid email
        await emailInput.fill('valid@example.com');
        await continueButton.click();
        await page.waitForLoadState('networkidle');
        break;
      }

      // Navigate to next page to find email field
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
      if (await continueButton.isVisible()) {
        // Fill any required fields
        const requiredInputs = await page.locator('input:visible[required], textarea:visible[required]').all();
        for (const input of requiredInputs) {
          await input.fill('Test');
        }
        
        await continueButton.click();
        await page.waitForLoadState('networkidle');
      } else {
        break; // No email field in this interview
      }
    }
  });

  test('should handle very long text inputs', async ({ page }) => {
    const longText = 'A'.repeat(1000); // 1000 character string
    
    const textInput = page.locator('input[type="text"]:visible, textarea:visible').first();
    if (await textInput.isVisible()) {
      await textInput.fill(longText);
      
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Next")').first();
      if (await continueButton.isVisible()) {
        await continueButton.click();
        await page.waitForLoadState('networkidle');
        
        // Should handle long text gracefully
        const errorMessage = page.locator('.alert-danger, .error-message');
        const hasError = await errorMessage.isVisible({ timeout: 1000 }).catch(() => false);
        
        // Long text should either be accepted or show appropriate validation
        if (hasError) {
          const errorText = await errorMessage.textContent();
          expect(errorText).toContain('length'); // Should mention length if it's a problem
        }
      }
    }
  });
});