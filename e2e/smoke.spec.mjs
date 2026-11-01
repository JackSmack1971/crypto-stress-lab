import { expect, test } from '@playwright/test';

const invalidSavedMessage = 'Saved inputs were invalid; demo loaded';

async function openApp(page) {
  await page.goto('/');
}

function savedDemoState() {
  return {
    version: 1,
    value: 100000,
    days: 30,
    baseCorrelation: 0.35,
    stressCorrelation: 0.85,
    multiplier: 1,
    preset: 'selloff',
    assets: [
      { id: 'btc', symbol: 'BTC', group: 'bitcoin', weight: 45, volatility: 65, shock: -25 },
      { id: 'eth', symbol: 'ETH', group: 'ethereum', weight: 30, volatility: 85, shock: -35 },
      { id: 'sol', symbol: 'SOL', group: 'altcoin', weight: 15, volatility: 110, shock: -50 },
      { id: 'usdc', symbol: 'USDC', group: 'stable', weight: 10, volatility: 5, shock: -2 }
    ]
  };
}

test('loads the demo scenario without console errors or external requests', async ({ page }) => {
  const consoleErrors = [];
  const pageErrors = [];
  const externalRequests = [];
  const localOrigin = new URL('http://127.0.0.1:4173').origin;
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.message));
  page.on('request', request => {
    if (new URL(request.url()).origin !== localOrigin) externalRequests.push(request.url());
  });

  await openApp(page);

  await expect(page.locator('#errors')).toBeHidden();
  await expect(page.locator('#results')).toBeVisible();
  await expect(page.locator('#metric-drawdown')).toHaveText('29.45%');
  expect(consoleErrors).toEqual([]);
  expect(pageErrors).toEqual([]);
  expect(externalRequests).toEqual([]);
});

test('restores the saved portfolio value after reload', async ({ page }) => {
  await openApp(page);
  await page.locator('#portfolio-value').fill('250000');
  await expect(page.locator('#save-status')).toHaveText('Saved in this browser');

  await page.reload();

  await expect(page.locator('#portfolio-value')).toHaveValue('250000');
  await expect(page.locator('#toast')).toHaveText('Restored your saved inputs');
  await expect(page.locator('#save-status')).toHaveText('Saved in this browser');
});

test('shows invalid allocation errors and normalizes back to results', async ({ page }) => {
  await openApp(page);
  await page.locator('[data-id="btc"] [data-field="weight"]').fill('40');

  await expect(page.locator('#errors')).toBeVisible();
  await expect(page.locator('#results')).toBeHidden();
  await expect(page.locator('#export')).toBeDisabled();

  await page.locator('#normalize').click();

  await expect(page.locator('#errors')).toBeHidden();
  await expect(page.locator('#results')).toBeVisible();
  await expect(page.locator('#export')).toBeEnabled();
});

test('falls back to demo for duplicate asset ids in saved state', async ({ page }) => {
  const invalidState = savedDemoState();
  invalidState.assets[1].id = invalidState.assets[0].id;
  await page.addInitScript(state => localStorage.setItem('crypto-stress-lab:v1', JSON.stringify(state)), invalidState);

  await openApp(page);

  await expect(page.locator('#toast')).toHaveText(invalidSavedMessage);
  await expect(page.locator('#asset-count')).toHaveText('4');
  await expect(page.locator('[data-id="btc"]')).toHaveCount(1);
  await expect(page.locator('#results')).toBeVisible();
});

test('falls back to demo for malformed saved JSON', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('crypto-stress-lab:v1', '{not json'));

  await openApp(page);

  await expect(page.locator('#toast')).toHaveText(invalidSavedMessage);
  await expect(page.locator('#asset-count')).toHaveText('4');
  await expect(page.locator('#results')).toBeVisible();
});

test('adds a focused asset, edits only the selected asset, and removes the new asset', async ({ page }) => {
  await openApp(page);
  await page.locator('#add-asset').click();

  await expect(page.locator('#asset-count')).toHaveText('5');
  const newAsset = page.locator('#asset-list .asset-card').nth(4);
  await expect(newAsset.locator('.symbol-input')).toBeFocused();
  await newAsset.locator('[data-field="weight"]').fill('5');

  const btcWeight = page.locator('[data-id="btc"] [data-field="weight"]');
  const ethWeight = page.locator('[data-id="eth"] [data-field="weight"]');
  const btcAttributionWeight = page.locator('#attribution tr').nth(0).locator('td').nth(0);
  const ethAttributionWeight = page.locator('#attribution tr').nth(1).locator('td').nth(0);
  await ethWeight.fill('25');
  await expect(ethWeight).toHaveValue('25');
  await expect(btcWeight).toHaveValue('45');
  await expect(page.locator('#weight-total')).toHaveText('100.00%');
  await expect(btcAttributionWeight).toHaveText('45.00%');
  await expect(ethAttributionWeight).toHaveText('25.00%');

  await page.getByRole('button', { name: 'Remove ASSET5' }).click();
  await expect(page.locator('#asset-count')).toHaveText('4');
});

test('exports a BOM-prefixed CSV with headers, scenario, and neutralized formula text', async ({ page }) => {
  await openApp(page);
  await page.locator('[data-id="btc"] [data-field="symbol"]').fill('=SUM(1)');

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#export').click()
  ]);
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const csv = Buffer.concat(chunks).toString('utf8');

  expect(csv.startsWith('\uFEFF')).toBe(true);
  expect(csv).toContain('"Asset","Group","Weight %","Annual volatility %","Base shock %","Effective shock %","Scenario P&L USD","Stressed variance risk share %"');
  expect(csv).toContain('"Scenario","Broad selloff"');
  expect(csv).toContain('"\'=SUM(1)","bitcoin"');
});

test('resets to the demo portfolio after accepting the confirmation', async ({ page }) => {
  await openApp(page);
  await page.locator('#portfolio-value').fill('250000');
  page.once('dialog', dialog => dialog.accept());
  await page.locator('#reset').click();

  await expect(page.locator('#portfolio-value')).toHaveValue('100000');
  await expect(page.locator('#asset-count')).toHaveText('4');
  await expect(page.locator('#toast')).toHaveText('Demo portfolio restored.');
});

test('fits the page within a 375px viewport', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await openApp(page);

  const dimensions = await page.evaluate(() => ({
    viewportWidth: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth
  }));
  expect(dimensions.documentWidth).toBeLessThanOrEqual(dimensions.viewportWidth);
});
