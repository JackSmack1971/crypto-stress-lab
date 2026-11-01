import { PRESETS, GROUPS, sampleState, validate, calculate, normalizeWeights, reverseStress } from './engine.mjs';
import { restoreState, serializeCsv, toCsvRows } from './persistence.mjs';
const $ = id => document.getElementById(id);
const STORAGE_KEY = 'crypto-stress-lab:v1';
const colors = ['#edb963','#a4a0fb','#7de2c3','#70b5eb','#f58f9e','#c3d879','#e4a8ef','#81c8ce','#d3a584','#8aafff','#bfccdd','#d989c2'];
const esc = v => String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num = (n,d=2) => n.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const pct = (n,d=2) => `${num(n*100,d)}%`;
const signedPct = n => `${n<0?'−':n>0?'+':''}${pct(Math.abs(n))}`;
const money = n => `${n<0?'−':''}$${num(Math.abs(n))}`;
const signedMoney = n => `${n>0?'+':''}${money(n)}`;
const summaryMoney = n => Math.abs(n)<1e6 ? signedMoney(n) : `${n<0?'−':n>0?'+':''}$${new Intl.NumberFormat('en-US',{notation:'compact',minimumFractionDigits:2,maximumFractionDigits:2}).format(Math.abs(n))}`;
const numericValue = el => el.value.trim() === '' ? NaN : Number(el.value);
let state = sampleState(), result = null, storageAvailable = true, toastTimer;
let loadMessage = '';
try {
  const restored = restoreState(localStorage.getItem(STORAGE_KEY), state);
  state = restored.state;
  loadMessage = restored.message;
} catch { storageAvailable=false;loadMessage='Browser storage unavailable; inputs remain in this tab'; }
function toast(message) { $('toast').textContent=message;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,3800); }
function save() {
  if (!storageAvailable) { $('save-status').textContent='Tab-only · storage unavailable'; return; }
  try { localStorage.setItem(STORAGE_KEY,JSON.stringify(state));$('save-status').textContent='Saved in this browser'; }
  catch { storageAvailable=false;$('save-status').textContent='Tab-only · storage unavailable'; }
}
function coin(a,i) { return `<span class="coin" style="--coin:${colors[i%colors.length]};--coin-bg:${colors[i%colors.length]}1c">${esc(a.symbol.slice(0,1).toUpperCase() || '·')}</span>`; }
function renderAssets() {
  $('asset-list').innerHTML=state.assets.map((a,i)=>`<div class="asset-card" data-id="${esc(a.id)}"><div class="asset-card-heading">${coin(a,i)}<input class="symbol-input" data-field="symbol" aria-label="Asset ${i+1} symbol" maxlength="12" value="${esc(a.symbol)}"><select class="asset-group" data-field="group" aria-label="${esc(a.symbol || 'Asset '+(i+1))} group">${Object.entries(GROUPS).map(([v,n])=>`<option value="${v}" ${a.group===v?'selected':''}>${n}</option>`).join('')}</select><button class="delete-asset" data-remove="${esc(a.id)}" aria-label="Remove ${esc(a.symbol || 'asset '+(i+1))}" ${state.assets.length===1?'disabled':''}><svg class="icon"><use href="#i-trash"/></svg></button></div><div class="asset-fields">${[['weight','Weight',0,100],['volatility','Annual vol.',0,300],['shock','Base shock',-100,300]].map(([field,label,min,max])=>`<div class="asset-field"><label for="${esc(a.id)}-${field}">${label} %</label><div class="percent-input"><input id="${esc(a.id)}-${field}" data-field="${field}" type="number" inputmode="${field==='shock'?'text':'decimal'}" min="${min}" max="${max}" step="any" value="${Number.isFinite(a[field])?a[field]:''}" aria-label="${esc(a.symbol || 'Asset '+(i+1))} ${label} percent"><span>%</span></div></div>`).join('')}</div></div>`).join('');
  $('asset-count').textContent=state.assets.length;
  $('add-asset').disabled=state.assets.length>=12;
}
function syncControls() {
  $('portfolio-value').value=state.value;$('days').value=state.days;$('scenario').value=Object.hasOwn(PRESETS,state.preset)?state.preset:'custom';
  $('intensity').value=state.multiplier;$('base-correlation').value=state.baseCorrelation;$('stress-correlation').value=state.stressCorrelation;
  renderAssets();
}
function updateLabels() {
  $('intensity-value').value=`${num(state.multiplier)}×`;
  $('base-correlation-value').value=num(state.baseCorrelation);
  $('stress-correlation-value').value=num(state.stressCorrelation);
  $('scenario-description').textContent=PRESETS[state.preset]?.description || 'Your per-asset shocks. Adjust each asset’s base shock above.';
  const total=state.assets.reduce((s,a)=>s+a.weight,0);
  $('weight-total').textContent=Number.isFinite(total)?`${num(total)}%`:'—';
  $('weight-total').classList.toggle('invalid',!Number.isFinite(total)||Math.abs(total-100)>1e-6);
}
function scenarioChart(r) {
  const data=[{name:'Your scenario',return:r.portfolioReturn,current:true},...r.comparisons];
  const bound=Math.max(.1,Math.ceil(Math.max(...data.map(d=>Math.abs(d.return)))*10)/10);
  $('scenario-chart').innerHTML=data.map(d=>{
    const width=Math.abs(d.return)/bound*50;
    const left=d.return<0?50-width:50;
    return `<div class="scenario-row ${d.current?'current':''}"><span class="scenario-name" title="${esc(d.name)}">${esc(d.name)}</span><div class="bar-track" role="img" aria-label="${esc(d.name)} return ${signedPct(d.return)}"><div class="scenario-bar" style="left:${left}%;width:${width}%;${d.return===0?'opacity:0':''}"></div></div><strong class="scenario-value ${d.return<0?'negative':d.return>0?'positive':''}">${signedPct(d.return)}</strong></div>`;
  }).join('')+`<div class="bar-axis" aria-hidden="true">${[-1,-.5,0,.5,1].map(t=>`<span>${t>0?'+':''}${num(t*bound*100,0)}%</span>`).join('')}</div>`;
}
function correlationChart(r) {
  const W=400,H=190,L=38,R=15,T=21,B=36,pw=W-L-R,ph=H-T-B;
  const ymax=Math.max(.01,Math.ceil(Math.max(...r.curve.map(p=>p.sigma))*100/5)*.05);
  const x=rho=>L+rho*pw,y=sigma=>T+ph-sigma/ymax*ph;
  const line=r.curve.map((p,i)=>`${i?'L':'M'}${x(p.rho).toFixed(2)},${y(p.sigma).toFixed(2)}`).join(' ');
  const points=[{rho:state.baseCorrelation,sigma:r.baselineSigma*r.horizonScale,color:'#8bafff',label:'Baseline'},{rho:state.stressCorrelation,sigma:r.stressedSigma*r.horizonScale,color:'#7de2c3',label:'Stressed'}];
  $('correlation-chart').innerHTML=`<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="correlation-title correlation-desc"><title id="correlation-title">Correlation sensitivity</title><desc id="correlation-desc">Horizon volatility rises as common asset correlation rises. Baseline correlation ${num(state.baseCorrelation)} gives ${pct(points[0].sigma)} volatility. Stressed correlation ${num(state.stressCorrelation)} gives ${pct(points[1].sigma)} volatility.</desc><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#7de2c3" stop-opacity=".12"/><stop offset="100%" stop-color="#7de2c3" stop-opacity="0"/></linearGradient></defs>${[0,.5,1].map(t=>`<line x1="${L}" x2="${W-R}" y1="${y(t*ymax)}" y2="${y(t*ymax)}" stroke="#283341" stroke-dasharray="3 5"/><text x="${L-8}" y="${y(t*ymax)+4}" fill="#8c9bae" font-size="10" text-anchor="end">${num(t*ymax*100,0)}%</text>`).join('')}<path d="${line} L${x(1)},${T+ph} L${L},${T+ph} Z" fill="url(#area)"/><path d="${line}" fill="none" stroke="#7de2c3" stroke-width="2"/>${points.map(p=>`<line x1="${x(p.rho)}" x2="${x(p.rho)}" y1="${T}" y2="${T+ph}" stroke="${p.color}" opacity=".4" stroke-dasharray="3 4"/><circle cx="${x(p.rho)}" cy="${y(p.sigma)}" r="4.5" fill="${p.color}" stroke="#111720" stroke-width="2"><title>${p.label}: ρ ${num(p.rho)}, volatility ${pct(p.sigma)}</title></circle>`).join('')}${[0,.25,.5,.75,1].map(t=>`<text x="${x(t)}" y="${H-18}" fill="#8c9bae" font-size="10" text-anchor="middle">${t===0?'0':t===1?'1.0':num(t)}</text>`).join('')}<text x="${L+pw/2}" y="${H-2}" fill="#8c9bae" font-size="9" text-anchor="middle">Common asset correlation (ρ)</text></svg>`;
}
function allocationChart(r) {
  let offset=0;
  const circles=state.assets.map((a,i)=>{const w=a.weight;const s=`<circle cx="75" cy="75" r="58" pathLength="100" fill="none" stroke="${colors[i%colors.length]}" stroke-width="13" stroke-dasharray="${w} ${100-w}" stroke-dashoffset="${-offset}" transform="rotate(-90 75 75)"><title>${esc(a.symbol)}: ${num(w)}%</title></circle>`;offset+=w;return w>0?s:'';}).join('');
  $('donut').innerHTML=`<svg class="chart" viewBox="0 0 150 150" role="img" aria-label="Portfolio allocation; largest position ${pct(r.largestWeight,1)}"><circle cx="75" cy="75" r="58" fill="none" stroke="#26303e" stroke-width="13"/>${circles}<text x="75" y="72" text-anchor="middle" fill="#eef3f7" font-size="24" font-weight="550">${num(r.effectiveAssets,1)}</text><text x="75" y="90" text-anchor="middle" fill="#8c9bae" font-size="8">effective positions</text></svg>`;
  $('allocation-legend').innerHTML=state.assets.map((a,i)=>`<div class="allocation-item" style="--coin:${colors[i%colors.length]}"><i></i><span class="allocation-symbol" title="${esc(a.symbol)}">${esc(a.symbol.toUpperCase())}</span><strong>${num(a.weight,a.weight%1?1:0)}%</strong></div>`).join('');
}
function renderResults(r) {
  $('metric-drawdown').textContent=pct(r.drawdown);
  $('metric-drawdown').className=r.drawdown>0?'negative':'';
  $('metric-end').textContent=`Ending value ${money(r.endValue)}`;
  $('metric-loss').textContent=summaryMoney(r.pnl);$('metric-loss').title=signedMoney(r.pnl);$('metric-loss').className=r.pnl<0?'negative':r.pnl>0?'positive':'';
  $('metric-loss-detail').textContent=Math.abs(r.pnl)>=1e6?`Exact P&L ${signedMoney(r.pnl)}`:`From a ${money(state.value)} portfolio`;
  const diff=(r.stressedSigma-r.baselineSigma)*r.horizonScale;
  $('metric-uplift').textContent=`${diff>0?'+':diff<0?'−':''}${num(Math.abs(diff)*100)} pp`;
  $('metric-uplift-detail').textContent=`${pct(r.baselineSigma*r.horizonScale)} → ${pct(r.stressedSigma*r.horizonScale)} horizon vol.`;
  $('metric-effective').textContent=`${num(r.effectiveAssets,2)} / ${state.assets.length}`;
  $('metric-concentration').textContent=`HHI ${num(r.hhi,3)} · largest weight ${pct(r.largestWeight,0)}`;
  $('scenario-label').textContent=PRESETS[state.preset]?.name || 'Custom scenario';
  $('base-sigma').textContent=pct(r.baselineSigma*r.horizonScale);$('stress-sigma').textContent=pct(r.stressedSigma*r.horizonScale);
  $('horizon-label').textContent=`${num(state.days,0)}D`;
  $('downside').textContent=`${pct(r.stressedDownside)} ↓`;
  $('downside-99').textContent=`${pct(r.stressedDownside99)} ↓`;
  $('expected-shortfall-95').textContent=pct(r.stressedExpectedShortfall95);
  $('expected-shortfall-99').textContent=pct(r.stressedExpectedShortfall99);
  $('downside-usd').textContent=money(r.stressedDownside*state.value);
  $('downside-99-usd').textContent=money(r.stressedDownside99*state.value);
  $('expected-shortfall-95-usd').textContent=money(r.stressedExpectedShortfall95*state.value);
  $('expected-shortfall-99-usd').textContent=money(r.stressedExpectedShortfall99*state.value);
  $('actual-vol').textContent=pct(r.stressedSigma*r.horizonScale);$('equal-vol').textContent=pct(r.equalSigma*r.horizonScale);
  $('actual-return').textContent=signedPct(r.portfolioReturn);$('equal-return').textContent=signedPct(r.equalReturn);
  $('concentration-note').textContent=`Equal weights: ${pct(1/state.assets.length,1)} per listed asset. ${r.stressedSigma>r.equalSigma?'Your allocation has higher':'Your allocation has equal or lower'} modeled volatility than equal weights.`;
  $('attribution').innerHTML=r.assets.map((a,i)=>`<tr><th scope="row">${coin(a,i)}${esc(a.symbol.toUpperCase())}</th><td class="numeric">${num(a.weight)}%</td><td class="numeric ${a.effectiveShock<0?'negative':a.effectiveShock>0?'positive':''}">${signedPct(a.effectiveShock)}</td><td class="numeric ${a.pnl<0?'negative':a.pnl>0?'positive':''}">${signedMoney(a.pnl)}</td><td class="numeric">${r.stressedSigma===0?'—':pct(a.riskShare,1)}</td></tr>`).join('');
  $('table-return').textContent=signedPct(r.portfolioReturn);$('table-pnl').textContent=signedMoney(r.pnl);$('table-risk').textContent=r.stressedSigma===0?'—':'100.0%';
  scenarioChart(r);correlationChart(r);allocationChart(r);
}
function updateReverse() {
  const mode=$('reverse-mode').value, unit=$('reverse-unit').value, select=$('reverse-selection');
  const wrap=$('reverse-selection-wrap');wrap.hidden=mode==='portfolio';
  const prior=select.value;select.replaceChildren();
  const choices=mode==='asset'?state.assets.map(a=>[a.symbol,a.symbol]):mode==='group'?Object.entries(GROUPS):[];
  for(const [value,label] of choices) select.add(new Option(label,value));
  if(choices.some(([value])=>value===prior))select.value=prior;
  const output=$('reverse-result');
  try {
    const reverse=reverseStress(state,{mode,selector:select.value,unit,target:numericValue($('reverse-target'))});
    output.classList.remove('reverse-error');
    if(!reverse.reachable){output.textContent=`Unreachable. Maximum loss for ${reverse.label} is ${pct(reverse.maxLoss)} (${money(reverse.maxLossUsd)}).`;return;}
    output.textContent=`${reverse.label}: required uniform shock ${signedPct(reverse.requiredShock)} · P&L ${signedMoney(reverse.pnl)} · ending value ${money(reverse.endValue)}${reverse.atFloor?' · maximum loss (−100% floor)':''}.`;
  } catch(error) { output.classList.add('reverse-error');output.textContent=error.message; }
}
function update() {
  updateLabels();
  const errors=validate(state);
  $('errors').hidden=!errors.length;$('results').hidden=!!errors.length;$('export').disabled=!!errors.length;$('run').disabled=!!errors.length;
  if(errors.length){
    result=null;$('errors').innerHTML=`<strong>Check your inputs to run the analysis.</strong><ul>${errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`;
    ['metric-drawdown','metric-loss','metric-uplift','metric-effective'].forEach(id=>$(id).textContent='—');
    ['metric-end','metric-loss-detail','metric-uplift-detail','metric-concentration'].forEach(id=>$(id).textContent='Waiting for valid inputs');
    $('analysis-status').textContent='Inputs need attention';$('save-status').textContent='Invalid edits · not saved';return;
  }
  result=calculate(state);renderResults(result);updateReverse();save();
  $('analysis-status').textContent=result.capped?'Updated · losses capped at −100% per asset':'Updated · all assumptions applied';
}
$('asset-list').addEventListener('input',e=>{
  const field=e.target.dataset.field;if(!field || field==='group')return;
  const a=state.assets.find(a=>a.id===e.target.closest('[data-id]').dataset.id);a[field]=field==='symbol'?e.target.value:numericValue(e.target);
  if(field==='shock') {state.preset='custom';$('scenario').value='custom';}
  if(field==='symbol') {
    const card=e.target.closest('[data-id]');card.querySelector('.coin').textContent=a.symbol.slice(0,1).toUpperCase()||'·';
    const label=a.symbol.trim()||'Asset';card.querySelector('[data-field="group"]').setAttribute('aria-label',`${label} group`);card.querySelector('[data-remove]').setAttribute('aria-label',`Remove ${label}`);
    for(const [fieldName,fieldLabel] of [['weight','Weight'],['volatility','Annual vol.'],['shock','Base shock']]) card.querySelector(`[data-field="${fieldName}"]`).setAttribute('aria-label',`${label} ${fieldLabel} percent`);
  }
  update();
});
$('asset-list').addEventListener('change',e=>{
  if(e.target.dataset.field!=='group')return;
  const a=state.assets.find(a=>a.id===e.target.closest('[data-id]').dataset.id);a.group=e.target.value;
  if(PRESETS[state.preset]) {a.shock=PRESETS[state.preset].shocks[a.group];renderAssets();}
  update();
});
$('asset-list').addEventListener('click',e=>{
  const button=e.target.closest('[data-remove]');if(!button || state.assets.length<=1)return;
  state.assets=state.assets.filter(a=>a.id!==button.dataset.remove);renderAssets();update();$('add-asset').focus();
});
$('add-asset').addEventListener('click',()=>{
  if(state.assets.length>=12)return;
  let i=state.assets.length+1;while(state.assets.some(a=>a.symbol===`ASSET${i}`))i++;
  const id=`asset-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,9)}`;state.assets.push({id,symbol:`ASSET${i}`,group:'altcoin',weight:0,volatility:100,shock:PRESETS[state.preset]?.shocks.altcoin??-40});renderAssets();update();document.querySelector(`[data-id="${id}"] .symbol-input`).focus();
});
$('normalize').addEventListener('click',()=>{try{state.assets=normalizeWeights(state.assets);renderAssets();update();toast('Weights normalized to 100%.');}catch(e){toast(e.message);}});
for(const [id,key] of [['portfolio-value','value'],['days','days'],['intensity','multiplier'],['base-correlation','baseCorrelation'],['stress-correlation','stressCorrelation']]) $(id).addEventListener('input',e=>{state[key]=numericValue(e.target);update();});
$('scenario').addEventListener('change',e=>{state.preset=e.target.value;if(PRESETS[state.preset])state.assets=state.assets.map(a=>({...a,shock:PRESETS[state.preset].shocks[a.group]}));renderAssets();update();});
$('run').addEventListener('click',()=>{update();if(result){$('results').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});toast('Stress test complete. Results reflect your current inputs.');}});
$('reset').addEventListener('click',()=>{if(!confirm('Replace your current inputs with the demo portfolio?'))return;state=sampleState();syncControls();update();toast('Demo portfolio restored.');});
$('downside-info').addEventListener('click',()=>{$('methodology').open=true;$('methodology').scrollIntoView({behavior:'smooth',block:'start'});$('methodology').querySelector('summary').focus();});
$('export').addEventListener('click',()=>{
  if(!result)return;
  const rows=toCsvRows(state,result,PRESETS[state.preset]?.name || 'Custom');
  const blob=new Blob(['\ufeff'+serializeCsv(rows)],{type:'text/csv;charset=utf-8;'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`crypto-stress-results-${new Date().toISOString().slice(0,10)}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('Results and assumptions exported as CSV.');
});
syncControls();update();if(loadMessage)toast(loadMessage);
$('reverse-mode').addEventListener('change',updateReverse);
$('reverse-unit').addEventListener('change',updateReverse);
$('reverse-selection').addEventListener('change',updateReverse);
$('reverse-target').addEventListener('input',updateReverse);
