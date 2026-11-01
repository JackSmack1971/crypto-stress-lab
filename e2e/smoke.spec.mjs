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
  expect(csv).toContain('"99% normal model downside %"');
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
  for (const id of ['#downside-usd', '#downside-99-usd', '#expected-shortfall-95-usd', '#expected-shortfall-99-usd']) {
    await expect(page.locator(id)).toBeVisible();
    await expect(page.locator(id)).toContainText('$');
  }
});

test('sensitivity heatmap selects metrics, marks nearest settings, and scrolls by keyboard', async ({ page }) => {
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  const state=savedDemoState();state.preset='custom';
  state.assets[0]={...state.assets[0],weight:20,shock:300};
  state.assets[1]={...state.assets[1],weight:80,shock:-100};
  state.assets[2]={...state.assets[2],weight:0,shock:-100};
  state.assets[3]={...state.assets[3],weight:0,shock:-100};
  await page.addInitScript(saved=>localStorage.setItem('crypto-stress-lab:v1',JSON.stringify(saved)),state);
  await page.setViewportSize({width:375,height:812});await openApp(page);
  const metric=page.locator('#sensitivity-metric'),table=page.locator('#sensitivity-table');
  await expect(metric).toHaveValue('volatility');
  await expect(page.locator('#sensitivity-note')).toContainText('rows are identical');
  await expect(table.locator('caption')).toContainText('Horizon volatility');
  await expect(page.locator('[data-current-setting="true"]')).toHaveCount(1);
  await expect(page.locator('[data-current-setting="true"]')).toHaveAttribute('data-rho','0.8');
  const initial=await table.locator('tbody tr').nth(0).locator('td').nth(0).textContent();
  await metric.selectOption('scenarioReturn');
  await expect(page.locator('#sensitivity-note')).toContainText('columns are identical');
  const changed=await table.locator('tbody tr').nth(0).locator('td').nth(0).textContent();
  expect(changed).not.toBe(initial);
  const colors=await table.locator('tbody tr').evaluateAll(rows=>[0,1,12].map(index=>rows[index].cells[1].style.backgroundColor.match(/[\d.]+/g).slice(0,3).map(Number)));
  expect(colors[1][0]).toBeGreaterThan(colors[1][1]);
  expect(colors[0]).toEqual([40,48,60]);
  expect(colors[2][1]).toBeGreaterThan(colors[2][0]);
  const scroll=page.locator('.heatmap-scroll');await scroll.focus();await expect(scroll).toBeFocused();
  await expect(scroll).toHaveAttribute('tabindex','0');
  const scrollBefore=await scroll.evaluate(element=>element.scrollLeft);await page.keyboard.press('ArrowRight');
  expect(await scroll.evaluate(element=>element.scrollLeft)).toBeGreaterThan(scrollBefore);
  const contrast=await table.locator('tbody td').evaluateAll(cells=>cells.map(cell=>{
    const rgb=getComputedStyle(cell).color.match(/[\d.]+/g).slice(0,3).map(Number);
    const bg=getComputedStyle(cell).backgroundColor.match(/[\d.]+/g).slice(0,3).map(Number);
    const luminance=values=>values.map(value=>{const channel=value/255;return channel<=.04045?channel/12.92:((channel+.055)/1.055)**2.4;}).reduce((sum,value,index)=>sum+value*[.2126,.7152,.0722][index],0);
    const light=luminance(rgb),dark=luminance(bg);return (Math.max(light,dark)+.05)/(Math.min(light,dark)+.05);
  }));
  expect(Math.min(...contrast)).toBeGreaterThanOrEqual(4.5);
  const dimensions=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
  expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport);
  expect(errors).toEqual([]);
});

test('reverse stress updates locally and keeps its validation out of the global banner', async ({ page }) => {
  await openApp(page);
  await expect(page.locator('#reverse-result')).toContainText('−20.00%');
  const saved = await page.evaluate(() => localStorage.getItem('crypto-stress-lab:v1'));
  await page.locator('#reverse-mode').selectOption('asset');
  await page.locator('#reverse-selection').selectOption('BTC');
  await page.locator('#reverse-target').fill('50');
  await expect(page.locator('#reverse-result')).toContainText('Unreachable');
  await expect(page.locator('#reverse-result')).toContainText('$45,000.00');
  await expect(page.locator('#errors')).toBeHidden();
  await expect(page.locator('#results')).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem('crypto-stress-lab:v1'))).toBe(saved);
  await page.setViewportSize({ width: 375, height: 812 });
  const dimensions = await page.evaluate(() => ({viewport:innerWidth,document:document.documentElement.scrollWidth}));
  expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport);
});

test('reverse controls work from the keyboard and asset symbols render as option text', async ({ page }) => {
  const pageErrors=[];
  page.on('pageerror',error=>pageErrors.push(error.message));
  await openApp(page);
  await page.locator('#reverse-unit').focus();
  await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page.locator('#reverse-unit')).toHaveValue('usd');
  await page.locator('#reverse-mode').focus();
  await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page.locator('#reverse-mode')).toHaveValue('asset');
  await page.locator('#reverse-selection').focus();
  await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(page.locator('#reverse-selection')).toHaveValue('ETH');
  const target=page.locator('#reverse-target');await target.focus();await page.keyboard.press('Control+A');await page.keyboard.type('1000');
  await expect(page.locator('#reverse-result')).toContainText('required uniform shock');
  await page.locator('[data-id="eth"] [data-field="symbol"]').fill('<img src=x>');
  await expect(page.locator('#reverse-selection')).toContainText('<img src=x>');
  await expect(page.locator('#reverse-selection img')).toHaveCount(0);
  expect(pageErrors).toEqual([]);
});
