const { test, expect } = require('@playwright/test');
const { WizardPage } = require('../pages/WizardPage');
const { testScenarios } = require('../fixtures/test-data');
const { 
  runCompleteScenario, 
  validateRecommendedForms,
  validateFinancialFormsPresence,
  validateCustodyFormsPresence,
  validateDivorceFormsPresence,
  takeDebugScreenshot 
} = require('../utils/test-helpers');

/**
 * Never Lived Together Pathways Test Suite
 * Tests all scenarios for people who never lived together but have family law matters
 */
test.describe('Never Lived Together Pathways', () => {
  let wizardPage;

  test.beforeEach(async ({ page }) => {
    wizardPage = new WizardPage(page);
  });

  test.describe('Custody and Support Scenarios', () => {
    test('should handle custody and child support case', async () => {
      const scenario = testScenarios.neverTogether.custodyAndSupport;
      
      await test.step('Complete custody and support flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'never_together_custody_support');
      });

      await test.step('Verify appropriate forms for custody and support', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 8 (General), not Form 8A (Divorce)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 8A'))).toBe(false);
        
        // Should include financial forms for child support
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should include custody forms
        validateCustodyFormsPresence(recommendedForms, true);
        
        // Should not include divorce forms
        validateDivorceFormsPresence(recommendedForms, false);
        
        // Should use Form 13 for lower property value
        expect(recommendedForms.some(form => form.includes('Form 13') && !form.includes('13.1'))).toBe(true);
      });

      await test.step('Verify correct court for never together case', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Ontario Court of Justice');
      });

      await test.step('Verify standard timeline', async () => {
        const timeline = await wizardPage.getTimeline();
        expect(timeline).toContain('12-18 months');
      });
    });
  });

  test.describe('Paternity/Parentage Scenarios', () => {
    test('should handle paternity declaration only', async () => {
      const scenario = testScenarios.neverTogether.paternityOnly;
      
      await test.step('Complete paternity only flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'never_together_paternity');
      });

      await test.step('Verify paternity-specific forms', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 8 (General)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        
        // Should include Form 34A for paternity
        expect(recommendedForms.some(form => form.includes('Form 34A') || form.includes('Parentage'))).toBe(true);
        
        // Should not include financial forms for paternity only
        validateFinancialFormsPresence(recommendedForms, false);
        
        // Should not include custody forms when not seeking custody
        validateCustodyFormsPresence(recommendedForms, false);
        
        // Should not include divorce forms
        validateDivorceFormsPresence(recommendedForms, false);
      });

      await test.step('Verify court and timeline for paternity', async () => {
        const court = await wizardPage.getCourt();
        const timeline = await wizardPage.getTimeline();
        
        expect(court).toContain('Ontario Court of Justice');
        expect(timeline).toContain('12-18 months');
      });
    });
  });

  test.describe('Protection Order Scenarios', () => {
    test('should handle restraining order only case', async () => {
      const scenario = testScenarios.neverTogether.restrainingOrderOnly;
      
      await test.step('Complete restraining order only flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'never_together_restraining_only');
      });

      await test.step('Verify minimal forms for restraining order', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 8 (General)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        
        // Should not include financial forms
        validateFinancialFormsPresence(recommendedForms, false);
        
        // Should not include custody forms
        validateCustodyFormsPresence(recommendedForms, false);
        
        // Should not include paternity forms
        expect(recommendedForms.some(form => form.includes('Form 34A'))).toBe(false);
        
        // Should not include divorce forms
        validateDivorceFormsPresence(recommendedForms, false);
      });

      await test.step('Verify appropriate jurisdiction', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Ontario Court of Justice');
      });
    });
  });

  test.describe('Never Together vs Other Relationship Types', () => {
    test('should show different question structure for never together', async () => {
      await test.step('Navigate to orders selection for never together', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        await wizardPage.waitForQuestion('What orders are you seeking?');
      });

      await test.step('Verify never together specific options', async () => {
        const pageContent = await wizardPage.page.content();
        
        // Should mention never lived together
        expect(pageContent).toContain('never lived together');
        
        // Should have paternity option
        expect(await wizardPage.page.locator(wizardPage.neverTogetherPaternityCheckbox).isVisible()).toBe(true);
        expect(pageContent).toContain('Paternity');
        
        // Should have custody and child support options
        expect(await wizardPage.page.locator(wizardPage.neverTogetherCustodyCheckbox).isVisible()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.neverTogetherChildSupportCheckbox).isVisible()).toBe(true);
        
        // Should have restraining order option
        expect(await wizardPage.page.locator(wizardPage.neverTogetherRestrainingCheckbox).isVisible()).toBe(true);
        
        // Should NOT have divorce option
        expect(await wizardPage.page.locator(wizardPage.seekingDivorceCheckbox).isVisible()).toBe(false);
        
        // Should NOT have spousal support or property options
        expect(await wizardPage.page.locator(wizardPage.seekingSpousalSupportCheckbox).isVisible()).toBe(false);
        expect(await wizardPage.page.locator(wizardPage.seekingPropertyCheckbox).isVisible()).toBe(false);
        expect(await wizardPage.page.locator(wizardPage.seekingExclusivePossessionCheckbox).isVisible()).toBe(false);
      });
    });

    test('should not allow spousal support or property division for never together', async () => {
      await test.step('Navigate to never together orders', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        await wizardPage.waitForQuestion('What orders are you seeking?');
      });

      await test.step('Verify unavailable options', async () => {
        const pageContent = await wizardPage.page.content();
        
        // These should not be available for never together cases
        expect(pageContent).not.toContain('Spousal support');
        expect(pageContent).not.toContain('Property division');
        expect(pageContent).not.toContain('equalization');
        expect(pageContent).not.toContain('Exclusive possession');
        expect(pageContent).not.toContain('matrimonial home');
      });
    });
  });

  test.describe('Financial Forms for Never Together', () => {
    test('should include financial forms when child support is sought', async () => {
      await test.step('Complete never together with child support', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        
        await wizardPage.handleNeverTogetherOrders({
          custody: false,
          child_support: true,
          paternity: false,
          restraining_order: false,
          other: false
        });

        await wizardPage.handleFinancialSituation({
          property_value: 25000,
          support_involved: true,
          business_owner: false,
          pension_involved: false
        });

        await wizardPage.handleRecommendations();
        await wizardPage.verifyFinalScreen(false);
      });

      await test.step('Verify financial forms for child support', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include financial forms for child support
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should use Form 13 for support claims
        expect(recommendedForms.some(form => form.includes('Form 13') && !form.includes('13.1'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 13A'))).toBe(true);
      });
    });

    test('should not include financial forms when no support sought', async () => {
      await test.step('Complete never together without support', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        
        await wizardPage.handleNeverTogetherOrders({
          custody: true,
          child_support: false,
          paternity: false,
          restraining_order: false,
          other: false
        });

        await wizardPage.handleRecommendations();
        await wizardPage.verifyFinalScreen(false);
      });

      await test.step('Verify no financial forms for custody only', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should not include financial forms when no support
        validateFinancialFormsPresence(recommendedForms, false);
        
        // Should include custody forms
        validateCustodyFormsPresence(recommendedForms, true);
      });
    });
  });

  test.describe('Combined Orders for Never Together', () => {
    test('should handle multiple orders correctly', async () => {
      await test.step('Complete never together with multiple orders', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        
        await wizardPage.handleNeverTogetherOrders({
          custody: true,
          child_support: true,
          paternity: true,
          restraining_order: false,
          other: false
        });

        await wizardPage.handleFinancialSituation({
          property_value: 35000,
          support_involved: true,
          business_owner: false,
          pension_involved: false
        });

        await wizardPage.handleRecommendations();
        await wizardPage.verifyFinalScreen(false);
      });

      await test.step('Verify comprehensive form package', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include Form 8 (General)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        
        // Should include financial forms for child support
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should include custody forms
        validateCustodyFormsPresence(recommendedForms, true);
        
        // Should include paternity forms
        expect(recommendedForms.some(form => form.includes('Form 34A') || form.includes('Parentage'))).toBe(true);
        
        // Should not include divorce forms
        validateDivorceFormsPresence(recommendedForms, false);
      });
    });
  });

  test.describe('Court Selection for Never Together', () => {
    test('should direct never together cases to appropriate court', async () => {
      const scenario = testScenarios.neverTogether.custodyAndSupport;
      
      await test.step('Complete typical never together case', async () => {
        await runCompleteScenario(wizardPage, scenario, 'never_together_court');
      });

      await test.step('Verify Ontario Court of Justice for typical case', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Ontario Court of Justice');
        expect(court).not.toContain('Superior Court of Justice');
      });
    });

    test('should not direct to Superior Court unless high value', async () => {
      await test.step('Complete lower-value never together case', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        
        await wizardPage.handleNeverTogetherOrders({
          custody: true,
          child_support: true,
          paternity: false,
          restraining_order: false,
          other: false
        });

        await wizardPage.handleFinancialSituation({
          property_value: 20000, // Low value
          support_involved: true,
          business_owner: false,
          pension_involved: false
        });

        await wizardPage.handleRecommendations();
        await wizardPage.verifyFinalScreen(false);
      });

      await test.step('Verify stays in Ontario Court of Justice', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Ontario Court of Justice');
      });
    });
  });

  test.describe('Variable Mapping for Never Together', () => {
    test('should correctly map never together variables', async () => {
      await test.step('Complete never together flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        
        await wizardPage.handleNeverTogetherOrders({
          custody: true,
          child_support: true,
          paternity: false,
          restraining_order: true,
          other: false
        });

        await wizardPage.handleFinancialSituation({
          property_value: 30000,
          support_involved: true,
          business_owner: false,
          pension_involved: false
        });

        await wizardPage.handleRecommendations();
      });

      await test.step('Verify final screen shows correct workflow data', async () => {
        await wizardPage.verifyFinalScreen(false);
        
        const pageContent = await wizardPage.page.content();
        
        // Should show correct relationship status
        expect(pageContent).toContain('never_together');
        
        // Should show correct orders
        expect(pageContent).toContain('Custody') || expect(pageContent).toContain('custody');
        expect(pageContent).toContain('Child Support') || expect(pageContent).toContain('child_support');
        expect(pageContent).toContain('Restraining') || expect(pageContent).toContain('restraining');
        
        // Should not show divorce or spousal support
        expect(pageContent).not.toContain('Divorce: true');
        expect(pageContent).not.toContain('Spousal Support: true');
      });
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle no orders selected for never together', async () => {
      await test.step('Navigate to orders selection', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        await wizardPage.waitForQuestion('What orders are you seeking?');
      });

      await test.step('Try to continue without selecting orders', async () => {
        // Don't select any orders, just try to continue
        await wizardPage.clickContinue();
        
        // Should either show validation or proceed with minimal forms
        await wizardPage.page.waitForTimeout(2000);
        
        // Should not show any errors
        await wizardPage.checkForErrors();
      });
    });

    test('should validate checkbox functionality for never together', async () => {
      await test.step('Navigate to never together orders', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
        await wizardPage.waitForQuestion('What orders are you seeking?');
      });

      await test.step('Test checkbox functionality', async () => {
        // Check multiple boxes
        await wizardPage.page.locator(wizardPage.neverTogetherCustodyCheckbox).check();
        await wizardPage.page.locator(wizardPage.neverTogetherChildSupportCheckbox).check();
        await wizardPage.page.locator(wizardPage.neverTogetherPaternityCheckbox).check();
        
        // Verify they are checked
        expect(await wizardPage.page.locator(wizardPage.neverTogetherCustodyCheckbox).isChecked()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.neverTogetherChildSupportCheckbox).isChecked()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.neverTogetherPaternityCheckbox).isChecked()).toBe(true);
        
        // Uncheck one
        await wizardPage.page.locator(wizardPage.neverTogetherPaternityCheckbox).uncheck();
        expect(await wizardPage.page.locator(wizardPage.neverTogetherPaternityCheckbox).isChecked()).toBe(false);
        
        // Others should still be checked
        expect(await wizardPage.page.locator(wizardPage.neverTogetherCustodyCheckbox).isChecked()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.neverTogetherChildSupportCheckbox).isChecked()).toBe(true);
      });
    });

    test('should handle form links correctly for never together cases', async () => {
      const scenario = testScenarios.neverTogether.custodyAndSupport;
      
      await test.step('Complete never together case', async () => {
        await runCompleteScenario(wizardPage, scenario, 'never_together_form_links');
      });

      await test.step('Verify form links are valid', async () => {
        // Navigate back to recommendations
        await wizardPage.page.goBack();
        await wizardPage.page.waitForLoadState('networkidle');
        
        const formLinks = wizardPage.page.locator('a[href*="/interview?i=docassemble.webapp:ontario-family-law/form"]');
        const count = await formLinks.count();
        
        expect(count, 'Should have form links').toBeGreaterThan(0);
        
        for (let i = 0; i < count; i++) {
          const href = await formLinks.nth(i).getAttribute('href');
          expect(href, `Form link ${i} should be valid`).toBeTruthy();
          expect(href, `Form link ${i} should point to interview`).toContain('/interview?i=');
        }
      });
    });

    test('should handle back navigation correctly', async () => {
      await test.step('Navigate through never together flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('never_together');
      });

      await test.step('Use back navigation', async () => {
        await wizardPage.page.goBack();
        await wizardPage.page.waitForLoadState('networkidle');
        
        // Should be back on MIP screen
        expect(await wizardPage.page.locator('text=MIP Session Information').isVisible()).toBe(true);
        
        // Should not show errors
        await wizardPage.checkForErrors();
      });

      await test.step('Continue forward again', async () => {
        await wizardPage.clickContinue();
        await wizardPage.waitForQuestion('What is your relationship status?');
      });
    });
  });

  test.describe('Integration with MIP Requirements', () => {
    test('should require MIP for never together cases', async () => {
      await test.step('Verify MIP requirement', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        
        // Should show MIP screen for never together cases
        await wizardPage.waitForQuestion('Mandatory Information Program');
        
        const pageContent = await wizardPage.page.content();
        expect(pageContent).toContain('must attend the Mandatory Information Program');
      });
    });
  });
});