import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sampleState, validate, calculate } from '../dist/engine.mjs';
import { MAX_IMPORT_BYTES, SCHEMA_ID, SCHEMA_VERSION, parsePortfolioImport, serializePortfolio, serializeCsv, toCsvRows } from '../dist/persistence.mjs';

function sample() { return sampleState(); }
function envelope(portfolio=sample()) { const {version,...rest}=portfolio; return {schema:SCHEMA_ID,schemaVersion:SCHEMA_VERSION,portfolio:rest}; }
function encode(value) { return JSON.stringify(value); }
function rejected(value) { const result=parsePortfolioImport(typeof value==='string'?value:encode(value));assert.equal(result.ok,false);assert.ok(result.errors.length);assert.ok(result.errors.every(error=>typeof error.path==='string'&&typeof error.message==='string'));return result; }

test('JSON export is deterministic, allowlisted, and round-trips the portfolio',()=>{
  const state=sample();
  const expected=`{
  "schema": "crypto-stress-lab/portfolio",
  "schemaVersion": 1,
  "portfolio": {
    "value": 100000,
    "days": 30,
    "baseCorrelation": 0.35,
    "stressCorrelation": 0.85,
    "multiplier": 1,
    "preset": "selloff",
    "assets": [
      {
        "id": "btc",
        "symbol": "BTC",
        "group": "bitcoin",
        "weight": 45,
        "volatility": 65,
        "shock": -25
      },
      {
        "id": "eth",
        "symbol": "ETH",
        "group": "ethereum",
        "weight": 30,
        "volatility": 85,
        "shock": -35
      },
      {
        "id": "sol",
        "symbol": "SOL",
        "group": "altcoin",
        "weight": 15,
        "volatility": 110,
        "shock": -50
      },
      {
        "id": "usdc",
        "symbol": "USDC",
        "group": "stable",
        "weight": 10,
        "volatility": 5,
        "shock": -2
      }
    ]
  }
}
`;
  const serialized=serializePortfolio(state);assert.equal(serialized,expected);
  const parsed=parsePortfolioImport(serialized);assert.equal(parsed.ok,true);assert.deepEqual(parsed.portfolio,envelope(state).portfolio);
  assert.equal(serializePortfolio({version:1,...parsed.portfolio}),serialized);
  assert.equal(serialized.includes('"version"'),false);
});

test('accepts documented numeric bounds and 12 assets with tolerated weight totals',()=>{
  const variants=[];
  const low=sample();low.value=1;low.days=1;low.baseCorrelation=0;low.stressCorrelation=0;low.multiplier=0;low.preset='custom';low.assets=[{id:'a',symbol:'A',group:'bitcoin',weight:100,volatility:0,shock:-100}];variants.push(low);
  const high=sample();high.value=1e12;high.days=365;high.baseCorrelation=1;high.stressCorrelation=1;high.multiplier=3;high.preset='custom';high.assets=Array.from({length:12},(_,i)=>({id:`a${i}`,symbol:`A${i}`,group:'bitcoin',weight:i===0?100:0,volatility:300,shock:300}));variants.push(high);
  for (const offset of [-0.000001,0.000001]) {const state=sample();state.assets[0].weight+=offset;variants.push(state);}
  for(const state of variants){assert.deepEqual(validate(state),[]);const result=parsePortfolioImport(serializePortfolio(state));assert.equal(result.ok,true,JSON.stringify(result.errors));assert.deepEqual(result.portfolio,envelope(state).portfolio);}
});

test('rejects malformed envelopes, unsupported versions, extra and missing keys',()=>{
  for(const raw of ['', '{', '\uFEFF', 'null', '[]', '5']) rejected(raw);
  for(const version of [0,1.5,'1',2,null,true]){const value=envelope();value.schemaVersion=version;const result=rejected(value);if(version===2)assert.match(result.errors.map(e=>e.message).join(' '),/version 1/);}
  const wrongSchema=envelope();wrongSchema.schema='other';rejected(wrongSchema);
  for(const level of ['top','portfolio','asset']){
    const extra=envelope();if(level==='top')extra.extra=1;else if(level==='portfolio')extra.portfolio.extra=1;else extra.portfolio.assets[0].extra=1;rejected(extra);
    const keys=level==='top'?['schema','schemaVersion','portfolio']:level==='portfolio'?['value','days','baseCorrelation','stressCorrelation','multiplier','preset','assets']:['id','symbol','group','weight','volatility','shock'];
    for(const key of keys){const missing=envelope();if(level==='top')delete missing[key];else if(level==='portfolio')delete missing.portfolio[key];else delete missing.portfolio.assets[0][key];const result=rejected(missing);if(level==='top'&&key==='schemaVersion')assert.match(result.errors.map(e=>e.message).join(' '),/version 1/);}
  }
});

