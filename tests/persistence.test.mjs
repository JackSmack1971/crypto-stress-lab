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
