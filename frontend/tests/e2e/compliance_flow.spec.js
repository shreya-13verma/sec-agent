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

    // Verify Navigation Tabs
    await expect(page.locator('button:has-text("Agent Chat")')).toBeVisible();
    await expect(page.locator('button:has-text("Fleet Posture")')).toBeVisible();
    await expect(page.locator('button:has-text("Report Center")')).toBeVisible();

    // Verify Prompt Chips & Input
    await expect(page.locator('input[placeholder*="Ask SUSE Compliance Agent"]')).toBeVisible();
    await expect(page.locator('text=Prompts:')).toBeVisible();

    expect(consoleErrors).toHaveLength(0);
  });

  test('TC-014: Conversational OpenSCAP inquiry streams response and reasoning trace', async ({ page }) => {
    await page.goto('/');

    // Type and send compliance inquiry
    const input = page.locator('input[placeholder*="Ask SUSE Compliance Agent"]');
    await input.fill('Which production servers failed CIS benchmark audits?');
    await page.locator('button:has-text("Send")').click();

    // Verify thought trace visualizer appears
    await expect(page.locator('text=Agent Reasoning & FastMCP Traces')).toBeVisible({ timeout: 10000 });

    // Verify markdown tables with OpenSCAP results render
    await expect(page.locator('text=OpenSCAP Compliance Audit Results')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Disable SSH Root Login')).toBeVisible({ timeout: 10000 });
  });

  test('TC-015: Human-in-the-loop remediation proposal renders approval card and executes upon approval', async ({ page }) => {
    await page.goto('/');

    // Send remediation request
    const input = page.locator('input[placeholder*="Ask SUSE Compliance Agent"]');
    await input.fill('Please patch and remediate pending security errata on server 1001');
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

  test('TC-016: Fleet Posture and Report Center generation and export', async ({ page }) => {
    await page.goto('/');

    // Navigate to Fleet Posture
    await page.locator('button:has-text("Fleet Posture")').click();
    await expect(page.locator('text=FLEET COMPLIANCE')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=sles15-sp5-web-prod01').first()).toBeVisible();

    // Navigate to Report Center
    await page.locator('button:has-text("Report Center")').click();
    await expect(page.locator('text=Compliance & Vulnerability Report Generator')).toBeVisible();

    // Click Generate Compliance Report
    const genBtn = page.locator('button:has-text("Generate Compliance Report")');
    await genBtn.click();

    // Verify success banner and download buttons
    await expect(page.locator('text=Report generated successfully!')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('a:has-text("PDF")').first()).toBeVisible();
    await expect(page.locator('a:has-text("CSV")').first()).toBeVisible();
    await expect(page.locator('a:has-text("JSON")').first()).toBeVisible();
  });

});