test('rejects wrong types, non-finite numeric values and out-of-range data without coercion',()=>{
  for(const value of ['1',null,true]){const bad=envelope();bad.portfolio.value=value;rejected(bad);}
  for(const key of ['value','days','baseCorrelation','stressCorrelation','multiplier']) for(const value of ['1',null,true]){const bad=envelope();bad.portfolio[key]=value;rejected(bad);}
  for(const key of ['weight','volatility','shock']) for(const value of ['1',null,true]){const bad=envelope();bad.portfolio.assets[0][key]=value;rejected(bad);}
  rejected('{"schema":"crypto-stress-lab/portfolio","schemaVersion":1,"portfolio":{"value":NaN}}');
  const overflow='{"schema":"crypto-stress-lab/portfolio","schemaVersion":1,"portfolio":{"value":1e999}}';rejected(overflow);
  const outside=[];
  for(const [key,value] of [['value',0],['value',1e12+1],['days',0],['days',366],['baseCorrelation',-0.1],['baseCorrelation',1.1],['stressCorrelation',-0.1],['stressCorrelation',1.1],['multiplier',-0.1],['multiplier',3.1]]){const bad=envelope();bad.portfolio[key]=value;outside.push(bad);}
  for(const [key,value] of [['weight',-0.1],['weight',100.1],['volatility',-0.1],['volatility',300.1],['shock',-100.1],['shock',300.1]]){const bad=envelope();bad.portfolio.assets[0][key]=value;outside.push(bad);}
  for(const bad of outside)rejected(bad);
  for(const total of [99.9,100.1]){const bad=envelope();bad.portfolio.assets[0].weight+=total-100;rejected(bad);}
  for(const count of [0,13]){const bad=envelope();bad.portfolio.assets=Array.from({length:count},(_,i)=>({id:`a${i}`,symbol:`A${i}`,group:'bitcoin',weight:100/count,volatility:0,shock:-25}));rejected(bad);}
});

test('rejects invalid identifiers, symbols, groups, presets and named preset mismatches',()=>{
  const duplicateSymbol=envelope();duplicateSymbol.portfolio.assets[1].symbol='btc';
  const duplicateResult=rejected(duplicateSymbol);
  assert.deepEqual(duplicateResult.errors,[{path:'portfolio.assets[1].symbol',message:'Use a symbol unique without regard to letter case.'}]);
  const duplicateId=envelope();duplicateId.portfolio.assets[1].id=duplicateId.portfolio.assets[0].id;rejected(duplicateId);
  for(const id of ['', 'a'.repeat(65),'has space','<bad>']){const bad=envelope();bad.portfolio.assets[0].id=id;rejected(bad);}
  for(const group of ['__proto__','toString']){const bad=envelope();bad.portfolio.assets[0].group=group;rejected(bad);}
  const preset=envelope();preset.portfolio.preset='unknown';rejected(preset);
  const mismatch=envelope();mismatch.portfolio.assets[0].shock=99;rejected(mismatch);
  for(const field of ['symbol','id']) for(const control of ['\u0000','\u001f','\u007f','\u009f']){const bad=envelope();bad.portfolio.assets[0][field]=`a${control}b`;rejected(bad);}
});

test('malformed asset entries and field values return validation errors without throwing',()=>{
  const assetValues=[null,5,'x',[],{},true];
  const validAsset=envelope().portfolio.assets[0];
  for(const value of assetValues){
    for(const assets of [[value],[validAsset,value]]){
      const input=envelope();input.portfolio.assets=assets;
      let result;assert.doesNotThrow(()=>{result=parsePortfolioImport(encode(input));});assert.equal(result.ok,false);
    }
    const input=envelope();input.portfolio.assets=value;
    let result;assert.doesNotThrow(()=>{result=parsePortfolioImport(encode(input));});assert.equal(result.ok,false);
  }
  for(const field of ['id','symbol','group','weight','volatility','shock']) for(const value of assetValues){
    const input=envelope();input.portfolio.preset='unsupported-probe';input.portfolio.assets[0][field]=value;
    let result;assert.doesNotThrow(()=>{result=parsePortfolioImport(encode(input));});assert.equal(result.ok,false);
  }
  for(const assets of [[null],[validAsset,null]]){
    const input=envelope();input.portfolio.assets=assets;
    let result;assert.doesNotThrow(()=>{result=parsePortfolioImport(encode(input));});assert.equal(result.ok,false);
  }
});

test('rejects own prototype-named keys without prototype mutation and collects errors',()=>{
  const polluted={};
  for(const level of ['top','portfolio','asset']){
    const value=envelope();let target=level==='top'?value:level==='portfolio'?value.portfolio:value.portfolio.assets[0];
    Object.defineProperty(target,'__proto__',{value:{polluted:true},enumerable:true});rejected(value);
  }
  const before=Object.getPrototypeOf(polluted);assert.equal(polluted.polluted,undefined);assert.equal(Object.getPrototypeOf(polluted),before);
  const multi=envelope();multi.portfolio.value='bad';multi.portfolio.assets[0].id='bad id';const result=rejected(multi);assert.ok(result.errors.length>=2);
});

test('checks UTF-8 byte size before parsing, strips one BOM, and catches deep nesting',()=>{
  const serialized=serializePortfolio(sample());assert.equal(parsePortfolioImport(`\uFEFF${serialized}`).ok,true);
  const manyBytes='"'+'é'.repeat(Math.floor(MAX_IMPORT_BYTES/2))+'"';assert.ok(manyBytes.length<MAX_IMPORT_BYTES);assert.ok(new TextEncoder().encode(manyBytes).length>MAX_IMPORT_BYTES);rejected(manyBytes);
  assert.doesNotThrow(()=>rejected('['.repeat(60000)));
});

test('does not mutate input and CSV neutralizes imported formula-like symbols',()=>{
  const state=envelope();state.portfolio.preset='custom';state.portfolio.assets[0].symbol='=SUM(1)';
  const before=structuredClone(state),parsed=parsePortfolioImport(encode(state));assert.equal(parsed.ok,true);assert.deepEqual(state,before);
  const full={version:1,...parsed.portfolio};assert.equal(validate(full).length,0);const rows=toCsvRows(full,calculate(full));assert.match(serializeCsv(rows),/"'=SUM\(1\)"/);
});
