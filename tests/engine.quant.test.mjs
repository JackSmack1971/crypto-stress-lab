import { test } from 'node:test';
import assert from 'node:assert/strict';
import { calculate, normalizeWeights, sampleState, validate } from '../dist/engine.mjs';

const close = (actual, expected, tolerance = 1e-12) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} ≠ ${expected} (tol ${tolerance})`);
const stateWith = (assets, overrides = {}) => ({
  ...sampleState(), value: 100000, days: 365, baseCorrelation: 0.4,
  stressCorrelation: 0.7, multiplier: 1, assets, ...overrides
});
const asset = (symbol, weight, volatility = 20, shock = -10) =>
  ({ id: symbol, symbol, group: 'bitcoin', weight, volatility, shock });

// Preconditions: a valid one-asset portfolio; each scalar is tested at both accepted domain bounds.
test('validation accepts documented scalar and asset-count boundaries', () => {
  for (const [key, values] of Object.entries({
    value: [1, 1e12], days: [1, 365], baseCorrelation: [0, 1],
    stressCorrelation: [0, 1], multiplier: [0, 3]
  })) for (const value of values) {
    const s = stateWith([asset('A', 100)], { [key]: value });
    assert.deepEqual(validate(s), [], `${key}=${value}`);
  }
  for (const volatility of [0, 300]) {
    assert.deepEqual(validate(stateWith([asset('A', 100, volatility)])), []);
  }
  for (const shock of [-100, 300]) {
    assert.deepEqual(validate(stateWith([asset('A', 100, 20, shock)])), []);
  }
  assert.deepEqual(validate(stateWith([asset('A', 100)])), []);
  assert.deepEqual(validate(stateWith(Array.from({ length: 12 }, (_, i) => asset(`A${i}`, 100 / 12)))), []);
  assert.deepEqual(validate(stateWith([asset('A', 50.00000025), asset('B', 50)])), []);
  assert.ok(validate(stateWith([asset('A', 50.000001), asset('B', 50.000001)])).length > 0);
});

// Preconditions: valid baseline with 100% total weight; each malformed case changes one contract field.
test('validation rejects malformed counts, symbols, numbers, entries, and state', () => {
  assert.ok(validate(stateWith(Array.from({ length: 13 }, (_, i) => asset(`A${i}`, 100 / 13)))).length);
  assert.ok(validate(stateWith([asset('ABCDEFGHIJKLM', 100)])).length);
  assert.ok(validate(stateWith([asset(' BTC', 50), asset('btc ', 50)])).some(e => e.includes('unique')));
  for (const key of ['value', 'days', 'baseCorrelation', 'stressCorrelation', 'multiplier']) {
    for (const value of ['1', null]) {
      assert.ok(validate({ ...stateWith([asset('A', 100)]), [key]: value }).length);
    }
  }
  for (const key of ['weight', 'volatility', 'shock']) {
    for (const value of ['1', null]) {
      const malformed = asset('A', 100); malformed[key] = value;
      assert.ok(validate(stateWith([malformed])).length);
    }
  }
  for (const assets of [[null], [asset('A', 100), null], [asset('A', 100), []]]) {
    assert.ok(validate(stateWith(assets)).length);
  }
  for (const value of [null, [], 'state', 7]) assert.ok(validate(value).length);
});

// Preconditions: weights are 50/30/20%, annual volatilities 10/20/30%, rho=0.5, and horizon is 365 days.
// Exposures w*v are 0.05, 0.06, 0.06: their sum is 0.17 and squared sum is 0.0097.
// Variance is 0.5*0.0097 + 0.5*0.17^2 = 0.0193; unscaled Euler terms are
// 0.0055, 0.0069, 0.0069, giving shares 55/193, 69/193, 69/193.
test('hand-derived 50/30/20 portfolio risk and Euler shares', () => {
  const assets = [asset('A', 50, 10), asset('B', 30, 20), asset('C', 20, 30)];
  const result = calculate(stateWith(assets, { baseCorrelation: 0.5, stressCorrelation: 0.5, days: 365 }));
  close(result.stressedSigma ** 2, 0.0193);
  [55 / 193, 69 / 193, 69 / 193].forEach((share, i) => close(result.assets[i].riskShare, share, 1e-12));
});

// Preconditions: rho=0 makes variance the sum of squared weighted volatility exposures.
// Annual volatilities are chosen so exposures are sqrt(0.0055), sqrt(0.0069), sqrt(0.0069).
// Thus annual variance = 0.0055 + 0.0069 + 0.0069 = 0.0193 (fractional-return squared),
// and Euler shares are respectively 55/193, 69/193, 69/193.
test('three-asset independent-risk fixture matches hand-computed variance and Euler shares', () => {
  const exposures = [Math.sqrt(0.0055), Math.sqrt(0.0069), Math.sqrt(0.0069)];
  const weights = [0.5, 0.3, 0.2];
  const assets = weights.map((w, i) => asset(`A${i}`, 100 * w, 100 * exposures[i] / w));
  const result = calculate(stateWith(assets, { baseCorrelation: 0, stressCorrelation: 0 }));
  close(result.stressedSigma ** 2, 0.0193);
  [55 / 193, 69 / 193, 69 / 193].forEach((share, i) => close(result.assets[i].riskShare, share));
});

// Preconditions: two equal-weight assets; the first effective shock floors at -100%, the second remains -52%.
// Returns are -0.5 + -0.26 = -0.76; on $100,000 this is -$76,000 and ending value $24,000.
test('mixed capped and uncapped shock fixture matches hand-computed USD outcomes', () => {
  const result = calculate(stateWith([asset('A', 50, 20, -100), asset('B', 50, 20, -26)], { multiplier: 2 }));
  close(result.portfolioReturn, -0.76);
  close(result.pnl, -76000, 1e-8);
  close(result.endValue, 24000, 1e-8);
  assert.equal(result.capped, true);
});

// Preconditions: shocks, weights, days, and model assumptions fixed; only positive portfolio value is rescaled.
test('value scaling is linear for USD outputs and preserves fractional return', () => {
  const s = stateWith([asset('A', 60, 30, -20), asset('B', 40, 50, 10)]);
  const a = calculate(s), b = calculate({ ...s, value: 7 * s.value });
  close(b.pnl, 7 * a.pnl, 1e-8); close(b.endValue, 7 * a.endValue, 1e-8);
  close(b.portfolioReturn, a.portfolioReturn);
});

// Preconditions: the same assets and inputs are supplied in a different order; compare numeric outputs by symbol.
test('asset ordering does not change portfolio result or per-symbol attribution', () => {
  const assets = [asset('A', 20, 30, -20), asset('B', 35, 50, -40), asset('C', 45, 70, 10)];
  const a = calculate(stateWith(assets));
  const b = calculate(stateWith([...assets].reverse()));
  for (const key of ['portfolioReturn', 'pnl', 'endValue', 'baselineSigma', 'stressedSigma', 'hhi', 'equalSigma']) close(a[key], b[key], 1e-12);
  for (const item of a.assets) {
    const other = b.assets.find(x => x.symbol === item.symbol);
    for (const key of ['pnl', 'contribution', 'riskShare']) close(item[key], other[key], 1e-12);
  }
});

// Preconditions: adding a zero-weight position preserves weighted portfolio statistics, but equal-weight metrics
// include every listed asset by documented design and therefore may change.
test('zero-weight asset preserves portfolio return, sigma, and HHI only', () => {
  const assets = [asset('A', 60, 30, -20), asset('B', 40, 50, -40)];
  const a = calculate(stateWith(assets));
  const b = calculate(stateWith([...assets, asset('ZERO', 0, 100, 300)]));
  for (const key of ['portfolioReturn', 'baselineSigma', 'stressedSigma', 'hhi']) close(a[key], b[key]);
  assert.notEqual(a.equalSigma, b.equalSigma);
  assert.notEqual(a.equalReturn, b.equalReturn);
});

// Preconditions: nonpositive asset shocks, nonnegative multiplier, fixed valid weights and all else unchanged.
test('portfolio return is non-increasing as multiplier rises for nonpositive shocks', () => {
  const s = stateWith([asset('A', 65, 30, -20), asset('B', 35, 50, 0)]);
  let prior = calculate({ ...s, multiplier: 0 }).portfolioReturn;
  for (let multiplier = 0.1; multiplier <= 3; multiplier += 0.1) {
    const current = calculate({ ...s, multiplier }).portfolioReturn;
    assert.ok(current <= prior + 1e-12); prior = current;
  }
});

// Preconditions: nonnegative weights and volatilities, rho in [0,1]; Cauchy and triangle bounds apply.
test('sigma lies between root-sum-square and sum exposure bounds', () => {
  const s = stateWith([asset('A', 20, 70), asset('B', 30, 120), asset('C', 50, 35)]);
  const x = s.assets.map(a => a.weight / 100 * a.volatility / 100);
  const lower = Math.sqrt(x.reduce((sum, value) => sum + value ** 2, 0));
  const upper = x.reduce((sum, value) => sum + value, 0);
  for (let i = 0; i <= 20; i++) {
    const rho = i / 20;
    const sigma = Math.sqrt((1 - rho) * lower ** 2 + rho * upper ** 2);
    const result = calculate({ ...s, stressCorrelation: rho });
    assert.ok(result.stressedSigma >= lower - 1e-12);
    assert.ok(result.stressedSigma <= upper + 1e-12);
    close(result.stressedSigma, sigma);
  }
});

// Preconditions: valid nonzero-vol portfolio and 365-day horizon; curve stores 21 rho points scaled by horizon.
test('correlation curve endpoints equal rho-zero and rho-one horizon sigma', () => {
  const s = stateWith([asset('A', 35, 40), asset('B', 65, 90)], { days: 137 });
  const result = calculate(s);
  const scale = Math.sqrt(s.days / 365);
  const exposures = s.assets.map(a => a.weight / 100 * a.volatility / 100);
  const rhoZeroSigma = Math.sqrt(exposures.reduce((sum, x) => sum + x ** 2, 0));
  close(result.curve[0].sigma, rhoZeroSigma * scale);
  close(result.curve[20].sigma, calculate({ ...s, stressCorrelation: 1 }).stressedSigma * scale);
});

// Preconditions: nonzero volatilities and rho from 0 through 1; Euler variance contributions are nonnegative.
test('Euler risk shares are nonnegative and sum to one across correlation bounds', () => {
  const s = stateWith([asset('A', 25, 40), asset('B', 35, 80), asset('C', 40, 20)]);
  for (let i = 0; i <= 20; i++) {
    const result = calculate({ ...s, stressCorrelation: i / 20 });
    assert.ok(result.assets.every(a => a.riskShare >= 0));
    close(result.assets.reduce((sum, a) => sum + a.riskShare, 0), 1);
  }
});

// Preconditions: valid positive-vol portfolio and any valid day horizon; z is the engine's one-sided 95% constant.
test('stressed downside uses z times annual sigma times square-root horizon', () => {
  const s = stateWith([asset('A', 40, 70), asset('B', 60, 110)], { days: 121, stressCorrelation: 0.65 });
  const result = calculate(s);
  close(result.stressedDownside, 1.6448536269514722 * result.stressedSigma * Math.sqrt(s.days / 365));
});

// Preconditions: nonempty finite nonnegative weights with positive sum; normalization uses 1e-6 percentage-point units.
test('weight normalization does not mutate input and totals exactly 100 micro-percent', () => {
  const input = [asset('A', 1), asset('B', 2), asset('C', 7)];
  const before = structuredClone(input);
  const normalized = normalizeWeights(input);
  assert.deepEqual(input, before);
  assert.equal(normalized.reduce((sum, a) => sum + Math.round(a.weight * 1e6), 0), 100000000);
  assert.deepEqual(normalizeWeights(normalized), normalized);
});

// Preconditions: each listed input violates one normalizeWeights domain requirement.
test('weight normalization rejects invalid totals and entries', () => {
  for (const weights of [[], [-1, 101], [Infinity, 1], [NaN, 1], [0, 0]]) {
    assert.throws(() => normalizeWeights(weights.map((weight, i) => ({ weight, symbol: `A${i}` }))));
  }
});

// Preconditions: deterministic LCG-seeded portfolios with valid normalized weights and supported numeric ranges.
test('seeded portfolios preserve return and risk invariants over varied inputs', () => {
  let seed = 0x51a7;
  const random = () => ((seed = (1664525 * seed + 1013904223) >>> 0) / 2 ** 32);
  for (let k = 0; k < 120; k++) {
    const count = 1 + Math.floor(random() * 12);
    const assets = normalizeWeights(Array.from({ length: count }, (_, i) => ({
      ...asset(`R${i}`, random() * 100, random() * 300, -random() * 100),
    })));
    const s = stateWith(assets, { stressCorrelation: random(), days: 1 + Math.floor(random() * 365) });
    const result = calculate(s);
    assert.ok(result.portfolioReturn <= 1e-12);
    assert.ok(result.assets.every(a => a.riskShare >= 0));
    close(result.assets.reduce((sum, a) => sum + a.riskShare, 0), 1, 1e-10);
  }
});
