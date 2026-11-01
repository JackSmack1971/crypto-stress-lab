import { PRESETS, validate } from './engine.mjs';

export const SCHEMA_ID = 'crypto-stress-lab/portfolio';
export const SCHEMA_VERSION = 1;
export const MAX_IMPORT_BYTES = 65536;

const PORTFOLIO_KEYS = ['value','days','baseCorrelation','stressCorrelation','multiplier','preset','assets'];
const ASSET_KEYS = ['id','symbol','group','weight','volatility','shock'];
const isRecord = value => value !== null && typeof value === 'object' && !Array.isArray(value) && Object.getPrototypeOf(value) === Object.prototype;

function checkKeys(value, expected, path, errors) {
  for (const key of expected) if (!Object.hasOwn(value, key)) errors.push({path:`${path}.${key}`,message:key==='schemaVersion'?`Add the supported schema version ${SCHEMA_VERSION}.`:'Add this required field.'});
  for (const key of Object.keys(value)) if (!expected.includes(key)) errors.push({path:`${path}.${key}`,message:'Remove this unsupported field.'});
}

function typeError(value, type) {
  if (type === 'number') return typeof value !== 'number' || !Number.isFinite(value);
  if (type === 'string') return typeof value !== 'string';
  return false;
}

function mapValidationMessage(message) {
  if (message.startsWith('Portfolio value')) return ['portfolio.value','Enter a finite USD value from 1 to 1,000,000,000,000.'];
  if (message.startsWith('Risk horizon')) return ['portfolio.days','Enter a whole number of days from 1 to 365.'];
  if (message.startsWith('Baseline correlation')) return ['portfolio.baseCorrelation','Enter a number from 0 to 1.'];
  if (message.startsWith('Stressed correlation')) return ['portfolio.stressCorrelation','Enter a number from 0 to 1.'];
  if (message.startsWith('Shock intensity')) return ['portfolio.multiplier','Enter a number from 0 to 3.'];
  if (message.startsWith('Enter between')) return ['portfolio.assets','Include between 1 and 12 assets.'];
  if (message.startsWith('Asset weights')) return ['portfolio.assets','Adjust asset weights so they total 100% (within 0.000001 percentage points); weights are not normalized on import.'];
  const assetMatch = message.match(/^Asset (\d+): (.*)$/);
  if (assetMatch) {
    const path = `portfolio.assets[${Number(assetMatch[1])-1}]`;
    const detail = assetMatch[2];
    const field = detail.includes('symbol') ? 'symbol' : detail.includes('group') ? 'group' : detail.includes('weight') ? 'weight' : detail.includes('volatility') ? 'volatility' : detail.includes('shock') ? 'shock' : '';
    return [field ? `${path}.${field}` : path, detail];
  }
  return ['portfolio',message];
}

export function serializePortfolio(state) {
  const errors = validate(state);
  if (errors.length) throw new TypeError(errors.join('\n'));
  const portfolio = {
    value:state.value,days:state.days,baseCorrelation:state.baseCorrelation,stressCorrelation:state.stressCorrelation,
    multiplier:state.multiplier,preset:state.preset,
    assets:state.assets.map(asset=>({id:asset.id,symbol:asset.symbol,group:asset.group,weight:asset.weight,volatility:asset.volatility,shock:asset.shock}))
  };
  const envelope = {schema:SCHEMA_ID,schemaVersion:SCHEMA_VERSION,portfolio};
  const serialized=`${JSON.stringify(envelope,null,2)}\n`;
  const checked=parsePortfolioImport(serialized);
  if(!checked.ok) throw new TypeError(checked.errors.map(error=>`${error.path}: ${error.message}`).join('\n'));
  return serialized;
}

