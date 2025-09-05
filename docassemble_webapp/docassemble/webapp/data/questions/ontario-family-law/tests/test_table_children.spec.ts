import { test, expect, Page } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test.describe('Table-based Children Flow', () => {
  test('add children using table interface', async ({ page }) => {
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
    
    // Orders - Just custody
    await page.getByRole('checkbox', { name: 'Child custody and/or access' }).click();
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
    
    // Other party contact
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing file
    await page.getByRole('radio', { name: 'No' }).click();
    await page.click('button:has-text("Continue")');
    
    // Do you have children together?
    console.log('At children yes/no question...');
    await expect(page.locator('h1#daMainQuestion')).toContainText('Do you have any children together?');
    await page.click('button:has-text("Yes")');
    
    // Now we should see the Children Information table screen
    console.log('At children table screen...');
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    
    // Click "Add a child" button
    const addChildButton = page.locator('a:has-text("Add a child")').first();
    await addChildButton.click();
    
    // Fill in first child's information
    await expect(page.locator('h1#daMainQuestion')).toContainText('Add Child Information');
    await page.getByLabel('First Name').fill('Emma');
    await page.getByLabel('Last Name').fill('Smith');
    await page.getByLabel('Date of Birth').fill('2015-03-15');
    await page.getByLabel('Lives with').selectOption('Both (shared)');
    await page.click('button:has-text("Continue")');
    
    // Should return to Children Information screen with the child in the table
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('table')).toContainText('Emma Smith');
    await expect(page.locator('table')).toContainText('2015-03-15');
    
    // Add another child
    await page.locator('a:has-text("Add a child")').first().click();
    
    // Fill in second child's information
    await expect(page.locator('h1#daMainQuestion')).toContainText('Add Child Information');
    await page.getByLabel('First Name').fill('Liam');
    await page.getByLabel('Last Name').fill('Smith');
    await page.getByLabel('Date of Birth').fill('2018-06-20');
    await page.getByLabel('Lives with').selectOption('Me');
    await page.click('button:has-text("Continue")');
    
    // Should return to Children Information screen with both children
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('table')).toContainText('Emma Smith');
    await expect(page.locator('table')).toContainText('Liam Smith');
    
    // Continue to summary
    await page.click('button:has-text("Continue")');
    
    // Should show the summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    
    // Verify children are in the summary
    await expect(page.locator('body')).toContainText('Number of Children: 2');
    await expect(page.locator('body')).toContainText('Emma Smith');
    await expect(page.locator('body')).toContainText('Liam Smith');
    
    console.log('Test completed successfully!');
  });
  
  test('no children flow', async ({ page }) => {
    await page.goto(INTERVIEW_URL);
    await page.waitForLoadState('networkidle');
    
    // Navigate through initial screens quickly
    await page.click('button:has-text("Continue")'); // Introduction
    await page.click('button:has-text("No, this is not an emergency")');
    await page.click('button:has-text("Yes, I have my certificate")');
    await page.click('button:has-text("Married")');
    
    // Orders - Just divorce
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
    
    // Other party contact
    await page.click('button:has-text("Continue")');
    
    // Other party lawyer - No
    await page.click('button:has-text("No")');
    
    // Court info - No existing file
    await page.getByRole('radio', { name: 'No' }).click();
    await page.click('button:has-text("Continue")');
    
    // Do you have children together? - NO
    console.log('At children yes/no question...');
    await expect(page.locator('h1#daMainQuestion')).toContainText('Do you have any children together?');
    await page.click('button:has-text("No")');
    
    // Should see Children Information screen saying no children
    console.log('At children info screen...');
    await expect(page.locator('h1#daMainQuestion')).toContainText('Children Information');
    await expect(page.locator('body')).toContainText('You indicated you do not have children together');
    
    // Continue to summary
    await page.click('button:has-text("Continue")');
    
    // Should show the summary
    await expect(page.locator('h1#daMainQuestion')).toContainText('Information Summary');
    
    // Verify no children in summary
    await expect(page.locator('body')).toContainText('Children: None');
    
    console.log('Test completed successfully!');
  });
});