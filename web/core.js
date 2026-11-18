// Pure report queries. No network access, UI state or Power BI dependency.
export const COLORS={Mining:'#183323',Refining:'#479A67',Imports:'#183323',Exports:'#479A67',CPS:'#00B6AD',STEPS:'#FF616A',HDS:'#465B60'};
export const PAGES=[['supply','Global Supply Landscape'],['trade','European Trade & Dependency'],['risk','Supply Chain Risk'],['outlook','Future Outlook']];
export const finite=x=>typeof x==='number'&&Number.isFinite(x);
export const sum=xs=>{const a=xs.filter(finite);return a.length?a.reduce((s,x)=>s+x,0):null;};
export const safe=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function defaults(page){return {page,material:page==='risk'?'All':page==='trade'?'REE':'Cu',year:page==='trade'?2024:page==='supply'?2025:2030,reporter:'DE',tradeYear:2024,basis:'trade_value',allGrades:page==='outlook'};}
export function normalize(d,raw){const page=PAGES.some(p=>p[0]===raw.page)?raw.page:'supply',s={...defaults(page),...raw,page};
 if(!d.Materials.some(m=>m.Symbol===s.material)&&!(page==='risk'&&s.material==='All'))s.material=defaults(page).material;
 const years=page==='trade'?[2018,2019,2020,2021,2022,2023,2024]:page==='outlook'?[2025,2030,2035,2040,2045,2050]:[2025,2030,2035,2040];
 if(!years.includes(+s.year))s.year=defaults(page).year;else s.year=+s.year;
 if(!d.Reporters.some(r=>r.ReporterCode===s.reporter))s.reporter='DE';
 if(![2018,2019,2020,2021,2022,2023,2024].includes(+s.tradeYear))s.tradeYear=2024;else s.tradeYear=+s.tradeYear;
 if(!['trade_value','product_mass'].includes(s.basis))s.basis='trade_value';
 s.allGrades=s.allGrades===true||s.allGrades==='true';return s;}
export function definition(d,s,symbol=s.material){const m=d.Materials.find(m=>m.Symbol===symbol);return d.Definitions.find(r=>r.Family===m?.Family&&(r.Material==='Graphite: all grades')===(symbol==='C'&&s.page==='outlook'&&s.allGrades));}
export const product=(d,s)=>d.Products.find(p=>p.Family===d.Materials.find(m=>m.Symbol===s.material)?.Family);
export const reporter=(d,s)=>d.Reporters.find(r=>r.ReporterCode===s.reporter);
export function supply(d,s){const def=definition(d,s);return ['Mining','Refining'].map(stage=>{
 const rows=d.Supply.filter(r=>r.DefinitionKey===def?.DefinitionKey&&r.Year===s.year&&r.Stage===stage);
 const concentration=d.Concentration.find(r=>r.DefinitionKey===def?.DefinitionKey&&r.Year===s.year&&r.Stage===stage)||null;
 return {stage,rows,total:rows.length?rows[0].PanelTonnes:null,concentration};});}
export function supplyTrend(d,s){const key=definition(d,s)?.DefinitionKey;return [2025,2030,2035,2040].map(year=>({year,...Object.fromEntries(['Mining','Refining'].map(stage=>[stage,sum(d.Supply.filter(r=>r.DefinitionKey===key&&r.Stage===stage&&r.Year===year).map(r=>r.QuantityTonnes))]))}));}
export function supplyCountries(d,s){const panels=supply(d,s),names=[...new Set(panels.flatMap(p=>p.rows.map(r=>r.Country)))].sort((a,b)=>a.localeCompare(b,'en'));return names.map(name=>({name,values:panels.map(p=>p.rows.find(r=>r.Country===name)?.Share??null)}));}
export function trade(d,s){const p=product(d,s),r=reporter(d,s),match=x=>x.ProductCode===p?.ProductCode&&x.ReporterKey===r?.ReporterKey&&x.Basis===s.basis;
 const trend=[2018,2019,2020,2021,2022,2023,2024].map(year=>({year,Imports:d.Trade.find(x=>match(x)&&x.Year===year)?.Imports??null,Exports:d.Trade.find(x=>match(x)&&x.Year===year)?.Exports??null}));
 const snapshot=d.Trade.find(x=>match(x)&&x.Year===s.year)||null,exposure=d.Exposure.find(x=>match(x)&&x.Year===s.year)||null;
 const partners=[...d.PartnerDisplay].sort((a,b)=>a.SortOrder-b.SortOrder).map(p=>({name:p.PartnerDisplay,values:[sum(d.Partners.filter(x=>match(x)&&x.Year===s.year&&x.Flow==='Import'&&x.PartnerDisplay===p.PartnerDisplay).map(x=>x.Share))]}));
 return {product:p,reporter:r,trend,snapshot,exposure,partners};}
export function risks(d,s){return [...d.Materials].sort((a,b)=>a.SortOrder-b.SortOrder).filter(m=>s.material==='All'||m.Symbol===s.material).map(m=>{const def=definition(d,s,m.Symbol);const get=stage=>d.Concentration.find(r=>r.DefinitionKey===def?.DefinitionKey&&r.Year===s.year&&r.Stage===stage)||null;return {name:m.Symbol,label:m.MaterialName,Mining:get('Mining'),Refining:get('Refining')};});}
export function sensitivity(d,s){const r=reporter(d,s);return d.Products.filter(p=>s.material==='All'||p.Family===d.Materials.find(m=>m.Symbol===s.material)?.Family).map(p=>({name:p.ProductShort,...(d.Sensitivity.find(x=>x.ReporterKey===r?.ReporterKey&&x.ProductCode===p.ProductCode&&x.Year===s.tradeYear)||{})})).sort((a,b)=>a.name.localeCompare(b.name,'en'));}
export function outlook(d,s){const key=definition(d,s)?.DefinitionKey,rows=d.Outlook.filter(r=>r.DefinitionKey===key),scenarios=['CPS','STEPS','HDS'];
 const at=(scenario,year)=>rows.find(r=>r.ScenarioShort===scenario&&r.Year===year&&r.SeriesKind==='demand_reported_end_uses_sum')||null;
 return {scenarios,cards:scenarios.map(name=>({name,row:at(name,s.year)})),trend:[2025,2030,2035,2040,2045,2050].map(year=>({year,...Object.fromEntries(scenarios.map(sc=>[sc,at(sc,year)?.QuantityTonnes??null]))})),
 endUses:[...d.EndUses].sort((a,b)=>a.SortOrder-b.SortOrder).map(e=>({name:e.EndUse,values:scenarios.map(sc=>sum(rows.filter(r=>r.ScenarioShort===sc&&r.Year===s.year&&r.SeriesKind==='demand_end_use'&&r.EndUse===e.EndUse).map(r=>r.QuantityTonnes)))})),
 supply:[2025,2030,2035,2040].map(year=>({year,...Object.fromEntries(['Mining','Refining'].map(stage=>[stage,sum(rows.filter(r=>r.SeriesKind==='supply_panel_output'&&r.Stage===stage&&r.Year===year).map(r=>r.QuantityTonnes))]))}))};}
