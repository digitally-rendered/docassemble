import { test, expect } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test.describe('All Interview Flows Complete to Summary', () => {
  test('simple flow - no divorce, no children - reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('🔄 Starting simple flow test...');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    console.log('✓ Introduction completed');
    
    // Emergency - No
    await page.click('button:has-text("No, this is not an emergency")');
    console.log('✓ Emergency assessment completed');
    
    // MIP - Completed
    await page.click('button:has-text("Yes, I have my certificate")');
    console.log('✓ MIP status completed');
    
    // Relationship - Separated (avoid married to skip divorce issues)
    await page.click('button:has-text("Separated")');
    console.log('✓ Relationship status completed');
    
    // Orders - Just custody (available for all relationships)
    await page.locator('label:has-text("Child custody")').click();
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
    await expect(page.locator('body')).toContainText('You indicated you do not have children together');
    await page.click('button:has-text("Continue")');
    console.log('✓ Children section completed - NO "How many children?" prompt seen!');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    console.log('🎉 REACHED SUMMARY PAGE!');
    
    // Verify summary content
    await expect(page.locator('body')).toContainText('Emergency: No');
    await expect(page.locator('body')).toContainText('Relationship: Separated');
    await expect(page.locator('body')).toContainText('Children: None');
    console.log('✅ SIMPLE FLOW COMPLETED SUCCESSFULLY!');
  });

  test('custody with table-based children - reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('🔄 Starting custody with children flow test...');
    
    // Quick navigation through initial screens
    await page.click('button:has-text("Continue")'); // Intro
    await page.click('button:has-text("No, this is not an emergency")');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.click('button:has-text("Common-law partners")'); // Relationship
    console.log('✓ Initial screens completed');
    
    // Orders - Custody and support
    await page.locator('label:has-text("Child custody")').click();
    await page.locator('label:has-text("Child support")').click();
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
    
    // Personal and contact info
    await page.getByLabel('First Name').fill('Mary');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('1985-03-20');
    await page.click('button:has-text("Continue")');
    
    await page.getByLabel('Street Address').fill('456 Queen St');
    await page.getByLabel('City').fill('Ottawa');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('K1A 0A1');
    await page.getByLabel('Phone Number').fill('6135551234');
    await page.click('button:has-text("Continue")');
    console.log('✓ Personal info completed');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party info
    await page.getByLabel('First Name').fill('Robert');
    await page.getByLabel('Last Name').fill('Jones');
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")'); // Contact skip
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ All preliminary info completed');
    
    // Children - YES (This is the key test of table interface)
    await page.click('button:has-text("Yes")');
    
    // Should see Children Information table screen (NOT "How many children?")
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('body')).toContainText('Click "Add a child" to add children');
    console.log('🎯 CONFIRMED: Table-based children interface - NO number prompt!');
    
    // Add first child using the table interface
    await page.locator('a:has-text("Add a child")').click();
    console.log('✓ Clicked Add a child button');
    
    // Fill first child info
    await expect(page.locator('h1#daMainQuestion')).toContainText('Add Child Information');
    await page.getByLabel('First Name').fill('Emma');
    await page.getByLabel('Last Name').fill('Jones');
    await page.getByLabel('Date of Birth').fill('2015-06-15');
    await page.selectOption('select[name*="lives_with"]', 'Both (shared)');
    await page.click('button:has-text("Continue")');
    console.log('✓ First child added');
    
    // Back to table screen - add second child
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('table')).toContainText('Emma Jones');
    await page.locator('a:has-text("Add a child")').click();
    
    // Fill second child info
    await page.getByLabel('First Name').fill('Liam');
    await page.getByLabel('Last Name').fill('Jones');  
    await page.getByLabel('Date of Birth').fill('2018-09-20');
    await page.selectOption('select[name*="lives_with"]', 'Me');
    await page.click('button:has-text("Continue")');
    console.log('✓ Second child added');
    
    // Verify both children in table and continue
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('table')).toContainText('Emma Jones');
    await expect(page.locator('table')).toContainText('Liam Jones');
    await page.click('button:has-text("Continue")');
    console.log('🎯 CONFIRMED: Table interface working with multiple children!');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Number of Children: 2');
    await expect(page.locator('body')).toContainText('Emma Jones');
    await expect(page.locator('body')).toContainText('Liam Jones');
    console.log('✅ CUSTODY WITH CHILDREN FLOW COMPLETED SUCCESSFULLY!');
  });

  test('emergency restraining order - reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('🔄 Starting emergency flow test...');
    
    // Introduction
    await page.click('button:has-text("Continue")');
    console.log('✓ Introduction completed');
    
    // Emergency - YES
    await page.click('button:has-text("Yes, this is an emergency")');
    await page.click('button:has-text("Continue (I understand the urgency)")');
    console.log('✓ Emergency declared and warning acknowledged');
    
    // MIP - Emergency defer
    await page.click('button:has-text("Emergency - will complete after")');
    
    // Check if MIP info screen appears
    const currentTitle = await page.locator('h1#daMainQuestion').textContent();
    if (currentTitle?.includes('MIP Registration') || currentTitle?.includes('Mandatory Information')) {
      await page.click('button:has-text("Continue")');
      console.log('✓ MIP info screen bypassed');
    }
    
    // Relationship - Never together
    await page.click('button:has-text("Never lived together")');
    console.log('✓ Relationship status completed');
    
    // Orders - Restraining order
    await page.locator('label:has-text("Restraining order")').click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Emergency orders selected');
    
    // Personal info
    await page.getByLabel('First Name').fill('Sarah');
    await page.getByLabel('Last Name').fill('Williams');
    await page.getByLabel('Date of Birth').fill('1990-07-10');
    await page.click('button:has-text("Continue")');
    console.log('✓ Personal info completed');
    
    // Contact info
    await page.getByLabel('Street Address').fill('789 King St');
    await page.getByLabel('City').fill('London');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('N6A 1E1');
    await page.getByLabel('Phone Number').fill('5195551234');
    await page.click('button:has-text("Continue")');
    console.log('✓ Contact info completed');
    
    // Legal rep - No
    await page.click('button:has-text("No")');
    
    // Other party info
    await page.getByLabel('First Name').fill('Mike');
    await page.getByLabel('Last Name').fill('Brown');
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")'); // Contact skip
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ All party and court info completed');
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.click('button:has-text("Continue")');
    console.log('✓ Children section completed');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Emergency: Yes - URGENT');
    await expect(page.locator('body')).toContainText('URGENT - File These Today');
    console.log('✅ EMERGENCY FLOW COMPLETED SUCCESSFULLY!');
  });

  test('property division flow - reaches summary', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('🔄 Starting property division flow test...');
    
    // Quick navigation
    await page.click('button:has-text("Continue")'); // Intro
    await page.click('button:has-text("No, this is not an emergency")');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.click('button:has-text("Common-law partners")'); // Relationship
    console.log('✓ Initial screens completed');
    
    // Orders - Property and spousal support (available for common-law)
    await page.locator('label:has-text("Property division")').click();
    await page.locator('label:has-text("Spousal support")').click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Property and support orders selected');
    
    // Financial situation (appears because seeking property/support)
    await page.locator('input[type="radio"][value="False"]').first().click(); // Not claiming
    await page.locator('input[type="radio"][value="True"]').nth(1).click(); // Paying support
    await page.locator('input[type="radio"][value="True"]').nth(2).click(); // Has real estate
    await page.locator('input[type="radio"][value="False"]').nth(3).click(); // No business
    await page.locator('input[type="radio"][value="True"]').nth(4).click(); // Has investments
    await page.locator('input[type="radio"][value="False"]').nth(5).click(); // No pension
    await page.click('button:has-text("Continue")');
    console.log('✓ Financial situation completed');
    
    // Personal and contact info
    await page.getByLabel('First Name').fill('David');
    await page.getByLabel('Last Name').fill('Chen');
    await page.getByLabel('Date of Birth').fill('1975-11-30');
    await page.click('button:has-text("Continue")');
    
    await page.getByLabel('Street Address').fill('999 Bay St');
    await page.getByLabel('City').fill('Toronto');
    await page.selectOption('select[name*="state"]', 'Ontario');
    await page.getByLabel('Postal Code').fill('M5S 1A1');
    await page.getByLabel('Phone Number').fill('4165559999');
    await page.click('button:has-text("Continue")');
    console.log('✓ Personal info completed');
    
    // Legal rep - Yes (test lawyer flow)
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
    console.log('✓ Lawyer information completed');
    
    // Other party info
    await page.getByLabel('First Name').fill('Lisa');
    await page.getByLabel('Last Name').fill('Wong');
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")'); // Contact skip
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing
    await page.locator('input[type="radio"][value="False"]').first().click();
    await page.click('button:has-text("Continue")');
    console.log('✓ Court info completed');
    
    // Children - No
    await page.click('button:has-text("No")');
    await page.click('button:has-text("Continue")');
    console.log('✓ Children section completed');
    
    // Verify we reached summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    await expect(page.locator('body')).toContainText('Relationship: Common Law');
    await expect(page.locator('body')).toContainText('Property division');
    await expect(page.locator('body')).toContainText('Your Lawyer: Jennifer Law');
    console.log('✅ PROPERTY DIVISION FLOW COMPLETED SUCCESSFULLY!');
  });
});