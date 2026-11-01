import { validate } from './engine.mjs';

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
  return [['Crypto Stress Lab — hypothetical scenario results'],['Exported at (UTC)',new Date().toISOString()],['Portfolio value USD',state.value],['Scenario',scenarioName],['Shock multiplier',state.multiplier],['Risk horizon days',state.days],['Baseline correlation',state.baseCorrelation],['Stressed correlation',state.stressCorrelation],[],['Asset','Group','Weight %','Annual volatility %','Base shock %','Effective shock %','Scenario P&L USD','Stressed variance risk share %'],...result.assets.map(a=>[a.symbol,a.group,a.weight,a.volatility,a.shock,a.effectiveShock*100,a.pnl,result.stressedSigma===0?'':a.riskShare*100]),[],['Metric','Value'],['Scenario return %',result.portfolioReturn*100],['Scenario drawdown %',result.drawdown*100],['Scenario P&L USD',result.pnl],['Ending value USD',result.endValue],['Baseline horizon volatility %',result.baselineSigma*result.horizonScale*100],['Stressed horizon volatility %',result.stressedSigma*result.horizonScale*100],['95% normal model downside %',result.stressedDownside*100],['HHI',result.hhi],['Effective positions',result.effectiveAssets],['Equal-weight scenario return %',result.equalReturn*100],['Equal-weight horizon volatility %',result.equalSigma*result.horizonScale*100],[],['Preset comparison','Return %'],...result.comparisons.map(a=>[a.name,a.return*100]),[],['Limitations','Hypothetical long-only spot model. No fees, liquidity, leverage, liquidation, taxes or path effects. Scenario drawdown is a one-step loss, not maximum path drawdown. Common equicorrelation normal risk model; no forecasts.']];
}
