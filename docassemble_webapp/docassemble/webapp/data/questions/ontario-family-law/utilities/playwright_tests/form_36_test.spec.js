/**
 * Playwright tests for Ontario Family Law Form 36
 * Generated from YAML interview: generated_interviews/form_36_enhanced.yml
 * Generated on: 2025-09-05 13:25:01
 * 
 * Title: Ontario Form 36 - Affidavit for Divorce
 */

const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
test.describe.configure({ mode: 'parallel' });

// Test data
const testData = {
  'applicant.name.first': 'Test First name',
  'applicant.name.middle': 'Test Middle name',
  'applicant.name.last': 'Test Last name',
  'respondent.address.address': 'Test Street address',
  'respondent.address.city': 'Test City',
  'respondent.address.state': 'Test Province',
  'respondent.address.zip': 'Test Postal code',
  'respondent.phone_number': 'Test Phone number',
  'respondent.email': 'test@example.com',
  'respondent.birthdate': '2024-01-01',
  'applicant.has_lawyer': true,
  'applicant.lawyer.name.first': 'Test Lawyer's first name',
  'applicant.lawyer.name.last': 'Test Lawyer's last name',
  'applicant.lawyer.firm_name': 'Test Law firm name',
  'applicant.lawyer.phone_number': 'Test Lawyer's phone',
  'applicant.lawyer.email': 'test@example.com',
  'case.court_file_number': 'Test Court file number',
  'case.related_case_number': 'Test Court file number of related case',
  'case.related_case_court': 'Test Court where related case was filed',
  'case.related_case_status': 'Test Status of related case',
  'marriage.marriage_date': '2024-01-01',
  'marriage.place_of_marriage': 'Test Place of marriage',
  'separation.date_of_separation': '2024-01-01',
  'children.target_number': 2,
  'children[i].name.first': 'Test First name',
  'children[i].name.middle': 'Test Middle name (if any)',
  'children[i].name.last': 'Test Last name',
  'children[i].birthdate': '2024-01-01',
  'children[i].lives_with': 'Test Value',
  'children[i].other_guardian': 'Test If someone else, who?',
  'children[i].relationship_type': 'Test Value',
  'children[i].relationship_details': 'Test Please specify',
  'children[i].has_special_needs': true,
  'children[i].special_needs_description': 'Test Description of special needs',
  'children[i].in_education': true,
  'children[i].education_details': 'Test School/program details',
  'custody.decision_making': 'Test Value',
  'custody.primary_residence': 'Test Value',
  'custody.weekly_schedule': 'Test Regular weekly schedule',
  'area': 'Test input type',
  'custody.holiday_schedule': 'Test Holiday and special occasion schedule',
  'custody.summer_schedule': 'Test Summer vacation schedule',
  'custody.supervised_access': true,
  'custody.no_contact': true,
  'custody.restraining_order': true,
  'custody.other_conditions': 'Test Other special conditions',
  'divorce.grounds': 'Test Value',
  'divorce.separation_date': '2024-01-01',
  'divorce.living_apart': true,
  'divorce.separation_description': 'Test Brief description of separation',
};

// Invalid test data for validation testing
const invalidData = {
  email: 'invalid-email',
  phone: '123',
  postal_code: 'INVALID',
  date: '2099-01-01', // Future date
  currency: '-100', // Negative value
};

