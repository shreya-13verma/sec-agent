import { test, expect } from '@playwright/test';

test.describe('Authentication & Navigation (TC-016)', () => {
  test('Unauthenticated user is redirected to login', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/.*login/);
    await expect(page.getByText('SUSE MLM Security & Compliance Agent')).toBeVisible();
  });

  test('Valid login redirects to dashboard and preserves session', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Enter username"]', 'admin');
    await page.fill('input[placeholder="Enter password"]', 'admin123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/');
    await expect(page.getByText('Fleet Posture & Agent Executive Summary')).toBeVisible();
    await expect(page.getByText('Registered Hosts', { exact: true })).toBeVisible();
  });

  test('Navigation through all primary sections works seamlessly', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[placeholder="Enter username"]', 'admin');
    await page.fill('input[placeholder="Enter password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');

    // Navigate to Hosts
    await page.click('a[href="/hosts"]');
    await expect(page).toHaveURL('/hosts');
    await expect(page.getByText('Host Inventory & MLM Registered Systems')).toBeVisible();

    // Navigate to Compliance
    await page.click('a[href="/compliance"]');
    await expect(page).toHaveURL('/compliance');
    await expect(page.getByText('Compliance & Regulatory Hardening Audits')).toBeVisible();

    // Navigate to Agent Console
    await page.click('a[href="/agent"]');
    await expect(page).toHaveURL('/agent');
    await expect(page.getByText('Autonomous Agent Reasoning & Posture Engine')).toBeVisible();

    // Navigate to Remediations
    await page.click('a[href="/remediation"]');
    await expect(page).toHaveURL('/remediation');
    await expect(page.getByText('Controlled Remediation Engine & Human Approval Gate')).toBeVisible();

    // Navigate to Reports
    await page.click('a[href="/reports"]');
    await expect(page).toHaveURL('/reports');
    await expect(page.getByText('Audit-Ready Compliance Reporting & Dossier Export')).toBeVisible();

    // Navigate to Audit Logs
    await page.click('a[href="/audit-logs"]');
    await expect(page).toHaveURL('/audit-logs');
    await expect(page.getByText('Immutable Security & Operational Audit Log')).toBeVisible();
  });
});
