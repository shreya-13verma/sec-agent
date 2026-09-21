import { test, expect } from '@playwright/test';

test.describe('Host Discovery & Compliance Audits (TC-017, TC-018)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Enter username"]', 'admin');
    await page.fill('input[placeholder="Enter password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  test('Host search, filtering, and detail inspection', async ({ page }) => {
    await page.goto('/hosts');
    await expect(page.getByText('Host Inventory & MLM Registered Systems')).toBeVisible();

    // Test Search input
    await page.fill('input[placeholder*="Search by hostname"]', 'sles15-prod');
    await expect(page.getByText('sles15-prod-db01.corp.internal')).toBeVisible();

    // Click Inspect / View Details
    await page.click('text=View Details');
    await expect(page).toHaveURL(/.*hosts\/\d+/);
    await expect(page.getByText('Installed Packages')).toBeVisible();
    await expect(page.getByText('Missing Security Errata')).toBeVisible();

    // Toggle Tabs
    await page.click('button:has-text("Missing Security Errata")');
    await page.click('button:has-text("Subscribed MLM Channels")');
    await page.click('button:has-text("Installed Packages")');
  });

  test('Trigger Compliance Audit Scan and view findings breakdown', async ({ page }) => {
    await page.goto('/compliance');
    await expect(page.getByText('Compliance & Regulatory Hardening Audits')).toBeVisible();

    // Click Audit Fleet Now on CIS Benchmark card
    const auditBtn = page.locator('button:has-text("Audit Fleet Now")').first();
    await auditBtn.click();

    // Wait for findings to appear
    await expect(page.getByText('Audit Findings')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Recent Audit Runs')).toBeVisible();
  });
});
