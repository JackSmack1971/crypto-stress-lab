import { test } from 'node:test';
import assert from 'node:assert/strict';
import { calculate, sampleState, sensitivityGrid } from '../dist/engine.mjs';

const close=(actual,expected,tol=1e-12)=>assert.ok(Math.abs(actual-expected)<=tol,`${actual} ≠ ${expected}`);
const fixture=()=>({...sampleState(),value:100000,days:365,baseCorrelation:0.35,stressCorrelation:0.3,multiplier:1,assets:[
  {id:'a',symbol:'A',group:'bitcoin',weight:50,volatility:20,shock:-40},
  {id:'b',symbol:'B',group:'altcoin',weight:50,volatility:40,shock:-10}
]});

test('sensitivity grid has exact axes, dimensions, and hand-computed fixture values',()=>{
  const grid=sensitivityGrid(fixture());
  assert.deepEqual(grid.rho,Array.from({length:11},(_,i)=>i/10));
  assert.deepEqual(grid.intensity,Array.from({length:13},(_,j)=>j*0.25));
  for(const matrix of [grid.volatility,grid.var99,grid.scenarioReturn]) {
    assert.equal(matrix.length,13);matrix.forEach(row=>assert.equal(row.length,11));
  }
  close(grid.volatility[0][0],0.223606797749979);
  close(grid.volatility[0][3],0.24899799195977468);
  close(grid.volatility[0][5],0.2645751311064591);
  close(grid.volatility[0][10],0.3);
  close(grid.var99[0][10],0.6979043622122524);
  close(grid.var99[0][0],0.5201871985667439);
  close(grid.scenarioReturn[0][0],0);
  close(grid.scenarioReturn[4][0],-0.25);
  close(grid.scenarioReturn[8][0],-0.5);
  close(grid.scenarioReturn[11][0],-0.6375);
  close(grid.scenarioReturn[12][0],-0.65);
});

test('every sensitivity cell matches calculate at its correlation and intensity',()=>{
  const state=fixture(),grid=sensitivityGrid(state);
  for(let j=0;j<grid.intensity.length;j++) for(let i=0;i<grid.rho.length;i++) {
    const r=calculate({...state,stressCorrelation:grid.rho[i],multiplier:grid.intensity[j]});
    close(grid.volatility[j][i],r.stressedSigma*r.horizonScale);
    close(grid.var99[j][i],r.stressedDownside99);
    close(grid.scenarioReturn[j][i],r.portfolioReturn);
  }
});

test('mathematically flat dimensions are exactly identical',()=>{
  const grid=sensitivityGrid(fixture());
  for(let j=1;j<grid.intensity.length;j++) for(let i=0;i<grid.rho.length;i++) {
    assert.equal(grid.volatility[j][i],grid.volatility[0][i]);
    assert.equal(grid.var99[j][i],grid.var99[0][i]);
  }
  for(const row of grid.scenarioReturn) for(let i=1;i<row.length;i++) assert.equal(row[i],row[0]);
});

test('sensitivity properties hold under documented preconditions',()=>{
  const state=fixture(),grid=sensitivityGrid(state);
  for(let j=0;j<grid.intensity.length;j++) for(let i=1;i<grid.rho.length;i++) assert.ok(grid.volatility[j][i]>=grid.volatility[j][i-1]);
  assert.ok(grid.scenarioReturn[0].every(value=>value===0));
  for(let j=1;j<grid.intensity.length;j++) assert.ok(grid.scenarioReturn[j][0]<=grid.scenarioReturn[j-1][0]);
  const reversed=sensitivityGrid({...state,assets:[...state.assets].reverse()});
  assert.deepEqual(reversed,grid);
  const changedValue=sensitivityGrid({...state,value:250000});
  assert.deepEqual(changedValue,grid);
});

test('zero-volatility and zero-shock grids are constant finite grids',()=>{
  const state=fixture();state.assets=state.assets.map(a=>({...a,volatility:0}));
  const noVol=sensitivityGrid(state);
  for(const row of noVol.volatility) assert.ok(row.every(value=>value===0));
  for(const row of noVol.var99) assert.ok(row.every(value=>value===0));
  state.assets=state.assets.map(a=>({...a,volatility:0,shock:0}));
  const flat=sensitivityGrid(state);
  for(const matrix of [flat.volatility,flat.var99,flat.scenarioReturn]) for(const row of matrix) {
    assert.ok(row.every(Number.isFinite));assert.ok(row.every(value=>value===row[0]));
  }
});

test('invalid states throw like calculate and valid inputs are not mutated',()=>{
  const state=fixture(),before=structuredClone(state);
  sensitivityGrid(state);
  assert.deepEqual(state,before);
  const invalid={...state,stressCorrelation:1.1};
  let calculateMessage;
  try { calculate(invalid); } catch(error) { calculateMessage=error.message; }
  assert.throws(()=>sensitivityGrid(invalid),error=>error.message===calculateMessage);
});