test.describe('Form 36 - Main Flow', () => {
  test('Complete form with all required fields', async ({ page }) => {
    // Navigate to the interview
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    // Wait for the interview to load
    await page.waitForSelector('.da-page-header', { timeout: 10000 });
    
    // Fill fields for: What is your full legal name?
    await page.fill('[name="applicant.name.first"]', testData['applicant.name.first'] || 'Test Value');
    await page.fill('[name="applicant.name.middle"]', testData['applicant.name.middle'] || 'Test Value');
    await page.fill('[name="applicant.name.last"]', testData['applicant.name.last'] || 'Test Value');
    // Fill fields for: What is your address?
    await page.fill('[name="respondent.address.address"]', testData['respondent.address.address'] || 'Test Value');
    await page.fill('[name="respondent.address.city"]', testData['respondent.address.city'] || 'Test Value');
    await page.fill('[name="respondent.address.state"]', testData['respondent.address.state'] || 'Test Value');
    await page.fill('[name="respondent.address.zip"]', testData['respondent.address.zip'] || 'Test Value');
    // Fill fields for: What are your contact details?
    await page.fill('[name="respondent.phone_number"]', testData['respondent.phone_number'] || 'Test Value');
    await page.fill('[name="respondent.email"]', testData['respondent.email'] || 'Test Value');
    // Fill fields for: What is your date of birth?
    await page.fill('[name="respondent.birthdate"]', testData['respondent.birthdate'] || '2024-01-01');
    // Fill fields for: Do you have a lawyer?
    await page.click('[name="applicant.has_lawyer"][value="True"]');
    // Fill fields for: What are your lawyer's details?
    await page.fill('[name="applicant.lawyer.name.first"]', testData['applicant.lawyer.name.first'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.name.last"]', testData['applicant.lawyer.name.last'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.firm_name"]', testData['applicant.lawyer.firm_name'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.phone_number"]', testData['applicant.lawyer.phone_number'] || 'Test Value');
    await page.fill('[name="applicant.lawyer.email"]', testData['applicant.lawyer.email'] || 'Test Value');
    // Fill fields for: Do you have a court file number?
    await page.fill('[name="case.court_file_number"]', testData['case.court_file_number'] || 'Test Value');
    // Fill fields for: What are the details of the related cases?
    await page.fill('[name="case.related_case_number"]', testData['case.related_case_number'] || 'Test Value');
    await page.fill('[name="case.related_case_court"]', testData['case.related_case_court'] || 'Test Value');
    await page.fill('[name="case.related_case_status"]', testData['case.related_case_status'] || 'Test Value');
    // Fill fields for: Marriage Information
    await page.fill('[name="marriage.marriage_date"]', testData['marriage.marriage_date'] || '2024-01-01');
    await page.fill('[name="marriage.place_of_marriage"]', testData['marriage.place_of_marriage'] || 'Test Value');
    // Fill fields for: Separation Information
    await page.fill('[name="separation.date_of_separation"]', testData['separation.date_of_separation'] || '2024-01-01');
    // Fill fields for: How many children are there?
    // TODO: Fill field children.target_number (type: integer)
    // Fill fields for: Tell me about ${ordinal(i)} child.
    await page.fill('[name="children[i].name.first"]', testData['children[i].name.first'] || 'Test Value');
    await page.fill('[name="children[i].name.middle"]', testData['children[i].name.middle'] || 'Test Value');
    await page.fill('[name="children[i].name.last"]', testData['children[i].name.last'] || 'Test Value');
    await page.fill('[name="children[i].birthdate"]', testData['children[i].birthdate'] || '2024-01-01');
    // Fill fields for: Where does ${children[i].name.first} live?
    await page.click('[name="children[i].lives_with"][value="{'applicant': 'Me (the applicant)'}"]');
    // TODO: Fill field [{'applicant': 'Me (the applicant)'}, {'respondent': 'The other party (the respondent)'}, {'shared': 'Both parties (shared residence)'}, {'other': 'Someone else (please specify below)'}] (type: radio)
    await page.fill('[name="children[i].other_guardian"]', testData['children[i].other_guardian'] || 'Test Value');
    await page.fill('[name="children[i].lives_with == 'other'"]', testData['children[i].lives_with == 'other''] || 'Test Value');
    // Fill fields for: What is ${children[i].name.first}'s relationship to you and the other party?
    await page.click('[name="children[i].relationship_type"][value="{'biological': 'Biological child of both parties'}"]');
    // TODO: Fill field [{'biological': 'Biological child of both parties'}, {'adopted_both': 'Adopted by both parties'}, {'adopted_applicant': 'Adopted by me only'}, {'adopted_respondent': 'Adopted by the other party only'}, {'stepchild_applicant': 'My biological/adopted child, stepchild to other party'}, {'stepchild_respondent': "Other party's biological/adopted child, my stepchild"}, {'other': 'Other relationship (please specify)'}] (type: radio)
    await page.fill('[name="children[i].relationship_details"]', testData['children[i].relationship_details'] || 'Test Value');
    await page.fill('[name="children[i].relationship_type == 'other'"]', testData['children[i].relationship_type == 'other''] || 'Test Value');
    // Fill fields for: Does ${children[i].name.first} have any special circumstances?
    await page.click('[name="children[i].has_special_needs"][value="True"]');
    await page.fill('[name="children[i].special_needs_description"]', testData['children[i].special_needs_description'] || 'Test Value');
    await page.fill('[name="children[i].has_special_needs"]', testData['children[i].has_special_needs'] || 'Test Value');
    await page.click('[name="children[i].in_education"][value="True"]');
    await page.fill('[name="children[i].education_details"]', testData['children[i].education_details'] || 'Test Value');
    await page.fill('[name="children[i].in_education"]', testData['children[i].in_education'] || 'Test Value');
    // Fill fields for: What decision-making responsibility are you asking for?
    await page.click('[name="custody.decision_making"][value="{'sole_applicant': 'Sole decision-making responsibility to me'}"]');
    // TODO: Fill field [{'sole_applicant': 'Sole decision-making responsibility to me'}, {'sole_respondent': 'Sole decision-making responsibility to the other party'}, {'joint': 'Joint decision-making responsibility (both parties decide together)'}, {'divided': 'Divided decision-making (different areas to different parties)'}] (type: radio)
    // Fill fields for: Where should the children primarily live?
    await page.click('[name="custody.primary_residence"][value="{'applicant': 'With me (the applicant)'}"]');
    // TODO: Fill field [{'applicant': 'With me (the applicant)'}, {'respondent': 'With the other party (the respondent)'}, {'shared': 'Shared residence (children spend equal or nearly equal time with both)'}] (type: radio)
    // Fill fields for: What parenting time schedule are you proposing?
    await page.fill('[name="custody.weekly_schedule"]', testData['custody.weekly_schedule'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    await page.fill('[name="custody.holiday_schedule"]', testData['custody.holiday_schedule'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    await page.fill('[name="custody.summer_schedule"]', testData['custody.summer_schedule'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    // Fill fields for: Are there any special conditions needed for the children's safety and wellbeing?
    await page.click('[name="custody.supervised_access"][value="True"]');
    await page.click('[name="custody.no_contact"][value="True"]');
    await page.click('[name="custody.restraining_order"][value="True"]');
    await page.fill('[name="custody.other_conditions"]', testData['custody.other_conditions'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    // Fill fields for: What are the grounds for divorce?
    await page.click('[name="divorce.grounds"][value="{'separation': 'Separation for at least one year'}"]');
    // TODO: Fill field [{'separation': 'Separation for at least one year'}, {'adultery': 'Adultery by the other spouse'}, {'cruelty': 'Physical or mental cruelty by the other spouse'}] (type: radio)
    // Fill fields for: Separation Details
    await page.fill('[name="divorce.separation_date"]', testData['divorce.separation_date'] || '2024-01-01');
    await page.click('[name="divorce.living_apart"][value="True"]');
    await page.fill('[name="divorce.separation_description"]', testData['divorce.separation_description'] || 'Test Value');
    await page.fill('[name="area"]', testData['area'] || 'Test Value');
    // Verify completion
    await expect(page.locator('h1')).toContainText('Complete');
  });
});

test.describe('Form 36 - Field Validation', () => {
  test('Validate email fields', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    // Test invalid email
    await page.fill('[type="email"]', 'invalid-email');
    await page.click('button:has-text("Continue")');
    
    // Should show validation error
    await expect(page.locator('.da-has-error')).toBeVisible();
  });

});

test.describe('Form 36 - Navigation', () => {
  test('Navigate back through questions', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    // Move forward a few screens
    await page.click('button:has-text("Continue")');
    await page.waitForLoadState('networkidle');
    
    // Test back button
    const backButton = page.locator('button:has-text("Back")');
    if (await backButton.isVisible()) {
      await backButton.click();
      await page.waitForLoadState('networkidle');
      
      // Verify we went back
      await expect(page).toHaveURL(/.*question.*/);
    }
  });
  
  test('Test progress bar updates', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    const progressBar = page.locator('.progress-bar, [role="progressbar"]');
    if (await progressBar.isVisible()) {
      const initialProgress = await progressBar.getAttribute('aria-valuenow') || 
                             await progressBar.getAttribute('style');
      
      // Move forward
      await page.click('button:has-text("Continue")');
      await page.waitForLoadState('networkidle');
      
      const newProgress = await progressBar.getAttribute('aria-valuenow') || 
                         await progressBar.getAttribute('style');
      
      // Progress should have increased
      expect(newProgress).not.toBe(initialProgress);
    }
  });
});

test.describe('Form 36 - Edge Cases', () => {
  test('Handle session timeout gracefully', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    // Simulate long delay
    await page.waitForTimeout(1000);
    
    // Try to continue
    await page.click('button:has-text("Continue")');
    
    // Should either continue or show appropriate message
    await expect(page).not.toHaveURL(/.*error.*/);
  });
  
  test('Handle browser refresh', async ({ page }) => {
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    // Fill some data
    const firstInput = page.locator('input[type="text"]').first();
    if (await firstInput.isVisible()) {
      await firstInput.fill('Test Data');
    }
    
    // Refresh page
    await page.reload();
    
    // Interview should resume
    await expect(page.locator('.da-page-header')).toBeVisible();
  });
  
  test('Verify mobile responsiveness', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    
    // Check that content is visible and accessible
    await expect(page.locator('.da-page-header')).toBeVisible();
    await expect(page.locator('button:has-text("Continue")')).toBeVisible();
    
    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
  });
});

// Performance tests
test.describe('Form 36 - Performance', () => {
  test('Measure page load time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/interview?i=docassemble.ontarioforms:data/questions/form_36.yml');
    await page.waitForSelector('.da-page-header');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Form 36 loaded in ${loadTime}ms`);
  });
});
