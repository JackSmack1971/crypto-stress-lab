import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sampleState, validate } from '../dist/engine.mjs';
import { restoreState, csvCell, serializeCsv, toCsvRows } from '../dist/persistence.mjs';
import { calculate } from '../dist/engine.mjs';

test('corrupt saved state falls back to demo and reports invalid data', () => {
  const demo = sampleState();
  for (const raw of ['{', 'null', '[]', JSON.stringify({ ...demo, assets: [null] })]) {
    const restored = restoreState(raw, demo);
    assert.equal(restored.state, demo);
    assert.equal(restored.message, 'Saved inputs were invalid; demo loaded');
  }
});

test('valid saved state restores and empty storage quietly uses demo', () => {
  const demo = sampleState();
  const saved = { ...demo, value: 25000 };
  assert.deepEqual(restoreState(JSON.stringify(saved), demo), { state: saved, message: 'Restored your saved inputs' });
  assert.deepEqual(restoreState(null, demo), { state: demo, message: '' });
});

test('unsupported versions and non-array assets fall back to demo', () => {
  const demo = sampleState();
  for (const raw of [JSON.stringify({ ...demo, version: 2 }), '5', JSON.stringify({ ...demo, assets: 'BTC' })]) {
    assert.deepEqual(restoreState(raw, demo), { state: demo, message: 'Saved inputs were invalid; demo loaded' });
  }
});

test('validation reports non-object assets without throwing', () => {
  for (const asset of [null, 'BTC', 4, []]) {
    const state = sampleState();
    state.assets = [asset];
    assert.doesNotThrow(() => validate(state));
    assert.ok(validate(state).some(error => error.includes('asset must be an object')));
  }
  assert.ok(validate(null).length);
});

test('CSV quoting and formula-like strings are safe', () => {
  assert.equal(csvCell('=SUM(A1:A2)'), `"'=SUM(A1:A2)"`);
  assert.equal(csvCell('a,"b"'), `"a,""b"""`);
  assert.equal(serializeCsv([['name', '=1+1'], ['line\nbreak', 2]]), `"name","'=1+1"\r\n"line\nbreak","2"`);
});

test('CSV rows include the asset header and blank risk shares at zero variance', () => {
  const state = sampleState();
  state.assets.forEach(asset => { asset.volatility = 0; });
  const result = calculate(state);
  const rows = toCsvRows(state, result);
  const headerIndex = rows.findIndex(row => row[0] === 'Asset');
  assert.deepEqual(rows[headerIndex], ['Asset','Group','Weight %','Annual volatility %','Base shock %','Effective shock %','Scenario P&L USD','Stressed variance risk share %']);
  assert.deepEqual(rows.slice(headerIndex + 1, headerIndex + 1 + state.assets.length).map(row => row[7]), ['', '', '', '']);
});

test('CSV appends Gaussian tail metrics after an exact legacy row prefix', () => {
  const state = sampleState();
  const result = calculate(state);
  const rows = toCsvRows(state, result);
  const limitationsIndex = rows.findIndex(row => row[0] === 'Limitations');
  const prefix = rows.slice(0, limitationsIndex + 1);
  const legacyPrefix = [
    ['Crypto Stress Lab — hypothetical scenario results'], rows[1], ['Portfolio value USD',state.value], ['Scenario',state.preset],
    ['Shock multiplier',state.multiplier], ['Risk horizon days',state.days], ['Baseline correlation',state.baseCorrelation], ['Stressed correlation',state.stressCorrelation], [],
    ['Asset','Group','Weight %','Annual volatility %','Base shock %','Effective shock %','Scenario P&L USD','Stressed variance risk share %'],
    ...result.assets.map(a=>[a.symbol,a.group,a.weight,a.volatility,a.shock,a.effectiveShock*100,a.pnl,result.stressedSigma===0?'':a.riskShare*100]),
    [], ['Metric','Value'], ['Scenario return %',result.portfolioReturn*100], ['Scenario drawdown %',result.drawdown*100], ['Scenario P&L USD',result.pnl],
    ['Ending value USD',result.endValue], ['Baseline horizon volatility %',result.baselineSigma*result.horizonScale*100],
    ['Stressed horizon volatility %',result.stressedSigma*result.horizonScale*100], ['95% normal model downside %',result.stressedDownside*100],
    ['HHI',result.hhi], ['Effective positions',result.effectiveAssets], ['Equal-weight scenario return %',result.equalReturn*100],
    ['Equal-weight horizon volatility %',result.equalSigma*result.horizonScale*100], [], ['Preset comparison','Return %'],
    ...result.comparisons.map(a=>[a.name,a.return*100]), [], ['Limitations','Hypothetical long-only spot model. No fees, liquidity, leverage, liquidation, taxes or path effects. Scenario drawdown is a one-step loss, not maximum path drawdown. Common equicorrelation normal risk model; no forecasts.']
  ];
  assert.match(rows[1][1], /^\d{4}-\d\d-\d\dT.*Z$/);
  assert.deepEqual(prefix, legacyPrefix);
  assert.deepEqual(rows.slice(prefix.length), [
    [], ['Gaussian tail risk (stressed)'], ['Metric','Value'],
    ['99% normal model downside %',result.stressedDownside99*100],
    ['95% normal model expected shortfall %',result.stressedExpectedShortfall95*100],
    ['99% normal model expected shortfall %',result.stressedExpectedShortfall99*100],
    ['95% normal model downside USD',result.stressedDownside*state.value],
    ['99% normal model downside USD',result.stressedDownside99*state.value],
    ['95% normal model expected shortfall USD',result.stressedExpectedShortfall95*state.value],
    ['99% normal model expected shortfall USD',result.stressedExpectedShortfall99*state.value]
  ]);
});

test('duplicate asset ids fall back to demo and report invalid data', () => {
  const demo = sampleState();
  const duplicateAssets = demo.assets.map(asset => ({ ...asset }));
  duplicateAssets[1].id = duplicateAssets[0].id;
  const saved = { ...demo, assets: duplicateAssets };
  assert.deepEqual(restoreState(JSON.stringify(saved), demo), {
    state: demo,
    message: 'Saved inputs were invalid; demo loaded'
  });
});
