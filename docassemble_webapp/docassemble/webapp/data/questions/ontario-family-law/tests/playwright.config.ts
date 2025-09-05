import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Ontario Family Law Common Intake tests
 */
export default defineConfig({
  testDir: './',
  testMatch: '**/*.spec.ts',
  
  // Maximum time one test can run
  timeout: 60000,
  
  // Maximum time the whole test suite can run
  globalTimeout: 600000,
  
  // Number of failures before stopping
  maxFailures: 5,
  
  // Retry failed tests
  retries: process.env.CI ? 2 : 1,
  
  // Number of parallel workers
  workers: process.env.CI ? 2 : 4,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'test-results/html' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],
  
  use: {
    // Base URL for the Docassemble instance
    baseURL: process.env.DOCASSEMBLE_URL || 'http://localhost:8080',
    
    // Browser options
    headless: process.env.CI ? true : false,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    // Artifacts
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
    
    // Timeouts
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  
  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  // Web server configuration (if running tests against local Docassemble)
  // Commented out - assuming server is already running on localhost:8080
  // webServer: process.env.CI ? undefined : {
  //   command: 'echo "Using existing Docassemble server"',
  //   port: 8080,
  //   reuseExistingServer: true,
  // },
  
  // Output folder for test artifacts
  outputDir: 'test-results/artifacts',
  
  // Preserve output between test runs
  preserveOutput: 'failures-only',
});