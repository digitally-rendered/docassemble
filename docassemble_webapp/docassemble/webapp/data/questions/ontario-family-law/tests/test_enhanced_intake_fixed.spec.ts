import { test, expect, Page } from '@playwright/test';

// Helper function to check a checkbox by partial label text
async function checkCheckbox(page: Page, labelText: string | RegExp) {
  // Use the input element directly, not the label
  const checkbox = page.locator(`input[type="checkbox"][alt*="${labelText}"]`).first();
  await checkbox.check();
}

// Helper function to start the interview
async function startInterview(page: Page) {
  await page.goto('http://localhost:8080/interview?i=docassemble.webapp%3Adata%2Fquestions%2Fontario-family-law%2Fcommon_intake_enhanced.yml');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('#daMainQuestion')).toContainText('Ontario Family Law Common Intake');
  await page.getByRole('button', { name: /Continue/i }).click();
}

// ============================================================================
// FIXED TEST SUITE: KEY FLOWS WITH PROPER SELECTORS
// ============================================================================

test.describe('Enhanced Intake - Core Flows', () => {
  
  test('Complete emergency flow', async ({ page }) => {
    await startInterview(page);
    
    // Emergency path
    await expect(page.locator('#daMainQuestion')).toContainText('Is this an emergency');
    await page.getByRole('button', { name: /Yes, this is an emergency/i }).click();
    
    // Emergency warning
    await expect(page.locator('#daMainQuestion')).toContainText('URGENT: Emergency Filing Required');
    await expect(page.locator('body')).toContainText('Form 8 - Application');
    await expect(page.locator('body')).toContainText('911');
    await page.getByRole('button', { name: /Continue.*understand/i }).click();
    
    // MIP status
    await expect(page.locator('#daMainQuestion')).toContainText('Mandatory Information Program');
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    
    // Relationship
    await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
    await page.getByRole('button', { name: /^Married$/i }).click();
    
    // Orders - should show divorce for married
    await expect(page.locator('#daMainQuestion')).toContainText('What orders are you seeking');
    await expect(page.locator('body')).toContainText('Divorce');
  });

  test('MIP not completed flow', async ({ page }) => {
    await startInterview(page);
    
    // No emergency
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    
    // MIP not completed
    await page.getByRole('button', { name: /No, I need to attend/i }).click();
    
    // Should show MIP info
    await expect(page.locator('#daMainQuestion')).toContainText('MIP Registration Required');
    await expect(page.locator('body')).toContainText('must attend MIP');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should continue to relationship
    await expect(page.locator('#daMainQuestion')).toContainText('relationship status');
  });

  test('Relationship affects available orders', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    
    // Test 1: Married - has divorce option
    await page.getByRole('button', { name: /^Married$/i }).click();
    await expect(page.locator('body')).toContainText('Divorce');
    await expect(page.locator('body')).toContainText('Property division');
    
    // Go back and test common-law
    await page.goBack();
    await page.waitForTimeout(500);
    
    // Test 2: Common-law - no divorce
    await page.getByRole('button', { name: /Common-law/i }).click();
    await expect(page.locator('body')).toContainText('Child custody');
    await expect(page.locator('body')).toContainText('Spousal support');
    // Divorce text should not be visible
    const divorceText = await page.locator('body').textContent();
    expect(divorceText).not.toMatch(/\bDivorce\b/);
    
    // Go back and test never together
    await page.goBack();
    await page.waitForTimeout(500);
    
    // Test 3: Never together - limited options
    await page.getByRole('button', { name: /Never lived together/i }).click();
    await expect(page.locator('body')).toContainText('Child custody');
    await expect(page.locator('body')).toContainText('Paternity/parentage');
    // Should not have spousal support or property
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).not.toMatch(/Spousal support/);
    expect(bodyText).not.toMatch(/Property division/);
  });

  test('Financial forms triggered by support orders', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    
    // Select financial orders using the input directly
    const childSupport = page.locator('input[type="checkbox"][alt*="Child support"]').first();
    await childSupport.check();
    
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should show financial information
    await expect(page.locator('#daMainQuestion')).toContainText('Financial Information');
    await expect(page.locator('body')).toContainText('claiming support');
    await expect(page.locator('body')).toContainText('own a business');
  });

  test('No financial orders skips financial section', async ({ page }) => {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    
    // Select only custody (non-financial)
    const custody = page.locator('input[type="checkbox"][alt*="Child custody"]').first();
    await custody.check();
    
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should skip financial and go to personal info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Personal Information');
  });
});

