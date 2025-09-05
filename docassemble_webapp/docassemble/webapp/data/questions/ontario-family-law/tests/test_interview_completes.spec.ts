import { test, expect } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test.describe('Interview Completion Tests', () => {
  test('simple divorce no children completes to summary', async ({ page }) => {
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
    
    // Orders - Just divorce (should be visible for married status)
    await page.getByRole('checkbox', { name: 'Divorce' }).click();
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('John');
    await page.getByLabel('Last Name').fill('Smith');
    await page.getByLabel('Date of Birth').fill('1980-01-15');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('123 Main St');
    await page.getByLabel('City').fill('Toronto');
    await page.getByLabel('Province').selectOption('Ontario');
    await page.getByLabel('Postal Code').fill('M5V 3A8');
    await page.getByLabel('Phone Number').fill('4165551234');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party info
    await page.getByLabel('First Name').fill('Jane');
    await page.getByLabel('Last Name').fill('Doe');
    await page.click('button:has-text("Continue")');
    
    // Other party contact - skip optional
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing file
    await page.getByRole('radio', { name: 'No' }).click();
    await page.click('button:has-text("Continue")');
    
    // Do you have children together? - NO
    await expect(page.locator('h1#daMainQuestion')).toContainText('Do you have any children together?');
    await page.click('button:has-text("No")');
    
    // Should see Children Information screen saying no children
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('body')).toContainText('You indicated you do not have children together');
    await page.click('button:has-text("Continue")');
    
    // Should reach the summary page
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Case Type');
    await expect(page.locator('body')).toContainText('Party Information');
    await expect(page.locator('body')).toContainText('Recommended Forms');
    
    console.log('✓ Simple divorce flow completed successfully!');
  });

  test('custody case with children completes to summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    
    // Emergency check - No
    await page.click('button:has-text("No, this is not an emergency")');
    
    // MIP Status - Completed
    await page.click('button:has-text("Yes, I have my certificate")');
    
    // Relationship status - Separated
    await page.click('button:has-text("Separated")');
    
    // Orders - Custody and support
    await page.getByRole('checkbox', { name: 'Child custody and/or access' }).click();
    await page.getByRole('checkbox', { name: 'Child support' }).click();
    await page.click('button:has-text("Continue")');
    
    // Financial situation (because seeking support)
    await page.getByRole('radio', { name: 'Yes' }).first().click(); // Claiming support
    await page.getByRole('radio', { name: 'No' }).nth(1).click(); // Not paying support
    await page.getByRole('radio', { name: 'No' }).nth(2).click(); // No real estate
    await page.getByRole('radio', { name: 'No' }).nth(3).click(); // No business
    await page.getByRole('radio', { name: 'No' }).nth(4).click(); // No investments
    await page.getByRole('radio', { name: 'No' }).nth(5).click(); // No pension
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('Mary');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('1985-03-20');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('456 Queen St');
    await page.getByLabel('City').fill('Ottawa');
    await page.getByLabel('Province').selectOption('Ontario');
    await page.getByLabel('Postal Code').fill('K1A 0A1');
    await page.getByLabel('Phone Number').fill('6135551234');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party info
    await page.getByLabel('First Name').fill('Robert');
    await page.getByLabel('Last Name').fill('Jones');
    await page.click('button:has-text("Continue")');
    
    // Other party contact
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer - Unknown
    await page.click('button:has-text("Unknown")');
    
    // Court info - Yes existing file
    await page.getByRole('radio', { name: 'Yes' }).click();
    await page.getByLabel('Court Name').selectOption('Superior Court of Justice');
    await page.getByLabel('Court Location').fill('Ottawa');
    await page.getByLabel('Court File Number').fill('FC-2024-1234');
    await page.click('button:has-text("Continue")');
    
    // Do you have children together? - YES
    await expect(page.locator('h1#daMainQuestion')).toContainText('Do you have any children together?');
    await page.click('button:has-text("Yes")');
    
    // Should see Children Information table screen
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    
    // Add first child
    await page.locator('a:has-text("Add a child")').click();
    await expect(page.locator('h1#daMainQuestion')).toContainText('Add Child Information');
    await page.getByLabel('First Name').fill('Emma');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('2015-06-15');
    await page.getByLabel('Lives with').selectOption('Both (shared)');
    await page.click('button:has-text("Continue")');
    
    // Back to table, add second child
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await page.locator('a:has-text("Add a child")').click();
    await page.getByLabel('First Name').fill('Liam');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('2018-09-20');
    await page.getByLabel('Lives with').selectOption('Me');
    await page.click('button:has-text("Continue")');
    
    // Continue from children table to summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await page.click('button:has-text("Continue")');
    
    // Should reach the summary page
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Case Type');
    await expect(page.locator('body')).toContainText('Party Information');
    await expect(page.locator('body')).toContainText('Number of Children: 2');
    await expect(page.locator('body')).toContainText('Emma Jones');
    await expect(page.locator('body')).toContainText('Liam Jones');
    await expect(page.locator('body')).toContainText('Recommended Forms');
    
    console.log('✓ Custody case with children completed successfully!');
  });

  test('emergency flow completes to summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    
    // Emergency check - YES
    await page.click('button:has-text("Yes, this is an emergency")');
    
    // Emergency warning - acknowledge
    await page.click('button:has-text("Continue (I understand the urgency)")');
    
    // MIP Status - Emergency defer
    await page.click('button:has-text("Emergency - will complete after")');
    
    // MIP information screen
    await page.click('button:has-text("Continue")');
    
    // Relationship status - Common law
    await page.click('button:has-text("Common-law partners")');
    
    // Orders - Restraining order and custody
    await page.getByRole('checkbox', { name: 'Restraining order' }).click();
    await page.getByRole('checkbox', { name: 'Child custody and/or access' }).click();
    await page.click('button:has-text("Continue")');
    
    // Personal info
    await page.getByLabel('First Name').fill('Sarah');
    await page.getByLabel('Last Name').fill('Williams');
    await page.getByLabel('Date of Birth').fill('1990-07-10');
    await page.click('button:has-text("Continue")');
    
    // Contact info
    await page.getByLabel('Street Address').fill('789 King St');
    await page.getByLabel('City').fill('London');
    await page.getByLabel('Province').selectOption('Ontario');
    await page.getByLabel('Postal Code').fill('N6A 1E1');
    await page.getByLabel('Phone Number').fill('5195551234');
    await page.click('button:has-text("Continue")');
    
    // Legal rep - Yes
    await page.click('button:has-text("Yes")');
    
    // Lawyer info
    await page.getByLabel('Lawyer Name').fill('James Miller');
    await page.getByLabel('Law Society Number').fill('12345A');
    await page.click('button:has-text("Continue")');
    
    // Lawyer contact
    await page.getByLabel('Street Address').fill('100 Bay St');
    await page.getByLabel('City').fill('London');
    await page.getByLabel('Postal Code').fill('N6A 2B2');
    await page.getByLabel('Phone').fill('5195555678');
    await page.click('button:has-text("Continue")');
    
    // Other party info
    await page.getByLabel('First Name').fill('Mike');
    await page.getByLabel('Last Name').fill('Brown');
    await page.click('button:has-text("Continue")');
    
    // Other party contact
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing file
    await page.getByRole('radio', { name: 'No' }).click();
    await page.click('button:has-text("Continue")');
    
    // Children - No
    await page.click('button:has-text("No")');
    
    // Children info screen
    await page.click('button:has-text("Continue")');
    
    // Should reach the summary page
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Emergency: Yes - URGENT');
    await expect(page.locator('body')).toContainText('URGENT - File These Today');
    await expect(page.locator('body')).toContainText('Form 25F - Restraining Order');
    
    console.log('✓ Emergency flow completed successfully!');
  });
});