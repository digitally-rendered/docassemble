// Playwright Configuration for Ontario Family Law Form Tests
// Generated: 2025-09-05

const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // Test directory
  testDir: './',
  
  // Test match pattern
  testMatch: 'test_form_*.spec.js',
  
  // Maximum time one test can run
  timeout: 60 * 1000, // 60 seconds per test
  
  // Global timeout for the whole test suite
  globalTimeout: 60 * 60 * 1000, // 1 hour total
  
  // Number of workers (parallel execution)
  workers: process.env.CI ? 1 : 4,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'test-results/html', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],
  
  // Retry failed tests
  retries: process.env.CI ? 2 : 1,
  
  // Shared settings for all projects
  use: {
    // Base URL for the application
    baseURL: process.env.DOCASSEMBLE_URL || 'http://localhost:8080',
    
    // Browser viewport
    viewport: { width: 1280, height: 720 },
    
    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,
    
    // Collect trace on failure
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Slow down actions for debugging (set to 0 in production)
    launchOptions: {
      slowMo: process.env.DEBUG ? 100 : 0,
    },
    
    // Action timeout
    actionTimeout: 10 * 1000, // 10 seconds
    
    // Navigation timeout
    navigationTimeout: 30 * 1000, // 30 seconds
  },
  
  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    // Uncomment to test on other browsers
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
    
    // Mobile testing
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],
  
  // Run local dev server before starting tests (if needed)
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
  
  // Output folder for test artifacts
  outputDir: 'test-results/artifacts',
  
  // Preserve output between test runs
  preserveOutput: 'failures-only',
  
  // Fail the build on test failure
  forbidOnly: !!process.env.CI,
  
  // Update snapshots in CI
  updateSnapshots: process.env.CI ? 'none' : 'missing',
});