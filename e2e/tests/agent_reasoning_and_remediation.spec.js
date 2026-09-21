import { test, expect } from '@playwright/test';

test.describe('Autonomous Agent Reasoning & Controlled Remediation (TC-019, TC-020)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Enter username"]', 'sec_officer');
    await page.fill('input[placeholder="Enter password"]', 'sec123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  test('Autonomous agent reasoning trace generation and drift detection', async ({ page }) => {
    await page.goto('/agent');
    await expect(page.getByText('Autonomous Agent Reasoning & Posture Engine')).toBeVisible();

    // Trigger analysis
    const runBtn = page.getByRole('button', { name: /Run Autonomous Analysis/i });
    await runBtn.click();

    // Verify thought steps appear with exact match or prefix
    await expect(page.getByText(/Step 1: OBSERVATION/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Step 2: CORRELATION/i)).toBeVisible();
    await expect(page.getByText(/Step 3: RISK_EVALUATION/i)).toBeVisible();
    await expect(page.getByText(/Step 4: DECISION/i)).toBeVisible();

    // Verify Review Staged Plan button is enabled
    const reviewBtn = page.getByRole('button', { name: /Review Staged Plan in Remediation Manager/i });
    await expect(reviewBtn).toBeVisible();
  });

  test('Controlled Remediation Approval Gate and Execution', async ({ page }) => {
    // 1. Ensure an analysis is run first to have a staged plan
    await page.goto('/agent');
    await page.getByRole('button', { name: /Run Autonomous Analysis/i }).click();
    await expect(page.getByText(/Step 4: DECISION/i)).toBeVisible({ timeout: 10000 });

    // 2. Go to Remediations
    await page.goto('/remediation');
    await expect(page.getByText('Controlled Remediation Engine & Human Approval Gate')).toBeVisible();

    // 3. If there is an Approve button, click it to open approval modal
    const approveBtn = page.locator('button:has-text("Approve")').first();
    if (await approveBtn.isVisible()) {
      await approveBtn.click();
      await expect(page.getByText('Approve Staged Remediation Plan')).toBeVisible();
      await page.click('button:has-text("Confirm Approval")');
      // Verify execute button appears after approval
      await expect(page.locator('button:has-text("Execute Remediation Actions")')).toBeVisible({ timeout: 8000 });
    }

    // 4. If Execute button is visible, execute
    const execBtn = page.locator('button:has-text("Execute Remediation Actions")').first();
    if (await execBtn.isVisible()) {
      await execBtn.click();
      await expect(page.getByText('Fully Executed & Verified')).toBeVisible({ timeout: 12000 });
    }
  });
});
