import { test } from 'node:test';
import assert from 'node:assert/strict';
import { calculate, variance, validate, sampleState, normalizeWeights, PRESETS } from '../dist/engine.mjs';
const close=(actual,expected,tol=1e-10)=>assert.ok(Math.abs(actual-expected)<tol,`${actual} ≠ ${expected}`);
const twoAssets=()=>({...sampleState(),days:365,baseCorrelation:0,stressCorrelation:1,assets:[
  {id:'a',symbol:'A',group:'bitcoin',weight:60,volatility:20,shock:-20},
  {id:'b',symbol:'B',group:'altcoin',weight:40,volatility:40,shock:-50}
]});
test('demo hand calculation: weighted shock, P&L, covariance, HHI',()=>{
  const r=calculate(sampleState());
  close(r.portfolioReturn,-.2945);close(r.pnl,-29450);close(r.endValue,70550);
  close(r.drawdown,.2945);close(r.baselineSigma**2,.2957725);close(r.stressedSigma**2,.46426);
  close(r.hhi,.325);close(r.effectiveAssets,1/.325);close(r.assets.reduce((s,a)=>s+a.riskShare,0),1);
  close(r.equalReturn,(-.25-.35-.5-.02)/4);
});
test('two-asset independent vs perfectly correlated analytic result',()=>{
  const r=calculate(twoAssets());
  close(r.portfolioReturn,-.32);close(r.pnl,-32000);close(r.baselineSigma,.2);close(r.stressedSigma,.28);
  close(r.equalSigma,.3);close(r.hhi,.52);close(r.stressedDownside,1.6448536269514722*.28);
  close(r.assets[0].riskShare,3/7);close(r.assets[1].riskShare,4/7);
});
test('correlation changes risk, not deterministic losses',()=>{
  const s=twoAssets(),a=calculate(s);s.stressCorrelation=.3;s.baseCorrelation=.8;const b=calculate(s);
  close(a.portfolioReturn,b.portfolioReturn);assert.ok(a.stressedSigma>b.stressedSigma);
  assert.ok(b.stressedSigma<b.baselineSigma);
});
test('horizon scales only risk by square root of time',()=>{
  const s=twoAssets(),a=calculate(s);s.days=1;const b=calculate(s);
  close(b.stressedDownside,a.stressedDownside/Math.sqrt(365));close(a.pnl,b.pnl);
});
test('losses capped per asset at minus 100%; capital cannot go negative',()=>{
  const s=twoAssets();s.multiplier=3;s.assets[0].shock=-100;s.assets[1].shock=-80;const r=calculate(s);
  close(r.portfolioReturn,-1);close(r.endValue,0);assert.equal(r.capped,true);
  r.comparisons.forEach(p=>assert.ok(p.return>=-1));
});
test('positive and zero shocks produce zero drawdown and correct P&L',()=>{
  const s=twoAssets();s.assets[0].shock=20;s.assets[1].shock=50;const r=calculate(s);
  close(r.portfolioReturn,.32);close(r.drawdown,0);close(r.pnl,32000);
  s.multiplier=0;const z=calculate(s);close(z.pnl,0);close(z.drawdown,0);assert.ok(z.stressedSigma>0);
});
test('all zero volatilities have zero variance and zero risk shares',()=>{
  const s=twoAssets();s.assets.forEach(a=>a.volatility=0);const r=calculate(s);
  close(r.stressedSigma,0);close(r.baselineSigma,0);close(r.stressedDownside,0);
  r.assets.forEach(a=>close(a.riskShare,0));r.curve.forEach(p=>close(p.sigma,0));
});
test('single asset volatility independent of correlation',()=>{
  const s=twoAssets();s.assets=[{...s.assets[0],weight:100}];const r=calculate(s);
  close(r.baselineSigma,.2);close(r.stressedSigma,.2);close(r.effectiveAssets,1);close(r.hhi,1);
});
test('weight validation blocks inconsistent allocations; normalization is explicit',()=>{
  const s=twoAssets();s.assets[0].weight=20;
  assert.ok(validate(s).some(e=>e.includes('100%')));assert.throws(()=>calculate(s));
  s.assets=normalizeWeights(s.assets);assert.deepEqual(validate(s),[]);close(s.assets[0].weight,33.333333,1e-6);
  assert.throws(()=>normalizeWeights(s.assets.map(a=>({...a,weight:0}))));
  assert.throws(()=>normalizeWeights(s.assets.map(a=>({...a,weight:NaN}))));
});
test('normalization handles 12 positions, zero weights and rounding without negative remainder',()=>{
  const assets=Array.from({length:12},(_,i)=>({weight:i===11?0:1,symbol:`A${i}`}));
  const r=normalizeWeights(assets);close(r.reduce((s,a)=>s+a.weight,0),100,1e-9);
  assert.ok(r.every(a=>a.weight>=0));close(r[11].weight,0);
});
test('range, duplicate, missing and nonfinite inputs rejected',()=>{
  for(const [key,value] of [['value',0],['days',0],['days',30.5],['days',366],['baseCorrelation',-.1],['stressCorrelation',1.1],['multiplier',4],['value',NaN]]){
    const s=twoAssets();s[key]=value;assert.ok(validate(s).length,`${key} ${value}`);
  }
  for(const [key,value] of [['weight',-1],['volatility',-1],['shock',-101],['shock',Infinity],['symbol',''],['symbol','b'],['group','invalid']]){
    const s=twoAssets();s.assets[0][key]=value;assert.ok(validate(s).length,`${key} ${value}`);
  }
  const s=twoAssets();s.assets=[];assert.ok(validate(s).length);
});
test('preset returns use each asset group and the intensity',()=>{
  const s=twoAssets();s.multiplier=2;const r=calculate(s);
  for(const p of r.comparisons){
    const expected=.6*Math.max(-1,PRESETS[p.id].shocks.bitcoin*.02)+.4*Math.max(-1,PRESETS[p.id].shocks.altcoin*.02);
    close(p.return,expected);
  }
});
test('300 deterministic portfolios agree with explicit covariance matrix multiplication',()=>{
  let seed=42;const random=()=>((seed=(1664525*seed+1013904223)>>>0)/2**32);
  for(let k=0;k<300;k++){
    const count=1+Math.floor(random()*12),s=sampleState();
    s.baseCorrelation=random();s.stressCorrelation=random();s.days=1+Math.floor(random()*365);
    s.assets=normalizeWeights(Array.from({length:count},(_,i)=>({id:`id${i}`,symbol:`T${i}`,group:'altcoin',weight:random()*100,volatility:random()*300,shock:random()*400-100})));
    const r=calculate(s),w=s.assets.map(a=>a.weight/100),v=s.assets.map(a=>a.volatility/100);
    let expected=0;
    for(let i=0;i<count;i++)for(let j=0;j<count;j++)expected+=w[i]*w[j]*v[i]*v[j]*(i===j?1:s.stressCorrelation);
    close(r.stressedSigma**2,expected,1e-9);close(r.assets.reduce((t,a)=>t+a.riskShare,0),1,1e-9);
    close(r.assets.reduce((t,a)=>t+a.pnl,0),r.pnl,1e-7);
    assert.ok(r.curve.every((p,i)=>i===0||p.sigma>=r.curve[i-1].sigma-1e-12));
    close(variance(w,v,1),w.reduce((t,a,i)=>t+a*v[i],0)**2,1e-9);
  }
});
