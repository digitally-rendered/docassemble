import { test, expect, Page } from '@playwright/test';

// Configuration
const BASE_URL = 'http://localhost';
const INTERVIEW_PATH = '/interview?i=docassemble.playground1:ontario-family-law/common_intake_enhanced_with_validation.yml';
const TIMEOUT = 60000;

test.describe('Common Intake Enhanced with Validation - Comprehensive Test Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}${INTERVIEW_PATH}`);
    await page.waitForLoadState('networkidle');
  });

  /**
   * Test 1: Interview loads without errors
   */
  test('interview loads without errors', async ({ page }) => {
    // Check that the introduction page loads
    await expect(page.locator('h1')).toContainText('Ontario Family Law Common Intake');
    
    // Verify no console errors
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Continue to emergency check
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify we reached emergency question
    await expect(page.locator('text=Is this an emergency situation?')).toBeVisible();
    
    // Check no errors occurred
    expect(consoleErrors).toHaveLength(0);
  });

  /**
   * Test 2: Divorce without children flow
   */
  test('divorce without children reaches summary', async ({ page }) => {
    // Introduction
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Emergency - No
    await page.getByRole('button', { name: 'No, this is not an emergency' }).click();
    await page.waitForLoadState('networkidle');
    
    // MIP Status - Completed
    await page.getByRole('button', { name: 'Yes, I have my certificate' }).click();
    await page.waitForLoadState('networkidle');
    
    // Relationship status - Married
    await page.getByRole('button', { name: 'Married' }).click();
    await page.waitForLoadState('networkidle');
    
    // Orders being sought - Select Divorce
    await page.locator('input[id*="seeking_divorce"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User information
    await fillUserInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User contact
    await fillUserContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Legal representation - No lawyer
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Other party information
    await fillOpposingPartyInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Other party contact
    await fillOpposingPartyContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Opposing lawyer - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Court information - No existing file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Children - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Children review
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify summary page
    await expect(page.locator('h1')).toContainText('Information Summary');
    await expect(page.locator('text=Divorce')).toBeVisible();
    await expect(page.locator('text=Relationship: Married')).toBeVisible();
  });

  /**
   * Test 3: Custody case with children using table interface
   */
  test('custody case with children table interface', async ({ page }) => {
    // Introduction
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Emergency - No
    await page.getByRole('button', { name: 'No, this is not an emergency' }).click();
    await page.waitForLoadState('networkidle');
    
    // MIP Status - Completed
    await page.getByRole('button', { name: 'Yes, I have my certificate' }).click();
    await page.waitForLoadState('networkidle');
    
    // Relationship status - Separated
    await page.getByRole('button', { name: 'Separated' }).click();
    await page.waitForLoadState('networkidle');
    
    // Orders being sought - Custody and Child Support
    await page.locator('input[id*="seeking_custody"]').check();
    await page.locator('input[id*="seeking_child_support"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Financial situation
    await page.locator('input[value="True"][id*="claiming_support"]').check();
    await page.locator('input[value="False"][id*="paying_support"]').check();
    await page.locator('input[value="False"][id*="owns_real_estate"]').check();
    await page.locator('input[value="False"][id*="owns_business"]').check();
    await page.locator('input[value="False"][id*="has_investments"]').check();
    await page.locator('input[value="False"][id*="has_pension"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User information
    await fillUserInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User contact
    await fillUserContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Legal representation - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Other party information
    await fillOpposingPartyInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Other party contact
    await fillOpposingPartyContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Opposing lawyer - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Court information - Has existing file
    await page.locator('input[value="True"]').first().check();
    await page.selectOption('select[id*="court_name"]', 'Family Court Branch');
    await page.fill('input[id*="court_location"]', 'Toronto');
    await page.fill('input[id*="court_file_number"]', 'FC-2024-12345');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Children - Yes
    await page.getByRole('button', { name: 'Yes' }).click();
    await page.waitForLoadState('networkidle');
    
    // Children review screen - Add first child
    await page.getByRole('button', { name: 'Add a child' }).click();
    await page.waitForLoadState('networkidle');
    
    // Fill first child information
    await page.fill('input[id*="first_name"]', 'Emma');
    await page.fill('input[id*="last_name"]', 'Johnson');
    await page.fill('input[type="date"]', '2015-03-15');
    await page.selectOption('select[id*="lives_with"]', 'Both (shared)');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify child appears in table
    await expect(page.locator('text=Emma Johnson')).toBeVisible();
    await expect(page.locator('text=2015-03-15')).toBeVisible();
    await expect(page.locator('text=Both (shared)')).toBeVisible();
    
    // Add second child
    await page.getByRole('button', { name: 'Add a child' }).click();
    await page.waitForLoadState('networkidle');
    
    // Fill second child information
    await page.fill('input[id*="first_name"]', 'Liam');
    await page.fill('input[id*="last_name"]', 'Johnson');
    await page.fill('input[type="date"]', '2018-07-22');
    await page.selectOption('select[id*="lives_with"]', 'Me');
    await page.fill('textarea[id*="special_needs"]', 'Asthma - requires daily inhaler');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify both children in table
    await expect(page.locator('text=Emma Johnson')).toBeVisible();
    await expect(page.locator('text=Liam Johnson')).toBeVisible();
    
    // Test edit functionality - Edit first child
    await page.locator('button:has-text("Edit")').first().click();
    await page.waitForLoadState('networkidle');
    
    // Modify first child
    await page.fill('input[id*="middle_name"]', 'Rose');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Continue to summary
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify summary includes children
    await expect(page.locator('h1')).toContainText('Information Summary');
    await expect(page.locator('text=Number of Children: 2')).toBeVisible();
    await expect(page.locator('text=Emma Johnson')).toBeVisible();
    await expect(page.locator('text=Liam Johnson')).toBeVisible();
  });

  /**
   * Test 4: Emergency restraining order flow
   */
  test('emergency restraining order flow', async ({ page }) => {
    // Introduction
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Emergency - Yes
    await page.getByRole('button', { name: 'Yes, this is an emergency' }).click();
    await page.waitForLoadState('networkidle');
    
    // Emergency warning
    await expect(page.locator('text=URGENT: Emergency Filing Required')).toBeVisible();
    await expect(page.locator('text=Form 8 - Application')).toBeVisible();
    await expect(page.locator('text=Form 25F - Restraining Order')).toBeVisible();
    await page.getByRole('button', { name: 'Continue (I understand the urgency)' }).click();
    await page.waitForLoadState('networkidle');
    
    // MIP Status - Emergency defer
    await page.getByRole('button', { name: 'Emergency - will complete after' }).click();
    await page.waitForLoadState('networkidle');
    
    // MIP information for emergency
    await expect(page.locator('text=you may file emergency motions before attending MIP')).toBeVisible();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Relationship status - Common-law
    await page.getByRole('button', { name: 'Common-law partners' }).click();
    await page.waitForLoadState('networkidle');
    
    // Orders being sought - Restraining order and exclusive possession
    await page.locator('input[id*="seeking_restraining_order"]').check();
    await page.locator('input[id*="seeking_exclusive_possession"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Financial situation
    await page.locator('input[value="False"][id*="claiming_support"]').check();
    await page.locator('input[value="False"][id*="paying_support"]').check();
    await page.locator('input[value="True"][id*="owns_real_estate"]').check();
    await page.locator('input[value="False"][id*="owns_business"]').check();
    await page.locator('input[value="False"][id*="has_investments"]').check();
    await page.locator('input[value="False"][id*="has_pension"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Continue through rest of flow quickly
    await fillUserInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    await fillUserContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Has lawyer - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    await fillOpposingPartyInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    await fillOpposingPartyContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Opposing lawyer - Unknown
    await page.getByRole('button', { name: 'Unknown' }).click();
    await page.waitForLoadState('networkidle');
    
    // Court information - No existing file
    await page.locator('input[value="False"]').first().check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Children - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Children review
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify summary
    await expect(page.locator('h1')).toContainText('Information Summary');
    await expect(page.locator('text=Emergency: Yes - URGENT')).toBeVisible();
    await expect(page.locator('text=Restraining order')).toBeVisible();
    await expect(page.locator('text=Exclusive possession')).toBeVisible();
  });

  /**
   * Test 5: Property division with lawyers
   */
  test('property division with lawyers flow', async ({ page }) => {
    // Introduction
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Emergency - No
    await page.getByRole('button', { name: 'No, this is not an emergency' }).click();
    await page.waitForLoadState('networkidle');
    
    // MIP Status - Completed
    await page.getByRole('button', { name: 'Yes, I have my certificate' }).click();
    await page.waitForLoadState('networkidle');
    
    // Relationship status - Married
    await page.getByRole('button', { name: 'Married' }).click();
    await page.waitForLoadState('networkidle');
    
    // Orders being sought - Property division and spousal support
    await page.locator('input[id*="seeking_property"]').check();
    await page.locator('input[id*="seeking_spousal_support"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Financial situation
    await page.locator('input[value="False"][id*="claiming_support"]').check();
    await page.locator('input[value="False"][id*="paying_support"]').check();
    await page.locator('input[value="True"][id*="owns_real_estate"]').check();
    await page.locator('input[value="False"][id*="owns_business"]').check();
    await page.locator('input[value="True"][id*="has_investments"]').check();
    await page.locator('input[value="True"][id*="has_pension"]').check();
    await page.fill('input[id*="total_assets"]', '750000');
    await page.fill('input[id*="total_debts"]', '200000');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User information
    await fillUserInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User contact
    await fillUserContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Legal representation - Yes
    await page.getByRole('button', { name: 'Yes' }).click();
    await page.waitForLoadState('networkidle');
    
    // User lawyer information
    await page.fill('input[id*="user_lawyer_name_text"]', 'Sarah Thompson');
    await page.fill('input[id*="firm_name"]', 'Thompson & Associates');
    await page.fill('input[id*="lsuc_number"]', '12345A');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // User lawyer contact
    await page.fill('input[id*="address"][id*="address"]', '123 Bay Street');
    await page.fill('input[id*="unit"]', 'Suite 500');
    await page.fill('input[id*="city"]', 'Toronto');
    await page.fill('input[id*="postal_code"]', 'M5H 2Y4');
    await page.fill('input[id*="phone_number"]', '416-555-1234');
    await page.fill('input[id*="extension"]', '101');
    await page.fill('input[id*="email"]', 'sarah@thompsonlaw.ca');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Other party information
    await fillOpposingPartyInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Other party contact
    await fillOpposingPartyContact(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Opposing lawyer - Yes
    await page.getByRole('button', { name: 'Yes' }).click();
    await page.waitForLoadState('networkidle');
    
    // Opposing lawyer information
    await page.fill('input[id*="opposing_lawyer_name_text"]', 'Michael Chen');
    await page.fill('input[id*="firm_name"]', 'Chen Legal Services');
    await page.fill('input[id*="lsuc_number"]', '67890');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Opposing lawyer contact
    await page.fill('input[id*="address"][id*="address"]', '456 King Street West');
    await page.fill('input[id*="city"]', 'Toronto');
    await page.fill('input[id*="postal_code"]', 'M5V 3A8');
    await page.fill('input[id*="phone_number"]', '416-555-5678');
    await page.fill('input[id*="email"]', 'mchen@chenlegal.ca');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Court information - Existing file
    await page.locator('input[value="True"]').first().check();
    await page.selectOption('select[id*="court_name"]', 'Superior Court of Justice');
    await page.fill('input[id*="court_location"]', 'Toronto');
    await page.fill('input[id*="court_file_number"]', 'SC-2024-00789');
    await page.fill('input[type="date"][id*="date_started"]', '2024-01-15');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Children - No
    await page.getByRole('button', { name: 'No' }).click();
    await page.waitForLoadState('networkidle');
    
    // Children review
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify summary
    await expect(page.locator('h1')).toContainText('Information Summary');
    await expect(page.locator('text=Property division')).toBeVisible();
    await expect(page.locator('text=Spousal support')).toBeVisible();
    await expect(page.locator('text=Your Lawyer: Sarah Thompson')).toBeVisible();
    await expect(page.locator('text=Their Lawyer: Michael Chen')).toBeVisible();
  });

  /**
   * Test 6: Conditional field visibility
   */
  test('conditional fields display correctly', async ({ page }) => {
    // Navigate to orders being sought
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'No, this is not an emergency' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Yes, I have my certificate' }).click();
    await page.waitForLoadState('networkidle');
    
    // Test 1: Divorce only shows for married
    await page.getByRole('button', { name: 'Married' }).click();
    await page.waitForLoadState('networkidle');
    
    // Divorce should be visible
    await expect(page.locator('label:has-text("Divorce")')).toBeVisible();
    
    // Go back and select never together
    await page.goBack();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Never lived together' }).click();
    await page.waitForLoadState('networkidle');
    
    // Divorce should NOT be visible
    await expect(page.locator('label:has-text("Divorce")')).not.toBeVisible();
    
    // Paternity should be visible for never together
    await expect(page.locator('label:has-text("Paternity/parentage declaration")')).toBeVisible();
    
    // Spousal support should NOT be visible
    await expect(page.locator('label:has-text("Spousal support")')).not.toBeVisible();
    
    // Property division should NOT be visible
    await expect(page.locator('label:has-text("Property division")')).not.toBeVisible();
  });

  /**
   * Test 7: Validation errors
   */
  test('field validation works correctly', async ({ page }) => {
    // Navigate to user contact info
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'No, this is not an emergency' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Yes, I have my certificate' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Married' }).click();
    await page.waitForLoadState('networkidle');
    await page.locator('input[id*="seeking_divorce"]').check();
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Fill user info
    await fillUserInfo(page);
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Test postal code validation
    await page.fill('input[id*="postal_code"]', 'INVALID');
    await page.fill('input[id*="address"][id*="address"]', '123 Test Street');
    await page.fill('input[id*="city"]', 'Toronto');
    await page.fill('input[id*="phone_number"]', '416-555-1234');
    await page.getByRole('button', { name: /Continue/i }).click();
    
    // Should see validation error
    await expect(page.locator('text=Please enter a valid Canadian postal code')).toBeVisible();
    
    // Fix postal code
    await page.fill('input[id*="postal_code"]', 'M5V 3A8');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Should proceed successfully
    await expect(page.locator('text=Do you have a lawyer?')).toBeVisible();
  });

  /**
   * Test 8: Children table delete functionality
   */
  test('children table delete works correctly', async ({ page }) => {
    // Navigate to children section quickly
    await navigateToChildren(page);
    
    // Say yes to children
    await page.getByRole('button', { name: 'Yes' }).click();
    await page.waitForLoadState('networkidle');
    
    // Add first child
    await page.getByRole('button', { name: 'Add a child' }).click();
    await page.waitForLoadState('networkidle');
    await page.fill('input[id*="first_name"]', 'Child');
    await page.fill('input[id*="last_name"]', 'One');
    await page.fill('input[type="date"]', '2010-01-01');
    await page.selectOption('select[id*="lives_with"]', 'Me');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Add second child
    await page.getByRole('button', { name: 'Add a child' }).click();
    await page.waitForLoadState('networkidle');
    await page.fill('input[id*="first_name"]', 'Child');
    await page.fill('input[id*="last_name"]', 'Two');
    await page.fill('input[type="date"]', '2012-01-01');
    await page.selectOption('select[id*="lives_with"]', 'Me');
    await page.getByRole('button', { name: /Continue/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Verify both children present
    await expect(page.locator('text=Child One')).toBeVisible();
    await expect(page.locator('text=Child Two')).toBeVisible();
    
    // Delete first child
    await page.locator('button:has-text("Delete")').first().click();
    await page.waitForLoadState('networkidle');
    
    // Verify only second child remains
    await expect(page.locator('text=Child One')).not.toBeVisible();
    await expect(page.locator('text=Child Two')).toBeVisible();
  });
});

/**
 * Helper Functions
 */

async function fillUserInfo(page: Page) {
  await page.fill('input[id*="first"][id*="name"]', 'John');
  await page.fill('input[id*="last"][id*="name"]', 'Smith');
  await page.fill('input[type="date"][id*="birthdate"]', '1980-01-15');
}

async function fillUserContact(page: Page) {
  await page.fill('input[id*="address"][id*="address"]', '123 Main Street');
  await page.fill('input[id*="city"]', 'Toronto');
  await page.fill('input[id*="postal_code"]', 'M5V 3A8');
  await page.fill('input[id*="phone_number"]', '416-555-1234');
  await page.fill('input[id*="email"]', 'john.smith@example.com');
}

async function fillOpposingPartyInfo(page: Page) {
  await page.fill('input[id*="first"][id*="name"]', 'Jane');
  await page.fill('input[id*="last"][id*="name"]', 'Doe');
  await page.fill('input[type="date"][id*="birthdate"]', '1982-05-20');
}

async function fillOpposingPartyContact(page: Page) {
  await page.fill('input[id*="address"][id*="address"]', '456 Queen Street');
  await page.fill('input[id*="city"]', 'Toronto');
  await page.fill('input[id*="postal_code"]', 'M5H 2N2');
  await page.fill('input[id*="phone_number"]', '416-555-5678');
}

async function navigateToChildren(page: Page) {
  // Quick navigation to children section
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'No, this is not an emergency' }).click();
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Yes, I have my certificate' }).click();
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Separated' }).click();
  await page.waitForLoadState('networkidle');
  await page.locator('input[id*="seeking_custody"]').check();
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
  
  // Fill minimum required info
  await fillUserInfo(page);
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
  await fillUserContact(page);
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'No' }).click();
  await page.waitForLoadState('networkidle');
  await fillOpposingPartyInfo(page);
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
  await fillOpposingPartyContact(page);
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'No' }).click();
  await page.waitForLoadState('networkidle');
  await page.locator('input[value="False"]').first().check();
  await page.getByRole('button', { name: /Continue/i }).click();
  await page.waitForLoadState('networkidle');
}