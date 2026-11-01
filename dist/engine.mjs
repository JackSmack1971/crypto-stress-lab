// Pure, deterministic long-only portfolio calculations. Percent inputs use 0–100 units.
export const PRESETS = {
  selloff: { name: 'Broad selloff', description: 'A broad risk-off move across crypto.', shocks: { bitcoin: -25, ethereum: -35, altcoin: -50, stable: -2, cash: 0 } },
  liquidity: { name: 'Liquidity squeeze', description: 'Smaller assets absorb a deeper liquidity shock.', shocks: { bitcoin: -40, ethereum: -50, altcoin: -70, stable: -5, cash: 0 } },
  depeg: { name: 'Stablecoin depeg', description: 'Stablecoins lose their peg with spillover into crypto.', shocks: { bitcoin: -12, ethereum: -18, altcoin: -25, stable: -20, cash: 0 } },
  rally: { name: 'Relief rally', description: 'A positive counter-scenario for comparison.', shocks: { bitcoin: 15, ethereum: 22, altcoin: 35, stable: 0, cash: 0 } }
};
export const GROUPS = { bitcoin:'Bitcoin', ethereum:'Ethereum', altcoin:'Altcoin', stable:'Stablecoin', cash:'Cash' };
export function sampleState() {
  return { version: 1, value: 100000, days: 30, baseCorrelation: 0.35, stressCorrelation: 0.85, multiplier: 1, preset: 'selloff', assets: [
    { id:'btc', symbol:'BTC', group:'bitcoin', weight:45, volatility:65, shock:-25 },
    { id:'eth', symbol:'ETH', group:'ethereum', weight:30, volatility:85, shock:-35 },
    { id:'sol', symbol:'SOL', group:'altcoin', weight:15, volatility:110, shock:-50 },
    { id:'usdc', symbol:'USDC', group:'stable', weight:10, volatility:5, shock:-2 }
  ] };
}
const finite = x => typeof x === 'number' && Number.isFinite(x);
export function validate(state) {
  const errors = [];
  if (!state || typeof state !== 'object' || Array.isArray(state)) return ['Saved inputs must be an object.'];
  const range = (v, min, max, label) => { if (!finite(v) || v < min || v > max) errors.push(`${label} must be between ${min} and ${max}.`); };
  range(state.value, 1, 1e12, 'Portfolio value');
  range(state.days, 1, 365, 'Risk horizon (days)');
  if (finite(state.days) && !Number.isInteger(state.days)) errors.push('Risk horizon must be a whole number of days.');
  range(state.baseCorrelation, 0, 1, 'Baseline correlation');
  range(state.stressCorrelation, 0, 1, 'Stressed correlation');
  range(state.multiplier, 0, 3, 'Shock intensity');
  if (!Array.isArray(state.assets) || !state.assets.length || state.assets.length > 12) return [...errors, 'Enter between 1 and 12 assets.'];
  const symbols = new Set();
  state.assets.forEach((a, i) => {
    const label = `Asset ${i+1}`;
    if (!a || typeof a !== 'object' || Array.isArray(a)) { errors.push(`${label}: asset must be an object.`); return; }
    if (typeof a.symbol !== 'string' || !a.symbol.trim() || a.symbol.length > 12) errors.push(`${label}: enter a symbol of 1–12 characters.`);
    else if (symbols.has(a.symbol.trim().toUpperCase())) errors.push(`${label}: asset symbols must be unique.`);
    else symbols.add(a.symbol.trim().toUpperCase());
    if (!Object.hasOwn(GROUPS, a.group)) errors.push(`${label}: choose an asset group.`);
    range(a.weight, 0, 100, `${label} weight (%)`);
    range(a.volatility, 0, 300, `${label} annual volatility (%)`);
    range(a.shock, -100, 300, `${label} scenario shock (%)`);
  });
  const total = state.assets.reduce((s,a)=>s+(a && typeof a === 'object' && !Array.isArray(a) ? a.weight : NaN),0);
  if (!finite(total) || Math.abs(total-100) > 0.000001) errors.push('Asset weights must total 100%. Use Normalize or adjust your weights.');
  return errors;
}
export function variance(weights, vols, correlation) {
  const sum = weights.reduce((s,w,i)=>s+w*vols[i],0);
  const individual = weights.reduce((s,w,i)=>s+(w*vols[i])**2,0);
  return Math.max(0, (1-correlation)*individual + correlation*sum**2);
}
export function calculate(state) {
  const errors = validate(state);
  if (errors.length) throw new Error(errors.join('\n'));
  const weights = state.assets.map(a=>a.weight/100);
  const vols = state.assets.map(a=>a.volatility/100);
  const shocks = state.assets.map(a=>Math.max(-1,a.shock/100*state.multiplier));
  const portfolioReturn = weights.reduce((s,w,i)=>s+w*shocks[i],0);
  const equal = weights.map(()=>1/weights.length);
  const baselineSigma = Math.sqrt(variance(weights,vols,state.baseCorrelation));
  const stressedSigma = Math.sqrt(variance(weights,vols,state.stressCorrelation));
  const equalSigma = Math.sqrt(variance(equal,vols,state.stressCorrelation));
  const hhi = weights.reduce((s,w)=>s+w*w,0);
  const horizonScale = Math.sqrt(state.days/365);
  const stressedVariance = stressedSigma**2;
  const exposureSum = weights.reduce((s,w,i)=>s+w*vols[i],0);
  const assets = state.assets.map((a,i)=>({ ...a, effectiveShock:shocks[i], pnl:state.value*weights[i]*shocks[i], contribution:weights[i]*shocks[i], riskShare:stressedVariance > 0 ? weights[i]*vols[i]*((1-state.stressCorrelation)*weights[i]*vols[i]+state.stressCorrelation*exposureSum)/stressedVariance : 0 }));
  const comparisons = Object.entries(PRESETS).map(([id,p])=>({id,name:p.name,return:weights.reduce((s,w,i)=>s+w*Math.max(-1,p.shocks[state.assets[i].group]/100*state.multiplier),0)}));
  return { portfolioReturn, pnl:state.value*portfolioReturn, endValue:state.value*(1+portfolioReturn), drawdown:Math.max(0,-portfolioReturn), baselineSigma, stressedSigma, equalSigma, hhi, effectiveAssets:1/hhi, horizonScale, baselineDownside:1.6448536269514722*baselineSigma*horizonScale, stressedDownside:1.6448536269514722*stressedSigma*horizonScale, equalReturn:equal.reduce((s,w,i)=>s+w*shocks[i],0), largestWeight:Math.max(...weights), assets, comparisons, curve:Array.from({length:21},(_,i)=>({rho:i/20,sigma:Math.sqrt(variance(weights,vols,i/20))*horizonScale})), capped:state.assets.some(a=>a.shock/100*state.multiplier < -1) };
}
export function reverseStress(state, options) {
  const errors = validate(state);
  if (errors.length) throw new Error(errors.join('\n'));
  const { mode, selector, unit = 'pct', target } = options ?? {};
  if (!['portfolio', 'asset', 'group'].includes(mode)) throw new Error('Choose a valid exposure selection.');
  if (!['pct', 'usd'].includes(unit)) throw new Error('Choose percent or USD as the target unit.');
  if (typeof target !== 'number' || !Number.isFinite(target) || target <= 0 || (unit === 'pct' && target > 100) || (unit === 'usd' && target > state.value)) throw new Error('Target loss must be a finite positive amount within the portfolio value.');
  let selected;
  let label;
  if (mode === 'portfolio') { selected = state.assets; label = 'Entire portfolio'; }
  else if (mode === 'asset') {
    selected = state.assets.filter(a => a.symbol === selector);
    if (selected.length !== 1) throw new Error('Choose an asset in the portfolio.');
    label = selected[0].symbol;
  } else {
    if (typeof selector !== 'string' || !Object.hasOwn(GROUPS, selector)) throw new Error('Choose a valid asset group.');
    selected = state.assets.filter(a => a.group === selector);
    label = GROUPS[selector];
  }
  const symbols = selected.map(a => a.symbol);
  const exposure = selected.reduce((sum, a) => sum + a.weight / 100, 0);
  const targetLoss = unit === 'pct' ? target / 100 : target / state.value;
  const maxLoss = exposure;
  const tolerance = 2e-8;
  const reachable = exposure > 0 && targetLoss <= exposure + tolerance;
  const requiredShock = reachable ? (targetLoss >= exposure - tolerance ? -1 : Math.max(-1, -targetLoss / exposure)) : null;
  const loss = reachable && requiredShock !== -1 ? targetLoss : maxLoss;
  const selectedSet = new Set(selected);
  return {
    mode, label, symbols, exposure, targetLoss, targetLossUsd: targetLoss * state.value,
    reachable, requiredShock, pnl: reachable ? -loss * state.value : null, endValue: reachable ? state.value * (1 - loss) : null,
    atFloor: reachable && requiredShock === -1,
    maxLoss, maxLossUsd: maxLoss * state.value,
    assets: state.assets.filter(a => selectedSet.has(a)).map(a => ({ symbol: a.symbol, effectiveShock: requiredShock, pnl: reachable ? state.value * (a.weight / 100) * requiredShock : null }))
  };
}
export function normalizeWeights(assets) {
  const total = assets.reduce((s,a)=>s+a.weight,0);
  if (!finite(total) || total <= 0 || assets.some(a=>!finite(a.weight) || a.weight < 0)) throw new Error('Enter nonnegative weights with a positive total before normalizing.');
  // Largest-remainder allocation preserves nonnegativity and an exact micro-percent total.
  const units = assets.map(a=>a.weight/total*100000000);
  const rounded = units.map(Math.floor);
  const remaining = 100000000-rounded.reduce((s,n)=>s+n,0);
  const order = units.map((n,i)=>({i,fraction:n-rounded[i]})).sort((a,b)=>b.fraction-a.fraction);
  for(let n=0;n<remaining;n++) rounded[order[n].i]++;
  return assets.map((a,i)=>({...a,weight:rounded[i]/1000000}));
}
