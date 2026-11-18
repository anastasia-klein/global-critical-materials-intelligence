"""Build the public, dependency-free browser snapshot from verified Power BI inputs."""
from pathlib import Path
import csv,hashlib,json,sys,argparse,collections
from verify_report_inputs import verify
ROOT=Path(__file__).resolve().parents[1]
COLUMNS={
 'Materials':'Family Symbol MaterialName AtomicNumber Category CategoryColor SortOrder',
 'Definitions':'DefinitionKey Material Family DefinitionScope QuantityBasis',
 'Products':'ProductCode ProductShort DefinitionScope Family',
 'Reporters':'ReporterKey ReporterLabel ReporterCode TradeScope',
 'Supply':'DefinitionKey Year Stage Country EntityType QuantityTonnes Share PanelTonnes DisplayLatitude DisplayLongitude',
 'Concentration':'DefinitionKey Year Stage HHILower HHIUpper Top3Lower Top3Upper ResidualShare MetricStatus',
 'Trade':'ProductCode ReporterKey Year Basis Imports Exports Balance',
 'Exposure':'ProductCode ReporterKey Year Basis HHILower HHIUpper TopSupplierLower TopSupplierUpper DenominatorStatus',
 'Sensitivity':'ProductCode ReporterKey Year ValueHHILower ValueHHIUpper MassHHILower MassHHIUpper',
 'Outlook':'DefinitionKey Year Stage ScenarioShort SeriesKind EndUse QuantityTonnes Growth CAGR',
 'PartnerDisplay':'PartnerDisplay SortOrder','EndUses':'EndUse SortOrder'}
def build(output):
 source=ROOT/'dashboards/powerbi';verify(source)
 manifest=json.loads((source/'data/export_manifest.json').read_text());tables={}
 def read(name):
  spec=manifest['tables'][name];types={c['name']:c['duckdb_type'] for c in spec['columns']}
  result=[]
  for row in csv.DictReader((source/'data'/(name+'.csv')).open(encoding='utf-8',newline='')):
   parsed={}
   for key,value in row.items():
    typ=types[key]
    parsed[key]=None if value=='' else (int(value) if typ in ('INTEGER','BIGINT') else float(value) if typ in ('DOUBLE','FLOAT') or typ.startswith('DECIMAL') else value)
   result.append(parsed)
  return result
 for name,columns in COLUMNS.items():tables[name]=[{c:r[c] for c in columns.split()} for r in read(name)]
 # Same fixed PartnerDisplay grouping and SUM/null semantics as the Power BI chart.
 groups={}
 for r in read('Partners'):
  key=tuple(r[c] for c in ['ProductCode','ReporterKey','Year','Basis','Flow','PartnerDisplay'])
  g=groups.setdefault(key,{'Amount':None,'Share':None})
  for col in ['Amount','Share']:
   if r[col] is not None:g[col]=(g[col] or 0)+r[col]
 tables['Partners']=[dict(zip(['ProductCode','ReporterKey','Year','Basis','Flow','PartnerDisplay'],k),**v) for k,v in sorted(groups.items())]
 data={'meta':{'selection':manifest['source_selection_key'],'capture':manifest['source_capture_label'],
 'sourceCaptures':manifest['source_captures'],'sourceHashes':{t:manifest['tables'][t]['sha256'] for t in [*COLUMNS,'Partners']},
 'attribution':'IEA (2026), Critical Minerals Dataset, GCMO2026, CC BY 4.0. Eurostat DS-045409, reuse with attribution. Derived analysis by Anastasia Klein; not endorsed by IEA or Eurostat.'},'tables':tables}
 output.mkdir(parents=True,exist_ok=True)
 (output/'snapshot.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n')
 geo=json.loads((ROOT/'dashboards/assets/ne_world_110m.geojson').read_text())
 # Only public-domain geographic display geometry; discard unrelated source attributes.
 world={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':f['properties'].get('NAME_EN',f['properties'].get('NAME',''))},'geometry':f['geometry']} for f in geo['features'] if f['properties'].get('ISO_A3_EH')!='ATA']}
 (output/'world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n')
 return {'selection':data['meta']['selection'],'tables':{k:len(v) for k,v in tables.items()},'snapshot_bytes':(output/'snapshot.json').stat().st_size}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'web/data');a=p.parse_args();print(json.dumps(build(a.output)))
