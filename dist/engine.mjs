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
