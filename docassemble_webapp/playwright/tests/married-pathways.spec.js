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
 * Married Pathways Test Suite
 * Tests all scenarios for married couples (non-emergency)
 */
test.describe('Married Pathways', () => {
  let wizardPage;

  test.beforeEach(async ({ page }) => {
    wizardPage = new WizardPage(page);
  });

  test.describe('Uncontested Divorce Scenarios', () => {
    test('should handle uncontested divorce with no children', async () => {
      const scenario = testScenarios.married.uncontestedDivorceNoChildren;
      
      await test.step('Complete uncontested divorce no children flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'uncontested_divorce_no_children');
      });

      await test.step('Verify divorce-specific forms', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include divorce forms
        validateDivorceFormsPresence(recommendedForms, true);
        
        // Should include Form 25A for uncontested simple divorce
        expect(recommendedForms.some(form => form.includes('Form 25A'))).toBe(true);
        
        // Should not include financial forms for divorce only
        validateFinancialFormsPresence(recommendedForms, false);
        
        // Should not include custody forms when no children
        validateCustodyFormsPresence(recommendedForms, false);
      });

      await test.step('Verify optimistic timeline for simple divorce', async () => {
        const timeline = await wizardPage.getTimeline();
        expect(timeline).toContain('4-6 months');
      });

      await test.step('Verify Superior Court jurisdiction for divorce', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Superior Court of Justice');
      });
    });

    test('should handle uncontested divorce with children', async () => {
      const scenario = testScenarios.married.uncontestedDivorceWithChildren;
      
      await test.step('Complete uncontested divorce with children flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'uncontested_divorce_with_children');
      });

      await test.step('Verify children affect form requirements', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include divorce forms
        validateDivorceFormsPresence(recommendedForms, true);
        
        // Should include custody forms due to children
        validateCustodyFormsPresence(recommendedForms, true);
        
        // Should NOT include Form 25A when children involved (more complex)
        expect(recommendedForms.some(form => form.includes('Form 25A'))).toBe(false);
      });

      await test.step('Verify longer timeline when children involved', async () => {
        const timeline = await wizardPage.getTimeline();
        expect(timeline).toContain('12-18'); // Longer timeline than simple divorce
      });
    });
  });

  test.describe('Contested/Complex Divorce Scenarios', () => {
    test('should handle divorce with additional orders', async () => {
      const scenario = testScenarios.married.divorceWithOtherOrders;
      
      await test.step('Complete divorce with other orders flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'divorce_with_other_orders');
      });

      await test.step('Verify comprehensive form package', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include divorce forms
        validateDivorceFormsPresence(recommendedForms, true);
        
        // Should include financial forms due to support and property claims
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should include custody forms due to custody claim
        validateCustodyFormsPresence(recommendedForms, true);
        
        // Should use Form 13.1 due to high property value
        expect(recommendedForms.some(form => form.includes('Form 13.1'))).toBe(true);
      });

      await test.step('Verify contested timeline', async () => {
        const timeline = await wizardPage.getTimeline();
        expect(timeline).toContain('12-18'); // Longer timeline for contested cases
      });

      await test.step('Verify proper court for high-value property', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Superior Court of Justice');
      });
    });
  });

  test.describe('Separation Without Divorce', () => {
    test('should handle separation only case', async () => {
      const scenario = testScenarios.married.separationOnly;
      
      await test.step('Complete separation only flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'separation_only');
      });

      await test.step('Verify separation forms (no divorce)', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 8 (General) not Form 8A (Divorce)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 8A'))).toBe(false);
        
        // Should not include divorce-specific forms
        expect(recommendedForms.some(form => form.includes('Form 36'))).toBe(false);
        expect(recommendedForms.some(form => form.includes('Form 25A'))).toBe(false);
        
        // Should include financial forms for support claims
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should include custody forms
        validateCustodyFormsPresence(recommendedForms, true);
      });

      await test.step('Verify appropriate court for separation', async () => {
        const court = await wizardPage.getCourt();
        // Medium value property, should go to Ontario Court of Justice
        expect(court).toContain('Ontario Court of Justice');
      });
    });
  });

  test.describe('MIP Requirements Handling', () => {
    test('should show MIP information for non-emergency married cases', async () => {
      await test.step('Start non-emergency married flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
      });

      await test.step('Verify MIP information screen appears', async () => {
        await wizardPage.waitForQuestion('Mandatory Information Program');
        
        // Check MIP-specific content
        expect(await wizardPage.page.locator('text=MIP').isVisible()).toBe(true);
        expect(await wizardPage.page.locator('text=certificate required').isVisible()).toBe(true);
      });

      await test.step('Test MIP completed path', async () => {
        await wizardPage.handleMipQuestion('completed');
        
        // Should proceed to relationship status
        await wizardPage.waitForQuestion('What is your relationship status?');
      });
    });

    test('should handle MIP not completed scenario', async () => {
      await test.step('Navigate through MIP not completed flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('not_completed');
      });

      await test.step('Verify MIP guidance is provided', async () => {
        // Should show information about attending MIP
        const pageContent = await wizardPage.page.content();
        expect(pageContent).toContain('must attend MIP');
        expect(pageContent).toContain('ontario.ca');
      });
    });

    test('should handle MIP unsure scenario', async () => {
      await test.step('Navigate through MIP unsure flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('unsure');
      });

      await test.step('Verify MIP guidance for unsure users', async () => {
        const pageContent = await wizardPage.page.content();
        expect(pageContent).toContain('contact your local courthouse');
      });
    });
  });

  test.describe('Divorce Complexity Logic', () => {
    test('should automatically set contested for divorce with other orders', async () => {
      await test.step('Start married divorce with multiple orders', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('married');
        
        // Select divorce plus other orders
        await wizardPage.handleOrdersSought({
          divorce: true,
          custody: true,
          child_support: false,
          spousal_support: false,
          property: false,
          exclusive_possession: false,
          restraining_order: false,
          enforcement: false,
          other: false
        });
      });

      await test.step('Verify complexity question is skipped', async () => {
        // Should skip directly to financial questions or recommendations
        // since divorce + other orders = automatically contested
        
        await wizardPage.page.waitForTimeout(2000); // Give time for processing
        const currentUrl = wizardPage.page.url();
        const pageContent = await wizardPage.page.content();
        
        // Should NOT be on the divorce complexity question
        expect(pageContent).not.toContain('contested or uncontested');
        
        // Should be on financial situation or recommendations
        const hasFinancialQuestion = pageContent.includes('financial situation');
        const hasRecommendations = pageContent.includes('Personalized Forms Package');
        
        expect(hasFinancialQuestion || hasRecommendations).toBe(true);
      });
    });

    test('should ask complexity for divorce only cases', async () => {
      await test.step('Start married divorce only case', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('married');
        
        // Select ONLY divorce
        await wizardPage.handleOrdersSought({
          divorce: true,
          custody: false,
          child_support: false,
          spousal_support: false,
          property: false,
          exclusive_possession: false,
          restraining_order: false,
          enforcement: false,
          other: false
        });
      });

      await test.step('Verify complexity question appears', async () => {
        await wizardPage.waitForQuestion('Is your divorce contested or uncontested?');
        
        // Should show complexity options
        expect(await wizardPage.page.locator('text=Uncontested').isVisible()).toBe(true);
        expect(await wizardPage.page.locator('text=Contested').isVisible()).toBe(true);
      });
    });
  });

  test.describe('Financial Form Selection', () => {
    test('should select Form 13 for lower property values', async () => {
      const scenario = testScenarios.married.separationOnly; // Uses 60000 property value
      
      await test.step('Complete flow with medium property value', async () => {
        await runCompleteScenario(wizardPage, scenario, 'medium_property_value');
      });

      await test.step('Verify Form 13 is selected over Form 13.1', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 13 for property value under 75000
        expect(recommendedForms.some(form => form.includes('Form 13') && !form.includes('13.1'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 13.1'))).toBe(false);
      });
    });

    test('should select Form 13.1 for higher property values', async () => {
      const scenario = testScenarios.married.divorceWithOtherOrders; // Uses 150000 property value
      
      await test.step('Complete flow with high property value', async () => {
        await runCompleteScenario(wizardPage, scenario, 'high_property_value');
      });

      await test.step('Verify Form 13.1 is selected', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 13.1 for property value over 75000
        expect(recommendedForms.some(form => form.includes('Form 13.1'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 13') && !form.includes('13.1'))).toBe(false);
      });
    });
  });

  test.describe('Court Selection Logic', () => {
    test('should direct divorce cases to Superior Court', async () => {
      const scenario = testScenarios.married.uncontestedDivorceNoChildren;
      
      await test.step('Complete divorce case', async () => {
        await runCompleteScenario(wizardPage, scenario, 'divorce_court_selection');
      });

      await test.step('Verify Superior Court for divorce', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Superior Court of Justice');
      });
    });

    test('should direct high-value property cases to Superior Court', async () => {
      const scenario = testScenarios.married.divorceWithOtherOrders; // High property value
      
      await test.step('Complete high-value property case', async () => {
        await runCompleteScenario(wizardPage, scenario, 'high_value_court_selection');
      });

      await test.step('Verify Superior Court for high value', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Superior Court of Justice');
      });
    });

    test('should direct lower-value cases to Ontario Court of Justice', async () => {
      const scenario = testScenarios.married.separationOnly; // Lower property value, no divorce
      
      await test.step('Complete lower-value case', async () => {
        await runCompleteScenario(wizardPage, scenario, 'lower_value_court_selection');
      });

      await test.step('Verify Ontario Court of Justice', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Ontario Court of Justice');
      });
    });
  });

  test.describe('Form Validation and Links', () => {
    test('should provide valid links for all recommended forms', async () => {
      const scenario = testScenarios.married.divorceWithOtherOrders;
      
      await test.step('Complete comprehensive married case', async () => {
        await runCompleteScenario(wizardPage, scenario, 'married_form_links');
      });

      await test.step('Verify all form links are valid', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        for (const form of recommendedForms) {
          // Extract form name for link checking
          const formName = form.substring(0, form.indexOf(' - ') + 1);
          if (formName) {
            const formLink = wizardPage.page.locator(`a:has-text("${formName.trim()}")`);
            if (await formLink.isVisible()) {
              const href = await formLink.getAttribute('href');
              expect(href, `Link for ${formName} should be valid`).toBeTruthy();
              expect(href, `Link for ${formName} should point to interview`).toContain('/interview?i=');
            }
          }
        }
      });
    });
  });

  test.describe('Edge Cases and Error Handling', () => {
    test('should handle back navigation correctly', async () => {
      await test.step('Navigate forward through married flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('married');
      });

      await test.step('Test back navigation', async () => {
        await wizardPage.page.goBack();
        await wizardPage.page.waitForLoadState('networkidle');
        
        // Should be back on MIP screen
        await wizardPage.waitForQuestion('MIP Session Information');
        
        // Should not show any errors
        await wizardPage.checkForErrors();
      });

      await test.step('Continue forward again', async () => {
        await wizardPage.clickContinue();
        await wizardPage.waitForQuestion('What is your relationship status?');
      });
    });

    test('should validate checkbox selections work correctly', async () => {
      await test.step('Navigate to orders selection', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(false);
        await wizardPage.handleMipQuestion('completed');
        await wizardPage.handleRelationshipStatus('married');
        await wizardPage.waitForQuestion('What orders are you seeking?');
      });

      await test.step('Test checkbox functionality', async () => {
        // Check multiple boxes
        await wizardPage.page.locator(wizardPage.seekingDivorceCheckbox).check();
        await wizardPage.page.locator(wizardPage.seekingCustodyCheckbox).check();
        await wizardPage.page.locator(wizardPage.seekingChildSupportCheckbox).check();
        
        // Verify they are checked
        expect(await wizardPage.page.locator(wizardPage.seekingDivorceCheckbox).isChecked()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.seekingCustodyCheckbox).isChecked()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.seekingChildSupportCheckbox).isChecked()).toBe(true);
        
        // Uncheck one
        await wizardPage.page.locator(wizardPage.seekingChildSupportCheckbox).uncheck();
        expect(await wizardPage.page.locator(wizardPage.seekingChildSupportCheckbox).isChecked()).toBe(false);
        
        // Others should still be checked
        expect(await wizardPage.page.locator(wizardPage.seekingDivorceCheckbox).isChecked()).toBe(true);
        expect(await wizardPage.page.locator(wizardPage.seekingCustodyCheckbox).isChecked()).toBe(true);
      });
    });
  });
});