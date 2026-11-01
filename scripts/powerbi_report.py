"""Native four-page PBIR report with paired stages and button slicers."""
from pathlib import Path
from build_powerbi import BASE,COLORS as C,save,lit,color,props,field,projection,ident

DISPLAY_FONT="Arial"
BODY_FONT="Avenir Next"
CAPTURE_LABEL="IEA: 30 OCT 2026 / TRADE: 30 OCT–01 NOV 2026"
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
      'general':props(altText=lit(alt or title or kind))}
  visual={'visualType':kind,'visualContainerObjects':vc,'drillFilterOtherVisuals':True}
  if objects:visual['objects']=objects
  if roles:visual['query']={'queryState':{role:{'projections':[projection(*f) for f in fields]} for role,fields in roles.items()}}
  out={'$schema':BASE+'item/report/definition/visualContainer/2.5.0/schema.json','name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':len(self.visuals)*1000,'tabOrder':len(self.visuals)*1000},'visual':visual}
  self.visuals.append(out);return out
 def text(self,x,y,w,h,text,size=12,fg=None,bold=False):
  return self.add('textbox',x,y,w,h,objects={'general':props(paragraphs=[{'textRuns':[{'value':text,'textStyle':{'fontFamily':DISPLAY_FONT if size>=18 or bold else BODY_FONT,'fontSize':str(size)+'pt','color':fg or C['muted'],'fontWeight':'bold' if bold else 'normal'}}]}])},transparent=True,alt=text)
 def slicer(self,x,y,w,label,table,column,default=None):
  objects={'data':props(mode=lit('Dropdown')),'header':props(show=lit(False)),
    'items':props(fontColor=color(C['text']),background=color(C['panel']),fontFamily=lit(BODY_FONT),textSize=lit(12),padding=lit(4)),
    'selection':props(singleSelect=lit(default is not None),strictSingleSelect=lit(default is not None),selectAllCheckboxEnabled=lit(False))}
  if default is not None:
   literal=str(default)+'L' if isinstance(default,int) else "'"+default.replace("'","''")+"'"
   objects['general']=props(filter={'filter':{'Version':2,'From':[{'Name':'s','Entity':table,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':column}}],'Values':[[{'Literal':{'Value':literal}}]]}}}]}})
  v=self.add('slicer',x,y,w,80,label,{'Values':[(table,column,False)]},objects);self.controls.add(v['name']);return v
 def buttons(self,x,y,w,label,table,column,default=None,count=None):
  return self.slicer(x,y,w,label,table,column,default)
 def materials(self,optional=False):
  x,y,w,h=898,110,674,112
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
   'selectionIcon':props(show=lit(False))}
  if not optional:
   objects['general']=props(filter={'filter':{'Version':2,'From':[{'Name':'s','Entity':'Materials','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':'Symbol'}}],'Values':[[{'Literal':{'Value':"'Li'"}}]]}}}]}})
  v=self.add('advancedSlicerVisual',x,y,w,h,'',{'Values':[('Materials','Symbol',False)],'Label':[('ReportMeasures','Material tile label',True)]},objects,transparent=True,alt='Material family: Cu Copper, Co Cobalt, Li Lithium, Ni Nickel, C Graphite, REE Rare earths. Colors identify chemical categories, not risk.')
  v['visual']['visualContainerObjects']['padding']=props(top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))
  v['visual']['query']['sortDefinition']={'sort':[{'field':field('Materials','Symbol'),'direction':'Ascending'}],'isDefaultSort':True}
  self.controls.add(v['name'])
  # Small static number annotations; the main symbol/name surface remains clickable.
  for i,n in enumerate(['29','27','3','28','6','group']):self.text(x+i*114+8,y+5,42,17,n,8,C['muted'])
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
   smooth=roles.get('Y',[('', '', False)])[0][1]=='Imports'
   objects['lineStyles']=props(showMarker=lit(True),showMarkerByDefault=lit(True),markerSize=lit(3),strokeWidth=lit(2.5),lineChartType=lit('smooth' if smooth else 'linear'),interpolationSmooth=lit('monotoneX'),strokeLineJoin=lit('round'))
  if kind in ['clusteredBarChart','barChart']:
   objects['categoryAxis'][0]['properties'].update(innerPadding=lit(35),outerPadding=lit(12))
  # Explicit measure colours survive filtering and series ordering.
  if 'Y' in roles:
   colors=[]
   for table,measure,is_measure in roles['Y']:
    if not is_measure:continue
    fg=C['blue'] if measure.startswith(('Refining','Exports')) or 'interval width' in measure else C['teal']
    colors.append({'selector':{'metadata':table+'.'+measure},'properties':{'fill':color(fg)}})
   if colors:objects['dataPoint']=colors
  if extra:objects.update(extra)
  v=self.add(kind,x,y,w,h,title,roles,objects)
  if sort:v['visual']['query']['sortDefinition']={'sort':[{'field':field(*sort[:2],measure=sort[2]),'direction':'Descending' if len(sort)<4 or sort[3]=='desc' else 'Ascending'}],'isDefaultSort':True}
  return v
 def table(self,x,y,w,h,title,fields):
  return self.add('tableEx',x,y,w,h,title,{'Values':fields},{
    'values':props(fontColor=color(C['text']),backColorPrimary=color(C['panel']),backColorSecondary=color('#F3F7F0'),fontFamily=lit(BODY_FONT),fontSize=lit(10),wordWrap=lit(True)),
    'columnHeaders':props(fontColor=color(C['teal']),backColor=color(C['panel']),fontFamily=lit(BODY_FONT),fontSize=lit(10),bold=lit(True),wordWrap=lit(True)),
    'grid':props(gridHorizontal=lit(True),gridHorizontalColor=color(C['edge']),gridVertical=lit(False),rowPadding=lit(5)),
    'total':props(totals=lit(False))})
 def common(self,headline,sub,footer):
  self.text(28,16,550,48,'Global critical materials',20,C['text'],True)
  self.text(29,58,570,30,'SUPPLY INTELLIGENCE / EUROPE',10,C['teal'])
  nav=self.add('pageNavigator',680,24,892,50,transparent=True,objects={
    'layout':props(orientation=lit(2),cellPadding=lit(8)),
    'text':[{'selector':{'id':'default'},'properties':{'fontFamily':lit(BODY_FONT),'fontSize':lit(11),'fontColor':color(C['muted']),'bold':lit(False)}},
            {'selector':{'id':'selected'},'properties':{'fontFamily':lit(BODY_FONT),'fontSize':lit(11),'fontColor':color(C['canvas']),'bold':lit(True)}}],
    'fill':[{'selector':{'id':'default'},'properties':{'show':lit(True),'fillColor':color(C['panel'])}},
            {'selector':{'id':'selected'},'properties':{'show':lit(True),'fillColor':color(C['teal'])}}],
    'outline':props(show=lit(False)),'shape':props(tileShape=lit('roundRect'),rectangleRoundedCurve=lit(14))})
  self.controls.add(nav['name'])
  self.text(28,108,830,78,headline,26,C['text'],True);self.text(29,190,820,46,sub,10,C['muted']);self.materials(optional=self.name=='03_risk')
  self.text(28,838,1544,37,footer,10,C['muted'])
  self.text(28,877,1544,22,'SOURCE: IEA · GCMO2026 / EUROSTAT · DS-045409     |     '+CAPTURE_LABEL+'     |     PORTFOLIO ANALYSIS',9,C['muted'])
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


