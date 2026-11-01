import { defineConfig } from '@playwright/test';
import { existsSync } from 'node:fs';

const chromePathIsSet = Object.hasOwn(process.env, 'PW_CHROME_PATH');
const chromePath = process.env.PW_CHROME_PATH;
if (chromePathIsSet && !existsSync(chromePath)) {
  throw new Error('PW_CHROME_PATH is set but the file does not exist.');
}

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.mjs',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:4173',
    browserName: 'chromium',
    launchOptions: chromePathIsSet ? { executablePath: chromePath } : {},
    trace: 'retain-on-failure'
  },
  webServer: {
    command: 'node e2e/serve.mjs',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: !process.env.CI,
    timeout: 10_000
  }
});
