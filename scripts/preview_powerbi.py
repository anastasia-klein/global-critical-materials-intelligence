"""Render an explicitly labelled design preview from PBIR geometry and the same CSV values.
This is not a Power BI screenshot or a DAX evaluation engine.
"""
from pathlib import Path
import argparse,csv,json,math,os,sys
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape

from build_powerbi import COLORS as C
from powerbi_report import SCENARIO_COLORS
PALETTE=[C['teal'],C['blue'],C['amber'],C['purple'],'#9CBDA0','#BDAD89']
W,H=1600,900

def clean(s):return str(s).replace('–','-').replace('—','-').replace('→','to').replace('≠','is not').replace('·','|')
def load(project):
 meta=json.loads((project/'data/export_manifest.json').read_text());out={}
 for t,spec in meta['tables'].items():
  types={x['name']:x['duckdb_type'] for x in spec['columns']};rows=[]
  for r in csv.DictReader((project/'data'/(t+'.csv')).open(encoding='utf-8')):
   for k,v in r.items():
    if v=='':r[k]=None
    elif types[k]in['DOUBLE','FLOAT']:r[k]=float(v)
    elif types[k]in['INTEGER','BIGINT','SMALLINT']:r[k]=int(v)
    elif types[k]=='BOOLEAN':r[k]=v.lower()=='true'
   rows.append(r)
  out[t]=rows
 return out

