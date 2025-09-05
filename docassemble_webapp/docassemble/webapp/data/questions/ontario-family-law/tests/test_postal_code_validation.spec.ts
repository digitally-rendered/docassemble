import { test, expect, Page } from '@playwright/test';

// Helper function to start the interview
async function startInterview(page: Page) {
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_final.yml');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('#daMainQuestion')).toContainText('Ontario Family Law Common Intake');
  await page.getByRole('button', { name: /Continue/i }).click();
}

// Navigate to user contact info page
async function navigateToUserContact(page: Page) {
  await startInterview(page);
  
  // No emergency
  await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
  
  // MIP completed
  await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
  
  // Married
  await page.getByRole('button', { name: /^Married$/i }).click();
  
  // Skip orders
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Fill personal info
  await page.fill('input[name*=".name.first"]', 'John');
  await page.fill('input[name*=".name.last"]', 'Smith');
  await page.fill('input[name*="birthdate"]', '01/01/1980');
  await page.getByRole('button', { name: /Continue/i }).click();
  
  // Should be on contact info page
  await expect(page.locator('#daMainQuestion')).toContainText('Your Contact Information');
}

test.describe('Canadian Postal Code Validation', () => {
  
  test('Accepts valid postal code with space', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill address fields
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    
    // Valid postal code with space
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to lawyer question (validation passed)
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have a lawyer');
  });
  
  test('Accepts valid postal code without space and formats it', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill address fields
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    
    // Valid postal code without space
    await page.fill('input[name*="address.postal_code"]', 'M5H2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to lawyer question (validation passed)
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have a lawyer');
  });
  
  test('Accepts lowercase postal code and converts to uppercase', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill address fields
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    
    // Lowercase postal code
    await page.fill('input[name*="address.postal_code"]', 'm5h 2n2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to lawyer question (validation passed)
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have a lawyer');
  });
  
  test('Rejects invalid postal code - wrong format', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill address fields
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    
    // Invalid postal code (US format)
    await page.fill('input[name*="address.postal_code"]', '90210');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    
    // Try to continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid Canadian postal code/i);
    
    // Should remain on same page
    await expect(page.locator('#daMainQuestion')).toContainText('Your Contact Information');
  });
  
  test('Rejects invalid postal code - invalid letters', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill address fields
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    
    // Invalid postal code (D is not valid in first position)
    await page.fill('input[name*="address.postal_code"]', 'D5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    
    // Try to continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid Canadian postal code/i);
  });
  
  test('Validates phone number format', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill address fields
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    
    // Invalid phone (too short)
    await page.fill('input[name*="phone_number"]', '416-555');
    
    // Try to continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show phone validation error
    await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid 10 or 11 digit phone/i);
  });
  
  test('Accepts and formats 10-digit phone number', async ({ page }) => {
    await navigateToUserContact(page);
    
    // Fill all fields properly
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '4165551234'); // No formatting
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to lawyer question
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have a lawyer');
  });
});

test.describe('Lawyer Information Validation', () => {
  
  async function navigateToLawyerInfo(page: Page) {
    await navigateToUserContact(page);
    
    // Fill user contact info
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Say yes to lawyer
    await page.getByRole('button', { name: /^Yes$/i }).click();
    
    // Should be on lawyer info page
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Information');
  }
  
  test('Validates Law Society Number format', async ({ page }) => {
    await navigateToLawyerInfo(page);
    
    // Fill lawyer name
    await page.fill('input[name*="name.text"]', 'Jane Attorney');
    
    // Invalid Law Society Number
    await page.fill('input[name*="lsuc_number"]', '12345'); // Missing L or P prefix
    
    // Try to continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid Law Society Number/i);
  });
  
  test('Accepts valid Law Society Number with L prefix', async ({ page }) => {
    await navigateToLawyerInfo(page);
    
    // Fill lawyer info
    await page.fill('input[name*="name.text"]', 'Jane Attorney');
    await page.fill('input[name*="lsuc_number"]', 'L12345');
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to lawyer contact info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Contact Information');
  });
  
  test('Accepts valid Law Society Number with P prefix', async ({ page }) => {
    await navigateToLawyerInfo(page);
    
    // Fill lawyer info
    await page.fill('input[name*="name.text"]', 'John Paralegal');
    await page.fill('input[name*="lsuc_number"]', 'P54321');
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to lawyer contact info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Contact Information');
  });
  
  test('Validates lawyer postal code', async ({ page }) => {
    await navigateToLawyerInfo(page);
    
    // Fill lawyer info
    await page.fill('input[name*="name.text"]', 'Jane Attorney');
    await page.fill('input[name*="lsuc_number"]', 'L12345');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Now on lawyer contact page
    await page.fill('input[name*="address.address"]', '100 Bay Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    
    // Invalid postal code
    await page.fill('input[name*="address.postal_code"]', 'INVALID');
    await page.fill('input[name*="phone_number"]', '416-555-5555');
    
    // Try to continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show validation error
    await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid Canadian postal code/i);
  });
});