export function parsePortfolioImport(text) {
  const errors=[];
  if (typeof text !== 'string') return {ok:false,errors:[{path:'$',message:'Select a UTF-8 JSON file.'}]};
  if (new TextEncoder().encode(text).byteLength > MAX_IMPORT_BYTES) return {ok:false,errors:[{path:'$',message:`File exceeds the ${MAX_IMPORT_BYTES}-byte import limit.`}]};
  const source=text.startsWith('\uFEFF')?text.slice(1):text;
  let parsed;
  try { parsed=JSON.parse(source); }
  catch { return {ok:false,errors:[{path:'$',message:'File is not valid JSON or is too deeply nested.'}]}; }
  if (!isRecord(parsed)) return {ok:false,errors:[{path:'$',message:'Use a JSON object with the supported portfolio envelope.'}]};
  checkKeys(parsed,['schema','schemaVersion','portfolio'],'$',errors);
  if (Object.hasOwn(parsed,'schema') && parsed.schema !== SCHEMA_ID) errors.push({path:'schema',message:`Use schema "${SCHEMA_ID}".`});
  if (Object.hasOwn(parsed,'schemaVersion') && (typeof parsed.schemaVersion !== 'number' || !Number.isInteger(parsed.schemaVersion) || parsed.schemaVersion !== SCHEMA_VERSION)) errors.push({path:'schemaVersion',message:`Only schema version ${SCHEMA_VERSION} is supported; export a version ${SCHEMA_VERSION} portfolio.`});
  const portfolio=parsed.portfolio;
  if (!isRecord(portfolio)) {
    if (Object.hasOwn(parsed,'portfolio')) errors.push({path:'portfolio',message:'Use an object containing the portfolio fields.'});
  } else {
    checkKeys(portfolio,PORTFOLIO_KEYS,'portfolio',errors);
    for (const key of ['value','days','baseCorrelation','stressCorrelation','multiplier']) if (Object.hasOwn(portfolio,key) && typeError(portfolio[key],'number')) errors.push({path:`portfolio.${key}`,message:'Enter a finite JSON number.'});
    if (Object.hasOwn(portfolio,'preset') && typeError(portfolio.preset,'string')) errors.push({path:'portfolio.preset',message:'Use a preset name or "custom".'});
    if (Object.hasOwn(portfolio,'assets') && !Array.isArray(portfolio.assets)) errors.push({path:'portfolio.assets',message:'Use an array containing 1 to 12 assets.'});
    if (Array.isArray(portfolio.assets)) portfolio.assets.forEach((asset,index)=>{
      const path=`portfolio.assets[${index}]`;
      if (!isRecord(asset)) { errors.push({path,message:'Use an asset object.'}); return; }
      checkKeys(asset,ASSET_KEYS,path,errors);
      for (const key of ['id','symbol','group']) if (Object.hasOwn(asset,key) && typeError(asset[key],'string')) errors.push({path:`${path}.${key}`,message:'Enter text for this field.'});
      for (const key of ['weight','volatility','shock']) if (Object.hasOwn(asset,key) && typeError(asset[key],'number')) errors.push({path:`${path}.${key}`,message:'Enter a finite JSON number.'});
      for (const key of ['id','symbol']) if (typeof asset[key] === 'string' && /[\u0000-\u001f\u007f-\u009f]/u.test(asset[key])) errors.push({path:`${path}.${key}`,message:'Remove control characters from this text.'});
      if (typeof asset.id === 'string' && !/^[A-Za-z0-9_-]{1,64}$/.test(asset.id)) errors.push({path:`${path}.id`,message:'Use 1–64 letters, numbers, underscores, or hyphens for the asset ID.'});
    });
    if (typeof portfolio.preset === 'string' && portfolio.preset !== 'custom' && !Object.hasOwn(PRESETS,portfolio.preset)) errors.push({path:'portfolio.preset',message:'Choose a supported preset or "custom".'});
    if (typeof portfolio.preset === 'string' && Object.hasOwn(PRESETS,portfolio.preset) && Array.isArray(portfolio.assets)) portfolio.assets.forEach((asset,index)=>{
      if (isRecord(asset) && typeof asset.group === 'string' && Object.hasOwn(PRESETS[portfolio.preset].shocks,asset.group) && typeof asset.shock === 'number' && asset.shock !== PRESETS[portfolio.preset].shocks[asset.group]) errors.push({path:`portfolio.assets[${index}].shock`,message:`Match the ${portfolio.preset} preset shock for this asset group, or set preset to "custom".`});
    });
    if (Array.isArray(portfolio.assets)) {
      const ids=new Set();
      portfolio.assets.forEach((asset,index)=>{if(isRecord(asset)&&typeof asset.id==='string'){if(ids.has(asset.id))errors.push({path:`portfolio.assets[${index}].id`,message:'Use a unique asset ID.'});ids.add(asset.id);}});
    }
    if (PORTFOLIO_KEYS.every(key=>Object.hasOwn(portfolio,key)) && Array.isArray(portfolio.assets)) {
      for (const message of validate({version:1,...portfolio})) {
        const [path,friendly]=mapValidationMessage(message);
        if (!errors.some(error=>error.path===path && error.message===friendly)) errors.push({path,message:friendly});
      }
      const symbolKeys=new Set();
      portfolio.assets.forEach((asset,index)=>{
        if(typeof asset.symbol==='string') {
          if(!asset.symbol.trim()||asset.symbol.length>12) errors.push({path:`portfolio.assets[${index}].symbol`,message:'Use a non-empty symbol of at most 12 characters.'});
          const key=asset.symbol.trim().toUpperCase();if(symbolKeys.has(key))errors.push({path:`portfolio.assets[${index}].symbol`,message:'Use a symbol unique without regard to letter case.'});symbolKeys.add(key);
        }
      });
    }
  }
  if(errors.length) return {ok:false,errors};
  const copy={value:portfolio.value,days:portfolio.days,baseCorrelation:portfolio.baseCorrelation,stressCorrelation:portfolio.stressCorrelation,multiplier:portfolio.multiplier,preset:portfolio.preset,assets:portfolio.assets.map(asset=>({id:asset.id,symbol:asset.symbol,group:asset.group,weight:asset.weight,volatility:asset.volatility,shock:asset.shock}))};
  return {ok:true,portfolio:copy};
}

