import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:3030',
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 15000,
  },
  webServer: [
    {
      command: 'PYTHONPATH=/home/shreya/sec-agent /home/shreya/sec-agent/.venv/bin/uvicorn backend.app.main:app --port 8030 --host 0.0.0.0',
      port: 8030,
      timeout: 15000,
      reuseExistingServer: true,
    },
    {
      command: 'npm run dev -- --port 3030',
      port: 3030,
      timeout: 15000,
      reuseExistingServer: true,
    }
  ]
});