def build_report(root,manifest,display_font='Avenir Next'):
 global DISPLAY_FONT,BODY_FONT,CAPTURE_LABEL
 DISPLAY_FONT=display_font
 BODY_FONT=display_font
 CAPTURE_LABEL=manifest.get('source_capture_label','SOURCE CAPTURE: SEE EXPORT MANIFEST')
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
 save(report/'definition.pbir',{'$schema':BASE+'item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../GlobalCriticalMaterials.SemanticModel'}}})
 save(report/'definition/version.json',{'$schema':BASE+'item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
 save(report/'definition/report.json',{'$schema':BASE+'item/report/definition/report/3.0.0/schema.json',
  'themeCollection':{'customTheme':{'name':'CriticalMaterialsSage','reportVersionAtImport':{'visual':'2.5.0','page':'2.0.0','report':'3.0.0'},'type':'RegisteredResources'}},
  'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'CriticalMaterialsSage','path':'CriticalMaterialsSage.json','type':'CustomTheme'}]}],
  'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized'}})
 save(report/'definition/pages/pages.json',{'$schema':BASE+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':[p[0] for p in PAGES],'activePageName':PAGES[0][0]})
 # 01 Supply: paired stages, one display-offset map.
 p=Page(report,*PAGES[0]);p.common('Where are mining and refining concentrated?',
  'STEPS / Base Case · Mining: forest green · Refining: leaf green · Independent stage denominators',
  'Expected output, not capacity. 2025 baseline / native basis unverified. Other countries is opaque. Map circles shifted ±3° longitude for readability; not facility locations.')
 p.slicer(28,244,220,'SUPPLY YEAR','SupplyYears','Year',2030)
 p.text(272,260,1280,50,'MATERIAL SCOPE: native IEA definition · Graphite excludes all-grades graphite · Coloured tiles indicate chemical category',11)
 for i,(label,m) in enumerate([('Mining · Output','Mining output label'),('Refining · Output','Refining output label'),('Mining · HHI bounds','Mining concentration label'),('Refining · HHI bounds','Refining concentration label'),('Mining · Top 3 bounds','Mining top3 label'),('Refining · Top 3 bounds','Refining top3 label')]):
  p.card(28+(i%2)*260,340+(i//2)*108,244,label,m,C['teal'] if i%2==0 else C['blue'])
 p.add('azureMap',550,340,604,308,'Country shares · Mining / Refining',{'Category':[('Supply','CountryISO3',False)],'Series':[('Supply','Stage',False)],'X':[('ReportMeasures','Map longitude',True)],'Y':[('ReportMeasures','Map latitude',True)],'Size':[('ReportMeasures','Map share',True)]},
  {'mapControls':props(defaultStyle=lit('grayscale_light'),autoZoom=lit(True),showStylePicker=lit(False),showNavigationControls=lit(True)),
   'bubbleLayer':props(show=lit(True),sizeByValue=lit(True),clusteringEnabled=lit(False),minBubbleRadius=lit(3),maxRadius=lit(18),mapTransparency=lit(20)),
   'legend':props(show=lit(True),showTitle=lit(False)),
   'dataPoint':props(fill={'solid':{'color':{'expr':field('ReportMeasures','Map color',True)}}})},alt='Country label anchors, mining shifted 3 degrees west and refining 3 degrees east. Display offset is not mine/refinery geography. Different countries can still overlap at world scale.')
 p.chart('clusteredBarChart',1172,340,400,484,'Named-country shares · Mining / Refining',{'Category':[('Supply','Country',False)],'Y':[('ReportMeasures','Mining country share',True),('ReportMeasures','Refining country share',True)]},('Supply','Country',False,'asc'),extra={'categoryAxis':props(labelColor=color(C['muted']),fontFamily=lit(BODY_FONT),fontSize=lit(10),innerPadding=lit(15))})
 p.chart('lineChart',28,666,1126,158,'Expected output · Mining / Refining · kt',{'Category':[('Supply','Year',False)],'Y':[('ReportMeasures','Mining output kt',True),('ReportMeasures','Refining output kt',True)]},('Supply','Year',False,'asc'))
 p.finish()
 # 02 Trade: fixed partner groups, correct native-scope denominator.
 p=Page(report,*PAGES[1]);p.common('How exposed is the reporting area?',
  'Countries include intra-EU trade · EU27 covers external partners only · A tile selects one native CN8 product form',
  'Partner order is fixed; Other partners groups the remainder. Dependency unavailable: consumption / domestic output missing. CN8 continuity unverified; partner ≠ mine origin. German cobalt mass unresolved.')
 p.slicer(28,244,350,'REPORTING AREA','Reporters','ReporterLabel','Germany')
 p.slicer(396,244,220,'SNAPSHOT YEAR','TradeYears','Year',2024)
 p.slicer(634,244,300,'MEASURE BASIS','BasisChoice','BasisLabel','Value · EUR')
 p.text(958,253,614,64,'TRADED FORMS: Cu / Ni ores; Co oxides; Li carbonates; natural graphite flakes; rare-earth-containing magnets. EU27 is a bloc, not these six countries added together.',10)
 for x,label,m in [(28,'Imports · Selected scope','Imports label'),(340,'Exports · Selected scope','Exports label'),(652,'Trade balance','Trade balance label'),(964,'Top supplier share','Top supplier label'),(1276,'Supplier HHI','Supplier HHI label')]:p.card(x,340,296,label,m,C['teal'] if x==28 else C['blue'] if x==340 else None)
 p.chart('lineChart',28,450,760,374,'Imports / Exports · selected scope',{'Category':[('Trade','Year',False)],'Y':[('ReportMeasures','Imports',True),('ReportMeasures','Exports',True)]},('Trade','Year',False,'asc'))
 v=p.chart('clusteredBarChart',806,450,766,374,'Import partners · fixed alphabetical order · share',{'Category':[('PartnerDisplay','PartnerDisplay',False)],'Y':[('ReportMeasures','Partner import share',True)]},('PartnerDisplay','PartnerDisplay',False,'asc'),extra={'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(10),labelPrecision=lit(1),labelPosition=lit('OutsideEnd'),showBlankAs=lit('—')),'categoryAxis':props(labelColor=color(C['muted']),fontSize=lit(10),innerPadding=lit(15))})
 v['visual']['query']['queryState']['Category']['showAll']=True
 p.finish()
 # 03 Risk: square scatter plus ONE paired stage bar chart.
 p=Page(report,*PAGES[2]);p.common('Where does concentration sit along the chain?',
  'Above diagonal: refining lower-bound HHI exceeds mining · Concentration comparison, not a physical deficit',
  'Bars show HHI lower bounds; upper bounds stay in tooltips. No physical gap, import dependency or capacity: compatible inputs absent. Clear the material tile to compare all six families.')
 p.slicer(28,244,220,'SUPPLY YEAR','SupplyYears','Year',2030)
 p.slicer(914,244,350,'TRADE REPORTING AREA','Reporters','ReporterLabel','Germany')
 p.slicer(1282,244,290,'TRADE YEAR','TradeYears','Year',2024)
 p.chart('scatterChart',28,340,484,484,'Mining vs. Refining · HHI lower bounds',{'Series':[('Materials','Symbol',False)],'X':[('ReportMeasures','Mining HHI lower',True)],'Y':[('ReportMeasures','Refining HHI lower',True)],'Tooltips':[('ReportMeasures','Mining HHI upper',True),('ReportMeasures','Refining HHI upper',True)]},extra={'categoryAxis':props(start=lit(0),end=lit(1),labelColor=color(C['muted']),showAxisTitle=lit(True),titleText=lit('Mining HHI · lower bound')),'valueAxis':props(start=lit(0),end=lit(1),labelColor=color(C['muted']),showAxisTitle=lit(True),titleText=lit('Refining HHI · lower bound')),'plotAreaShading':props(show=lit(True),upperShadingColor=color('#F2F7EF'),lowerShadingColor=color('#E3EFDF'),transparency=lit(25)),'ratioLine':props(show=lit(False)),'legend':props(show=lit(False)),'categoryLabels':props(show=lit(True),color=color(C['text']),fontSize=lit(10))})
 p.chart('clusteredBarChart',530,340,624,484,'Supply concentration · Mining / Refining',{'Category':[('Materials','Symbol',False)],'Y':[('ReportMeasures','Mining HHI lower',True),('ReportMeasures','Refining HHI lower',True)],'Tooltips':[('ReportMeasures','Mining HHI upper',True),('ReportMeasures','Refining HHI upper',True)]},('Materials','Symbol',False,'asc'),extra={'valueAxis':props(start=lit(0),end=lit(1),labelColor=color(C['muted']),fontSize=lit(10)),'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(10),labelPrecision=lit(3),labelPosition=lit('OutsideEnd'))})
 p.table(1172,340,400,484,'Supplier HHI · EUR / Mass',[('Products','ProductShort',False),('ReportMeasures','Value exposure HHI',True),('ReportMeasures','Mass exposure HHI',True)])
 p.finish()
 # 04 Outlook: stable end-use dimension, source zeros remain zeros.
 p=Page(report,*PAGES[3]);p.common('How does the outlook change across scenarios?',
  '2025 native baseline and scenario years · Demand sums returned end uses · Supply: STEPS only',
  '0 = source reported zero; — = end use not returned. Physical gap / capacity unavailable. Supply ends 2040, demand 2050. Graphite scopes remain separate; lines are guides.')
 p.slicer(28,244,310,'KPI SCENARIO','ScenarioChoice','ScenarioShort','STEPS')
 p.slicer(356,244,220,'KPI ENDPOINT','FutureYears','Year',2040)
 p.slicer(594,244,320,'GRAPHITE DEFINITION','DefinitionChoice','GraphiteScope','Graphite')
 p.text(938,256,634,52,'End-use order stays fixed across materials, scenarios and years. Missing source categories remain blank; they are not converted to zero.',11)
 for x,label,m in [(28,'Demand at endpoint · native scope','Demand endpoint label'),(550,'Demand growth from baseline','Demand growth label'),(1072,'Annualised growth','Demand CAGR label')]:p.card(x,340,500,label,m,C['teal'] if x==28 else None)
 p.chart('lineChart',28,450,930,210,'Demand scenarios · native kt · all scenarios',{'Category':[('Outlook','Year',False)],'Y':[('ReportMeasures','Demand kt',True)],'Series':[('Outlook','ScenarioShort',False)]},('Outlook','Year',False,'asc'))
 v=p.chart('clusteredBarChart',976,450,596,374,'End uses · fixed order · native kt',{'Category':[('EndUses','EndUse',False)],'Y':[('ReportMeasures','Demand end use kt',True)],'Tooltips':[('ReportMeasures','End use status',True)]},('EndUses','EndUse',False,'asc'),extra={'labels':props(show=lit(True),fontFamily=lit(BODY_FONT),fontSize=lit(10),labelPosition=lit('OutsideEnd'),labelDisplayUnits=lit(1),valueFormatString=lit('#,0.0; -#,0.0; 0'),showBlankAs=lit('—')),'categoryAxis':props(labelColor=color(C['muted']),fontSize=lit(10),innerPadding=lit(20))})
 v['visual']['query']['queryState']['Category']['showAll']=True
 p.chart('lineChart',28,678,930,146,'Expected output · Mining / Refining · STEPS · kt',{'Category':[('Outlook','Year',False)],'Y':[('ReportMeasures','Mining outlook kt',True),('ReportMeasures','Refining outlook kt',True)]},('Outlook','Year',False,'asc'))
 p.finish()