class Renderer:
 def __init__(self,pdf,data,world):self.c=canvas.Canvas(str(pdf),pagesize=(W,H));self.d=data;self.world=world;self.materials={x['DefinitionKey']:x['Material'] for x in data['Definitions']};self.li=next(k for k,v in self.materials.items() if v=='Lithium');self.scope=[];self.reporter_key=next(r['ReporterKey'] for r in data['Reporters'] if r['Reporter']=='Germany')
 def text(self,x,y,text,size=12,fg=None,bold=False,maxwidth=None):
  c=self.c;s=clean(text);font='ArialNarrowBold' if bold else 'ArialNarrow' if size>=18 else 'Arial';c.setFont(font,size);c.setFillColor(HexColor(fg or C['text']))
  if maxwidth:
   while pdfmetrics.stringWidth(s,font,size)>maxwidth and len(s)>3:s=s[:-4]+'...'
  c.drawString(x,H-y-size,s)
 def wrapped(self,x,y,w,h,text,size=13,fg=None,bold=False,font=None,align='left'):
  style=ParagraphStyle('p',alignment={'left':0,'center':1,'right':2}[align],fontName=font or ('ArialNarrowBold' if bold else 'ArialNarrow' if size>=18 else 'Arial'),fontSize=size,leading=size*1.22,textColor=HexColor(fg or C['muted']),spaceAfter=0)
  para=Paragraph(escape(clean(text)).replace('\n','<br/>'),style);pw,ph=para.wrap(w,h);para.drawOn(self.c,x,H-y-ph)
 def box(self,x,y,w,h):
  self.c.setFillColor(HexColor('#DFE9DB'));self.c.roundRect(x+1,H-y-h-3,w,h,20,fill=1,stroke=0)
  self.c.setFillColor(HexColor(C['panel']));self.c.setStrokeColor(HexColor(C['edge']));self.c.setLineWidth(.8);self.c.roundRect(x,H-y-h,w,h,20,fill=1,stroke=1)
 def line(self,x1,y1,x2,y2,fg,width=1):self.c.setStrokeColor(HexColor(fg));self.c.setLineWidth(width);self.c.line(x1,H-y1,x2,H-y2)
 def bar(self,x,y,w,h,fg):self.c.setFillColor(HexColor(fg));self.c.rect(x,H-y-h,w,h,fill=1,stroke=0)
 def dot(self,x,y,r,fg):self.c.setFillColor(HexColor(fg));self.c.circle(x,H-y,r,fill=1,stroke=0)
 def measures(self):
  supply=[r for r in self.d['Supply'] if r['DefinitionKey']==self.li and r['Stage']=='Mining' and r['Year']==2030]
  con=next(r for r in self.d['Concentration'] if r['DefinitionKey']==self.li and r['Stage']=='Mining' and r['Year']==2030)
  tr=next(r for r in self.d['Trade'] if r['ProductCode']=='28369100' and r['ReporterKey']==self.reporter_key and r['Year']==2024 and r['Basis']=='trade_value')
  ex=next(r for r in self.d['Exposure'] if r['ProductCode']=='28369100' and r['ReporterKey']==self.reporter_key and r['Year']==2024 and r['Basis']=='trade_value')
  dem=next(r for r in self.d['Outlook'] if r['DefinitionKey']==self.li and r['Year']==2040 and r['ScenarioShort']=='STEPS' and r['SeriesKind']=='demand_reported_end_uses_sum')
  fmt=lambda x:f'{x:.1%}';interval=lambda a,b,fmt:f'{fmt(a)} - {fmt(b)}'
  self.labels={'Supply volume label':f"{supply[0]['PanelTonnes']/1000:,.1f} kt",'Supply HHI label':interval(con['HHILower'],con['HHIUpper'],lambda x:f'{x:.3f}'),
   'Supply top3 label':interval(con['Top3Lower'],con['Top3Upper'],fmt),'Supply top5 label':interval(con['Top5Lower'],con['Top5Upper'],fmt),'Residual label':fmt(con['ResidualShare']),
   'Imports label':f"€{tr['Imports']/1e6:,.1f}m",'Exports label':f"€{tr['Exports']/1e6:,.1f}m",'Trade balance label':f"€{tr['Balance']/1e6:,.1f}m",
   'Top supplier label':fmt(ex['TopSupplierLower']),'Supplier HHI label':f"{ex['HHILower']:.3f}",
   'Import dependency label':'Unavailable','No physical gap label':'Unavailable','No capacity label':'Unavailable',
   'Demand endpoint label':f"{dem['QuantityTonnes']/1000:,.1f} kt",'Demand growth label':f"{dem['Growth']:+.1%}",'Demand CAGR label':fmt(dem['CAGR'])}
  for stage in ['Mining','Refining']:
   panel=next(r for r in self.d['Concentration'] if r['DefinitionKey']==self.li and r['Stage']==stage and r['Year']==2030)
   volume=next(r['PanelTonnes'] for r in self.d['Supply'] if r['DefinitionKey']==self.li and r['Stage']==stage and r['Year']==2030)
   self.labels[stage+' output label']=f'{volume/1000:,.1f} kt'
   self.labels[stage+' concentration label']=interval(panel['HHILower'],panel['HHIUpper'],lambda x:f'{x:.3f}')
   self.labels[stage+' top3 label']=interval(panel['Top3Lower'],panel['Top3Upper'],fmt)
  for scenario in SCENARIO_COLORS:
   r=next(r for r in self.d['Outlook'] if r['DefinitionKey']==self.li and r['Year']==2040 and r['ScenarioShort']==scenario and r['SeriesKind']=='demand_reported_end_uses_sum')
   for suffix,value in [('endpoint label',f"{r['QuantityTonnes']/1000:,.1f} kt"),('growth label',f"{r['Growth']:+.1%}"),('CAGR label',f"{r['CAGR']:.1%}")]:self.labels[scenario+' '+suffix]=value
  self.context={'material':'Lithium','supply_stage':'Mining and Refining','supply_year':2030,'trade_product':'28369100','reporting_area':'Germany','trade_year':2024,'trade_basis':'trade_value','outlook_scenario':'CPS / STEPS / HDS','outlook_endpoint':2040,'kpi_labels':self.labels,'kind':'SQL/CSV-derived design preview, not Power BI output'}
 def bar_chart(self,x,y,w,h,rows,percent=False):
  rows=[(clean(n),v) for n,v in rows];total=len(rows)
  if not rows:return
  top=y+45;bottom=y+h-20;labelw=min(w*.38,250);plotx=x+labelw;plotw=w-labelw-77;maxv=max((v for _,v in rows if v is not None),default=1) or 1;rh=min(27,(bottom-top)/max(len(rows),1))
  for index,(name,value) in enumerate(rows):
   yy=top+index*rh;self.text(x+15,yy,name,10.5,C['muted'],maxwidth=labelw-22)
   if value is None:self.text(plotx+5,yy,'—',10.5,C['muted']);continue
   self.bar(plotx,yy+2,plotw*value/maxv,rh*.57,C['teal']);self.text(plotx+plotw*value/maxv+8,yy,f'{value:.1%}' if percent else '0' if value==0 else f'{value:,.1f}',10.5,C['text'])
  if total>len(rows):self.text(x+w-190,y+h-20,f'{len(rows)} of {total} shown in preview',9.5,C['muted'])
 def line_chart(self,x,y,w,h,series,years,valuefmt=None,smooth=False,colors=None):
  palette=colors or PALETTE
  valuefmt=valuefmt or (lambda v:f'{v:,.0f}');top=y+49;left=x+64;right=x+w-28;bottom=y+h-28;has_legend=len(series)>1
  if has_legend:
   offset=x+17
   for j,(label,pts) in enumerate(series):self.dot(offset+4,y+43,3.3,palette[j%len(palette)]);self.text(offset+13,y+35,label,10.3,C['text']);offset+=max(140,len(label)*8)
   top+=15
  allvals=[v for _,points in series for _,v in points if v is not None]
  if not allvals:return
  maxv=max(allvals)*1.12 or 1
  for j in range(4):
   val=maxv*j/3;yy=bottom-(bottom-top)*j/3;self.line(left,yy,right,yy,C['edge'],.6);self.text(x+12,yy-8,valuefmt(val),10.5,C['muted'],maxwidth=48)
  xs={year:left+(right-left)*k/max(1,len(years)-1) for k,year in enumerate(years)}
  for yr,xx in xs.items():self.text(xx-16,bottom+7,str(yr),10.5,C['muted'])
  for j,(_,points) in enumerate(series):
   coords=[(xs[yr],bottom-(bottom-top)*val/maxv) for yr,val in sorted(points) if val is not None]
   # Shape-preserving cubic guide through source points; never extrapolate.
   if smooth and len(coords)>2:
    delta=[(coords[i+1][1]-coords[i][1])/(coords[i+1][0]-coords[i][0]) for i in range(len(coords)-1)]
    slope=[delta[0]]+[0 if a*b<=0 else 2*a*b/(a+b) for a,b in zip(delta[:-1],delta[1:])]+[delta[-1]]
    path=self.c.beginPath();path.moveTo(coords[0][0],H-coords[0][1])
    for i,((a,b),(cc,d)) in enumerate(zip(coords[:-1],coords[1:])):
     third=(cc-a)/3;path.curveTo(a+third,H-(b+slope[i]*third),cc-third,H-(d-slope[i+1]*third),cc,H-d)
    self.c.setStrokeColor(HexColor(palette[j%len(palette)]));self.c.setLineWidth(2.5);self.c.setLineCap(1);self.c.drawPath(path,stroke=1,fill=0)
   else:
    previous=None
    for yr,val in sorted(points):
     if val is None:previous=None;continue
     pt=(xs[yr],bottom-(bottom-top)*val/maxv)
     if previous:self.line(*previous,*pt,palette[j%len(palette)],2.5)
     previous=pt
   for pt in coords:self.dot(*pt,2.5,palette[j%len(palette)])

 def table(self,x,y,w,h,headers,rows,widths):
  header_y=y+43;lineh=18;cx=x+14
  for title,share in zip(headers,widths):self.text(cx,header_y,title,10.8,C['teal'],True,maxwidth=(w-28)*share-7);cx+=(w-28)*share
  self.line(x+14,header_y+22,x+w-14,header_y+22,C['edge'])
  maxrows=int((h-77)/lineh);visible=rows[:maxrows]
  for index,row in enumerate(visible):
   yy=header_y+27+index*lineh
   if index%2:self.bar(x+8,yy-1,w-16,lineh,'#F3F7F0')
   cx=x+14
   for value,share in zip(row,widths):self.text(cx,yy,value,11.5,C['muted'] if value=='No data' else C['text'],maxwidth=(w-28)*share-7);cx+=(w-28)*share
  if len(rows)>len(visible):self.text(x+w-250,y+h-18,f'{len(rows)} rows | scroll in Power BI',9.5,C['muted'])
 def map(self,x,y,w,h,stage):
  scale=min((w-32)/360,(h-115)/145);yscale=scale;left=x+16+(w-32-360*scale)/2;top=y+70
  def project(lon,lat):return left+(lon+180)*scale,top+(85-lat)*yscale
  for feat in self.world['features']:
   if feat['properties'].get('ISO_A3')=='ATA':continue
   geom=feat['geometry'];polys=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
   for poly in polys:
    if not poly:continue
    ring=poly[0];path=self.c.beginPath();started=False
    for lon,lat,*_ in ring:
     if lat< -60:lat=-60
     xx,yy=project(lon,lat)
     if not started:path.moveTo(xx,H-yy);started=True
     else:path.lineTo(xx,H-yy)
    path.close();self.c.setFillColor(HexColor('#E1EBDD'));self.c.setStrokeColor(HexColor('#C0D1BA'));self.c.setLineWidth(.35);self.c.drawPath(path,fill=1,stroke=1)
  geo={f['properties'].get('ISO_A3_EH'):f['properties'] for f in self.world['features']};rows=[r for r in self.d['Supply'] if r['DefinitionKey']==self.li and r['Year']==2030 and (stage=='Both' or r['Stage']==stage) and r['EntityType']=='country_or_territory' and r['Share']>0]
  unmatched=[]
  for r in rows:
   item=geo.get(r['CountryISO3'])
   if item is None:unmatched.append(r['CountryISO3']);continue
   xx,yy=project(float(r['DisplayLongitude']),float(r['DisplayLatitude']));self.dot(xx,yy,3+13*math.sqrt(r['Share']),C['teal'] if r['Stage']=='Mining' else C['blue']);self.c.setStrokeColor(HexColor(C['text']));self.c.setLineWidth(.5);self.c.circle(xx,H-yy,3+13*math.sqrt(r['Share']),stroke=1,fill=0)
  self.context['preview_map_unmatched_country_iso3_'+stage]=unmatched

 def scatter(self,x,y,w,h):
  cs=[r for r in self.d['Concentration'] if r['Year']==2030];pairs=[]
  for key,name in self.materials.items():
   a=next((r for r in cs if r['DefinitionKey']==key and r['Stage']=='Mining'),None);b=next((r for r in cs if r['DefinitionKey']==key and r['Stage']=='Refining'),None)
   if a and b:pairs.append((next(r['Symbol'] for r in self.d['Materials'] if r['Family']==next(d['Family'] for d in self.d['Definitions'] if d['DefinitionKey']==key)),a['HHILower'],b['HHILower']))
  side=min(w-108,h-128);l=x+66;t=y+68;r=l+side;b=t+side
  for vertices,fg in [([(l,t),(r,t),(l,b)],'#F2F7EF'), ([(l,b),(r,t),(r,b)],'#E3EFDF')]:
   path=self.c.beginPath();path.moveTo(vertices[0][0],H-vertices[0][1])
   for xx,yy in vertices[1:]:path.lineTo(xx,H-yy)
   path.close();self.c.setFillColor(HexColor(fg));self.c.drawPath(path,fill=1,stroke=0)
  for k in range(6):
   val=k/5;xx=l+side*val;yy=b-side*val;self.line(xx,t,xx,b,C['edge'],.5);self.line(l,yy,r,yy,C['edge'],.5);self.text(xx-9,b+6,f'{val:.1f}',10,C['muted']);self.text(x+23,yy-7,f'{val:.1f}',10,C['muted'])
  self.c.saveState();self.c.setDash(5,4);self.line(l,b,r,t,C['muted'],1.1);self.c.restoreState()
  self.text(l+side/2-60,b+24,'Mining HHI (lower)',10,C['muted'])
  self.c.saveState();self.c.translate(x+12,H-(t+b)/2);self.c.rotate(90);self.c.setFont('Arial',10);self.c.setFillColor(HexColor(C['muted']));self.c.drawCentredString(0,0,'Refining HHI (lower)');self.c.restoreState()
  for j,(name,a,bb) in enumerate(pairs):
   fg=PALETTE[j%6];xx=l+side*a;yy=b-side*bb;self.dot(xx,yy,5.8,fg);self.text(xx+8,yy+(5 if name=='Co' else -18 if name=='REE' else -14),name.replace('Magnet rare earth elements','Magnet REE'),10,C['text'],maxwidth=r-xx+15)
 def paired_bars(self,x,y,w,h):
  rows=[r for r in self.d['Supply'] if r['DefinitionKey']==self.li and r['Year']==2030 and r['EntityType']=='country_or_territory']
  lookup={(r['Country'],r['Stage']):r['Share'] for r in rows};countries=sorted({r['Country'] for r in rows})
  self.dot(x+20,y+44,3.5,C['teal']);self.text(x+30,y+36,'Mining',10,C['text']);self.dot(x+140,y+44,3.5,C['blue']);self.text(x+150,y+36,'Refining',10,C['text'])
  left=x+150;pw=w-220;top=y+67;rh=(h-92)/max(len(countries),1);mx=max(lookup.values()) or 1
  for j,country in enumerate(countries):
   yy=top+j*rh;self.text(x+15,yy+3,country,11,C['muted'],maxwidth=125)
   for off,stage,col in [(0,'Mining',C['teal']),(rh*.4,'Refining',C['blue'])]:
    val=lookup.get((country,stage))
    if val is not None:self.bar(left,yy+off,pw*val/mx,rh*.3,col);self.text(left+pw*val/mx+5,yy+off-2,f'{val:.1%}',10,C['text'])

 def bounds_bars(self,x,y,w,h,stage):
  rows=[r for r in self.d['Concentration'] if r['Year']==2030 and r['Stage']==stage];rows.sort(key=lambda r:r['HHILower'],reverse=True)
  left=x+164;pw=w-278;top=y+45;rh=(h-75)/max(len(rows),1);fg=C['teal'] if stage=='Mining' else C['blue']
  for j,r in enumerate(rows):
   yy=top+j*rh;name=self.materials[r['DefinitionKey']].replace('Magnet rare earth elements','Magnet REE');lo,hi=r['HHILower'],r['HHIUpper']
   self.text(x+14,yy,name,11,C['muted'],maxwidth=140);self.bar(left,yy+3,pw*lo,rh*.5,fg);self.bar(left+pw*lo,yy+3,pw*(hi-lo),rh*.5,'#BACDB8');self.text(left+pw*hi+7,yy,f'{lo:.3f}–{hi:.3f}',10,C['text'])
  self.text(left,y+h-20,'0',9,C['muted']);self.text(left+pw-5,y+h-20,'1',9,C['muted'])

 def risk_bars(self,x,y,w,h):
  names={r['Family']:r['Symbol'] for r in self.d['Materials']};defs={r['Material']:r['DefinitionKey'] for r in self.d['Definitions']}
  self.dot(x+20,y+44,3.5,C['teal']);self.text(x+30,y+36,'Mining',10);self.dot(x+140,y+44,3.5,C['blue']);self.text(x+150,y+36,'Refining',10)
  top=y+75;rh=(h-110)/6;left=x+65;pw=w-140
  for i,r in enumerate(sorted(self.d['Materials'],key=lambda r:r['SortOrder'])):
   material='Magnet rare earth elements' if r['Symbol']=='REE' else r['MaterialName'];key=defs[material];yy=top+i*rh;self.text(x+18,yy+7,r['Symbol'],14,bold=True)
   for j,st in enumerate(['Mining','Refining']):
    a=next(r for r in self.d['Concentration'] if r['DefinitionKey']==key and r['Stage']==st and r['Year']==2030);value=a['HHILower'];self.bar(left,yy+j*20,pw*value,15,C['teal'] if j==0 else C['blue']);self.text(left+pw*value+6,yy+j*20-1,f'{value:.3f}',10)
 def scenario_enduses(self,x,y,w,h):
  vals={(r['EndUse'],r['ScenarioShort']):r['QuantityTonnes']/1000 for r in self.d['Outlook'] if r['DefinitionKey']==self.li and r['Year']==2040 and r['SeriesKind']=='demand_end_use'}
  enduses=sorted(self.d['EndUses'],key=lambda r:r['SortOrder']);left=x+263;pw=w-330;top=y+72;rh=(h-112)/8;mx=max(vals.values())*1.02
  for i,(sc,fg) in enumerate(SCENARIO_COLORS.items()):self.dot(x+21+i*105,y+45,3,fg);self.text(x+31+i*105,y+37,sc,10,fg)
  for i,r in enumerate(enduses):
   yy=top+i*rh;self.text(x+14,yy+8,r['EndUse'],10,C['muted'],maxwidth=237)
   for j,(sc,fg) in enumerate(SCENARIO_COLORS.items()):
    value=vals.get((r['EndUse'],sc));by=yy+j*rh/3
    if value is None:self.text(left+5,by,'—',8.5,C['muted']);continue
    self.bar(left,by+1,pw*value/mx,rh/3-3,fg);self.text(left+pw*value/mx+5,by-1,'0' if value==0 else f'{value:,.1f}',8.5,C['text'])
 def visual(self,page,v):
  p=v['position'];x,y,w,h=[p[k] for k in ['x','y','width','height']];z=v['visual'];kind=z['visualType'];title=z['visualContainerObjects']['title'][0]['properties']['text']['expr']['Literal']['Value'].strip("'")
  if kind=='textbox':
   runs=z['objects']['general'][0]['properties']['paragraphs'][0]['textRuns']
   if len(runs)>1:
    xx=x
    for run in runs:
     sty=run['textStyle'];size=float(sty['fontSize'][:-2])*1.14;self.text(xx,y,run['value'],size,sty['color']);xx+=pdfmetrics.stringWidth(clean(run['value']),'Arial',size)
    return
   text=''.join(r['value'] for r in runs);sty=runs[0]['textStyle'];self.wrapped(x,y,w,h,text,float(sty['fontSize'][:-2])*1.14,sty['color'],sty.get('fontWeight')=='bold',align=z['objects']['general'][0]['properties']['paragraphs'][0].get('horizontalTextAlignment','left'));return
  if kind=='pageNavigator':
   labels=['Global Supply Landscape','European Trade & Dependency','Supply Chain Risk','Future Outlook'];bw=(w-24)/4
   for j,label in enumerate(labels):
    selected=j==page;self.c.setFillColor(HexColor(C['teal'] if selected else C['panel']));self.c.roundRect(x+j*(bw+8),H-y-h,bw,h,8,fill=1,stroke=0);self.wrapped(x+j*(bw+8)+10,y+14,bw-20,h-5,label,11.5,C['canvas'] if selected else C['muted'],selected)
   return
  if kind!='advancedSlicerVisual' and z['visualContainerObjects']['background'][0]['properties']['show']['expr']['Literal']['Value']=='true':self.box(x,y,w,h)
  if title:
   tp=z['visualContainerObjects']['title'][0]['properties'];center=tp.get('alignment',{}).get('expr',{}).get('Literal',{}).get('Value')=="'center'"
   self.wrapped(x+14,y+9,w-28,22,title,10 if center else 12,tp.get('fontColor',{}).get('solid',{}).get('color',{}).get('expr',{}).get('Literal',{}).get('Value',"'"+C['text']+"'").strip("'"),True,align='center' if center else 'left')
  if kind=='shape':return
  if kind=='advancedSlicerVisual':
   ref=z['query']['queryState']['Values']['projections'][0]['field']['Column'];table=ref['Expression']['SourceRef']['Entity'];col=ref['Property']
   if table!='Materials':
    vals=sorted({r[col] for r in self.d[table]},key=lambda v:(v!='Graphite',str(v)) if table=='DefinitionChoice' else v)
    chosen=z.get('objects',{}).get('general',[{'properties':{}}])[0]['properties'].get('filter',{}).get('filter',{}).get('Where',[{'Condition':{'In':{'Values':[[{'Literal':{'Value':''}}]]}}}])[0]['Condition']['In']['Values'][0][0]['Literal']['Value'].strip("'").rstrip('L')
    if table=='DefinitionChoice':vals=['All grades']
    width=(w-8*(len(vals)-1))/len(vals)
    for i,val in enumerate(vals):
     xx=x+i*(width+8);selected=str(val)==chosen;self.c.setFillColor(HexColor(C['teal'] if selected else C['panel']));self.c.setStrokeColor(HexColor(C['edge']));self.c.roundRect(xx,H-y-34,width,34,6,fill=1,stroke=1);self.text(xx+12,y+8,str(val),11,C['canvas'] if selected else C['text'],selected)
    return
   values=sorted(self.d['Materials'],key=lambda r:r['SortOrder'])
   for i,r in enumerate(values):
    xx=x+i*114;chosen=page!=2 and r['Symbol']=='Li';fg=r['CategoryColor'];self.c.setFillColor(HexColor(fg));self.c.setStrokeColor(HexColor(C['teal'] if chosen else '#A6B8A5'));self.c.setLineWidth(3 if chosen else 1);self.c.roundRect(xx,H-y-104,104,104,4,fill=1,stroke=1)
    self.text(xx+29 if r['Symbol']!='REE' else xx+19,y+24,r['Symbol'],29,C['text'],True)
    self.text(xx+10,y+76,r['MaterialName'],11,C['text'],maxwidth=89)
   return
  if kind=='slicer':
   try:value=z['objects']['general'][0]['properties']['filter']['filter']['Where'][0]['Condition']['In']['Values'][0][0]['Literal']['Value'];value=value[1:-1] if value.startswith("'") else value.rstrip('L')
   except KeyError:value='All definitions' if 'NATIVE' in title else 'All products'
   self.text(x+14,y+43,value,15,C['text'],maxwidth=w-55);self.text(x+w-26,y+43,'v',12,C['muted']);return
  roles=z.get('query',{}).get('queryState',{});fields={k:[q['field'].get('Measure',q['field'].get('Column'))['Property'] for q in o['projections']] for k,o in roles.items()}
  if kind=='card':
   val=self.labels[fields['Values'][0]];size=float(z['objects']['labels'][0]['properties']['fontSize']['expr']['Literal']['Value'][:-1]);xx=x+(w-pdfmetrics.stringWidth(clean(val),'ArialNarrowBold',size))/2;self.text(xx,y+43,val,size,z['objects']['labels'][0]['properties']['color']['solid']['color']['expr']['Literal']['Value'].strip("'"),True,maxwidth=w-28);return
  if kind=='azureMap':self.map(x,y,w,h,'Both');return
  if kind=='barChart':self.bounds_bars(x,y,w,h,'Mining' if fields['Y'][0].startswith('Mining') else 'Refining');return
  if kind=='clusteredBarChart':
   measure=fields['Y'][0]
   if measure=='Mining country share':self.paired_bars(x,y,w,h);return
   if measure=='CPS end use kt':self.scenario_enduses(x,y,w,h);return
   if measure=='Country share':rows=[(r['Country'],r['Share']) for r in self.d['Supply'] if r['DefinitionKey']==self.li and r['Year']==2030 and r['Stage']=='Mining' and r['EntityType']=='country_or_territory'];pct=True
   elif measure=='Partner import share':
    totals=defaultdict(float)
    for r in self.d['Partners']:
     if r['ProductCode']=='28369100' and r['ReporterKey']==self.reporter_key and r['Year']==2024 and r['Flow']=='Import' and r['Basis']=='trade_value':totals[r['PartnerDisplay']]+=r['Share']
    rows=[(r['PartnerDisplay'],totals.get(r['PartnerDisplay'])) for r in sorted(self.d['PartnerDisplay'],key=lambda z:z['SortOrder'])];pct=True
   elif measure=='Mining HHI lower':self.risk_bars(x,y,w,h);return
   else:
    vals={r['EndUse']:r['QuantityTonnes']/1000 for r in self.d['Outlook'] if r['DefinitionKey']==self.li and r['Year']==2040 and r['ScenarioShort']=='STEPS' and r['SeriesKind']=='demand_end_use'}
    rows=[(r['EndUse'],vals.get(r['EndUse'])) for r in sorted(self.d['EndUses'],key=lambda z:z['SortOrder'])];pct=False
   self.bar_chart(x,y,w,h,rows,pct);return
  if kind=='lineChart':
   measure=fields['Y'][0]
   if measure=='Mining output kt':
    rows=[r for r in self.d['Supply'] if r['DefinitionKey']==self.li];totals=defaultdict(float)
    for r in rows:totals[(r['Stage'],r['Year'])]+=r['QuantityTonnes']/1000
    self.line_chart(x,y,w,h,[(stage,[(yr,qty) for (st,yr),qty in totals.items() if st==stage]) for stage in ['Mining','Refining']],sorted({r['Year'] for r in rows}));return
   if measure=='Supply trend kt':
    totals=defaultdict(float)
    for r in self.d['Supply']:
     if r['DefinitionKey']==self.li and r['Stage']=='Mining':totals[r['Year']]+=r['QuantityTonnes']/1000
    self.line_chart(x,y,w,h,[('Expected output',list(totals.items()))],sorted(totals));return
   if measure=='Imports':
    rows=[r for r in self.d['Trade'] if r['ProductCode']=='28369100' and r['ReporterKey']==self.reporter_key and r['Basis']=='trade_value'];self.line_chart(x,y,w,h,[(lab,[(r['Year'],r[lab]/1e6) for r in rows]) for lab in ['Imports','Exports']],sorted(r['Year'] for r in rows),lambda v:f'€{v:,.0f}m',smooth=True);return
   if measure in ['Demand kt','CPS demand kt']:
    rows=[r for r in self.d['Outlook'] if r['DefinitionKey']==self.li and r['SeriesKind']=='demand_reported_end_uses_sum'];self.line_chart(x,y,w,h,[(s,[(r['Year'],r['QuantityTonnes']/1000) for r in rows if r['ScenarioShort']==s]) for s in SCENARIO_COLORS],sorted({r['Year'] for r in rows}),colors=list(SCENARIO_COLORS.values()));return
   rows=[r for r in self.d['Outlook'] if r['DefinitionKey']==self.li and r['SeriesKind']=='supply_panel_output'];self.line_chart(x,y,w,h,[(s,[(r['Year'],r['QuantityTonnes']/1000) for r in rows if r['Stage']==s]) for s in ['Mining','Refining']],sorted({r['Year'] for r in rows}));return
  if kind=='scatterChart':self.scatter(x,y,w,h);return
  if kind=='tableEx':
   if page==1:
    r=next(p for p in self.d['Products'] if p['ProductCode']=='28369100');self.table(x,y,w,h,['Product','Form','Quantity basis'],[(r['ProductShort'],r['ProductForm'],r['QuantityBasis'])],[.45,.25,.3]);return
   if 'supplier HHI' in title or 'Supplier' in title:
    names={p['ProductCode']:p['ProductShort'] for p in self.d['Products']};rows=[(names[r['ProductCode']],f"{r['ValueHHILower']:.3f}",f"{r['MassHHILower']:.3f}") for r in self.d['Sensitivity'] if r['Year']==2024 and r['ReporterKey']==self.reporter_key];rows.sort();self.table(x,y,w,h,['Product','Value HHI lower','Mass HHI lower'],rows,[.5,.25,.25]);return
   rows=[]
   for r in self.d['SupplyRisk']:
    if r['Year']==2030:rows.append((self.materials[r['DefinitionKey']],r['Stage'],'No data' if r['LowerBound'] is None else f"{r['LowerBound']:.3f}",'No data' if r['UpperBound'] is None else f"{r['UpperBound']:.3f}",r['Availability']))
   rows.sort();self.table(x,y,w,h,['Native material','Stage','HHI lower','HHI upper','Availability'],rows,[.38,.15,.14,.14,.19])
 def page(self,project,name,index):
  self.c.setFillColor(HexColor(C['canvas']));self.c.rect(0,0,W,H,fill=1,stroke=0);folder=project/'GlobalCriticalMaterials.Report/definition/pages'/name
  visuals=[json.loads(f.read_text()) for f in folder.glob('visuals/*/visual.json')]
  for v in sorted(visuals,key=lambda z:z['position']['z']):self.visual(index,v)
  self.text(1100,84,'DESIGN PREVIEW | DESKTOP QA PENDING',10,C['amber'],True)
  self.c.showPage()

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--arial-folder',type=Path,default=(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts' if sys.platform=='win32' else Path('/System/Library/Fonts/Supplemental')));args=parser.parse_args()
 regular=next((args.arial_folder/n for n in ['Arial.ttf','arial.ttf'] if (args.arial_folder/n).exists()),None);bold=next((args.arial_folder/n for n in ['Arial Bold.ttf','arialbd.ttf'] if (args.arial_folder/n).exists()),None)
 if regular is None or bold is None:raise FileNotFoundError('Arial regular/bold not found; supply --arial-folder')
 pdfmetrics.registerFont(TTFont('Arial',str(regular)));pdfmetrics.registerFont(TTFont('ArialBold',str(bold)))
 narrow=next((args.arial_folder/n for n in ['Arial Narrow.ttf','ARIALN.TTF','arialn.ttf'] if (args.arial_folder/n).exists()),None);narrow_bold=next((args.arial_folder/n for n in ['Arial Narrow Bold.ttf','ARIALNB.TTF','arialnb.ttf'] if (args.arial_folder/n).exists()),None)
 if json.loads((args.project/'CriticalMaterialsSage.theme.json').read_text())['textClasses']['title']['fontFace']=='Arial':narrow,narrow_bold=regular,bold
 if json.loads((args.project/'CriticalMaterialsSage.theme.json').read_text())['textClasses']['title']['fontFace'].find('Avenir Next')>=0:
  avenir=Path('/System/Library/Fonts/Avenir Next.ttc')
  if not avenir.exists():raise FileNotFoundError('Avenir Next unavailable for preview; build the Arial variant or install a licensed font')
  for alias,index in [('Arial',7),('ArialBold',0),('ArialNarrow',7),('ArialNarrowBold',0)]:pdfmetrics.registerFont(TTFont(alias,str(avenir),subfontIndex=index))
 else:
  if narrow is None or narrow_bold is None:raise FileNotFoundError('Selected preview font unavailable')
  pdfmetrics.registerFont(TTFont('ArialNarrow',str(narrow)));pdfmetrics.registerFont(TTFont('ArialNarrowBold',str(narrow_bold)))
 args.output.parent.mkdir(parents=True,exist_ok=True);data=load(args.project);world=json.loads((args.project.parent/'assets/ne_world_110m.geojson').read_text());r=Renderer(args.output,data,world);r.measures();pages=json.loads((args.project/'GlobalCriticalMaterials.Report/definition/pages/pages.json').read_text())['pageOrder']
 for index,page in enumerate(pages):r.page(args.project,page,index)
 r.c.setTitle('Global Critical Materials - Design preview - Desktop QA pending');r.c.setAuthor('Global Critical Materials portfolio project');r.c.save();(args.output.parent/'preview_context.json').write_text(json.dumps(r.context,indent=2,ensure_ascii=False)+'\n');print('Created four-page SQL-derived design preview')
