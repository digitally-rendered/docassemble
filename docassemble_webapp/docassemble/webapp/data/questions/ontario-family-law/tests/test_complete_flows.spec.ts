import { test, expect } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test.describe('Complete Interview Flows', () => {
  test('divorce flow completes to summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('Starting divorce flow test...');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    console.log('✓ Introduction completed');
    
    // Emergency - No
    await page.click('button:has-text("No, this is not an emergency")');
    console.log('✓ Emergency assessment completed');
    
    // MIP - Completed
    await page.click('button:has-text("Yes, I have my certificate")');
    console.log('✓ MIP status completed');
    
    // Relationship - Married
    await page.click('button:has-text("Married")');
    console.log('✓ Relationship status completed');
    
    // Orders - Find and click divorce checkbox (use text-based approach)
    await page.locator('text=Divorce').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Orders selection completed');
    
    // Personal info
    await page.getByLabel('First Name').fill('John');
    await page.getByLabel('Last Name').fill('Smith');
    await page.getByLabel('Date of Birth').fill('1980-01-15');
    await page.click('button:has-text("Continue")');
    console.log('✓ Personal info completed');
    
    // Contact info
    await page.getByLabel('Street Address').fill('123 Main St');
    await page.getByLabel('City').fill('Toronto');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('M5V 3A8');
    await page.getByLabel('Phone Number').fill('4165551234');
    await page.click('button:has-text("Continue")');
    console.log('✓ Contact info completed');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    console.log('✓ Legal representation completed');
    
    // Other party info
    await page.getByLabel('First Name').fill('Jane');
    await page.getByLabel('Last Name').fill('Doe');
    await page.click('button:has-text("Continue")');
    console.log('✓ Other party info completed');
    
    // Other party contact
    await page.click('button:has-text("Continue")');
    console.log('✓ Other party contact completed');
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    console.log('✓ Other party lawyer completed');
    
    // Court info - No existing file
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Court info completed');
    
    // Children - No
    await page.click('button:has-text("No")');
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await page.click('button:has-text("Continue")');
    console.log('✓ Children section completed - NO "How many children?" prompt!');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    console.log('✓ REACHED SUMMARY PAGE!');
    
    // Verify summary content
    await expect(page.locator('body')).toContainText('Emergency: No');
    await expect(page.locator('body')).toContainText('Relationship: Married');
    await expect(page.locator('body')).toContainText('Children: None');
    console.log('✅ Divorce flow COMPLETED successfully to summary page!');
  });

  test('custody with children flow completes to summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('Starting custody with children flow test...');
    
    // Quick navigation through initial screens
    await page.click('button:has-text("Continue")'); // Intro
    await page.click('button:has-text("No, this is not an emergency")');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.click('button:has-text("Separated")');
    
    // Orders - Custody and support
    await page.locator('text=Child custody').first().click();
    await page.locator('text=Child support').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Orders with custody and support selected');
    
    // Financial situation (appears because we're seeking support)
    await page.locator('input[type="radio"][value="True"]').first().click(); // Claiming support
    await page.locator('input[type="radio"][value="False"]').nth(1).click(); // Not paying
    await page.locator('input[type="radio"][value="False"]').nth(2).click(); // No real estate
    await page.locator('input[type="radio"][value="False"]').nth(3).click(); // No business
    await page.locator('input[type="radio"][value="False"]').nth(4).click(); // No investments
    await page.locator('input[type="radio"][value="False"]').nth(5).click(); // No pension
    await page.click('button:has-text("Continue")');
    console.log('✓ Financial situation completed');
    
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
    
    // Court info - No existing
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ All preliminary info completed');
    
    // Children - YES (This is the key test)
    await page.click('button:has-text("Yes")');
    
    // Should see Children Information table screen (NOT "How many children?")
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    console.log('✓ Children Information table screen appeared - NO number prompt!');
    
    // Add a child using the table interface
    await page.locator('a:has-text("Add a child")').click();
    console.log('✓ Clicked Add a child button');
    
    // Fill child info
    await expect(page.locator('h1#daMainQuestion')).toContainText('Add Child Information');
    await page.getByLabel('First Name').fill('Emma');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('2015-06-15');
    await page.selectOption('select[name*="lives_with"]', 'Both (shared)');
    await page.click('button:has-text("Continue")');
    console.log('✓ Child information added');
    
    // Back to table screen with child listed
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('table')).toContainText('Emma Jones');
    await page.click('button:has-text("Continue")');
    console.log('✓ Children table interface working correctly');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Number of Children: 1');
    await expect(page.locator('body')).toContainText('Emma Jones');
    console.log('✅ Custody with children flow COMPLETED successfully to summary page!');
  });

  test('emergency flow completes to summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('Starting emergency flow test...');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    
    // Emergency - YES
    await page.click('button:has-text("Yes, this is an emergency")');
    await page.click('button:has-text("Continue (I understand the urgency)")');
    console.log('✓ Emergency assessment completed');
    
    // MIP - Emergency defer
    await page.click('button:has-text("Emergency - will complete after")');
    await page.click('button:has-text("Continue")');
    console.log('✓ MIP emergency defer completed');
    
    // Relationship - Never together
    await page.click('button:has-text("Never lived together")');
    
    // Orders - Restraining order
    await page.locator('text=Restraining order').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Emergency orders selected');
    
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
    console.log('✓ All sections completed');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Emergency: Yes - URGENT');
    await expect(page.locator('body')).toContainText('URGENT - File These Today');
    console.log('✅ Emergency flow COMPLETED successfully to summary page!');
  });
});