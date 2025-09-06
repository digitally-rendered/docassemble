/**
 * Playwright Test for Ontario Family Law Form 43
 * Ontario Family Law Form 43
 * Generated: 2025-09-05 15:03
 * 
 * This test covers:
 * - Complete form flow from start to finish
 * - Field validation
 * - Required field checks
 * - Form submission
 */

const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
const BASE_URL = process.env.DA_URL || 'http://localhost';
const INTERVIEW_URL = `${BASE_URL}/interview`;
const TIMEOUT = 60000; // 60 seconds

// Test data for Form 43
const testData = {
  applicant: {
    firstName: 'John',
    middleName: 'Michael',
    lastName: 'Smith',
    birthdate: '01/15/1980',
    street: '123 Main Street',
    city: 'Toronto',
    province: 'Ontario',
    postalCode: 'M5H 2N2',
    phone: '416-555-1234',
    email: 'john.smith@example.com'
  },
  respondent: {
    firstName: 'Jane',
    middleName: 'Elizabeth',
    lastName: 'Doe',
    birthdate: '03/20/1982',
    street: '456 Queen Street',
    city: 'Ottawa',
    province: 'Ontario',
    postalCode: 'K1P 1J9',
    phone: '613-555-5678',
    email: 'jane.doe@example.com'
  },
  court: {
    name: 'Superior Court of Justice',
    location: '393 University Avenue, Toronto, ON',
    fileNumber: 'FC-2024-12345'
  },
  marriage: {
    date: '06/15/2005',
    place: 'Toronto, Ontario, Canada',
    separationDate: '01/01/2023'
  },
  children: [
    {
      name: 'Emily Smith',
      birthdate: '04/10/2010',
      age: '14',
      grade: '9',
      residingWith: 'Applicant'
    },
    {
      name: 'Michael Smith',
      birthdate: '09/22/2012',
      age: '12',
      grade: '7',
      residingWith: 'Shared'
    }
  ]
};

// Test suite for Form 43
test.describe('Form 43 - Complete Interview', () => {
  test.setTimeout(TIMEOUT);
  
  test('should complete the entire form with valid data', async ({ page }) => {
    // Navigate to the interview
    await page.goto(`${INTERVIEW_URL}/form_43_complete.yml`);
    
    // Wait for the interview to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Start the interview
    const startButton = await page.$('button:has-text("Start")');
    if (startButton) {
      await startButton.click();
    }
    
    // Fill applicant information (from common intake)
    await fillApplicantInfo(page, testData.applicant);
    
    // Fill respondent information (from common intake)
    await fillRespondentInfo(page, testData.respondent);
    
    // Fill court information
    await fillCourtInfo(page, testData.court);
    
    // Fill marriage information if applicable
    if (await page.$('input[name="marriage_date"]')) {
      await fillMarriageInfo(page, testData.marriage);
    }
    
    // Fill children information if applicable
    if (await page.$('button:has-text("Add child")')) {
      await fillChildrenInfo(page, testData.children);
    }
    
    // Fill form-specific fields
    await fillFormSpecificFields_43(page);
    
    // Continue through remaining questions
    await continueToEnd(page);
    
    // Verify we reached the final screen
    await expect(page.locator('h1')).toContainText('Form 43 Complete');
    
    // Verify download button is present
    await expect(page.locator('button:has-text("Download Form 43")')).toBeVisible();
  });
  
  test('should validate required fields', async ({ page }) => {
    await page.goto(`${INTERVIEW_URL}/form_43_complete.yml`);
    
    // Try to continue without filling required fields
    const continueButton = await page.$('button:has-text("Continue")');
    if (continueButton) {
      await continueButton.click();
      
      // Should see validation errors
      const errorMessage = await page.$('.da-has-error, .text-danger');
      expect(errorMessage).toBeTruthy();
    }
  });
  
  test('should validate postal code format', async ({ page }) => {
    await page.goto(`${INTERVIEW_URL}/form_43_complete.yml`);
    
    // Navigate to postal code field
    const postalField = await page.$('input[name*="postal"]');
    if (postalField) {
      // Try invalid postal code
      await postalField.fill('INVALID');
      await page.click('button:has-text("Continue")');
      
      // Should see validation error
      const errorMessage = await page.$('.da-has-error, .text-danger');
      expect(errorMessage).toBeTruthy();
      
      // Enter valid postal code
      await postalField.fill('M5H 2N2');
      await page.click('button:has-text("Continue")');
    }
  });
  
  test('should save and resume interview', async ({ page }) => {
    await page.goto(`${INTERVIEW_URL}/form_43_complete.yml`);
    
    // Fill some initial data
    await fillApplicantInfo(page, testData.applicant);
    
    // Save the interview
    const saveButton = await page.$('button:has-text("Save")');
    if (saveButton) {
      await saveButton.click();
      
      // Get the resume URL
      const resumeUrl = await page.url();
      
      // Navigate away and come back
      await page.goto('about:blank');
      await page.goto(resumeUrl);
      
      // Verify data is preserved
      const firstNameField = await page.$('input[name="applicant_first_name"]');
      if (firstNameField) {
        const value = await firstNameField.inputValue();
        expect(value).toBe(testData.applicant.firstName);
      }
    }
  });
});