const INVALID_MESSAGE = 'Saved inputs were invalid; demo loaded';

export function restoreState(raw, demoState) {
  if (!raw) return { state: demoState, message: '' };
  try {
    const parsed = JSON.parse(raw);
    if (parsed?.version === 1 && validate(parsed).length === 0 && parsed.assets.every(a => typeof a.id === 'string') && new Set(parsed.assets.map(a => a.id)).size === parsed.assets.length) {
      return { state: parsed, message: 'Restored your saved inputs' };
    }
  } catch {
    // Malformed or structurally invalid saved data falls back to the demo.
  }
  return { state: demoState, message: INVALID_MESSAGE };
}

export function csvCell(value) {
  const safeValue = typeof value === 'string' && /^[=+\-@\t\r]/.test(value) ? `'${value}` : value;
  return `"${String(safeValue).replaceAll('"', '""')}"`;
}

export function serializeCsv(rows) {
  return rows.map(row => row.map(csvCell).join(',')).join('\r\n');
}

export function toCsvRows(state, result, scenarioName = state.preset) {
  const rows = [['Crypto Stress Lab — hypothetical scenario results'],['Exported at (UTC)',new Date().toISOString()],['Portfolio value USD',state.value],['Scenario',scenarioName],['Shock multiplier',state.multiplier],['Risk horizon days',state.days],['Baseline correlation',state.baseCorrelation],['Stressed correlation',state.stressCorrelation],[],['Asset','Group','Weight %','Annual volatility %','Base shock %','Effective shock %','Scenario P&L USD','Stressed variance risk share %'],...result.assets.map(a=>[a.symbol,a.group,a.weight,a.volatility,a.shock,a.effectiveShock*100,a.pnl,result.stressedSigma===0?'':a.riskShare*100]),[],['Metric','Value'],['Scenario return %',result.portfolioReturn*100],['Scenario drawdown %',result.drawdown*100],['Scenario P&L USD',result.pnl],['Ending value USD',result.endValue],['Baseline horizon volatility %',result.baselineSigma*result.horizonScale*100],['Stressed horizon volatility %',result.stressedSigma*result.horizonScale*100],['95% normal model downside %',result.stressedDownside*100],['HHI',result.hhi],['Effective positions',result.effectiveAssets],['Equal-weight scenario return %',result.equalReturn*100],['Equal-weight horizon volatility %',result.equalSigma*result.horizonScale*100],[],['Preset comparison','Return %'],...result.comparisons.map(a=>[a.name,a.return*100]),[],['Limitations','Hypothetical long-only spot model. No fees, liquidity, leverage, liquidation, taxes or path effects. Scenario drawdown is a one-step loss, not maximum path drawdown. Common equicorrelation normal risk model; no forecasts.']];
  return rows.concat([[],['Gaussian tail risk (stressed)'],['Metric','Value'],['99% normal model downside %',result.stressedDownside99*100],['95% normal model expected shortfall %',result.stressedExpectedShortfall95*100],['99% normal model expected shortfall %',result.stressedExpectedShortfall99*100],['95% normal model downside USD',result.stressedDownside*state.value],['99% normal model downside USD',result.stressedDownside99*state.value],['95% normal model expected shortfall USD',result.stressedExpectedShortfall95*state.value],['99% normal model expected shortfall USD',result.stressedExpectedShortfall99*state.value]]);
}
