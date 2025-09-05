import { test, expect } from '@playwright/test';

const INTERVIEW_URL = '/interview?i=docassemble.webapp:data/questions/ontario-family-law/common_intake_enhanced_with_validation.yml';

test('minimal flow - interview loads and starts', async ({ page }) => {
  // Navigate to interview
  await page.goto(INTERVIEW_URL);
  await page.waitForLoadState('networkidle');
  
  // Check for error messages
  const errorMessage = await page.locator('.alert-danger, .error-message').count();
  if (errorMessage > 0) {
    const errorText = await page.locator('.alert-danger, .error-message').first().textContent();
    console.error('Interview error:', errorText);
  }
  
  // Should see introduction
  await expect(page.locator('h1#daMainQuestion')).toContainText('Ontario Family Law Common Intake');
  console.log('✓ Interview loads successfully');
  
  // Click Continue
  await page.click('button:has-text("Continue")');
  
  // Should see emergency question
  await expect(page.locator('h1#daMainQuestion')).toContainText('Is this an emergency situation?');
  console.log('✓ Emergency question appears');
  
  // Select No emergency
  await page.click('button:has-text("No, this is not an emergency")');
  
  // Should see MIP status
  await expect(page.locator('h1#daMainQuestion')).toContainText('Mandatory Information Program');
  console.log('✓ MIP status question appears');
  
  // Select completed
  await page.click('button:has-text("Yes, I have my certificate")');
  
  // Should see relationship status
  await expect(page.locator('h1#daMainQuestion')).toContainText('What is your relationship status');
  console.log('✓ Relationship status question appears');
  
  // Select married
  await page.click('button:has-text("Married")');
  
  // Should see orders
  await expect(page.locator('h1#daMainQuestion')).toContainText('What orders are you seeking');
  console.log('✓ Orders question appears');
  
  // Check if Divorce checkbox is visible for married status
  const divorceCheckbox = page.getByRole('checkbox', { name: 'Divorce' });
  const divorceVisible = await divorceCheckbox.isVisible();
  
  if (!divorceVisible) {
    console.error('ERROR: Divorce checkbox should be visible for married status but is not!');
    
    // Log all visible checkboxes
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    console.log('Visible checkboxes:');
    for (const cb of checkboxes) {
      const label = await cb.locator('..').textContent();
      console.log(' -', label);
    }
  } else {
    console.log('✓ Divorce checkbox is correctly visible for married status');
  }
});