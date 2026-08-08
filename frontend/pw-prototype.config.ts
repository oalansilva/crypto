import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  fullyParallel: false,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:5175',
    headless: true,
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'gate',
      testMatch: /prototype-wallet-zebra\.spec\.cjs/,
      use: { viewport: { width: 1440, height: 900 } },
    },
  ],
});