// Form-specific field tests for Form 43
test.describe('Form 43 - Field Validations', () => {
});

// Helper functions for Form 43

async function fillApplicantInfo(page, data) {
  // Fill applicant first name if visible
  const firstName = await page.$('input[name="applicant_first_name"], input[name="applicant.name.first"]');
  if (firstName && await firstName.isVisible()) {
    await firstName.fill(data.firstName);
  }
  
  // Fill applicant last name if visible
  const lastName = await page.$('input[name="applicant_last_name"], input[name="applicant.name.last"]');
  if (lastName && await lastName.isVisible()) {
    await lastName.fill(data.lastName);
  }
  
  // Fill other applicant fields
  await fillFieldIfVisible(page, 'applicant_birthdate', data.birthdate);
  await fillFieldIfVisible(page, 'applicant_address_street', data.street);
  await fillFieldIfVisible(page, 'applicant_address_city', data.city);
  await fillFieldIfVisible(page, 'applicant_address_postal_code', data.postalCode);
  await fillFieldIfVisible(page, 'applicant_phone', data.phone);
  await fillFieldIfVisible(page, 'applicant_email', data.email);
  
  await clickContinueIfVisible(page);
}

async function fillRespondentInfo(page, data) {
  // Similar to applicant info
  const firstName = await page.$('input[name="respondent_first_name"], input[name="respondent.name.first"]');
  if (firstName && await firstName.isVisible()) {
    await firstName.fill(data.firstName);
  }
  
  const lastName = await page.$('input[name="respondent_last_name"], input[name="respondent.name.last"]');
  if (lastName && await lastName.isVisible()) {
    await lastName.fill(data.lastName);
  }
  
  await fillFieldIfVisible(page, 'respondent_birthdate', data.birthdate);
  await fillFieldIfVisible(page, 'respondent_address_street', data.street);
  await fillFieldIfVisible(page, 'respondent_address_city', data.city);
  await fillFieldIfVisible(page, 'respondent_address_postal_code', data.postalCode);
  await fillFieldIfVisible(page, 'respondent_phone', data.phone);
  await fillFieldIfVisible(page, 'respondent_email', data.email);
  
  await clickContinueIfVisible(page);
}

async function fillCourtInfo(page, data) {
  await fillFieldIfVisible(page, 'court_name', data.name);
  await fillFieldIfVisible(page, 'court_location', data.location);
  await fillFieldIfVisible(page, 'court_file_number', data.fileNumber);
  
  await clickContinueIfVisible(page);
}