test.describe('Enhanced Intake - Party Information', () => {
  
  async function navigateToUserInfo(page: Page) {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip orders
  }

  test('Collects user and contact information', async ({ page }) => {
    await navigateToUserInfo(page);
    
    // Personal info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Personal Information');
    await page.fill('input[name*=".name.first"]', 'John');
    await page.fill('input[name*=".name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/1980');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Contact info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Contact Information');
    await page.fill('input[name*="address.address"]', '123 Main St');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should reach lawyer question
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have a lawyer');
  });

  test('Lawyer information collected when applicable', async ({ page }) => {
    await navigateToUserInfo(page);
    
    // Quick fill user info
    await page.fill('input[name*=".name.first"]', 'John');
    await page.fill('input[name*=".name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/1980');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    await page.fill('input[name*="address.address"]', '123 Main St');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Has lawyer
    await page.getByRole('button', { name: /^Yes$/i }).click();
    
    // Lawyer info
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Information');
    await page.fill('input[name*="name.text"]', 'Jane Attorney');
    await page.fill('input[name*="lsuc_number"]', 'L12345');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Lawyer contact
    await expect(page.locator('#daMainQuestion')).toContainText('Your Lawyer Contact');
    await page.fill('input[name*="address.address"]', '100 Bay St');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5J 2N8');
    await page.fill('input[name*="phone_number"]', '416-555-5555');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to other party
    await expect(page.locator('#daMainQuestion')).toContainText('Other Party Information');
  });
});

test.describe('Enhanced Intake - Children and Court', () => {
  
  async function navigateToCourtInfo(page: Page) {
    await startInterview(page);
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Quick fill required fields
    await page.fill('input[name*=".name.first"]', 'John');
    await page.fill('input[name*=".name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/1980');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    await page.fill('input[name*="address.address"]', '123 Main St');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M5H 2N2');
    await page.fill('input[name*="phone_number"]', '416-555-1234');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    await page.getByRole('button', { name: /^No$/i }).click(); // No lawyer
    
    await page.fill('input[name*="opposing_party.name.first"]', 'Jane');
    await page.fill('input[name*="opposing_party.name.last"]', 'Doe');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click(); // Skip contact
    await page.getByRole('button', { name: /^No$/i }).click(); // No opposing lawyer
  }

  test('Court information with existing file', async ({ page }) => {
    await navigateToCourtInfo(page);
    
    // Has existing file
    await page.locator('input[value="True"]').first().check();
    
    // Fill court details
    await page.selectOption('select[name*="court.name"]', 'Superior Court of Justice');
    await page.fill('input[name*="court.location"]', 'Toronto');
    await page.fill('input[name*="court.file_number"]', 'FL-2024-123');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should proceed to children
    await expect(page.locator('#daMainQuestion')).toContainText('Do you have children');
  });

  test('Children information collection', async ({ page }) => {
    await navigateToCourtInfo(page);
    
    // No court file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Has children
    await page.getByRole('button', { name: /^Yes$/i }).click();
    
    // Number of children
    await expect(page.locator('#daMainQuestion')).toContainText('Children Information');
    await page.fill('input[type="number"]', '1');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Child details
    await expect(page.locator('#daMainQuestion')).toContainText('Information for Child 1');
    await page.fill('input[name*="name.first"]', 'Bobby');
    await page.fill('input[name*="name.last"]', 'Smith');
    await page.fill('input[name*="birthdate"]', '01/01/2020');
    await page.selectOption('select[name*="lives_with"]', 'Me');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should reach summary
    await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Bobby Smith');
  });

  test('Complete minimal flow to summary', async ({ page }) => {
    await startInterview(page);
    
    // No emergency, MIP complete, married, no orders
    await page.getByRole('button', { name: /No, this is not an emergency/i }).click();
    await page.getByRole('button', { name: /Yes, I have my certificate/i }).click();
    await page.getByRole('button', { name: /^Married$/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // User info
    await page.fill('input[name*=".name.first"]', 'Test');
    await page.fill('input[name*=".name.last"]', 'User');
    await page.fill('input[name*="birthdate"]', '01/01/1990');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Contact
    await page.fill('input[name*="address.address"]', '1 Test St');
    await page.fill('input[name*="address.city"]', 'Toronto');
    await page.fill('input[name*="address.postal_code"]', 'M1M 1M1');
    await page.fill('input[name*="phone_number"]', '416-111-1111');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // No lawyer
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Other party
    await page.fill('input[name*="opposing_party.name.first"]', 'Other');
    await page.fill('input[name*="opposing_party.name.last"]', 'Party');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // No opposing lawyer
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // No court file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // No children
    await page.getByRole('button', { name: /^No$/i }).click();
    
    // Should reach summary
    await expect(page.locator('#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Test User');
    await expect(page.locator('body')).toContainText('Other Party');
    await expect(page.locator('body')).toContainText('Self-represented');
    await expect(page.locator('body')).toContainText('Children: None');
    await expect(page.locator('body')).toContainText('Recommended Forms');
  });
});