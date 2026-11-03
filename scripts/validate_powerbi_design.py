"""Check the report's presentation contracts against original exported facts.

This does not evaluate DAX or emulate the Desktop rendering engine.
"""
from pathlib import Path
import argparse,csv,json,math,collections

def validate(project):
 project=Path(project)
 def rows(t):return list(csv.DictReader((project/'data'/(t+'.csv')).open(encoding='utf-8')))
 def literal(v):return v['expr']['Literal']['Value']
 pages=list((project/'GlobalCriticalMaterials.Report/definition/pages').glob('*/page.json'))
 tiles=[];zero_count=0;scalars=0
 from build_powerbi import FONT_STACK
 def fonts(node):
  if isinstance(node,dict):
   for k,v in node.items():
    if k in ['fontFamily','fontFace']:yield v if isinstance(v,str) else literal(v)[1:-1].replace("''","'")
    else:yield from fonts(v)
  elif isinstance(node,list):
   for v in node:yield from fonts(v)
 for page in pages:
  cfg=json.loads(page.read_text());assert (cfg['width'],cfg['height'],cfg['displayOption'])==(1600,900,'FitToPage')
  visuals=[json.loads(p.read_text()) for p in page.parent.glob('visuals/*/visual.json')]
  material=[v for v in visuals if v['visual']['visualType']=='advancedSlicerVisual' and v['visual']['query']['queryState']['Values']['projections'][0]['queryRef']=='Materials.Symbol'];assert len(material)==1
  v=material[0];tiles.append(v['position']);obj=v['visual']['objects'];layout=obj['layout'][0]['properties']
  for key,value in [('fixedHeight','104D'),('fixedWidth','104D'),('columnCount','6D'),('showFixedSize','true')]:assert literal(layout[key])==value
  for card in ['value','label','padding','outline','fillCustom']:
   assert {r['selector']['id'] for r in obj[card]}=={'default','selection:selected','interaction:hover'},card
  assert v['visual']['query']['queryState']['Label']['projections'][0]['queryRef']=='ReportMeasures.Material tile label'
  for v in visuals:
   assert all(f==FONT_STACK for f in fonts(v))
   assert literal(v['visual']['visualContainerObjects']['general'][0]['properties']['keepLayerOrder'])=='true'
   if v['visual']['visualType']=='slicer':assert v['position']['height']>=80
   if v['visual']['visualType']=='advancedSlicerVisual':
    for name in ['image','accentBar','selectionIcon']:
     if name=='image' and v['visual']['query']['queryState']['Values']['projections'][0]['queryRef']=='DefinitionChoice.GraphiteScope':continue
     assert all(literal(row['properties']['show'])=='false' for row in v['visual']['objects'][name])
  text=[v for v in visuals if v['visual']['visualType']=='textbox']
  numbers=[v for v in text if v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value'] in ['29','27','3','28','6','group']]
  assert len(numbers)==6 and all(v['position']['height']>=32 for v in numbers)
  licenses=[v for v in text if any('CC BY 4.0' in r['value'] for p in v['visual']['objects']['general'][0]['properties']['paragraphs'] for r in p['textRuns'])]
  assert len(licenses)==1 and licenses[0]['position']['x']>=800
  assert licenses[0]['visual']['objects']['general'][0]['properties']['paragraphs'][0]['horizontalTextAlignment']=='right'
  visible=' '.join(run['value'] for v in text for paragraph in v['visual']['objects']['general'][0]['properties']['paragraphs'] for run in paragraph['textRuns'])
  assert 'EXPLORATORY ANALYSIS  ·  IEA & EUROSTAT DATA' in visible
  heading=next(v for v in text if v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value']=='Global critical materials')
  assert heading['position']['height']==60
  assert tiles[-1]['y']==90
  assert 'PORTFOLIO ANALYSIS' not in visible and 'SUPPLY INTELLIGENCE / EUROPE' not in visible
  if cfg['name']=='01_supply':
   country=next(v for v in visuals if v['visual']['visualType']=='clusteredBarChart')
   assert literal(country['visual']['objects']['labels'][0]['properties']['show'])=='true'
   legend=next(v for v in text if v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value']=='● Mining     ')
   assert legend['position']['x']>=950 and legend['position']['y']<260
   assert legend['visual']['objects']['general'][0]['properties']['paragraphs'][0]['horizontalTextAlignment']=='right'
   m=next(v for v in visuals if v['visual']['visualType']=='azureMap')['visual'];assert 'Series' not in m['query']['queryState']
   assert m['query']['queryState']['Category']['projections'][0]['queryRef']=='Supply.MapPoint'
  if cfg['name']=='04_outlook':
   assert not any(v['visual'].get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[{}])[0].get('queryRef','').startswith('ScenarioChoice.') for v in visuals)
   scenario_cards=[v for v in visuals if v['visual']['visualType']=='card']
   assert len(scenario_cards)==9
   assert all(literal(v['visual']['visualContainerObjects']['title'][0]['properties']['alignment'])=="'center'" for v in scenario_cards)
   toggle=next(v for v in visuals if v['visual'].get('query',{}).get('queryState',{}).get('Values',{}).get('projections',[{}])[0].get('queryRef')=='DefinitionChoice.GraphiteScope')
   assert toggle['position']['width']==48 and toggle['position']['height']==28 and toggle['position']['x']==1412 and toggle['position']['y']==103
   assert toggle['visual']['objects']['general'][0]['properties']['filter']['filter']['Where'][0]['Condition']['In']['Values']==[[{'Literal':{'Value':"'All grades'"}}]]
   for card in ['value','label']:
    assert all(literal(r['properties']['transparency'])=='100D' for r in toggle['visual']['objects'][card])
   assert all(literal(r['properties']['show'])=='false' for r in toggle['visual']['objects']['value'])
   state_images={r['selector']['id']:r['properties'] for r in toggle['visual']['objects']['image']}
   for state in ['default','interaction:hover','interaction:press','selection:selected','selection:selected-interaction:hover','selection:selected-interaction:press']:
    image=state_images[state];assert literal(image['show'])=='true' and literal(image['sourceType'])=="'image'"
    expected='GraphiteToggle'+('On' if 'selection:selected' in state else 'Off')+'0001.svg'
    assert image['imageFile']['image']['url']['expr']['ResourcePackageItem']['ItemName']==expected
   from xml.etree import ElementTree as ET
   report=project/'GlobalCriticalMaterials.Report'
   package=json.loads((report/'definition/report.json').read_text())['resourcePackages'][0]
   for on in [False,True]:
    name='GraphiteToggle'+('On' if on else 'Off')+'0001.svg'
    assert any(r['name']==name and r['path']==name and r['type']=='Image' for r in package['items'])
    svg=ET.fromstring((report/'StaticResources/RegisteredResources'/name).read_text())
    circle=svg.find('{http://www.w3.org/2000/svg}circle');assert circle.attrib['cx']==('47' if on else '13')
    assert svg.find('.//{http://www.w3.org/2000/svg}text').text==('On' if on else 'Off')
   for scenario,expected in [('CPS','#08B7AE'),('STEPS','#FF686B'),('HDS','#465A5D')]:
    run=next(v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0] for v in text if v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value']==scenario)
    assert run['textStyle']['color']==expected
   assert literal(toggle['visual']['objects']['selection'][0]['properties']['strictSingleSelect'])=='false'
   assert toggle['filterConfig']['filters'][0]['filter']['Where'][0]['Condition']['In']['Values']==[[{'Literal':{'Value':"'All grades'"}}]]
   labels=[v['visual']['query']['queryState']['Values']['projections'][0]['queryRef'].split('.')[1] for v in scenario_cards]
   assert all(sum(name.startswith(sc+' ') for name in labels)==3 for sc in ['CPS','STEPS','HDS'])
   end=next(v for v in visuals if v['visual']['visualType']=='clusteredBarChart')
   assert [v['displayName'] for v in end['visual']['query']['queryState']['Y']['projections']]==['CPS','STEPS','HDS']
  if cfg['name']=='03_risk':
   scatter=next(v for v in visuals if v['visual']['visualType']=='scatterChart')
   assert scatter['position']['width']==scatter['position']['height']
   assert 'output tonnes' in literal(scatter['visual']['objects']['categoryAxis'][0]['properties']['titleText'])
   t=next(v for v in visuals if v['visual']['visualType']=='tableEx')
   assert sum(float(literal(v['properties']['value'])[:-1]) for v in t['visual']['objects']['columnWidth'])<=t['position']['width']-24

  if cfg['name'] in ['02_trade','04_outlook']:
   chart=next(v for v in visuals if v['visual']['visualType']=='clusteredBarChart')
   if cfg['name']=='02_trade':
    assert chart['position']['height']>=488
    assert literal(chart['visual']['objects']['categoryAxis'][0]['properties']['preferredCategoryWidth'])=='12D'
   q=chart['visual']['query'];assert q['queryState']['Category']['showAll']
   assert q['sortDefinition']['sort'][0]['direction']=='Ascending'
  if cfg['name']=='03_risk':
   charts=[v for v in visuals if v['visual']['visualType']=='clusteredBarChart'];assert len(charts)==1
   assert len(charts[0]['visual']['query']['queryState']['Y']['projections'])==2
 assert len({tuple(p[k] for k in ['x','y','width','height']) for p in tiles})==1
 supply_model=(project/'GlobalCriticalMaterials.SemanticModel/definition/tables/Supply.tmdl').read_text()
 assert 'WithMapPoint = if Table.HasColumns(Headers, "MapPoint")' in supply_model and 'Table.TransformColumnTypes(WithMapPoint' in supply_model
 materials=rows('Materials');assert len(materials)==6
 assert {r['Symbol']:r['AtomicNumber'] for r in materials}=={'Cu':'29','Co':'27','Li':'3','Ni':'28','C':'6','REE':''}
 assert len({r['CategoryColor'] for r in materials if r['Category']=='Transition metal'})==1
 # Grouping only changes display labels, never country-level amounts or denominators.
 groups={r['PartnerDisplay'] for r in rows('PartnerDisplay')};assert 'Other partners' in groups
 p=rows('Partners');raw=collections.defaultdict(float);grouped=collections.defaultdict(lambda:collections.defaultdict(float))
 for r in p:
  key=tuple(r[k] for k in ['ReporterKey','ProductCode','Year','Flow','Basis'])
  assert r['PartnerDisplay'] in groups
  if r['Share']:
   raw[key]+=float(r['Share']);grouped[key][r['PartnerDisplay']]+=float(r['Share'])
 for key,val in raw.items():assert math.isclose(val,sum(grouped[key].values()),abs_tol=1e-12);scalars+=1
 # Distinguish 9 explicit reported zeros from absent end-use observations.
 ends=rows('EndUses');out=rows('Outlook');end_names={r['EndUse'] for r in ends}
 detail=[r for r in out if r['SeriesKind']=='demand_end_use'];assert len(end_names)==8
 assert all(r['EndUse'] in end_names for r in detail)
 for r in detail:
  assert r['QuantityTonnes']!=''
  if float(r['QuantityTonnes'])==0:
   zero_count+=1;assert r['EndUse']=='Grid battery storage'
 assert zero_count==9
 index={(r['DefinitionKey'],r['Scenario'],r['Year'],r['EndUse']):r for r in detail};assert len(index)==len(detail)
 # Shared tiles must filter both exact definitions and traded product forms.
 rel=(project/'GlobalCriticalMaterials.SemanticModel/definition/relationships.tmdl').read_text()
 for table in ['Definitions','Products']:assert 'fromColumn: '+table+'.Family\n\ttoColumn: Materials.Family' in rel
 for table,col in [('Materials','Symbol'),('PartnerDisplay','PartnerDisplay'),('EndUses','EndUse')]:
  model=(project/'GlobalCriticalMaterials.SemanticModel/definition/tables'/(table+'.tmdl')).read_text();assert '\tcolumn '+col+'\n' in model and 'sortByColumn: SortOrder' in model
 # Complete country bars include the opaque residual without assigning it a location.
 from build_powerbi import MEASURES
 assert 'IN {"country_or_territory","residual"}' in MEASURES['Country share']['expression']
 assert 'Supply[EntityType]="country_or_territory"' in MEASURES['Map share']['expression']
 panels=collections.defaultdict(list)
 for r in rows('Supply'):panels[(r['DefinitionKey'],r['Year'],r['Stage'])].append(r)
 assert all(math.isclose(sum(float(r['Share']) for r in rs),1,abs_tol=1e-9) for rs in panels.values())
 assert all(sum(r['EntityType']=='residual' for r in rs)==1 for rs in panels.values())
 # Display offsets are available for every genuine country point; residuals stay excluded.
 map_rows=[r for r in rows('Supply') if r['EntityType']=='country_or_territory']
 assert all(r['DisplayLatitude'] and r['DisplayLongitude'] for r in map_rows)
 assert all(r['MapPoint']==r['Country']+' / '+r['Stage'] for r in map_rows)
 scenarios=collections.defaultdict(dict)
 for r in detail:scenarios[(r['DefinitionKey'],r['Year'],r['EndUse'])][r['ScenarioShort']]=float(r['QuantityTonnes'])
 assert all(set(v)=={'CPS','STEPS','HDS'} for v in scenarios.values())
 inversions=sum(not (v['CPS']<=v['STEPS']+1e-9<=v['HDS']+1e-9) for v in scenarios.values())

 return {'status':'passed_presentation_contracts_pending_Desktop','pages':len(pages),'identical_material_tile_groups':len(tiles),'partner_axis_groups':len(groups),'partner_scope_totals_preserved':scalars,'end_use_axis_categories':len(ends),'reported_zero_observations_preserved':zero_count,'reported_end_use_rows':len(detail),'supply_panels_with_residual_and_unit_share_sum':len(panels),'map_country_rows_with_display_coordinates':len(map_rows),'scenario_end_use_groups_compared':len(scenarios),'nonmonotonic_scenario_groups':inversions,'scenario_chart':'three_comparable_bars_not_additive_stacks','Desktop_rendering_and_DAX_evaluation':'pending'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.project);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