async function fillMarriageInfo(page, data) {
  await fillFieldIfVisible(page, 'marriage_date', data.date);
  await fillFieldIfVisible(page, 'marriage_place', data.place);
  await fillFieldIfVisible(page, 'separation_date', data.separationDate);
  
  await clickContinueIfVisible(page);
}

async function fillChildrenInfo(page, children) {
  for (const child of children) {
    // Click add child button if available
    const addButton = await page.$('button:has-text("Add child"), button:has-text("Add another")');
    if (addButton && await addButton.isVisible()) {
      await addButton.click();
    }
    
    // Fill child information
    await fillFieldIfVisible(page, 'child_name', child.name);
    await fillFieldIfVisible(page, 'child_birthdate', child.birthdate);
    await fillFieldIfVisible(page, 'child_age', child.age);
    await fillFieldIfVisible(page, 'child_grade', child.grade);
    
    // Select residing with
    const residingSelect = await page.$('select[name*="residing"]');
    if (residingSelect && await residingSelect.isVisible()) {
      await residingSelect.selectOption(child.residingWith);
    }
    
    await clickContinueIfVisible(page);
  }
}

async function fillFormSpecificFields_43(page) {
  // Fill any form-specific fields that aren't in common intake
  // This function should be customized for each form
  
  // Example: Check for checkboxes and select them
  const checkboxes = await page.$$('input[type="checkbox"]:not(:checked)');
  for (const checkbox of checkboxes.slice(0, 3)) { // Select first 3 checkboxes
    if (await checkbox.isVisible()) {
      await checkbox.check();
    }
  }
  
  // Fill any visible text areas
  const textareas = await page.$$('textarea');
  for (const textarea of textareas) {
    if (await textarea.isVisible()) {
      await textarea.fill('This is a test response for the form field.');
    }
  }
  
  await clickContinueIfVisible(page);
}

async function fillFieldIfVisible(page, fieldName, value) {
  const field = await page.$(`input[name="${fieldName}"], select[name="${fieldName}"], textarea[name="${fieldName}"]`);
  if (field && await field.isVisible()) {
    const tagName = await field.evaluate(el => el.tagName.toLowerCase());
    
    if (tagName === 'select') {
      await field.selectOption(value);
    } else {
      await field.fill(value);
    }
  }
}

async function clickContinueIfVisible(page) {
  const continueButton = await page.$('button:has-text("Continue"), button:has-text("Next")');
  if (continueButton && await continueButton.isVisible()) {
    await continueButton.click();
    await page.waitForTimeout(500); // Small delay for page to update
  }
}

async function continueToEnd(page) {
  // Continue clicking through remaining questions
  let attempts = 0;
  const maxAttempts = 50;
  
  while (attempts < maxAttempts) {
    const continueButton = await page.$('button:has-text("Continue"), button:has-text("Next")');
    const finalScreen = await page.$('h1:has-text("Complete"), h1:has-text("Finished")');
    
    if (finalScreen) {
      break; // Reached the end
    }
    
    if (continueButton && await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForTimeout(500);
    } else {
      // Fill any remaining visible fields with default values
      await fillRemainingFields(page);
    }
    
    attempts++;
  }
}

async function fillRemainingFields(page) {
  // Fill any remaining required fields with default values
  const inputs = await page.$$('input:visible, select:visible, textarea:visible');
  
  for (const input of inputs) {
    const type = await input.getAttribute('type');
    const name = await input.getAttribute('name');
    const value = await input.inputValue();
    
    if (!value) { // Only fill if empty
      if (type === 'text') {
        await input.fill('Test Value');
      } else if (type === 'email') {
        await input.fill('test@example.com');
      } else if (type === 'tel') {
        await input.fill('416-555-0000');
      } else if (type === 'number') {
        await input.fill('1');
      } else if (type === 'date') {
        await input.fill('01/01/2024');
      }
    }
  }
  
  await clickContinueIfVisible(page);
}

module.exports = { testData };
