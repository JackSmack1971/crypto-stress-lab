import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sampleState, reverseStress } from '../dist/engine.mjs';

const close=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<=t,`${a} ≠ ${b}`);
function fixture(){return {...sampleState(),value:100000,assets:[
  {id:'btc',symbol:'BTC',group:'bitcoin',weight:45,volatility:65,shock:-25},
  {id:'eth',symbol:'ETH',group:'ethereum',weight:30,volatility:85,shock:-35},
  {id:'sol',symbol:'SOL',group:'altcoin',weight:15,volatility:110,shock:-50},
  {id:'usdc',symbol:'USDC',group:'stable',weight:10,volatility:5,shock:-2}
]};}

test('portfolio reverse stress matches hand-computed uniform loss and selected P&L',()=>{
  const r=reverseStress(fixture(),{mode:'portfolio',unit:'pct',target:20});
  assert.equal(r.reachable,true);close(r.requiredShock,-.2);close(r.pnl,-20000);close(r.endValue,80000);
  assert.deepEqual(r.assets.map(a=>a.pnl),[-9000,-6000,-3000,-2000]);
});
test('asset, group, floor and unreachable outputs follow selected exposure bounds',()=>{
  const s=fixture();
  close(reverseStress(s,{mode:'asset',selector:'BTC',target:22.5}).requiredShock,-.5);
  const floor=reverseStress(s,{mode:'asset',selector:'BTC',unit:'usd',target:45000});assert.equal(floor.requiredShock,-1);assert.equal(floor.atFloor,true);
  const unreachable=reverseStress(s,{mode:'asset',selector:'BTC',target:50});assert.equal(unreachable.reachable,false);assert.equal(unreachable.requiredShock,null);assert.equal(unreachable.pnl,null);assert.equal(unreachable.endValue,null);close(unreachable.maxLoss,.45);close(unreachable.maxLossUsd,45000);
  close(reverseStress(s,{mode:'group',selector:'stable',unit:'usd',target:5000}).requiredShock,-.5);
  close(reverseStress(s,{mode:'portfolio',target:100}).endValue,0);
});
test('group sums tolerate floating-point boundary and report maximum loss',()=>{
  const s=fixture();s.value=250000;s.assets=[
    {id:'a',symbol:'A',group:'altcoin',weight:40,volatility:10,shock:0},{id:'b',symbol:'B',group:'altcoin',weight:20,volatility:10,shock:0},
    {id:'c',symbol:'C',group:'bitcoin',weight:30,volatility:10,shock:0},{id:'d',symbol:'D',group:'stable',weight:10,volatility:10,shock:0}
  ];
  const edge=reverseStress(s,{mode:'group',selector:'altcoin',target:60});assert.equal(edge.reachable,true);assert.equal(edge.requiredShock,-1);
  assert.equal(reverseStress(s,{mode:'group',selector:'altcoin',target:60.001}).reachable,false);
  const partial=reverseStress(s,{mode:'group',selector:'altcoin',unit:'usd',target:50000});close(partial.requiredShock,-1/3);close(partial.assets[0].pnl,-33333.3333333333);close(partial.assets[1].pnl,-16666.6666666667);
  s.assets.push({id:'e',symbol:'E',group:'cash',weight:0,volatility:10,shock:0});
  const zero=reverseStress(s,{mode:'group',selector:'cash',target:1});assert.equal(zero.reachable,false);assert.equal(zero.maxLossUsd,0);
  const zeroAsset=reverseStress(s,{mode:'asset',selector:'E',target:1});assert.equal(zeroAsset.reachable,false);assert.equal(zeroAsset.maxLoss,0);
  const max=reverseStress(s,{mode:'group',selector:'bitcoin',target:40});assert.equal(max.reachable,false);close(max.maxLossUsd,75000);
});
test('portfolio weight-validation tolerance still permits a full loss at the floor',()=>{
  const s=fixture();s.assets[0].weight=44.9999995;
  const r=reverseStress(s,{mode:'portfolio',target:100});
  assert.equal(r.reachable,true);assert.equal(r.requiredShock,-1);assert.equal(r.atFloor,true);close(r.exposure,.999999995);close(r.pnl,-99999.9995);
});
test('equivalent pct and USD targets and portfolio scaling preserve the right quantities',()=>{
  const s=fixture(),a=reverseStress(s,{mode:'group',selector:'bitcoin',target:22.5}),b=reverseStress(s,{mode:'group',selector:'bitcoin',unit:'usd',target:22500});
  close(a.requiredShock,b.requiredShock);close(a.pnl,b.pnl);
  const c=reverseStress({...s,value:200000},{mode:'group',selector:'bitcoin',target:22.5});close(c.requiredShock,a.requiredShock);close(c.pnl,2*a.pnl);
});
test('reverse result is independent of scenario, correlation, horizon and volatility assumptions',()=>{
  const s=fixture(),a=reverseStress(s,{mode:'portfolio',target:25});
  const changed={...s,days:365,baseCorrelation:0,stressCorrelation:1,multiplier:3,assets:s.assets.map(x=>({...x,volatility:300,shock:250}))};
  assert.deepEqual(reverseStress(changed,{mode:'portfolio',target:25}),a);
});
test('asset ordering leaves the reverse result unchanged by symbol',()=>{
  const s=fixture(),opts={mode:'group',selector:'altcoin',target:10};
  assert.deepEqual(reverseStress(s,opts),reverseStress({...s,assets:[...s.assets].reverse()},opts));
});
test('seeded selected P&L round trips the requested target and larger losses need larger shocks',()=>{
  let seed=0x5eed;const random=()=>((seed=(1664525*seed+1013904223)>>>0)/2**32);
  for(let i=0;i<100;i++){
    const weights=[random()*50,random()*50,0];weights[2]=100-weights[0]-weights[1];
    const s=fixture();s.assets=s.assets.slice(0,3).map((a,j)=>({...a,group:j===1?'altcoin':'bitcoin',weight:weights[j]}));
    const mode=i%2?'asset':'group',selector=mode==='asset'?s.assets[i%3].symbol:(i%4?'bitcoin':'altcoin');
    const selected=s.assets.filter(a=>mode==='asset'?a.symbol===selector:a.group===selector);
    const target=random()*selected.reduce((sum,a)=>sum+a.weight,0);
    if(target===0)continue;
    const r=reverseStress(s,{mode,selector,target});assert.equal(r.reachable,true);close(r.assets.reduce((sum,a)=>sum+a.pnl,0),-target/100*s.value,1e-7);
  }
  const s=fixture();assert.ok(reverseStress(s,{mode:'portfolio',target:30}).requiredShock<reverseStress(s,{mode:'portfolio',target:10}).requiredShock);
});
test('invalid targets and selectors reject malformed values safely',()=>{
  const s=fixture();
  for(const target of [NaN,Infinity,1e308,0,-1,'10',null])assert.throws(()=>reverseStress(s,{mode:'portfolio',target}));
  assert.throws(()=>reverseStress(s,{mode:'portfolio',unit:'pct',target:101}));assert.throws(()=>reverseStress(s,{mode:'portfolio',unit:'usd',target:100001}));
  for(const options of [{mode:'bad',target:1},{mode:'asset',selector:'missing',target:1},{mode:'group',selector:'__proto__',target:1},{mode:'group',selector:'<img src=x onerror=alert(1)>',target:1},{mode:'asset',selector:'__proto__',target:1}])assert.throws(()=>reverseStress(s,options));
  assert.throws(()=>reverseStress({...s,value:NaN},{mode:'portfolio',target:1}));
});
