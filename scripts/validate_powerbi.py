"""Verify the native project, CSV values and source contracts without claiming Desktop execution."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,re,sys,urllib.parse,warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.common import dumps,utc_now
from build_powerbi import MEASURES


def validate(project,database):
 import duckdb,jsonschema
 project=Path(project);root=Path(__file__).resolve().parents[1];schemas=root/'config/powerbi_schemas'
 manifest=json.loads((project/'data/export_manifest.json').read_text());store={}
 for f in schemas.rglob('*.json'):
  x=json.loads(f.read_text());url='https://developer.microsoft.com/json-schemas/'+str(f.relative_to(schemas));store[url]=x;store[f.resolve().as_uri()]=x
  if '$id'in x:store[x['$id']]=x
 count=0;visual_count=0;issues=[];references=0
 for path in project.rglob('*'):
  if path.suffix not in ['.json','.pbip','.pbir','.pbism'] or path.name=='export_manifest.json' or '.pbi'in path.parts:continue
  x=json.loads(path.read_text(),parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)));uri=x.get('$schema')
  if not uri:
   if 'theme'in path.name.lower() or 'StaticResources'in path.parts:schema=json.loads((schemas/'reportThemeSchema-2.159.json').read_text());validator=jsonschema.Draft7Validator(schema)
   else:continue
  else:
   schema=store[uri];resolver=jsonschema.RefResolver(base_uri=uri,referrer=schema,store=store);validator=jsonschema.Draft7Validator(schema,resolver=resolver)
  for err in validator.iter_errors(x):issues.append(str(path.relative_to(project))+':'+err.message[:300])
  count+=1
  if path.name=='visual.json':
   visual_count+=1;pos=x['position'];assert pos['x']>=0 and pos['y']>=0 and pos['x']+pos['width']<=1600 and pos['y']+pos['height']<=900
   for role,config in x['visual'].get('query',{}).get('queryState',{}).items():
    for projection in config.get('projections',[]):
     obj=projection['field'];kind='Measure' if 'Measure'in obj else 'Column';ref=obj[kind];table=ref['Expression']['SourceRef']['Entity'];column=ref['Property'];references+=1
     if kind=='Measure':assert table=='ReportMeasures' and column in MEASURES,(table,column)
     else:assert column in {v['name'] for v in manifest['tables'][table]['columns']},(table,column)
 # PBIR structural schemas intentionally allow free visual types/format objects.
 # Check native type/card names against Microsoft's vendored theme schema as well.
 theme_schema=json.loads((schemas/'reportThemeSchema-2.159.json').read_text())
 formatting_checked=0
 for path in project.glob('GlobalCriticalMaterials.Report/definition/pages/*/visuals/*/visual.json'):
  visual=json.loads(path.read_text())['visual'];kind=visual['visualType']
  assert 'visual-'+kind in theme_schema['definitions'],('Unknown native visual type',kind)
  cards={}
  for part in theme_schema['definitions']['visual-'+kind].get('allOf',[]):cards.update(part.get('properties',{}))
  for card,entries in visual.get('objects',{}).items():
   assert card in cards,(kind,'Unknown formatting card',card)
   allowed=cards[card].get('items',{}).get('properties',{})
   if allowed:
    for entry in entries:
     assert not (set(entry.get('properties',{}))-set(allowed)-{'filter'}),(kind,card,'Unknown property')
     formatting_checked+=len(entry.get('properties',{}))
 assert not issues,issues
 # DAX metadata checks cover column/measure references; evaluation needs a real Desktop model.
 dax_refs=0
 for name,spec in MEASURES.items():
  for table,column in re.findall(r'\b([A-Za-z][A-Za-z0-9_]*)\[([^\]]+)\]',spec['expression']):
   assert table in manifest['tables'] and column in {x['name'] for x in manifest['tables'][table]['columns']},(name,table,column);dax_refs+=1
 bare_refs={}
 for name,spec in MEASURES.items():
  bare_refs[name]=re.findall(r'(?<![A-Za-z0-9_])\[([^\]]+)\]',spec['expression'])
  assert set(bare_refs[name])<=set(MEASURES),(name,bare_refs[name])
 def acyclic(name,ancestors):
  assert name not in ancestors,'Circular DAX measure reference'
  for dep in bare_refs[name]:acyclic(dep,ancestors|{name})
 for name in MEASURES:acyclic(name,set())
 c=duckdb.connect(str(Path(database).resolve()),read_only=True);values_checked=0;rows_checked=0
 for table,meta in manifest['tables'].items():
  file=project/'data'/(table+'.csv');assert hashlib.sha256(file.read_bytes()).hexdigest()==meta['sha256'],table
  expected=c.execute('select * from ('+meta['source_sql']+') as checked order by all').fetchall()
  types={x['name']:x['duckdb_type'] for x in meta['columns']}
  actual=c.execute('select * from read_csv(?,header=true,columns=?) order by all',[str(file.resolve()),types]).fetchall()
  assert expected==actual,table+' CSV values differ from source SQL'
  assert len(actual)==meta['rows'];values_checked+=len(actual)*len(meta['columns']);rows_checked+=len(actual)
 # Native relationships may not introduce unmatched keys or ambiguous dimension duplicates.
 rel=(project/'GlobalCriticalMaterials.SemanticModel/definition/relationships.tmdl').read_text()
 columns={t:{col['name'] for col in info['columns']} for t,info in manifest['tables'].items()}
 relations=re.findall(r'fromColumn: (\w+)\.(\w+)\s+toColumn: (\w+)\.(\w+)',rel)
 loaded={t:list(csv.DictReader((project/'data'/(t+'.csv')).open(encoding='utf-8'))) for t in manifest['tables']}
 for ft,fc,tt,tc in relations:
  assert fc in columns[ft] and tc in columns[tt];vals=[r[tc] for r in loaded[tt]];assert len(vals)==len(set(vals)) and '' not in vals
  assert {r[fc] for r in loaded[ft] if r[fc]}<=set(vals),(ft,fc,tt,tc)
 c.close()
 return {'checked_at_utc':utc_now(),'status':'passed_static_and_data_checks_pending_Desktop','schema_files_validated':count,'native_visuals':visual_count,'native_formatting_properties_checked':formatting_checked,'visual_field_references_checked':references,'dax_column_references_checked':dax_refs,'tables':len(manifest['tables'])+1,'measures':len(MEASURES),'relationships_checked':len(relations),'export_rows_checked':rows_checked,'export_scalar_values_checked':values_checked,'source_selection_key':manifest['source_selection_key'],'source_csv_value_comparison':'exact_typed_round_trip_against_DuckDB','font':{'display':json.loads((project/'CriticalMaterialsSage.theme.json').read_text())['textClasses']['title']['fontFace'],'body':json.loads((project/'CriticalMaterialsSage.theme.json').read_text())['textClasses']['label']['fontFace']},'Desktop_open_refresh_DAX_evaluation':'not_executed_by_this_static_and_data_validator','PBIX_created':False}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',type=Path,required=True);parser.add_argument('--database',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();report=validate(args.project,args.database);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(dumps(report)+'\n');print(dumps(report))
