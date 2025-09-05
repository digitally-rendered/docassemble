import { test, expect } from '@playwright/test';

test.describe('Debug Interview Path', () => {
  test('check what loads at the interview URL', async ({ page }) => {
    const BASE_URL = 'http://localhost';
    const INTERVIEW_PATH = '/interview?i=docassemble.playground1:ontario-family-law/common_intake_enhanced_with_validation.yml';
    
    console.log('Attempting to load:', `${BASE_URL}${INTERVIEW_PATH}`);
    
    await page.goto(`${BASE_URL}${INTERVIEW_PATH}`);
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot to see what's actually loading
    await page.screenshot({ path: 'debug-interview-load.png', fullPage: true });
    
    // Get page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Get page URL
    const url = page.url();
    console.log('Actual URL:', url);
    
    // Check for any h1 elements
    const h1Elements = await page.locator('h1').allTextContents();
    console.log('H1 elements found:', h1Elements);
    
    // Check for any error messages
    const errorMessages = await page.locator('.alert-danger, .error, [class*="error"]').allTextContents();
    console.log('Error messages:', errorMessages);
    
    // Get the main content
    const bodyText = await page.locator('body').textContent();
    console.log('First 500 characters of body:', bodyText?.substring(0, 500));
    
    // Try alternative paths
    const altPaths = [
      '/interview?i=docassemble.base:ontario-family-law/common_intake_enhanced_with_validation.yml',
      '/interview?i=ontario-family-law/common_intake_enhanced_with_validation.yml',
      '/interview?i=docassemble.webapp:ontario-family-law/common_intake_enhanced_with_validation.yml'
    ];
    
    for (const altPath of altPaths) {
      console.log('\\nTrying alternative path:', altPath);
      try {
        await page.goto(`${BASE_URL}${altPath}`);
        await page.waitForLoadState('networkidle', { timeout: 5000 });
        const altTitle = await page.title();
        const altH1 = await page.locator('h1').allTextContents();
        console.log('Alt path title:', altTitle);
        console.log('Alt path H1s:', altH1);
      } catch (e) {
        console.log('Alt path failed:', e.message);
      }
    }
  });
});