import { test, expect, Page } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test.describe('Debug Children Flow', () => {
  test('basic flow with children', async ({ page }) => {
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
    // Skip optional lawyer screens
    await page.click('button:has-text("Continue")');
    await page.click('button:has-text("Continue")');
    
    // Court info - No existing file
    await page.getByRole('radio', { name: 'No' }).click();
    await page.click('button:has-text("Continue")');
    
    // Now the children question should appear
    console.log('At children question...');
    await page.waitForTimeout(1000);
    
    // Get page content to debug
    const heading = await page.locator('h1#daMainQuestion').textContent();
    console.log('Heading:', heading);
    
    // Click Yes for children
    await page.click('button:has-text("Yes")');
    
    // Wait a bit and check what screen appears
    await page.waitForTimeout(1000);
    const nextHeading = await page.locator('h1#daMainQuestion').textContent();
    console.log('Next heading after Yes:', nextHeading);
    
    // Try to continue and see what error appears
    const errorExists = await page.locator('.da-has-error, .text-danger, blockquote').isVisible().catch(() => false);
    if (errorExists) {
      const errorText = await page.locator('blockquote').textContent().catch(() => 'No error text');
      console.log('Error found:', errorText);
    }
    
    // Take a screenshot for debugging
    await page.screenshot({ path: 'test-results/children-debug.png' });
  });
});