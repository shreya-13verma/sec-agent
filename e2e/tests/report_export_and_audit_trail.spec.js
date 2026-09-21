import { test, expect } from '@playwright/test';

test.describe('Compliance Reporting & Audit Trail (TC-021, TC-022)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Enter username"]', 'admin');
    await page.fill('input[placeholder="Enter password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  test('Reports preview and export controls', async ({ page }) => {
    await page.goto('/reports');
    await expect(page.getByText('Audit-Ready Compliance Reporting & Dossier Export')).toBeVisible();
    await expect(page.getByText('Executive Security Posture Overview')).toBeVisible();
    await expect(page.getByRole('button', { name: /Export CSV/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Download PDF Report/i })).toBeVisible();
  });

  test('Audit trail logs display and filtering', async ({ page }) => {
    await page.goto('/audit-logs');
    await expect(page.getByText('Immutable Security & Operational Audit Log')).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible();
    await expect(page.getByText('USER_LOGIN_SUCCESS').first()).toBeVisible();
  });

  test('Settings configuration page loads and saves parameters', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.getByText('System Settings & Operational Parameters')).toBeVisible();
    await page.click('button[type="submit"]');
    await expect(page.getByText('Settings updated successfully')).toBeVisible();
  });
});
