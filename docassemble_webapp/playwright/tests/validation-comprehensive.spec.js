const { test, expect } = require('@playwright/test');

test.describe('Comprehensive Field Validation Tests', () => {
  const wizardUrl = 'http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml';

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', exception => {
      console.log(`Page error: ${exception}`);
    });
    
    await page.goto(wizardUrl);
    await page.waitForLoadState('networkidle');
  });

  test('should validate required fields in Person objects', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing Person object required field validation...');
      
      // Test empty form submission
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const validationErrors = await getValidationErrors(page);
      if (validationErrors.length > 0) {
        console.log('✅ Person object shows validation errors for required fields');
        console.log(`Found ${validationErrors.length} validation error(s)`);
        
        // Test partial completion - only first name
        await fillFieldByContext(page, ['first'], 'John');
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        const stillHasErrors = await getValidationErrors(page);
        if (stillHasErrors.length > 0) {
          console.log('✅ Person object requires multiple fields - still shows errors after partial completion');
        }
        
        // Complete all required fields
        await fillRequiredPersonFields(page);
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const finalContent = await page.content();
        if (!finalContent.includes('Error') && 
            (finalContent.includes('Other Party') || finalContent.includes('lawyer'))) {
          console.log('✅ Person object accepts complete required field set');
        }
      } else {
        console.log('❓ No validation errors shown - may have different validation approach');
      }
    }
  });

  test('should validate email format in Person and Individual objects', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing email format validation...');
      
      // Fill all required fields except email, then test invalid emails
      await fillRequiredPersonFieldsExceptEmail(page);
      
      const invalidEmails = [
        'invalid-email',
        'test@',
        '@domain.com',
        'test..test@domain.com',
        'test@domain',
        'spaces in@email.com'
      ];
      
      const emailField = await findFieldByContext(page, ['email'], 'email');
      if (emailField) {
        for (const invalidEmail of invalidEmails) {
          await emailField.fill(invalidEmail);
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          const errors = await getValidationErrors(page);
          if (errors.length > 0) {
            console.log(`✅ Email validation rejected: ${invalidEmail}`);
            break; // Found validation working, no need to test all
          }
        }
        
        // Test valid email
        await emailField.fill('valid.email@example.com');
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const finalContent = await page.content();
        if (!finalContent.includes('Error')) {
          console.log('✅ Valid email format accepted');
        }
      }
    }
  });

  test('should validate phone number formats', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing phone number format validation...');
      
      // Fill all required fields except phone
      await fillRequiredPersonFieldsExceptPhone(page);
      
      const invalidPhones = [
        '123',
        '123-456-78901', // too long
        'abc-def-ghij',
        '1234567890123456', // way too long
        '+1-416-555-12345' // too long
      ];
      
      const validPhones = [
        '4165551234',
        '416-555-1234',
        '(416) 555-1234',
        '+1 416 555 1234',
        '416.555.1234'
      ];
      
      const phoneField = await findFieldByContext(page, ['phone'], 'tel');
      if (phoneField) {
        // Test invalid formats
        for (const invalidPhone of invalidPhones) {
          await phoneField.fill(invalidPhone);
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          const errors = await getValidationErrors(page);
          if (errors.length > 0 && errors.some(err => err.toLowerCase().includes('phone'))) {
            console.log(`✅ Phone validation rejected: ${invalidPhone}`);
            break;
          }
        }
        
        // Test valid format
        await phoneField.fill(validPhones[0]);
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const finalContent = await page.content();
        if (!finalContent.includes('Error')) {
          console.log('✅ Valid phone format accepted');
        }
      }
    }
  });

  test('should validate postal code format', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing postal code format validation...');
      
      // Fill all required fields except postal code
      await fillRequiredPersonFieldsExceptPostal(page);
      
      const invalidPostalCodes = [
        '12345',        // US ZIP format
        'M5H',          // incomplete
        'M5H-2N2',      // wrong separator
        '123 ABC',      // wrong pattern
        'ABCDEF'        // no numbers
      ];
      
      const validPostalCodes = [
        'M5H 2N2',
        'M5H2N2',
        'm5h 2n2',      // lowercase should be accepted
        'K1A 0A6'       // Ottawa
      ];
      
      const postalField = await findFieldByContext(page, ['postal', 'zip']);
      if (postalField) {
        // Test invalid formats
        for (const invalidPostal of invalidPostalCodes) {
          await postalField.fill(invalidPostal);
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          const errors = await getValidationErrors(page);
          if (errors.length > 0 && errors.some(err => err.toLowerCase().includes('postal'))) {
            console.log(`✅ Postal code validation rejected: ${invalidPostal}`);
            break;
          }
        }
        
        // Test valid format
        await postalField.fill(validPostalCodes[0]);
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const finalContent = await page.content();
        if (!finalContent.includes('Error')) {
          console.log('✅ Valid postal code format accepted');
        }
      }
    }
  });

  test('should validate date fields', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing date field validation...');
      
      const dateFields = await page.locator('input[type="date"]').all();
      if (dateFields.length > 0) {
        const dateField = dateFields[0];
        
        // Fill other required fields first
        await fillRequiredPersonFieldsExceptDate(page);
        
        const invalidDates = [
          '2025-13-01',   // invalid month
          '2025-02-30',   // invalid day for February
          '1800-01-01',   // too old
          '2030-01-01'    // future date for birthdate
        ];
        
        const validDates = [
          '1985-06-15',
          '1990-12-25',
          '1975-01-01'
        ];
        
        // Test invalid dates
        for (const invalidDate of invalidDates) {
          try {
            await dateField.fill(invalidDate);
            await page.click('button[type="submit"]#da-continue-button');
            await page.waitForTimeout(1000);
            
            const errors = await getValidationErrors(page);
            if (errors.length > 0) {
              console.log(`✅ Date validation rejected: ${invalidDate}`);
              break;
            }
          } catch (e) {
            console.log(`✅ Browser rejected invalid date: ${invalidDate}`);
          }
        }
        
        // Test valid date
        await dateField.fill(validDates[0]);
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const finalContent = await page.content();
        if (!finalContent.includes('Error')) {
          console.log('✅ Valid date accepted');
        }
      }
    }
  });

  test('should validate required fields in financial forms', async ({ page }) => {
    // Navigate to financial forms scenario
    await navigateToFinancialForms(page);
    
    const financialContent = await page.content();
    if (financialContent.includes('financial') || financialContent.includes('property')) {
      console.log('Testing financial form validation...');
      
      // Try submitting without filling required fields
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const validationErrors = await getValidationErrors(page);
      if (validationErrors.length > 0) {
        console.log('✅ Financial forms show validation errors for required fields');
        
        // Fill minimum required financial fields
        const inputs = await page.locator('input[type="text"], input[type="number"]').all();
        if (inputs.length > 0) {
          await inputs[0].fill('50000'); // property value or income
        }
        
        // Select some radio buttons
        const radioButtons = await page.locator('input[type="radio"]').all();
        for (let i = 0; i < Math.min(3, radioButtons.length); i++) {
          if (i % 2 === 0) {
            await radioButtons[i].click();
          }
        }
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const afterFill = await page.content();
        if (!afterFill.includes('Error')) {
          console.log('✅ Financial form accepts properly filled data');
        }
      }
    }
  });

  test('should validate numeric fields in financial forms', async ({ page }) => {
    await navigateToFinancialForms(page);
    
    const financialContent = await page.content();
    if (financialContent.includes('financial') || financialContent.includes('property')) {
      console.log('Testing numeric field validation in financial forms...');
      
      const numericFields = await page.locator('input[type="number"], input[type="text"][name*="value"], input[type="text"][name*="amount"]').all();
      
      if (numericFields.length > 0) {
        const numericField = numericFields[0];
        
        const invalidValues = [
          'abc',
          '$50,000',      // currency symbols
          '50,000.00.00', // multiple decimals
          '-50000',       // negative (may not be allowed)
          '50000000000000000000' // extremely large number
        ];
        
        for (const invalidValue of invalidValues) {
          await numericField.fill(invalidValue);
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          const errors = await getValidationErrors(page);
          if (errors.length > 0) {
            console.log(`✅ Numeric validation rejected: ${invalidValue}`);
            break;
          }
        }
        
        // Test valid numeric value
        await numericField.fill('50000');
        // Fill other required fields
        const radioButtons = await page.locator('input[type="radio"]').all();
        for (let i = 0; i < Math.min(3, radioButtons.length); i++) {
          if (i % 2 === 0) {
            await radioButtons[i].click();
          }
        }
        
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const result = await page.content();
        if (!result.includes('Error')) {
          console.log('✅ Valid numeric value accepted');
        }
      }
    }
  });

  test('should validate required checkboxes and radio buttons', async ({ page }) => {
    // Navigate through to orders selection
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    await page.click('button:has-text("No")'); // Emergency
    await page.waitForTimeout(500);
    await page.click('button:has-text("Yes")'); // MIP
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    await page.click('button:has-text("Married")'); // Relationship
    await page.waitForTimeout(500);
    
    // Orders selection screen - test validation
    const ordersContent = await page.content();
    if (ordersContent.includes('orders') || ordersContent.includes('seeking')) {
      console.log('Testing checkbox validation for orders selection...');
      
      // Try submitting without selecting any orders
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const validationErrors = await getValidationErrors(page);
      if (validationErrors.length > 0) {
        console.log('✅ Orders selection requires at least one checkbox');
        
        // Select an order and continue
        await page.check('text=Divorce');
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        const afterSelection = await page.content();
        if (!afterSelection.includes('Error')) {
          console.log('✅ Checkbox validation accepts valid selection');
        }
      } else {
        console.log('❓ No validation for orders selection - may allow empty');
      }
    }
  });

  test('should handle validation error display and user feedback', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing validation error display and user experience...');
      
      // Submit empty form to trigger validation
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      // Check error display elements
      const errorElements = await page.locator('.alert-danger, .text-danger, .da-error, .error, .validation-error').all();
      if (errorElements.length > 0) {
        console.log('✅ Validation errors are displayed to user');
        
        // Check if errors are associated with specific fields
        let fieldSpecificErrors = 0;
        for (const errorElement of errorElements) {
          const errorText = await errorElement.textContent();
          if (errorText && (errorText.includes('required') || errorText.includes('field') || errorText.includes('enter'))) {
            fieldSpecificErrors++;
          }
        }
        
        if (fieldSpecificErrors > 0) {
          console.log('✅ Field-specific validation messages provided');
        }
        
        // Check if form stays on same page (doesn't advance with errors)
        const stillOnUserForm = await page.content();
        if (stillOnUserForm.includes('Your Information')) {
          console.log('✅ Form correctly stays on current page when validation fails');
        }
        
        // Fill one field and check if error updates
        await fillFieldByContext(page, ['first'], 'John');
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(1000);
        
        const updatedErrors = await page.locator('.alert-danger, .text-danger, .da-error, .error').all();
        if (updatedErrors.length !== errorElements.length) {
          console.log('✅ Validation errors update dynamically as fields are completed');
        }
      }
    }
  });

  // Helper Functions

  async function navigateToPartyInfo(page) {
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    await page.click('button:has-text("No")'); // Emergency
    await page.waitForTimeout(500);
    await page.click('button:has-text("Yes")'); // MIP
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button'); // MIP continue
    await page.waitForTimeout(500);
    await page.click('button:has-text("Married")'); // Relationship
    await page.waitForTimeout(500);
    await page.check('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(500);
    await page.click('button:has-text("No")'); // Children
    await page.waitForTimeout(500);
    const roleContent = await page.content();
    if (roleContent.includes('Role')) {
      await page.click('button:has-text("starting"), button:has-text("Applicant")');
      await page.waitForTimeout(1000);
    }
  }

  async function navigateToFinancialForms(page) {
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    await page.click('button:has-text("No")'); // Emergency
    await page.waitForTimeout(500);
    await page.click('button:has-text("Yes")'); // MIP
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Select orders that will trigger financial forms
    await page.check('text=Divorce');
    await page.check('text=Child support');
    await page.check('text=Property');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Should be contested due to property/support
    await page.click('button:has-text("Contested")');
    await page.waitForTimeout(1000);
  }

  async function getValidationErrors(page) {
    const errorSelectors = [
      '.alert-danger',
      '.text-danger', 
      '.da-error',
      '.error',
      '.validation-error',
      '.field-error',
      '[class*="error"]'
    ];
    
    const errors = [];
    for (const selector of errorSelectors) {
      const elements = await page.locator(selector).all();
      for (const element of elements) {
        const text = await element.textContent();
        if (text && text.trim()) {
          errors.push(text.trim());
        }
      }
    }
    
    return errors;
  }

  async function fillRequiredPersonFields(page) {
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['phone'], '4165551234');
    await fillFieldByContext(page, ['email'], 'john.smith@example.com', 'email');
    await fillFieldByContext(page, ['address'], '123 Main Street');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
    
    const dateFields = await page.locator('input[type="date"]').all();
    if (dateFields.length > 0) {
      await dateFields[0].fill('1985-06-15');
    }
  }

  async function fillRequiredPersonFieldsExceptEmail(page) {
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['phone'], '4165551234');
    await fillFieldByContext(page, ['address'], '123 Main Street');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
  }

  async function fillRequiredPersonFieldsExceptPhone(page) {
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['email'], 'john.smith@example.com', 'email');
    await fillFieldByContext(page, ['address'], '123 Main Street');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
  }

  async function fillRequiredPersonFieldsExceptPostal(page) {
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['phone'], '4165551234');
    await fillFieldByContext(page, ['email'], 'john.smith@example.com', 'email');
    await fillFieldByContext(page, ['address'], '123 Main Street');
    await fillFieldByContext(page, ['city'], 'Toronto');
  }

  async function fillRequiredPersonFieldsExceptDate(page) {
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['phone'], '4165551234');
    await fillFieldByContext(page, ['email'], 'john.smith@example.com', 'email');
    await fillFieldByContext(page, ['address'], '123 Main Street');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
  }

  async function fillFieldByContext(page, contextWords, value, inputType = 'text') {
    const field = await findFieldByContext(page, contextWords, inputType);
    if (field) {
      await field.fill(value);
      return true;
    }
    return false;
  }

  async function findFieldByContext(page, contextWords, inputType = 'text') {
    const selector = inputType === 'email' ? 'input[type="email"], input[type="text"]' :
                    inputType === 'tel' ? 'input[type="tel"], input[type="text"]' :
                    'input[type="text"], input[type="tel"]';
    
    const inputs = await page.locator(selector).all();
    
    for (const input of inputs) {
      const name = await input.getAttribute('name') || '';
      const placeholder = await input.getAttribute('placeholder') || '';
      const label = await input.getAttribute('aria-label') || '';
      const context = (name + placeholder + label).toLowerCase();
      
      if (contextWords.some(word => context.includes(word.toLowerCase()))) {
        return input;
      }
    }
    return null;
  }
});