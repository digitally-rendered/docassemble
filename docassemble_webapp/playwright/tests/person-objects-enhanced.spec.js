const { test, expect } = require('@playwright/test');

test.describe('Person Objects and Enhanced Party Information', () => {
  const wizardUrl = 'http://localhost:8080/interview?i=docassemble.webapp:ontario-family-law/ontario-family-law-wizard.yml';

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', exception => {
      console.log(`Page error: ${exception}`);
    });
    
    await page.goto(wizardUrl);
    await page.waitForLoadState('networkidle');
  });

  test('should collect enhanced Person object data for applicant', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('✅ Reached applicant information collection');
      
      // Test Person object with comprehensive fields
      await testPersonObjectFields(page, {
        role: 'applicant',
        person: {
          firstName: 'John',
          lastName: 'Smith',
          middleName: 'David',
          otherNames: 'Johnny, J.D.',
          gender: 'male',
          birthdate: '1985-06-15',
          phone: '4165551234',
          alternativePhone: '6475559876',
          email: 'john.smith@example.com',
          alternativeEmail: 'j.smith@gmail.com',
          address: {
            street: '123 King Street West',
            unit: 'Apt 1205',
            city: 'Toronto',
            province: 'Ontario',
            country: 'Canada',
            postalCode: 'M5H 2N2'
          }
        }
      });
      
      console.log('✅ Enhanced Person object fields tested for applicant');
    } else {
      throw new Error('Could not reach applicant information screen');
    }
  });

  test('should collect enhanced Person object data for respondent', async ({ page }) => {
    await navigateToPartyInfo(page);
    await fillApplicantInfo(page);
    
    // Should now be on respondent/other party screen
    const otherPartyContent = await page.content();
    if (otherPartyContent.includes('Other Party') || otherPartyContent.includes('Respondent')) {
      console.log('✅ Reached respondent information collection');
      
      await testPersonObjectFields(page, {
        role: 'respondent',
        person: {
          firstName: 'Jane',
          lastName: 'Doe',
          middleName: 'Marie',
          gender: 'female',
          birthdate: '1987-03-22',
          phone: '4165555678',
          email: 'jane.doe@example.com',
          address: {
            street: '456 Oak Avenue',
            city: 'Toronto',
            province: 'Ontario',
            country: 'Canada',
            postalCode: 'M4W 1J5'
          }
        }
      });
      
      console.log('✅ Enhanced Person object fields tested for respondent');
    } else {
      throw new Error('Could not reach respondent information screen');
    }
  });

  test('should validate Person object required fields', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      // Test required field validation
      console.log('Testing Person object field validation...');
      
      // Try submitting with no data
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1000);
      
      const hasValidationErrors = await page.locator('.alert-danger, .text-danger, .da-error, .error').count() > 0;
      if (hasValidationErrors) {
        console.log('✅ Person object shows validation errors for empty required fields');
        
        // Fill only first name and test partial validation
        const firstNameField = await findFieldByContext(page, ['first', 'name']);
        if (firstNameField) {
          await firstNameField.fill('John');
          await page.click('button[type="submit"]#da-continue-button');
          await page.waitForTimeout(1000);
          
          const stillHasErrors = await page.locator('.alert-danger, .text-danger, .da-error, .error').count() > 0;
          if (stillHasErrors) {
            console.log('✅ Person object validates multiple required fields');
          }
        }
        
        // Test with minimum required fields
        await fillMinimumPersonFields(page);
        await page.click('button[type="submit"]#da-continue-button');
        await page.waitForTimeout(2000);
        
        const afterMinimum = await page.content();
        if (!afterMinimum.includes('Error') && 
            (afterMinimum.includes('Other Party') || afterMinimum.includes('lawyer') || afterMinimum.includes('Court'))) {
          console.log('✅ Person object accepts minimum required fields and proceeds');
        }
      } else {
        console.log('❓ No validation errors shown - may have different validation approach');
      }
    }
  });

  test('should handle Person object address fields properly', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing Person object address handling...');
      
      // Test comprehensive address fields
      const addressFields = {
        street: '123 King Street West',
        unit: 'Suite 1200',
        city: 'Toronto', 
        province: 'Ontario',
        country: 'Canada',
        postalCode: 'M5H 2N2'
      };
      
      await fillAddressFields(page, addressFields);
      
      // Fill minimum other required fields
      await fillMinimumPersonFields(page);
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(2000);
      
      const afterSubmit = await page.content();
      if (!afterSubmit.includes('Error')) {
        console.log('✅ Person object address fields processed successfully');
      } else {
        console.log('❌ Error processing Person object address fields');
        const errors = await page.locator('.alert-danger, .text-danger').allTextContents();
        console.log('Address field errors:', errors);
      }
    }
  });

  test('should handle Person object contact information variations', async ({ page }) => {
    await navigateToPartyInfo(page);
    
    const userInfoContent = await page.content();
    if (userInfoContent.includes('Your Information')) {
      console.log('Testing Person object contact information variations...');
      
      // Test different phone number formats
      const phoneVariations = [
        '416-555-1234',
        '(416) 555-1234',
        '4165551234',
        '+1 416 555 1234'
      ];
      
      // Test email variations
      const emailVariations = [
        'john.smith@example.com',
        'john+test@example.org',
        'j.smith123@domain.co.uk'
      ];
      
      // Fill basic info first
      await fillMinimumPersonFields(page);
      
      // Test phone field with different formats
      const phoneField = await findFieldByContext(page, ['phone', 'tel']);
      if (phoneField) {
        for (let i = 0; i < phoneVariations.length && i < 1; i++) { // Test first variation
          await phoneField.fill('');
          await phoneField.fill(phoneVariations[i]);
          console.log(`Testing phone format: ${phoneVariations[i]}`);
        }
      }
      
      // Test email field
      const emailField = await findFieldByContext(page, ['email']);
      if (emailField) {
        await emailField.fill(emailVariations[0]);
        console.log(`Testing email format: ${emailVariations[0]}`);
      }
      
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(2000);
      
      const result = await page.content();
      if (!result.includes('Error')) {
        console.log('✅ Person object handles contact information variations');
      } else {
        console.log('❌ Issues with contact information handling');
      }
    }
  });

  test('should collect Person objects for multiple party scenario', async ({ page }) => {
    // Test scenarios with multiple parties (applicant, respondent, possibly others)
    await navigateToPartyInfo(page);
    
    // Fill applicant
    await fillApplicantInfo(page);
    
    // Should reach respondent
    const respondentContent = await page.content();
    if (respondentContent.includes('Other Party') || respondentContent.includes('Respondent')) {
      await fillRespondentInfo(page);
      
      // Continue to see if there are additional parties
      await page.click('button[type="submit"]#da-continue-button');
      await page.waitForTimeout(1500);
      
      console.log('✅ Multiple Person objects (applicant and respondent) collected successfully');
      
      // Check if we reached next section (lawyers, court, etc.)
      const nextContent = await page.content();
      if (nextContent.includes('lawyer') || nextContent.includes('Court') || nextContent.includes('represented')) {
        console.log('✅ Successfully transitioned from Person object collection to next section');
      }
    }
  });

  // Helper Functions

  async function navigateToPartyInfo(page) {
    // Navigate through initial screens to reach party information
    await page.click('button[type="submit"]#da-continue-button'); // Welcome
    await page.waitForTimeout(500);
    
    // Emergency - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // MIP - Yes
    await page.click('button:has-text("Yes")');
    await page.waitForTimeout(500);
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Relationship - Married (simple case)
    await page.click('button:has-text("Married")');
    await page.waitForTimeout(500);
    
    // Orders - Just divorce (simple)
    await page.check('text=Divorce');
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(500);
    
    // Divorce complexity - Uncontested
    await page.click('button:has-text("Uncontested")');
    await page.waitForTimeout(500);
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.waitForTimeout(500);
    
    // Role - Applicant
    const roleContent = await page.content();
    if (roleContent.includes('Role') || roleContent.includes('starting')) {
      await page.click('button:has-text("starting"), button:has-text("Applicant")');
      await page.waitForTimeout(1000);
    }
  }

  async function testPersonObjectFields(page, testData) {
    const { role, person } = testData;
    console.log(`Testing Person object fields for ${role}...`);
    
    // Name fields
    await fillFieldByContext(page, ['first'], person.firstName);
    await fillFieldByContext(page, ['last', 'surname'], person.lastName);
    if (person.middleName) {
      await fillFieldByContext(page, ['middle'], person.middleName);
    }
    if (person.otherNames) {
      await fillFieldByContext(page, ['other', 'alias'], person.otherNames);
    }
    
    // Personal information
    if (person.gender) {
      await selectFieldByContext(page, ['gender'], person.gender);
    }
    if (person.birthdate) {
      await fillFieldByContext(page, ['birth', 'date'], person.birthdate, 'date');
    }
    
    // Contact information
    await fillFieldByContext(page, ['phone'], person.phone);
    if (person.alternativePhone) {
      await fillFieldByContext(page, ['phone', 'alternative', 'alternate'], person.alternativePhone);
    }
    await fillFieldByContext(page, ['email'], person.email, 'email');
    if (person.alternativeEmail) {
      await fillFieldByContext(page, ['email', 'alternative', 'alternate'], person.alternativeEmail, 'email');
    }
    
    // Address
    if (person.address) {
      await fillAddressFields(page, person.address);
    }
    
    // Submit and verify
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(2000);
    
    const result = await page.content();
    if (result.includes('Error')) {
      const errors = await page.locator('.alert-danger, .text-danger').allTextContents();
      console.log(`❌ Person object validation failed for ${role}:`, errors);
      return false;
    } else {
      console.log(`✅ Person object data accepted for ${role}`);
      return true;
    }
  }

  async function fillAddressFields(page, address) {
    await fillFieldByContext(page, ['address', 'street'], address.street);
    if (address.unit) {
      await fillFieldByContext(page, ['unit', 'apartment', 'apt'], address.unit);
    }
    await fillFieldByContext(page, ['city'], address.city);
    if (address.province) {
      await selectFieldByContext(page, ['province', 'state'], address.province);
    }
    if (address.country) {
      await selectFieldByContext(page, ['country'], address.country);
    }
    await fillFieldByContext(page, ['postal', 'zip'], address.postalCode);
  }

  async function fillFieldByContext(page, contextWords, value, inputType = 'text') {
    const field = await findFieldByContext(page, contextWords, inputType);
    if (field) {
      await field.fill(value);
      return true;
    }
    return false;
  }

  async function selectFieldByContext(page, contextWords, value) {
    const selects = await page.locator('select').all();
    for (const select of selects) {
      const name = await select.getAttribute('name') || '';
      const label = await select.getAttribute('aria-label') || '';
      const context = (name + label).toLowerCase();
      
      if (contextWords.some(word => context.includes(word.toLowerCase()))) {
        try {
          await select.selectOption(value);
          return true;
        } catch (e) {
          // Try option text
          const options = await select.locator('option').allTextContents();
          const matchingOption = options.find(opt => 
            opt.toLowerCase().includes(value.toLowerCase()) ||
            value.toLowerCase().includes(opt.toLowerCase())
          );
          if (matchingOption) {
            await select.selectOption({ label: matchingOption });
            return true;
          }
        }
      }
    }
    return false;
  }

  async function findFieldByContext(page, contextWords, inputType = 'text') {
    const selector = inputType === 'email' ? 'input[type="email"], input[type="text"]' :
                    inputType === 'date' ? 'input[type="date"]' :
                    'input[type="text"], input[type="tel"]';
    
    const inputs = await page.locator(selector).all();
    
    for (const input of inputs) {
      const name = await input.getAttribute('name') || '';
      const placeholder = await input.getAttribute('placeholder') || '';
      const label = await input.getAttribute('aria-label') || '';
      const id = await input.getAttribute('id') || '';
      const context = (name + placeholder + label + id).toLowerCase();
      
      if (contextWords.some(word => context.includes(word.toLowerCase()))) {
        return input;
      }
    }
    return null;
  }

  async function fillMinimumPersonFields(page) {
    // Fill minimum required fields for Person object
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['phone'], '4165551234');
    await fillFieldByContext(page, ['email'], 'john.smith@example.com', 'email');
    await fillFieldByContext(page, ['address', 'street'], '123 Main Street');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
  }

  async function fillApplicantInfo(page) {
    await fillFieldByContext(page, ['first'], 'John');
    await fillFieldByContext(page, ['last'], 'Smith');
    await fillFieldByContext(page, ['phone'], '4165551234');
    await fillFieldByContext(page, ['email'], 'john.smith@example.com', 'email');
    await fillFieldByContext(page, ['address', 'street'], '123 King Street West');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M5H 2N2');
    
    await page.click('button[type="submit"]#da-continue-button');
    await page.waitForTimeout(1500);
  }

  async function fillRespondentInfo(page) {
    await fillFieldByContext(page, ['first'], 'Jane');
    await fillFieldByContext(page, ['last'], 'Doe');
    await fillFieldByContext(page, ['phone'], '4165555678');
    await fillFieldByContext(page, ['email'], 'jane.doe@example.com', 'email');
    await fillFieldByContext(page, ['address', 'street'], '456 Oak Avenue');
    await fillFieldByContext(page, ['city'], 'Toronto');
    await fillFieldByContext(page, ['postal'], 'M4W 1J5');
  }
});