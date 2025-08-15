const { test, expect } = require('@playwright/test');
const { WizardPage } = require('../pages/WizardPage');
const { testScenarios } = require('../fixtures/test-data');
const { 
  runCompleteScenario, 
  validateRecommendedForms,
  validateFinancialFormsPresence,
  validateCustodyFormsPresence,
  takeDebugScreenshot 
} = require('../utils/test-helpers');

/**
 * Emergency Pathways Test Suite
 * Tests all emergency scenarios where users need immediate filing
 */
test.describe('Emergency Pathways', () => {
  let wizardPage;

  test.beforeEach(async ({ page }) => {
    wizardPage = new WizardPage(page);
  });

  test.describe('Emergency - Married Scenarios', () => {
    test('should handle emergency divorce only scenario', async () => {
      const scenario = testScenarios.emergency.emergencyDivorceOnly;
      
      await test.step('Complete emergency divorce only flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'emergency_divorce_only');
      });

      await test.step('Verify emergency forms are included', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include emergency forms
        expect(recommendedForms.some(form => form.includes('Form 8'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 14'))).toBe(true);
        
        // Should not include financial forms for divorce only
        validateFinancialFormsPresence(recommendedForms, false);
      });

      await test.step('Verify emergency timeline and court', async () => {
        const timeline = await wizardPage.getTimeline();
        const court = await wizardPage.getCourt();
        
        expect(timeline).toContain('Immediate');
        expect(court).toContain('Superior Court');
      });
    });

    test('should handle emergency divorce with multiple orders', async () => {
      const scenario = testScenarios.emergency.emergencyDivorceMultiple;
      
      await test.step('Complete emergency divorce with multiple orders flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'emergency_divorce_multiple');
      });

      await test.step('Verify comprehensive forms are included', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should include emergency forms
        expect(recommendedForms.some(form => form.includes('Form 8'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 14'))).toBe(true);
        
        // Should include financial forms due to support claims
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should include custody forms due to custody claim
        validateCustodyFormsPresence(recommendedForms, true);
      });

      await test.step('Verify emergency status maintained', async () => {
        // Should still show immediate filing even with complex case
        const timeline = await wizardPage.getTimeline();
        expect(timeline).toContain('Immediate');
      });
    });
  });

  test.describe('Emergency - Common-Law Scenarios', () => {
    test('should handle emergency common-law multiple issues', async () => {
      const scenario = testScenarios.emergency.emergencyCommonLawMultiple;
      
      await test.step('Complete emergency common-law flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'emergency_common_law');
      });

      await test.step('Verify proper forms for common-law emergency', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 8 (General) not Form 8A (Divorce)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        expect(recommendedForms.some(form => form.includes('Form 8A'))).toBe(false);
        
        // Should include emergency forms
        expect(recommendedForms.some(form => form.includes('Form 14'))).toBe(true);
        
        // Should include financial forms for property/support
        validateFinancialFormsPresence(recommendedForms, true);
        
        // Should include custody forms
        validateCustodyFormsPresence(recommendedForms, true);
      });

      await test.step('Verify property value triggers correct financial form', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Property value of 100000 should trigger Form 13.1
        expect(recommendedForms.some(form => form.includes('Form 13.1'))).toBe(true);
      });

      await test.step('Verify correct court for property claims', async () => {
        const court = await wizardPage.getCourt();
        expect(court).toContain('Superior Court'); // High value property goes to Superior Court
      });
    });
  });

  test.describe('Emergency - Never Lived Together Scenarios', () => {
    test('should handle emergency never lived together case', async () => {
      const scenario = testScenarios.emergency.emergencyNeverTogether;
      
      await test.step('Complete emergency never together flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'emergency_never_together');
      });

      await test.step('Verify appropriate forms for never together case', async () => {
        const recommendedForms = await wizardPage.getRecommendedForms();
        
        // Should use Form 8 (General)
        expect(recommendedForms.some(form => form.includes('Form 8') && !form.includes('8A'))).toBe(true);
        
        // Should not include divorce forms
        expect(recommendedForms.some(form => form.includes('Form 8A'))).toBe(false);
        expect(recommendedForms.some(form => form.includes('Form 36'))).toBe(false);
        
        // Should include emergency forms
        expect(recommendedForms.some(form => form.includes('Form 14'))).toBe(true);
        
        // Should include financial and custody forms
        validateFinancialFormsPresence(recommendedForms, true);
        validateCustodyFormsPresence(recommendedForms, true);
      });

      await test.step('Verify correct court for never together case', async () => {
        const court = await wizardPage.getCourt();
        // Lower value case should go to Ontario Court of Justice
        expect(court).toContain('Ontario Court of Justice');
      });
    });
  });

  test.describe('Emergency Flow Validation', () => {
    test('should show emergency warning screen', async () => {
      await test.step('Navigate to wizard and start emergency flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(true);
      });

      await test.step('Verify emergency warning appears', async () => {
        await wizardPage.waitForQuestion('URGENT: Emergency Filing Required');
        
        // Check for emergency-specific content
        expect(await wizardPage.page.locator('text=URGENT').isVisible()).toBe(true);
        expect(await wizardPage.page.locator('text=call 911').isVisible()).toBe(true);
        expect(await wizardPage.page.locator('text=Assaulted Women\'s Helpline').isVisible()).toBe(true);
      });

      await test.step('Verify can continue after emergency warning', async () => {
        await wizardPage.handleEmergencyFormsScreen();
        
        // Should proceed to relationship status question
        await wizardPage.waitForQuestion('What is your relationship status?');
      });
    });

    test('should skip MIP for emergency cases', async () => {
      const scenario = testScenarios.emergency.emergencyDivorceOnly;
      
      await test.step('Start emergency flow', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        await wizardPage.handleEmergencyQuestion(true);
        await wizardPage.handleEmergencyFormsScreen();
      });

      await test.step('Verify MIP screen is skipped', async () => {
        // Should go directly to relationship status, not MIP
        await wizardPage.waitForQuestion('What is your relationship status?');
        
        // MIP question should not appear in emergency cases
        const pageContent = await wizardPage.page.content();
        expect(pageContent).not.toContain('Mandatory Information Program');
      });
    });

    test('should show emergency completion screen', async () => {
      const scenario = testScenarios.emergency.emergencyDivorceOnly;
      
      await test.step('Complete full emergency flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'emergency_completion');
      });

      await test.step('Verify emergency completion screen content', async () => {
        await wizardPage.waitForQuestion('Complete Case Assessment - EMERGENCY FILING REQUIRED');
        
        // Check for emergency-specific final screen content
        expect(await wizardPage.page.locator('text=IMMEDIATE ACTION REQUIRED').isVisible()).toBe(true);
        expect(await wizardPage.page.locator('text=File these forms TODAY').isVisible()).toBe(true);
        expect(await wizardPage.page.locator('text=Emergency: Yes').isVisible()).toBe(true);
      });
    });
  });

  test.describe('Emergency Error Handling', () => {
    test('should handle network issues gracefully during emergency flow', async () => {
      await test.step('Start emergency flow with network simulation', async () => {
        await wizardPage.goto();
        await wizardPage.handleIntroduction();
        
        // Simulate slow network
        await wizardPage.page.route('**/*', route => {
          setTimeout(() => route.continue(), 1000);
        });
        
        await wizardPage.handleEmergencyQuestion(true);
      });

      await test.step('Verify flow continues despite delays', async () => {
        await wizardPage.handleEmergencyFormsScreen();
        await wizardPage.waitForQuestion('What is your relationship status?');
        
        // Should not show any error messages
        await wizardPage.checkForErrors();
      });
    });

    test('should validate emergency form recommendations', async () => {
      const scenario = testScenarios.emergency.emergencyDivorceOnly;
      
      await test.step('Complete emergency flow', async () => {
        await runCompleteScenario(wizardPage, scenario, 'emergency_validation');
      });

      await test.step('Verify all emergency forms have valid links', async () => {
        const emergencyForms = ['Form 8', 'Form 14', 'Form 14A'];
        
        for (const formName of emergencyForms) {
          const formLink = wizardPage.page.locator(`a:has-text("${formName}")`);
          if (await formLink.isVisible()) {
            const href = await formLink.getAttribute('href');
            expect(href).toBeTruthy();
            expect(href).toContain('/interview?i=');
          }
        }
      });
    });
  });

  // Test to verify emergency forms are prioritized correctly
  test('should prioritize emergency forms in recommendations', async () => {
    const scenario = testScenarios.emergency.emergencyDivorceMultiple;
    
    await test.step('Complete complex emergency case', async () => {
      await runCompleteScenario(wizardPage, scenario, 'emergency_priority');
    });

    await test.step('Verify emergency forms appear first', async () => {
      // Navigate back to recommendations
      await wizardPage.page.goBack();
      await wizardPage.page.waitForLoadState('networkidle');
      
      const allFormText = await wizardPage.page.locator('text=Form').allTextContents();
      const emergencyFormIndices = allFormText.map((text, index) => 
        (text.includes('Form 8') || text.includes('Form 14')) ? index : -1
      ).filter(index => index !== -1);
      
      const otherFormIndices = allFormText.map((text, index) => 
        (text.includes('Form 13') || text.includes('Form 35.1')) ? index : -1
      ).filter(index => index !== -1);
      
      // Emergency forms should appear before other forms
      if (emergencyFormIndices.length > 0 && otherFormIndices.length > 0) {
        expect(Math.min(...emergencyFormIndices)).toBeLessThan(Math.min(...otherFormIndices));
      }
    });
  });
});