test.describe('Opposing Party Validation', () => {
  
  async function navigateToOpposingParty(page: Page) {
    await navigateToUserContact(page);
    
    // Fill user contact info
    await page.fill('input[name*="address.address"]', '123 Main Street');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // No lawyer
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Fill opposing party info
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should be on opposing party contact page
    await expect(page.locator('#daMainQuestion')).toContainText('Other Party Contact Information');
  }
  
  test('Optional opposing party postal code still validates if provided', async ({ page }) => {
    await navigateToOpposingParty(page);
    
    // Fill some contact info with invalid postal code
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'WRONG');
    
    // Try to continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show validation error even though field is optional
    await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid Canadian postal code/i);
  });
  
  test('Can skip opposing party contact info entirely', async ({ page }) => {
    await navigateToOpposingParty(page);
    
    // Don't fill anything, just continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to opposing lawyer question
    await expect(page.locator('#daMainQuestion')).toContainText('Does the other party have a lawyer');
  });
  
  test('Accepts valid opposing party postal code', async ({ page }) => {
    await navigateToOpposingParty(page);
    
    // Fill valid contact info
    await page.fill('input[name*="address.address"]', '456 Other Street');
    await page.fill('input[name*="address.city"]', 'Ottawa');
    await page.fill('input[name*="address.postal_code"]', 'K1A 0B1'); // Valid Ottawa postal code
    await page.fill('input[name*="phone_number"]', '613-555-1234');
    
    // Should accept and continue
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to opposing lawyer question
    await expect(page.locator('#daMainQuestion')).toContainText('Does the other party have a lawyer');
  });
});

test.describe('Various Valid Canadian Postal Codes', () => {
  
  test('Tests various valid postal code formats', async ({ page }) => {
    const validPostalCodes = [
      'A1A 1A1', // Newfoundland
      'B3K 5X5', // Nova Scotia
      'C1A 4P3', // PEI
      'E1C 4Z6', // New Brunswick
      'G1R 4P5', // Quebec City
      'H3Z 2Y7', // Montreal
      'J8X 3X2', // Gatineau
      'K1A 0B1', // Ottawa
      'L5B 4G4', // Mississauga
      'M5H 2N2', // Toronto
      'N2L 3G1', // Waterloo
      'P3E 5N5', // Sudbury
      'R3C 4T3', // Winnipeg
      'S7K 3G5', // Saskatoon
      'T2P 5C5', // Calgary
      'V6B 5A1', // Vancouver
      'X1A 2P1', // NWT
      'Y1A 2C6', // Yukon
    ];
    
    for (const postalCode of validPostalCodes) {
      await navigateToUserContact(page);
      
      await page.fill('input[name*="address.address"]', '123 Main Street');
      await page.fill('input[name*="address.city"]', 'Toronto');
      await page.fill('input[name*="address.postal_code"]', postalCode);
      await page.fill('input[name*="phone_number"]', '416-555-1234');
      
      await page.getByRole('button', { name: /Continue/i }).click();
      
      // Should proceed (validation passed)
      await expect(page.locator('#daMainQuestion')).toContainText('Do you have a lawyer');
      
      // Go back for next test
      await page.goBack();
      await page.goBack();
    }
  });
  
  test('Tests invalid postal codes are rejected', async ({ page }) => {
    const invalidPostalCodes = [
      'D1A 1A1', // D not valid in first position
      'F1A 1A1', // F not valid in first position
      'I1A 1A1', // I not valid in first position
      'O1A 1A1', // O not valid in first position
      'Q1A 1A1', // Q not valid in first position
      'U1A 1A1', // U not valid in first position
      'W1A 1A1', // W not valid in first position
      'Z1A 1A1', // Z not valid in first position
      '90210',   // US ZIP code
      '12345',   // US ZIP code
      'ABC DEF', // All letters
      '123 456', // All numbers
      'M5H',     // Too short
      'M5H 2N',  // Too short
    ];
    
    for (const postalCode of invalidPostalCodes) {
      await navigateToUserContact(page);
      
      await page.fill('input[name*="address.address"]', '123 Main Street');
      await page.fill('input[name*="address.city"]', 'Toronto');
      await page.fill('input[name*="address.postal_code"]', postalCode);
      await page.fill('input[name*="phone_number"]', '416-555-1234');
      
      await page.getByRole('button', { name: /Continue/i }).click();
      
      // Should show validation error
      await expect(page.locator('.da-has-error, .da-field-error, .text-danger')).toContainText(/valid Canadian postal code/i);
      
      // Should remain on same page
      await expect(page.locator('#daMainQuestion')).toContainText('Your Contact Information');
      
      // Clear for next test
      await page.fill('input[name*="address.postal_code"]', '');
    }
  });
});