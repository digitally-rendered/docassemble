import { test, expect } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test.describe('All Interview Flows Complete', () => {
  test('divorce without children reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    
    // Emergency check - No
    await page.click('button:has-text("No, this is not an emergency")');
    
    // MIP Status - Completed
    await page.click('button:has-text("Yes, I have my certificate")');
    
    // Relationship status - Married
    await page.click('button:has-text("Married")');
    
    // Orders - Divorce (use the checkbox directly, not by role)
    await page.locator('input[type="checkbox"][name="seeking_divorce"]').click();
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('John');
    await page.getByLabel('Last Name').fill('Smith');
    await page.getByLabel('Date of Birth').fill('1980-01-15');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('123 Main St');
    await page.getByLabel('City').fill('Toronto');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('M5V 3A8');
    await page.getByLabel('Phone Number').fill('4165551234');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party info
    await page.getByLabel('First Name').fill('Jane');
    await page.getByLabel('Last Name').fill('Doe');
    await page.click('button:has-text("Continue")');
    
    // Other party contact - skip
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing file
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    
    // Children - No
    await page.click('button:has-text("No")');
    
    // Children info screen
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await page.click('button:has-text("Continue")');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Emergency: No');
    await expect(page.locator('body')).toContainText('Relationship: Married');
    await expect(page.locator('body')).toContainText('Divorce');
    await expect(page.locator('body')).toContainText('Children: None');
    await expect(page.locator('body')).toContainText('Form 8A - Application (Divorce)');
    
    console.log('✅ Divorce without children flow COMPLETED to summary');
  });

  test('custody with children reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Quick navigation through initial screens
    await page.click('button:has-text("Continue")'); // Intro
    await page.click('button:has-text("No, this is not an emergency")');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.click('button:has-text("Separated")');
    
    // Orders - Custody and support
    await page.locator('input[name="seeking_custody"]').click();
    await page.locator('input[name="seeking_child_support"]').click();
    await page.click('button:has-text("Continue")');
    
    // Financial situation
    await page.locator('input[type="radio"][value="True"]').first().click(); // Claiming support
    await page.locator('input[type="radio"][value="False"]').nth(1).click(); // Not paying
    await page.locator('input[type="radio"][value="False"]').nth(2).click(); // No real estate
    await page.locator('input[type="radio"][value="False"]').nth(3).click(); // No business
    await page.locator('input[type="radio"][value="False"]').nth(4).click(); // No investments
    await page.locator('input[type="radio"][value="False"]').nth(5).click(); // No pension
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('Mary');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('1985-03-20');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('456 Queen St');
    await page.getByLabel('City').fill('Ottawa');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('K1A 0A1');
    await page.getByLabel('Phone Number').fill('6135551234');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party
    await page.getByLabel('First Name').fill('Robert');
    await page.getByLabel('Last Name').fill('Jones');
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")'); // Contact
    
    // Other party lawyer - Unknown
    await page.click('button:has-text("Unknown")');
    
    // Court info - Existing file
    await page.locator('input[type="radio"][value="True"]').first().click();
    await page.selectOption('select[name*="court.name"]', 'Superior Court of Justice');
    await page.getByLabel('Court Location').fill('Ottawa');
    await page.getByLabel('Court File Number').fill('FC-2024-1234');
    await page.click('button:has-text("Continue")');
    
    // Children - Yes
    await page.click('button:has-text("Yes")');
    
    // Children table screen - add one child
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await page.locator('a:has-text("Add a child")').click();
    
    // Add child info
    await page.getByLabel('First Name').fill('Emma');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('2015-06-15');
    await page.selectOption('select[name*="lives_with"]', 'Both (shared)');
    await page.click('button:has-text("Continue")');
    
    // Back to table, continue to summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('table')).toContainText('Emma Jones');
    await page.click('button:has-text("Continue")');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Relationship: Separated');
    await expect(page.locator('body')).toContainText('Child custody/access');
    await expect(page.locator('body')).toContainText('Child support');
    await expect(page.locator('body')).toContainText('Number of Children: 1');
    await expect(page.locator('body')).toContainText('Emma Jones');
    await expect(page.locator('body')).toContainText('Form 8 - Application (General)');
    await expect(page.locator('body')).toContainText('Form 13 - Financial Statement (Support)');
    
    console.log('✅ Custody with children flow COMPLETED to summary');
  });

  test('emergency restraining order reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    
    // Emergency - YES
    await page.click('button:has-text("Yes, this is an emergency")');
    
    // Emergency warning
    await page.click('button:has-text("Continue (I understand the urgency)")');
    
    // MIP Status - Emergency defer
    await page.click('button:has-text("Emergency - will complete after")');
    
    // MIP info
    await page.click('button:has-text("Continue")');
    
    // Relationship - Never together
    await page.click('button:has-text("Never lived together")');
    
    // Orders - Restraining order only
    await page.locator('input[name="seeking_restraining_order"]').click();
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('Sarah');
    await page.getByLabel('Last Name').fill('Williams');
    await page.getByLabel('Date of Birth').fill('1990-07-10');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('789 King St');
    await page.getByLabel('City').fill('London');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('N6A 1E1');
    await page.getByLabel('Phone Number').fill('5195551234');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party
    await page.getByLabel('First Name').fill('Mike');
    await page.getByLabel('Last Name').fill('Brown');
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")'); // Contact
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.click('button:has-text("Continue")');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Emergency: Yes - URGENT');
    await expect(page.locator('body')).toContainText('URGENT - File These Today');
    await expect(page.locator('body')).toContainText('Form 8 - Application');
    await expect(page.locator('body')).toContainText('Form 14B - Motion');
    await expect(page.locator('body')).toContainText('Form 25F - Restraining Order');
    
    console.log('✅ Emergency restraining order flow COMPLETED to summary');
  });

  test('property division with lawyer reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Quick navigation
    await page.click('button:has-text("Continue")'); // Intro
    await page.click('button:has-text("No, this is not an emergency")');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.click('button:has-text("Common-law partners")');
    
    // Orders - Property and spousal support
    await page.locator('input[name="seeking_property"]').click();
    await page.locator('input[name="seeking_spousal_support"]').click();
    await page.click('button:has-text("Continue")');
    
    // Financial situation
    await page.locator('input[type="radio"][value="False"]').first().click(); // Not claiming
    await page.locator('input[type="radio"][value="True"]').nth(1).click(); // Paying support
    await page.locator('input[type="radio"][value="True"]').nth(2).click(); // Has real estate
    await page.locator('input[type="radio"][value="False"]').nth(3).click(); // No business
    await page.locator('input[type="radio"][value="True"]').nth(4).click(); // Has investments
    await page.locator('input[type="radio"][value="True"]').nth(5).click(); // Has pension
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('David');
    await page.getByLabel('Last Name').fill('Chen');
    await page.getByLabel('Date of Birth').fill('1975-11-30');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('999 Bay St');
    await page.getByLabel('City').fill('Toronto');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('M5S 1A1');
    await page.getByLabel('Phone Number').fill('4165559999');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - Yes
    await page.click('button:has-text("Yes")');
    
    // Lawyer info
    await page.getByLabel('Lawyer Name').fill('Jennifer Law');
    await page.getByLabel('Law Society Number').fill('54321B');
    await page.click('button:has-text("Continue")');
    
    // Lawyer contact
    await page.getByLabel('Street Address').fill('200 University Ave');
    await page.getByLabel('City').fill('Toronto');
    await page.getByLabel('Postal Code').fill('M5H 3C6');
    await page.getByLabel('Phone').fill('4165556789');
    await page.click('button:has-text("Continue")');
    
    // Other party
    await page.getByLabel('First Name').fill('Lisa');
    await page.getByLabel('Last Name').fill('Wong');
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")'); // Contact
    
    // Other party lawyer - Yes
    await page.click('button:has-text("Yes")');
    
    // Other party lawyer info
    await page.getByLabel('Lawyer Name').fill('Michael Justice');
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer contact
    await page.click('button:has-text("Continue")');
    
    // Court info - No existing
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.click('button:has-text("Continue")');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Relationship: Common Law');
    await expect(page.locator('body')).toContainText('Property division');
    await expect(page.locator('body')).toContainText('Spousal support');
    await expect(page.locator('body')).toContainText('Your Lawyer: Jennifer Law');
    await expect(page.locator('body')).toContainText('Their Lawyer: Michael Justice');
    await expect(page.locator('body')).toContainText('Form 13 - Financial Statement (Support)');
    await expect(page.locator('body')).toContainText('Form 13.1 - Financial Statement (Property)');
    
    console.log('✅ Property division with lawyers flow COMPLETED to summary');
  });
});