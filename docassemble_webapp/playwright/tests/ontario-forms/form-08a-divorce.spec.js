// Test suite for Form 8A - Application (Divorce)
import { test, expect, formAssertions, commonScenarios, testData } from './base-form-test.js';

test.describe('Form 8A - Application (Divorce)', () => {
  test.beforeEach(async ({ page, formHelpers }) => {
    await formHelpers.startInterview('form_08A_interview.yml');
  });

  test('Complete divorce application with all required fields', async ({ page, formHelpers }) => {
    const data = testData.common;
    const divorceData = testData.form8A;
    
    // Page 1: Court Information
    await formHelpers.verifyPageTitle('Court Information');
    await formHelpers.fillTextField('court_name', data.courtInfo.courtName);
    await formHelpers.fillTextField('court_file_number', data.courtInfo.courtFileNumber);
    await formHelpers.fillTextField('court_address', data.courtInfo.courtAddress);
    await formHelpers.continueForm();
    
    // Page 2: Applicant Information
    await formHelpers.verifyPageTitle('Applicant Information');
    await formHelpers.fillPersonInfo('applicant', data.applicant);
    await formHelpers.fillAddress('applicant', data.applicant.address);
    await formHelpers.continueForm();
    
    // Page 3: Lawyer Information (if represented)
    await formHelpers.verifyPageTitle('Legal Representation');
    await formHelpers.selectRadio('has_lawyer', 'yes');
    await formHelpers.fillTextField('lawyer_name', data.applicant.lawyerInfo.name);
    await formHelpers.fillTextField('lawyer_firm', data.applicant.lawyerInfo.firmName);
    await formHelpers.fillTextField('lawyer_lso', data.applicant.lawyerInfo.lsoNumber);
    await formHelpers.fillTextField('lawyer_phone', data.applicant.lawyerInfo.phone);
    await formHelpers.fillTextField('lawyer_email', data.applicant.lawyerInfo.email);
    await formHelpers.continueForm();
    
    // Page 4: Respondent Information
    await formHelpers.verifyPageTitle('Respondent Information');
    await formHelpers.fillPersonInfo('respondent', data.respondent);
    await formHelpers.fillAddress('respondent', data.respondent.address);
    await formHelpers.continueForm();
    
    // Page 5: Marriage Information
    await formHelpers.verifyPageTitle('Marriage Details');
    await formHelpers.fillDateField('date_of_marriage', data.marriage.dateOfMarriage);
    await formHelpers.fillTextField('place_of_marriage', data.marriage.placeOfMarriage);
    await formHelpers.fillDateField('date_of_separation', data.marriage.dateOfSeparation);
    await formHelpers.continueForm();
    
    // Page 6: Grounds for Divorce
    await formHelpers.verifyPageTitle('Grounds for Divorce');
    await formHelpers.selectRadio('divorce_grounds', divorceData.groundsForDivorce);
    if (divorceData.groundsForDivorce === 'separation') {
      await formHelpers.checkBox('confirm_one_year_separation', true);
    }
    await formHelpers.continueForm();
    
    // Page 7: Children
    await formHelpers.verifyPageTitle('Children');
    await formHelpers.selectRadio('has_children', 'yes');
    await formHelpers.fillTextField('number_of_children', data.children.length.toString());
    
    // Fill children details
    for (let i = 0; i < data.children.length; i++) {
      const child = data.children[i];
      await formHelpers.fillTextField(`child_${i}_first_name`, child.firstName);
      await formHelpers.fillTextField(`child_${i}_last_name`, child.lastName);
      await formHelpers.fillDateField(`child_${i}_date_of_birth`, child.dateOfBirth);
      await formHelpers.selectRadio(`child_${i}_resides_with`, child.residesWith);
    }
    await formHelpers.continueForm();
    
    // Page 8: Claims
    await formHelpers.verifyPageTitle('Claims');
    await formHelpers.checkBox('claim_divorce', true);
    await formHelpers.checkBox('claim_custody', divorceData.claimCustody);
    await formHelpers.checkBox('claim_support', divorceData.claimSupport);
    await formHelpers.checkBox('claim_property', divorceData.claimProperty);
    await formHelpers.checkBox('claim_costs', divorceData.claimCosts);
    await formHelpers.continueForm();
    
    // Page 9: Previous Court Cases
    await formHelpers.verifyPageTitle('Previous Proceedings');
    await formHelpers.selectRadio('previous_proceedings', divorceData.previousProceedings ? 'yes' : 'no');
    await formHelpers.continueForm();
    
    // Page 10: Reconciliation
    await formHelpers.verifyPageTitle('Reconciliation');
    await formHelpers.selectRadio('reconciliation_attempted', 'yes');
    await formHelpers.fillTextField('reconciliation_details', divorceData.reconciliationAttempts);
    await formHelpers.continueForm();
    
    // Page 11: Barriers to Divorce
    await formHelpers.verifyPageTitle('Barriers to Divorce');
    await formHelpers.fillTextField('religious_barriers', divorceData.barriers);
    await formHelpers.continueForm();
    
    // Page 12: Review and Sign
    await formHelpers.verifyPageTitle('Review and Sign');
    await formHelpers.checkBox('confirm_truth', true);
    await formHelpers.fillTextField('signature_name', data.applicant.fullLegalName);
    await formHelpers.fillDateField('signature_date', new Date().toISOString().split('T')[0]);
    await formHelpers.continueForm();
    
    // Verify completion
    await formAssertions.verifyFormComplete(page);
    await formAssertions.verifyPDFAvailable(page);
  });

  test('Validate required fields', async ({ page, formHelpers }) => {
    // Try to continue without filling required fields
    await formHelpers.continueForm();
    
    // Should see validation errors
    await formHelpers.verifyValidationError('court_name', 'This field is required');
    await formHelpers.verifyValidationError('court_file_number', 'This field is required');
  });

  test('Validate date fields', async ({ page, formHelpers }) => {
    const data = testData.common;
    
    // Fill court info to get to date fields
    await formHelpers.fillTextField('court_name', data.courtInfo.courtName);
    await formHelpers.fillTextField('court_file_number', data.courtInfo.courtFileNumber);
    await formHelpers.fillTextField('court_address', data.courtInfo.courtAddress);
    await formHelpers.continueForm();
    
    // Skip to marriage details
    await formHelpers.fillPersonInfo('applicant', data.applicant);
    await formHelpers.fillAddress('applicant', data.applicant.address);
    await formHelpers.continueForm();
    await formHelpers.selectRadio('has_lawyer', 'no');
    await formHelpers.continueForm();
    await formHelpers.fillPersonInfo('respondent', data.respondent);
    await formHelpers.fillAddress('respondent', data.respondent.address);
    await formHelpers.continueForm();
    
    // Test invalid marriage date
    await formHelpers.fillDateField('date_of_marriage', '2030-01-01');
    await formHelpers.continueForm();
    await formHelpers.verifyValidationError('date_of_marriage', 'Date cannot be in the future');
    
    // Test separation date before marriage
    await formHelpers.fillDateField('date_of_marriage', '2010-06-15');
    await formHelpers.fillDateField('date_of_separation', '2009-01-01');
    await formHelpers.continueForm();
    await formHelpers.verifyValidationError('date_of_separation', 'Separation date must be after marriage date');
  });

  test('Test conditional logic for children section', async ({ page, formHelpers }) => {
    const data = testData.common;
    
    // Fill required fields to get to children section
    await formHelpers.fillTextField('court_name', data.courtInfo.courtName);
    await formHelpers.fillTextField('court_file_number', data.courtInfo.courtFileNumber);
    await formHelpers.fillTextField('court_address', data.courtInfo.courtAddress);
    await formHelpers.continueForm();
    
    await formHelpers.fillPersonInfo('applicant', data.applicant);
    await formHelpers.fillAddress('applicant', data.applicant.address);
    await formHelpers.continueForm();
    
    await formHelpers.selectRadio('has_lawyer', 'no');
    await formHelpers.continueForm();
    
    await formHelpers.fillPersonInfo('respondent', data.respondent);
    await formHelpers.fillAddress('respondent', data.respondent.address);
    await formHelpers.continueForm();
    
    await formHelpers.fillDateField('date_of_marriage', data.marriage.dateOfMarriage);
    await formHelpers.fillTextField('place_of_marriage', data.marriage.placeOfMarriage);
    await formHelpers.fillDateField('date_of_separation', data.marriage.dateOfSeparation);
    await formHelpers.continueForm();
    
    await formHelpers.selectRadio('divorce_grounds', 'separation');
    await formHelpers.checkBox('confirm_one_year_separation', true);
    await formHelpers.continueForm();
    
    // Test with no children
    await formHelpers.selectRadio('has_children', 'no');
    await formHelpers.continueForm();
    
    // Should skip to claims page
    await formHelpers.verifyPageTitle('Claims');
    
    // Go back and select yes for children
    await formHelpers.goBack();
    await formHelpers.selectRadio('has_children', 'yes');
    await formHelpers.fillTextField('number_of_children', '1');
    
    // Child fields should now be visible
    const childFirstNameField = page.locator('input[name="child_0_first_name"]');
    await expect(childFirstNameField).toBeVisible();
  });

  test('Save and resume interview', async ({ page, formHelpers }) => {
    const data = testData.common;
    
    // Fill some fields
    await formHelpers.fillTextField('court_name', data.courtInfo.courtName);
    await formHelpers.fillTextField('court_file_number', data.courtInfo.courtFileNumber);
    
    // Save progress
    await formHelpers.saveProgress();
    
    // Should see save confirmation
    await formHelpers.verifySuccessMessage('Your progress has been saved');
    
    // Get resume link
    const resumeLink = page.locator('a:has-text("Resume Later")');
    const resumeUrl = await resumeLink.getAttribute('href');
    
    // Navigate away and come back
    await page.goto('about:blank');
    await page.goto(resumeUrl);
    
    // Should be back at the same page with fields filled
    await expect(page.locator('input[name="court_name"]')).toHaveValue(data.courtInfo.courtName);
    await expect(page.locator('input[name="court_file_number"]')).toHaveValue(data.courtInfo.courtFileNumber);
  });

  test('Download completed form in different formats', async ({ page, formHelpers }) => {
    // Complete the form (abbreviated for testing)
    const data = testData.common;
    
    // Quick fill minimum required fields
    await formHelpers.fillTextField('court_name', data.courtInfo.courtName);
    await formHelpers.fillTextField('court_file_number', data.courtInfo.courtFileNumber);
    await formHelpers.fillTextField('court_address', data.courtInfo.courtAddress);
    await formHelpers.continueForm();
    
    // ... (complete rest of form - abbreviated for example)
    
    // After completion, test downloads
    const pdfDownload = await formHelpers.downloadForm('pdf');
    expect(pdfDownload.suggestedFilename()).toContain('Form_8A');
    expect(pdfDownload.suggestedFilename()).toContain('.pdf');
    
    const docxDownload = await formHelpers.downloadForm('docx');
    expect(docxDownload.suggestedFilename()).toContain('Form_8A');
    expect(docxDownload.suggestedFilename()).toContain('.docx');
  });
});