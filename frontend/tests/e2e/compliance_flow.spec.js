import { test, expect } from '@playwright/test';

test.describe('SUSE MLM Security & Compliance Agent E2E Verification', () => {

  test('TC-013: Frontend renders initial Header, Navigation, and Agent Chat', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    await page.goto('/');

    // Verify Title and FastMCP status
    await expect(page.locator('text=SUSE MLM Security Agent')).toBeVisible();
    await expect(page.locator('text=MLM Connected')).toBeVisible();
    await expect(page.locator('text=FastMCP v1.0')).toBeVisible();

    // Verify Navigation Tabs in Header
    await expect(page.locator('header').getByRole('button', { name: 'Agent Chat', exact: true })).toBeVisible();
    await expect(page.locator('header').getByRole('button', { name: 'Fleet Posture', exact: true })).toBeVisible();
    await expect(page.locator('header').getByRole('button', { name: 'Report Center', exact: true })).toBeVisible();

    // Verify Prompt Chips & Input
    await expect(page.locator('input[placeholder*="Ask SUSE Compliance Agent"]')).toBeVisible();
    await expect(page.locator('text=Prompts:')).toBeVisible();

    expect(consoleErrors).toHaveLength(0);
  });

  test('TC-014: Conversational OpenSCAP inquiry streams response and reasoning trace for live server', async ({ page }) => {
    await page.goto('/');

    // Type and send compliance inquiry
    const input = page.locator('input[placeholder*="Ask SUSE Compliance Agent"]');
    await input.fill('Which production servers failed CIS benchmark audits?');
    await page.locator('button:has-text("Send")').click();

    // Verify thought trace visualizer appears
    await expect(page.locator('text=Agent Reasoning & FastMCP Traces')).toBeVisible({ timeout: 15000 });

    // Verify markdown tables with OpenSCAP results render
    await expect(page.locator('text=OpenSCAP Compliance Audit Results')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('text=Disable SSH Root Login')).toBeVisible({ timeout: 15000 });
  });

  test('TC-015: Human-in-the-loop remediation proposal renders approval card and executes upon approval', async ({ page }) => {
    await page.goto('/');

    // Send remediation request for live server
    const input = page.locator('input[placeholder*="Ask SUSE Compliance Agent"]');
    await input.fill('Please patch and remediate pending security errata on server trento-server');
    await page.locator('button:has-text("Send")').click();

    // Verify approval card renders
    await expect(page.locator('text=Human-in-the-Loop Remediation Review')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Target Server ID:')).toBeVisible();

    // Click Approve & Deploy
    const approveBtn = page.locator('button:has-text("Approve & Deploy")');
    await expect(approveBtn).toBeVisible();
    await approveBtn.click();

    // Verify approval confirmation and Action ID
    await expect(page.locator('text=Remediation Approved!')).toBeVisible({ timeout: 10000 });
  });

  test('TC-016: Fleet Posture and Report Center generation and export with live hosts', async ({ page }) => {
    await page.goto('/');

    // Navigate to Fleet Posture
    await page.locator('header').getByRole('button', { name: 'Fleet Posture', exact: true }).click();
    await expect(page.locator('text=FLEET COMPLIANCE')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=trento-server').first()).toBeVisible();

    // Navigate to Report Center
    await page.locator('header').getByRole('button', { name: 'Report Center', exact: true }).click();
    await expect(page.locator('text=Compliance & Vulnerability Report Generator')).toBeVisible();

    // Click Generate Compliance Report
    const genBtn = page.locator('button:has-text("Generate Compliance Report")');
    await genBtn.scrollIntoViewIfNeeded();
    await genBtn.click();

    // Verify download buttons appear in the archive list
    await expect(page.locator('a:has-text("PDF")').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('a:has-text("CSV")').first()).toBeVisible();
    await expect(page.locator('a:has-text("JSON")').first()).toBeVisible();
  });

});
