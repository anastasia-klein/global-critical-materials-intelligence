"""Native four-page PBIR report with paired stages and button slicers."""
from pathlib import Path
from datetime import date
from build_powerbi import BASE,COLORS as C,save,lit,color,props,field,projection,ident,FONT_STACK

DISPLAY_FONT="Arial"
BODY_FONT="Avenir Next"
CAPTURE_LABEL='Source capture: see export manifest'
SCENARIO_COLORS={'CPS':'#08B7AE','STEPS':'#FF686B','HDS':'#465A5D'}
STAGE_COLORS={"Mining":C["teal"],"Refining":C["blue"]}

PAGES=[('01_supply','Global Supply Landscape'),('02_trade','European Trade & Dependency'),('03_risk','Supply Chain Risk'),('04_outlook','Future Outlook')]

class Page:
 def __init__(self,report,name,title):self.report,self.name,self.title=report,name,title;self.visuals=[];self.controls=set()
 def add(self,kind,x,y,w,h,title='',roles=None,objects=None,transparent=False,alt=''):
  name=ident(self.name+'/'+str(len(self.visuals))+'/'+kind).replace('-','')[:20]
  vc={'background':props(show=lit(not transparent),color=color(C['panel']),transparency=lit(100 if transparent else 0)),
      'border':props(show=lit(not transparent),color=color(C['edge']),radius=lit(20),width=lit(1)),
      'visualHeader':props(show=lit(False)),
      'dropShadow':props(show=lit(not transparent),color=color('#496148'),position=lit('Outer'),preset=lit('Custom'),shadowBlur=lit(12),shadowDistance=lit(2),shadowSpread=lit(0),angle=lit(90),transparency=lit(92)),
      'title':props(show=lit(bool(title)),text=lit(title),fontColor=color(C['text']),fontFamily=lit(DISPLAY_FONT),fontSize=lit(12),bold=lit(True)),
      'padding':props(top=lit(0 if transparent else 10),bottom=lit(0 if transparent else 8),left=lit(0 if transparent else 12),right=lit(0 if transparent else 12)),
      'general':props(altText=lit(alt or title or kind),keepLayerOrder=lit(True))}
  visual={'visualType':kind,'visualContainerObjects':vc,'drillFilterOtherVisuals':True}
  if objects:visual['objects']=objects
  if roles:visual['query']={'queryState':{role:{'projections':[projection(*f) for f in fields]} for role,fields in roles.items()}}
  out={'$schema':BASE+'item/report/definition/visualContainer/2.5.0/schema.json','name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':len(self.visuals)*1000,'tabOrder':len(self.visuals)*1000},'visual':visual}
  self.visuals.append(out);return out
 def text(self,x,y,w,h,text,size=12,fg=None,bold=False,align='left'):
  return self.add('textbox',x,y,w,h,objects={'general':props(paragraphs=[{'textRuns':[{'value':text,'textStyle':{'fontFamily':DISPLAY_FONT if size>=18 or bold else BODY_FONT,'fontSize':str(size)+'pt','color':fg or C['muted'],'fontWeight':'bold' if bold else 'normal'}}],'horizontalTextAlignment':align}])},transparent=True,alt=text)
 def slicer(self,x,y,w,label,table,column,default=None):
  objects={'data':props(mode=lit('Dropdown')),'header':props(show=lit(False)),
    'items':props(fontColor=color(C['text']),background=color(C['panel']),fontFamily=lit(BODY_FONT),textSize=lit(12),padding=lit(4)),
    'selection':props(singleSelect=lit(default is not None),strictSingleSelect=lit(default is not None),selectAllCheckboxEnabled=lit(False))}
  if default is not None:
   literal=str(default)+'L' if isinstance(default,int) else "'"+default.replace("'","''")+"'"
   objects['general']=props(filter={'filter':{'Version':2,'From':[{'Name':'s','Entity':table,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':column}}],'Values':[[{'Literal':{'Value':literal}}]]}}}]}})
  v=self.add('slicer',x,y,w,80,label,{'Values':[(table,column,False)]},objects);self.controls.add(v['name']);return v
 def buttons(self,x,y,w,label,table,column,default=None,count=None):
  count=count or 4
  states=['default','selection:selected','interaction:hover']
  def st(fn):return [{'selector':{'id':state},'properties':fn(state)} for state in states]
  if label:self.text(x+4,y+12,112,30,label,10,C['muted'],True);x+=124;w-=124
  gap=8;tile_width=int((w-gap*(count-1))/count)
  objects={
   'layout':props(orientation=lit(2),rowCount=lit(1),columnCount=lit(count),showFixedSize=lit(False),autoGrid=lit(True),cellPadding=lit(gap),style=lit('Cards'),topOuterMargin=lit(0),bottomOuterMargin=lit(0),leftOuterMargin=lit(0),rightOuterMargin=lit(0)),
   'selection':props(singleSelect=lit(True),strictSingleSelect=lit(True),selectAllCheckboxEnabled=lit(False)),
   'padding':st(lambda _:dict(paddingSelection=lit('Custom'),topMargin=lit(1),bottomMargin=lit(1),leftMargin=lit(2),rightMargin=lit(2))),
   'value':st(lambda state:dict(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(11),labelDisplayUnits=lit(1),bold=lit(state=='selection:selected'),fontColor=color(C['canvas'] if state=='selection:selected' else C['text']),horizontalAlignment=lit('center'),verticalAlignment=lit('middle'),textWrap=lit(False))),
   'label':st(lambda _:dict(show=lit(False))), 'image':st(lambda _:dict(show=lit(False))), 'accentBar':st(lambda _:dict(show=lit(False))), 'selectionIcon':st(lambda _:dict(show=lit(False))),
   'fillCustom':st(lambda state:dict(show=lit(True),fillColor=color(C['teal'] if state=='selection:selected' else C['panel']),transparency=lit(0))),
   'outline':st(lambda _:dict(show=lit(True),lineColor=color(C['edge']),weight=lit(1))),
   'shapeCustomRectangle':st(lambda _:dict(tileShape=lit('rectangleRoundedByPixel'),rectangleRoundedCurve=lit(6)))}
  if default is not None:
   literal=str(default)+'L' if isinstance(default,int) else "'"+default.replace("'","''")+"'"
   objects['general']=props(filter={'filter':{'Version':2,'From':[{'Name':'s','Entity':table,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':column}}],'Values':[[{'Literal':{'Value':literal}}]]}}}]}})
  v=self.add('advancedSlicerVisual',x,y,w,44,'',{'Values':[(table,column,False)]},objects,transparent=True,alt=label or 'Graphite scope: Graphite or All grades')
  v['visual']['query']['sortDefinition']={'sort':[{'field':field(table,column),'direction':'Descending' if table=='DefinitionChoice' else 'Ascending'}],'isDefaultSort':True}
  self.controls.add(v['name']);return v
 def scenario_panel(self,x,y,w,label,suffix):
  self.add('shape',x,y,w,106,label,objects={'shape':props(tileShape=lit('rectangle')),'fill':props(show=lit(False)),'outline':props(show=lit(False))})
  inner=(w-24)/3
  for i,scenario in enumerate(SCENARIO_COLORS):
   v=self.add('card',x+12+i*inner,y+32,inner,70,scenario,{'Values':[('ReportMeasures',scenario+' '+suffix,True)]},{'labels':props(color=color(SCENARIO_COLORS[scenario]),fontFamily=lit(DISPLAY_FONT),fontSize=lit(18),labelDisplayUnits=lit(1)),'categoryLabels':props(show=lit(False))},transparent=True)
   v['visual']['visualContainerObjects']['title'][0]['properties'].update(fontSize=lit(10),fontColor=color(SCENARIO_COLORS[scenario]),alignment=lit('center'))
 def graphite_toggle(self):
  # The visible item applies All grades; clearing it restores the Graphite
  # default. The saved report starts with All grades selected.
  v=self.buttons(1412,103,48,'','DefinitionChoice','GraphiteScope','All grades',1)
  v['position']['height']=28
  # Use embedded vector states: a slicer callout cannot replace its field's
  # displayed text with a decorative glyph. No font glyph represents the thumb.
  states=['default','selection:selected','interaction:hover','selection:selected-interaction:hover','interaction:press','selection:selected-interaction:press']
  def st(fn):return [{'selector':{'id':state},'properties':fn('selection:selected' in state)} for state in states]
  obj=v['visual']['objects']
  obj['value']=st(lambda _:dict(show=lit(False),fontSize=lit(8),transparency=lit(100)))
  obj['label']=st(lambda _:dict(show=lit(False),fontSize=lit(8),transparency=lit(100)))
  obj['padding']=st(lambda _:dict(paddingSelection=lit('Custom'),topMargin=lit(0),bottomMargin=lit(0),leftMargin=lit(0),rightMargin=lit(0)))
  obj['fillCustom']=st(lambda _:dict(show=lit(False)))
  obj['outline']=st(lambda _:dict(show=lit(False)))
  obj['shapeCustomRectangle']=st(lambda _:dict(tileShape=lit('pill')))
  def image_state(on):
   name='GraphiteToggle'+('On' if on else 'Off')+'0001.svg'
   resource={'expr':{'ResourcePackageItem':{'PackageName':'RegisteredResources','PackageType':1,'ItemName':name}}}
   return dict(show=lit(True),sourceType=lit('image'),imageFile={'image':{'name':lit(name),'url':resource,'scaling':lit('Normal')}},imageFit=lit('Normal'),setAsBackGround=lit(True),ignorePadding=lit(True),padding=lit(0),transparency=lit(0),altText=lit('All grades On' if on else 'All grades Off'))
  obj['image']=st(image_state)
  v['visual']['visualContainerObjects']['general'][0]['properties']['altText']=lit('All grades graphite toggle: off = Graphite; on = All grades. Click to change scope.')
  self.text(1359,105,54,26,'All grades',8,align='left')
  v['visual']['objects']['selection']=props(singleSelect=lit(False),strictSingleSelect=lit(False),selectAllCheckboxEnabled=lit(False))
  definition={'Version':2,'From':[{'Name':'g','Entity':'DefinitionChoice','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'g'}},'Property':'GraphiteScope'}}],'Values':[[{'Literal':{'Value':"'All grades'"}}]]}}}]}
  v['filterConfig']={'filters':[{'name':'graphite_scope_domain','field':field('DefinitionChoice','GraphiteScope'),'type':'Categorical','filter':definition,'howCreated':'User','isHiddenInViewMode':True,'isLockedInViewMode':True}]}
  return v
 def note(self,x,y,w,h,title,text):
  self.add('shape',x,y,w,h,title,objects={'shape':props(tileShape=lit('rectangle')),'fill':props(show=lit(False)),'outline':props(show=lit(False))})
  self.text(x+14,y+28,w-28,h-32,text,10)
 def materials(self,optional=False):
  x,y,w,h=898,90,674,112
  states=['default','selection:selected','interaction:hover']
  def st(fn):return [{'selector':{'id':state},'properties':fn(state)} for state in states]
  objects={
   'layout':props(orientation=lit(0),rowCount=lit(1),columnCount=lit(6),showFixedSize=lit(True),fixedHeight=lit(104),fixedWidth=lit(104),autoGrid=lit(False),cellPadding=lit(10),style=lit('Cards'),topOuterMargin=lit(0),bottomOuterMargin=lit(0),leftOuterMargin=lit(0),rightOuterMargin=lit(0)),
   'selection':props(singleSelect=lit(True),strictSingleSelect=lit(not optional),selectAllCheckboxEnabled=lit(False)),
   'padding':st(lambda _:dict(paddingSelection=lit('Custom'),topMargin=lit(16),bottomMargin=lit(8),leftMargin=lit(3),rightMargin=lit(3))),
   'value':st(lambda state:dict(show=lit(True),fontFamily=lit(DISPLAY_FONT),fontSize=lit(28),bold=lit(True),fontColor=color(C['text']),horizontalAlignment=lit('center'),verticalAlignment=lit('middle'),textWrap=lit(False),transparency=lit(0))),
   'label':st(lambda _:dict(show=lit(True),labelSource=lit('auto'),position=lit('belowValue'),fontFamily=lit(BODY_FONT),fontSize=lit(10),fontColor=color(C['text']),horizontalAlignment=lit('center'),textWrap=lit(False))),
   'fillCustom':st(lambda _:dict(show=lit(True),fillColor={'solid':{'color':{'expr':field('ReportMeasures','Material tile color',True)}}},transparency=lit(0))),
   'outline':st(lambda state:dict(show=lit(True),lineColor=color(C['teal'] if state=='selection:selected' else '#A6B8A5'),weight=lit(3 if state=='selection:selected' else 1))),
   'shapeCustomRectangle':st(lambda _:dict(tileShape=lit('rectangleRoundedByPixel'),rectangleRoundedCurve=lit(4))),
   'selectionIcon':st(lambda _:dict(show=lit(False))),
   'accentBar':st(lambda _:dict(show=lit(False))),
   'image':st(lambda _:dict(show=lit(False)))}
  for entry in objects['fillCustom']:entry['selector']['data']=[{'dataViewWildcard':{'matchingOption':1}}]
  if not optional:
   default_material={'01_supply':'Cu','02_trade':'REE','04_outlook':'Cu'}[self.name]
   objects['general']=props(filter={'filter':{'Version':2,'From':[{'Name':'s','Entity':'Materials','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':'Symbol'}}],'Values':[[{'Literal':{'Value':"'"+default_material+"'"}}]]}}}]}})
  v=self.add('advancedSlicerVisual',x,y,w,h,'',{'Values':[('Materials','Symbol',False)],'Label':[('ReportMeasures','Material tile label',True)]},objects,transparent=True,alt='Material family: Cu Copper, Co Cobalt, Li Lithium, Ni Nickel, C Graphite, REE Rare earths. Colors identify chemical categories, not risk.')
  v['visual']['visualContainerObjects']['padding']=props(top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))
  v['visual']['query']['sortDefinition']={'sort':[{'field':field('Materials','Symbol'),'direction':'Ascending'}],'isDefaultSort':True}
  self.controls.add(v['name'])
  # Tall number blocks avoid text scrollbars; fixed layer order keeps them visible.
  for i,n in enumerate(['29','27','3','28','6','group']):self.text(x+i*114+6,y+1,44,32,n,7 if n=='group' else 8,C['muted'])
  return v
 def card(self,x,y,w,label,name,accent=None):
  return self.add('card',x,y,w,92,label,{'Values':[('ReportMeasures',name,True)]},{'labels':props(color=color(accent or C['text']),fontFamily=lit(DISPLAY_FONT),fontSize=lit(19 if ('concentration' in name or 'top3' in name or name=='Supplier HHI label') else 25),labelDisplayUnits=lit(1)),'categoryLabels':props(show=lit(False))})
 def chart(self,kind,x,y,w,h,title,roles,sort=None,extra=None):
  objects={'categoryAxis':props(labelColor=color(C['muted']),fontFamily=lit(BODY_FONT),fontSize=lit(10),showAxisTitle=lit(False)),
   'valueAxis':props(labelColor=color(C['muted']),fontFamily=lit(BODY_FONT),fontSize=lit(10),showAxisTitle=lit(False),gridlineColor=color(C['edge']),gridlineShow=lit(True)),
   'legend':props(show=lit('Series' in roles or len(roles.get('Y',[]))>1),showTitle=lit(False),labelColor=color(C['text']),fontFamily=lit(BODY_FONT),fontSize=lit(10),position=lit('Top')),
   'labels':props(color=color(C['text']),fontFamily=lit(BODY_FONT),fontSize=lit(10))}
  if kind=='scatterChart':objects.pop('labels',None)
  if kind=='lineChart':
   objects['categoryAxis'][0]['properties']['axisType']=lit('Categorical')
   smooth=roles.get('Y',[('', '', False)])[0][1]=='Imports'
   objects['lineStyles']=props(showMarker=lit(True),showMarkerByDefault=lit(True),markerSize=lit(3),strokeWidth=lit(2.5),lineChartType=lit('smooth' if smooth else 'linear'),interpolationSmooth=lit('monotoneX'),strokeLineJoin=lit('round'))
  if kind in ['clusteredBarChart','barChart']:
   objects['categoryAxis'][0]['properties'].update(innerPadding=lit(35),outerPadding=lit(12))
  # Explicit measure colours survive filtering and series ordering.
  if 'Y' in roles:
   colors=[]
   for table,measure,is_measure in roles['Y']:
    if not is_measure:continue
    fg=SCENARIO_COLORS.get(measure.split()[0],C['blue'] if measure.startswith(('Refining','Exports')) or 'interval width' in measure else C['teal'])
    colors.append({'selector':{'metadata':table+'.'+measure},'properties':{'fill':color(fg)}})
   if colors:objects['dataPoint']=colors
  if extra:objects.update(extra)
  v=self.add(kind,x,y,w,h,title,roles,objects)
  for role in ['Y','X','Tooltips']:
   for item in v['visual']['query']['queryState'].get(role,{}).get('projections',[]):
    name=item['field'].get('Measure',{}).get('Property','')
    if name.split(' ')[0] in SCENARIO_COLORS:item['displayName']=name.split(' ')[0]
    elif name.startswith(('Mining','Refining')):item['displayName']=name.split(' ')[0]
  if sort:v['visual']['query']['sortDefinition']={'sort':[{'field':field(*sort[:2],measure=sort[2]),'direction':'Descending' if len(sort)<4 or sort[3]=='desc' else 'Ascending'}],'isDefaultSort':True}
  return v
 def table(self,x,y,w,h,title,fields):
  return self.add('tableEx',x,y,w,h,title,{'Values':fields},{
    'values':props(fontColor=color(C['text']),backColorPrimary=color(C['panel']),backColorSecondary=color('#F3F7F0'),fontFamily=lit(BODY_FONT),fontSize=lit(10),wordWrap=lit(True)),
    'columnHeaders':props(fontColor=color(C['teal']),backColor=color(C['panel']),fontFamily=lit(BODY_FONT),fontSize=lit(10),bold=lit(True),wordWrap=lit(True)),
    'grid':props(gridHorizontal=lit(True),gridHorizontalColor=color(C['edge']),gridVertical=lit(False),rowPadding=lit(5)),
    'total':props(totals=lit(False))})
 def common(self,headline,sub,footer):
  self.text(28,12,550,60,'Global critical materials',26,C['text'],True)
  subtitle=self.text(29,57,550,26,'EXPLORATORY ANALYSIS · IEA & EUROSTAT DATA',10)
  base_style=subtitle['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['textStyle']
  subtitle['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns']=[{'value':'EXPLORATORY ANALYSIS ','textStyle':dict(base_style)},{'value':'·','textStyle':dict(base_style,fontWeight='bold',fontSize='9pt',color=C['teal'])},{'value':' IEA & EUROSTAT DATA','textStyle':dict(base_style)}]
  nav=self.add('pageNavigator',600,24,972,50,transparent=True,objects={
    'layout':props(orientation=lit(2),cellPadding=lit(8)),
    'text':[{'selector':{'id':state},'properties':{'fontFamily':lit(BODY_FONT),'fontSize':lit(10.5),'fontColor':color(C['canvas'] if state=='selected' else C['muted']),'bold':lit(state=='selected'),'leftMargin':lit(4),'rightMargin':lit(4)}} for state in ['default','selected']],
    'fill':[{'selector':{'id':state},'properties':{'show':lit(True),'fillColor':color(C['teal'] if state=='selected' else C['panel'])}} for state in ['default','selected']],
    'outline':props(show=lit(False)),'shape':props(tileShape=lit('roundRect'),rectangleRoundedCurve=lit(14))})
  self.controls.add(nav['name'])
  self.text(28,92,830,48,headline,26,C['text'],True)
  self.text(29,143,820,34,sub,10,C['muted'])
  self.materials(optional=self.name=='03_risk')
  self.text(28,858,740,42,footer,8.5,C['muted'])
  self.text(850,854,722,22,'IEA GCMO2026 · CC BY 4.0 · Eurostat DS-045409',9,C['teal'],align='right')
  self.text(850,876,722,22,CAPTURE_LABEL+' · Reuse with attribution',9,C['teal'],align='right')
 def finish(self):
  interactions=[]
  charts=[v for v in self.visuals if v['visual']['visualType'] not in ['slicer','advancedSlicerVisual','textbox','pageNavigator','card']]
  targets=[v for v in self.visuals if v['visual']['visualType']!='textbox']
  for a in charts:
   for b in targets:
    if a['name']!=b['name']:interactions.append({'source':a['name'],'target':b['name'],'type':'NoFilter'})
  cfg={'$schema':BASE+'item/report/definition/page/2.0.0/schema.json','name':self.name,'displayName':self.title,'displayOption':'FitToPage','width':1600,'height':900,
   'objects':{'background':props(color=color(C['canvas']),transparency=lit(0)),'outspace':props(color=color(C['canvas']),transparency=lit(0))},'visualInteractions':interactions}
  folder=self.report/'definition/pages'/self.name;save(folder/'page.json',cfg)
  for v in self.visuals:save(folder/'visuals'/v['name']/'visual.json',v)


def build_report(root,manifest,display_font=FONT_STACK):
 global DISPLAY_FONT,BODY_FONT,CAPTURE_LABEL
 DISPLAY_FONT=display_font
 BODY_FONT=display_font
 captures=list(manifest.get('source_captures',{}).values())
 if captures:
  first=min(date.fromisoformat(c['first'][:10]) for c in captures);last=max(date.fromisoformat(c['last'][:10]) for c in captures)
  start=f'{first.day} {first:%b}'+(f' {first.year}' if first.year!=last.year else '')
  CAPTURE_LABEL='Captured '+(f'{last.day} {last:%b %Y}' if first==last else start+f'–{last.day} {last:%b %Y}')
 else:CAPTURE_LABEL='Source capture: see export manifest'
 report=root/'GlobalCriticalMaterials.Report';report.mkdir(exist_ok=True)
 import shutil
 for page_name,_ in PAGES:
  visual_dir=report/'definition/pages'/page_name/'visuals'
  if visual_dir.exists():shutil.rmtree(visual_dir)
 theme={'name':'Critical Materials · Sage','dataColors':[C['teal'],C['blue'],C['amber'],C['purple'],'#9CBDA0','#BDAD89'],
  'background':C['canvas'],'foreground':C['text'],'tableAccent':C['teal'],
  'good':C['teal'],'neutral':C['blue'],'bad':C['amber'],
  'textClasses':{k:{'fontFace':BODY_FONT if k=='label' else DISPLAY_FONT,'fontSize':n,'color':C['text'] if k!='label' else C['muted']} for k,n in [('callout',28),('title',14),('header',12),('label',10)]}}
 save(root/'CriticalMaterialsSage.theme.json',theme)
 save(report/'StaticResources/RegisteredResources/CriticalMaterialsSage.json',theme)
 # Original SVG artwork matches Power BI's compact On/Off control language.
 for on in [False,True]:
  name='GraphiteToggle'+('On' if on else 'Off')+'0001.svg'
  track='<rect x="1" y="1" width="58" height="26" rx="13" fill="#008272"/>' if on else '<rect x="1" y="1" width="58" height="26" rx="13" fill="#FFFFFF" stroke="#8A8886" stroke-width="1.5"/>'
  thumb='<circle cx="47" cy="14" r="8" fill="#FFFFFF"/>' if on else '<circle cx="13" cy="14" r="8" fill="#8A8886"/>'
  label='<text x="9" y="18" fill="#FFFFFF">On</text>' if on else '<text x="27" y="18" fill="#605E5C">Off</text>'
  svg='<svg xmlns="http://www.w3.org/2000/svg" width="60" height="28" viewBox="0 0 60 28" role="img" aria-label="All grades '+('On' if on else 'Off')+'">'+track+thumb+'<g font-family="Arial, sans-serif" font-size="12">'+label+'</g></svg>\n'
  (report/'StaticResources/RegisteredResources'/name).write_text(svg)
 save(report/'definition.pbir',{'$schema':BASE+'item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../GlobalCriticalMaterials.SemanticModel'}}})
 save(report/'definition/version.json',{'$schema':BASE+'item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
 save(report/'definition/report.json',{'$schema':BASE+'item/report/definition/report/3.0.0/schema.json',
  'themeCollection':{'customTheme':{'name':'CriticalMaterialsSage','reportVersionAtImport':{'visual':'2.5.0','page':'2.0.0','report':'3.0.0'},'type':'RegisteredResources'}},
  'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'CriticalMaterialsSage','path':'CriticalMaterialsSage.json','type':'CustomTheme'}]+[{'name':'GraphiteToggle'+state+'0001.svg','path':'GraphiteToggle'+state+'0001.svg','type':'Image'} for state in ['Off','On']]}],
  'objects':{'outspacePane':props(expanded=lit(False))},
  'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized','useEnhancedTooltips':False}})
 save(report/'definition/pages/pages.json',{'$schema':BASE+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':[p[0] for p in PAGES],'activePageName':PAGES[0][0]})
 # Supply: independent stage points, no legend field that could trigger pies.
 p=Page(report,*PAGES[0]);p.common('Where are mining and refining concentrated?',
  'STEPS / Base Case · Mining: forest green · Refining: leaf green · Independent stage denominators',
  'Expected output, not capacity · 2025 baseline/basis unverified · Other countries is opaque')
 p.buttons(28,180,650,'Supply year','SupplyYears','Year',2025,4)
 p.text(896,200,672,32,'Material scope: native IEA definition · Graphite excludes all-grades graphite · Tile colours identify chemical category',9)
 for i,(label,m) in enumerate([('Mining · Output','Mining output label'),('Refining · Output','Refining output label'),('Mining · HHI bounds','Mining concentration label'),('Refining · HHI bounds','Refining concentration label'),('Mining · Top 3 bounds','Mining top3 label'),('Refining · Top 3 bounds','Refining top3 label')]):
  p.card(28+(i%2)*260,230+(i//2)*108,244,label,m,C['teal'] if i%2==0 else C['blue'])
 p.add('azureMap',550,230,604,308,'Country shares · Mining / Refining',{'Category':[('Supply','MapPoint',False)],'X':[('ReportMeasures','Map longitude',True)],'Y':[('ReportMeasures','Map latitude',True)],'Size':[('ReportMeasures','Map share',True)],'Tooltips':[('ReportMeasures','Map country',True),('ReportMeasures','Map stage',True)]},
  {'mapControls':props(defaultStyle=lit('grayscale_light'),autoZoom=lit(True),showStylePicker=lit(False),showNavigationControls=lit(True)),
   'bubbleLayer':props(show=lit(True),sizeByValue=lit(True),clusteringEnabled=lit(False),minBubbleRadius=lit(3),maxRadius=lit(18),mapTransparency=lit(15)),
   'commonDataOptions':props(showZeros=lit(False)), 'legend':props(show=lit(False)),
   'dataPoint':[{'properties':{'showAllDataPoints':lit(True)}},{'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}]},'properties':{'fill':{'solid':{'color':{'expr':field('ReportMeasures','Map color',True)}}}}}]},alt='Country display anchors, mining 3 degrees west and refining 3 degrees east; not facilities. Separate country/stage marker identities; stages never added. Circles may overlap at world scale.')
 legend=p.text(958,234,184,28,'● Mining     ● Refining',10,align='right')
 runs=legend['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'];style=runs[0]['textStyle'];legend['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns']=[{'value':'● Mining     ','textStyle':dict(style,color=C['teal'])},{'value':'● Refining','textStyle':dict(style,color=C['blue'])}]
 v=p.chart('clusteredBarChart',1172,230,400,612,'Country shares · Mining / Refining',{'Category':[('Supply','Country',False)],'Y':[('ReportMeasures','Mining country share',True),('ReportMeasures','Refining country share',True)]},('Supply','Country',False,'asc'),extra={'categoryAxis':props(labelColor=color(C['muted']),fontFamily=lit(BODY_FONT),fontSize=lit(9),innerPadding=lit(15),maxMarginFactor=lit(40)),'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(9),labelPrecision=lit(1),labelDisplayUnits=lit(1),labelPosition=lit('OutsideEnd'),labelOverflow=lit(True))})
 v['visual']['visualContainerObjects']['general'][0]['properties']['altText']=lit('Shares of each stage output, including the source residual Other countries. The residual is an undisclosed country group, not a single country. Mining and refining have separate denominators; shares are not rebased to visible bars.')
 p.chart('lineChart',28,556,1126,286,'Expected output · Mining / Refining · kt',{'Category':[('Supply','Year',False)],'Y':[('ReportMeasures','Mining output kt',True),('ReportMeasures','Refining output kt',True)]},('Supply','Year',False,'asc'))
 p.finish()
 # Trade: compact fixed partner axis with its own missing-data explanation.
 p=Page(report,*PAGES[1]);p.common('How exposed is the reporting area?',
  'Countries include intra-EU trade · EU27 covers external partners only · One native CN8 form per material',
  'Dependency unavailable: consumption/output missing · CN8 continuity unverified · Partner ≠ mine origin · German cobalt mass unresolved')
 p.slicer(28,164,280,'Reporting area','Reporters','ReporterLabel','Germany')
 p.slicer(326,164,220,'Snapshot year','TradeYears','Year',2024)
 p.slicer(564,164,300,'Measure basis','BasisChoice','BasisLabel','Value · EUR')
 p.text(880,204,692,44,'Traded forms: Cu/Ni ores; Co oxides; Li carbonates; natural graphite flakes; rare-earth-containing magnets. EU27 is a bloc, not these six countries added together.',10)
 for x,label,m in [(28,'Imports · Selected scope','Imports label'),(340,'Exports · Selected scope','Exports label'),(652,'Trade balance','Trade balance label'),(964,'Top supplier share','Top supplier label'),(1276,'Supplier HHI','Supplier HHI label')]:p.card(x,254,296,label,m,C['teal'] if x==28 else C['blue'] if x==340 else None)['position'].update(height=84)
 p.chart('lineChart',28,354,760,488,'Imports / Exports · selected scope',{'Category':[('Trade','Year',False)],'Y':[('ReportMeasures','Imports',True),('ReportMeasures','Exports',True)]},('Trade','Year',False,'asc'))
 v=p.chart('clusteredBarChart',806,354,766,488,'Import partners · share',{'Category':[('PartnerDisplay','PartnerDisplay',False)],'Y':[('ReportMeasures','Partner import share',True)]},('PartnerDisplay','PartnerDisplay',False,'asc'),extra={'dataPoint':props(fill=color(C['teal'])),'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(9),labelPrecision=lit(1),labelPosition=lit('OutsideEnd'),showBlankAs=lit('—')),'categoryAxis':props(labelColor=color(C['muted']),fontFamily=lit(BODY_FONT),fontSize=lit(9),innerPadding=lit(10),outerPadding=lit(0),preferredCategoryWidth=lit(12))})
 v['visual']['query']['queryState']['Category']['showAll']=True
 p.text(1090,360,468,34,'— / blank = not returned · Small positive shares may round to 0.0%',8,align='right')
 p.finish()
 # Risk: supplier-only controls are directly above the wider supplier table.
 p=Page(report,*PAGES[2]);p.common('Where does concentration sit along the chain?',
  'HHI: country shares of expected output in tonnes, 0–1 · Above diagonal: refining is more concentrated',
  'No physical gap, import dependency or capacity: compatible inputs absent')
 p.buttons(28,180,650,'Supply year','SupplyYears','Year',2030,4)
 p.slicer(1056,230,516,'Reporting area','Reporters','ReporterLabel','Germany')
 p.slicer(1056,328,516,'Trade year','TradeYears','Year',2024)
 p.chart('scatterChart',28,230,612,612,'Mining vs. Refining · Output-share HHI (lower)',{'Series':[('Materials','Symbol',False)],'X':[('ReportMeasures','Mining HHI lower',True)],'Y':[('ReportMeasures','Refining HHI lower',True)],'Tooltips':[('ReportMeasures','Mining HHI upper',True),('ReportMeasures','Refining HHI upper',True)]},extra={'categoryAxis':props(start=lit(0),end=lit(1),labelColor=color(C['muted']),showAxisTitle=lit(True),titleText=lit('Mining HHI · output tonnes')),'valueAxis':props(start=lit(0),end=lit(1),labelColor=color(C['muted']),showAxisTitle=lit(True),titleText=lit('Refining HHI · output tonnes')),'plotAreaShading':props(show=lit(True),upperShadingColor=color('#F2F7EF'),lowerShadingColor=color('#E3EFDF'),transparency=lit(25)),'ratioLine':props(show=lit(False)),'legend':props(show=lit(False)),'categoryLabels':props(show=lit(True),color=color(C['text']),fontSize=lit(10))})
 p.chart('clusteredBarChart',658,230,380,612,'Supply concentration · Mining / Refining',{'Category':[('Materials','Symbol',False)],'Y':[('ReportMeasures','Mining HHI lower',True),('ReportMeasures','Refining HHI lower',True)],'Tooltips':[('ReportMeasures','Mining HHI upper',True),('ReportMeasures','Refining HHI upper',True)]},('Materials','Symbol',False,'asc'),extra={'valueAxis':props(start=lit(0),end=lit(1),labelColor=color(C['muted']),fontSize=lit(10)),'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(10),labelPrecision=lit(3),labelPosition=lit('OutsideEnd'))})
 v=p.table(1056,426,516,294,'Supplier HHI · EUR / Mass',[('Products','ProductShort',False),('ReportMeasures','Value exposure HHI',True),('ReportMeasures','Mass exposure HHI',True)])
 for item,label,width in zip(v['visual']['query']['queryState']['Values']['projections'],['Product','HHI (EUR)','HHI (mass)'],[280,90,90]):item['displayName']=label
 v['visual']['objects']['columnHeaders'][0]['properties'].update(autoSizeColumnWidth=lit(True))
 v['visual']['objects']['columnWidth']=[{'selector':{'metadata':item['queryRef']},'properties':{'value':lit(width)}} for item,width in zip(v['visual']['query']['queryState']['Values']['projections'],[280,90,90])]
 p.note(1056,738,516,104,'Interpretation','Supply HHI uses country shares of expected-output tonnes. Higher refining HHI means greater concentration, not surplus. The trade table compares EUR and product-mass HHI; partners can differ from mine origin.')
 p.finish()
 # Outlook: every scenario appears in each KPI and comparison chart.
 p=Page(report,*PAGES[3]);p.common('How does the outlook change across scenarios?',
  '2025 native baseline and scenario years · Demand sums returned end uses · Supply: STEPS only',
  'Physical gap/capacity unavailable · Supply ends 2040, demand 2050')
 p.buttons(28,180,800,'Outlook year','FutureYears','Year',2030,6)
 p.graphite_toggle()
 for x,label,suffix in [(28,'Demand at endpoint · native scope','endpoint label'),(550,'Demand growth from baseline','growth label'),(1072,'Annualised growth','CAGR label')]:p.scenario_panel(x,230,500,label,suffix)
 p.chart('lineChart',28,354,886,256,'Demand scenarios · kt',{'Category':[('Outlook','Year',False)],'Y':[('ReportMeasures',sc+' demand kt',True) for sc in SCENARIO_COLORS]},('Outlook','Year',False,'asc'))
 v=p.chart('clusteredBarChart',932,354,640,488,'End-use demand · kt',{'Category':[('EndUses','EndUse',False)],'Y':[('ReportMeasures',sc+' end use kt',True) for sc in SCENARIO_COLORS],'Tooltips':[('ReportMeasures','End use status',True)]},('EndUses','EndUse',False,'asc'),extra={'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(9),labelPosition=lit('OutsideEnd'),labelDisplayUnits=lit(1),valueFormatString=lit('#,0.0;-#,0.0;0'),showBlankAs=lit('—')),'categoryAxis':props(labelColor=color(C['muted']),fontFamily=lit(BODY_FONT),fontSize=lit(9),innerPadding=lit(12),preferredCategoryWidth=lit(40),maxMarginFactor=lit(45)),'layout':props(clusteredGapSize=lit(10))})
 v['visual']['query']['queryState']['Category']['showAll']=True
 p.text(1160,360,398,34,'0 = reported zero · — / blank = not returned',8,align='right')
 p.chart('lineChart',28,616,600,226,'Expected output · Mining / Refining · STEPS · kt',{'Category':[('Outlook','Year',False)],'Y':[('ReportMeasures','Mining outlook kt',True),('ReportMeasures','Refining outlook kt',True)]},('Outlook','Year',False,'asc'))
 p.note(646,616,268,226,'Scenario context','')
 for i,(scenario,description) in enumerate([('CPS','Current Policies'),('STEPS','Stated Policies'),('HDS','High Demand')]):
  v=p.text(660,646+i*23,240,23,scenario+': '+description,10)
  style=v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['textStyle']
  v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns']=[{'value':scenario,'textStyle':dict(style,color=SCENARIO_COLORS[scenario],fontWeight='bold')},{'value':': '+description,'textStyle':style}]
 p.text(660,728,240,102,'Scenarios are alternatives. Supply output is available only for STEPS; it is not installed capacity.',10)
 p.finish()
