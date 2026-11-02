"""Build a reviewable Power BI PBIP/TMDL/PBIR project from verified CSV exports."""
from pathlib import Path
import argparse,json,uuid
ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/fabric/'
FONT_STACK="'Avenir Next', Arial, sans-serif"
COLORS={'canvas':'#EDF4E9','panel':'#FFFFFF','edge':'#DDE7DA','text':'#18271D','muted':'#59695D','teal':'#183323','blue':'#479A67','amber':'#96712E','purple':'#7D8261'}

def ident(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,'gcm-powerbi/'+x))
def save(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def lit(x):
 if isinstance(x,bool):v='true' if x else 'false'
 elif isinstance(x,str):v="'"+x.replace("'","''")+"'"
 else:v=str(x)+'D'
 return {'expr':{'Literal':{'Value':v}}}
def color(x):return {'solid':{'color':lit(x)}}
def props(**kw):return [{'properties':kw}]
def field(table,column,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':column}}
def projection(table,column,measure=False):return {'field':field(table,column,measure),'queryRef':table+'.'+column,'nativeQueryRef':column,'active':True}

MEASURES={}
def measure(name,expression,fmt=None,folder='Context'):
 MEASURES[name]={'expression':expression,'format':fmt,'folder':folder}
measure('Selected supply year','SELECTEDVALUE(SupplyYears[Year],2030)')
measure('Selected trade year','SELECTEDVALUE(TradeYears[Year],2024)')
measure('Selected endpoint','SELECTEDVALUE(FutureYears[Year],2040)')
measure('Selected basis','SELECTEDVALUE(BasisChoice[Basis],"trade_value")')
measure('Selected scenario','SELECTEDVALUE(ScenarioChoice[Scenario],"Stated Policies Scenario")')
measure('One definition','HASONEVALUE(Definitions[DefinitionKey])')
measure('One product','HASONEVALUE(Products[ProductCode])')
measure('One reporter','HASONEVALUE(Reporters[ReporterKey])')
measure('Panel tonnes','IF([One definition] && HASONEVALUE(Stages[Stage]),CALCULATE(MAX(Supply[PanelTonnes]),TREATAS({[Selected supply year]},Supply[Year])))','#,0','Supply')
measure('Country share','IF([One definition] && HASONEVALUE(Stages[Stage]),CALCULATE(MAX(Supply[Share]),Supply[EntityType]="country_or_territory",TREATAS({[Selected supply year]},Supply[Year])))','0.0%','Supply')
measure('Supply trend kt','IF([One definition] && HASONEVALUE(Stages[Stage]),DIVIDE(SUM(Supply[QuantityTonnes]),1000))','#,0.0','Supply')
for suffix,col in [('lower','HHILower'),('upper','HHIUpper'),('residual','ResidualShare'),('top3 lower','Top3Lower'),('top3 upper','Top3Upper'),('top5 lower','Top5Lower'),('top5 upper','Top5Upper')]:
 measure('Supply '+suffix,'IF([One definition] && HASONEVALUE(Stages[Stage]),CALCULATE(MAX(Concentration['+col+']),TREATAS({[Selected supply year]},Concentration[Year])))','0.000' if 'lower' in suffix and suffix=='lower' or suffix=='upper' else '0.0%','Supply')
measure('Supply HHI label','IF(ISBLANK([Supply lower]),"Not available",FORMAT([Supply lower],"0.000") & " – " & FORMAT([Supply upper],"0.000"))',folder='Supply')
measure('Supply top3 label','IF(ISBLANK([Supply top3 lower]),"Not available",FORMAT([Supply top3 lower],"0.0%") & " – " & FORMAT([Supply top3 upper],"0.0%"))',folder='Supply')
measure('Supply top5 label','IF(ISBLANK([Supply top5 lower]),"Not available",FORMAT([Supply top5 lower],"0.0%") & " – " & FORMAT([Supply top5 upper],"0.0%"))',folder='Supply')
measure('Residual label','IF(ISBLANK([Supply residual]),"Not available",FORMAT([Supply residual],"0.0%"))',folder='Supply')
measure('Supply volume label','IF(ISBLANK([Panel tonnes]),"Not available",FORMAT(DIVIDE([Panel tonnes],1000),"#,0.0") & " kt")',folder='Supply')
for name,col in [('Imports','Imports'),('Exports','Exports'),('Trade balance','Balance')]:
 measure(name,'IF([One product] && [One reporter],CALCULATE(SUM(Trade['+col+']),TREATAS({[Selected basis]},Trade[Basis])))','#,0','Trade')
 measure(name+' snapshot','CALCULATE(['+name+'],TREATAS({[Selected trade year]},Trade[Year]))','#,0','Trade')
 measure(name+' label','VAR n=['+name+' snapshot] RETURN IF(ISBLANK(n),"Not available",IF([Selected basis]="trade_value",FORMAT(DIVIDE(n,1000000),"€#,0.0") & "m",FORMAT(n,"#,0.0") & " t"))',folder='Trade')
measure('Partner import share','IF([One product] && [One reporter],CALCULATE(SUM(Partners[Share]),Partners[Flow]="Import",TREATAS({[Selected basis]},Partners[Basis]),TREATAS({[Selected trade year]},Partners[Year])))','0.0%','Trade')
measure('Partner import amount','IF([One product] && [One reporter],CALCULATE(SUM(Partners[Amount]),Partners[Flow]="Import",TREATAS({[Selected basis]},Partners[Basis]),TREATAS({[Selected trade year]},Partners[Year])))','#,0','Trade')
for label,col in [('Supplier HHI lower','HHILower'),('Supplier HHI upper','HHIUpper'),('Top supplier lower','TopSupplierLower'),('Unallocated share','UnallocatedShare')]:
 measure(label,'IF([One product] && [One reporter],CALCULATE(MAX(Exposure['+col+']),TREATAS({[Selected basis]},Exposure[Basis]),TREATAS({[Selected trade year]},Exposure[Year])))','0.000' if 'HHI' in label else '0.0%','Trade')
measure('Supplier HHI label','IF(ISBLANK([Supplier HHI lower]),"Not available",FORMAT([Supplier HHI lower],"0.000") & IF(ABS([Supplier HHI upper]-[Supplier HHI lower])>0.000000001," – " & FORMAT([Supplier HHI upper],"0.000"),""))',folder='Trade')
measure('Top supplier label','IF(ISBLANK([Top supplier lower]),"Not available",FORMAT([Top supplier lower],"0.0%"))',folder='Trade')
measure('Import dependency label','"Unavailable"',folder='Readiness')
measure('No physical gap label','"Unavailable"',folder='Readiness')
measure('No capacity label','"Unavailable"',folder='Readiness')
# Risk-page measures preserve a single definition per scatter point; selected year is disconnected.
for stage in ['Mining','Refining']:
 for bound,col in [('lower','HHILower'),('upper','HHIUpper')]:
  measure(stage+' HHI '+bound,'IF([One definition],CALCULATE(MAX(Concentration['+col+']),REMOVEFILTERS(Stages),Concentration[Stage]="'+stage+'",TREATAS({[Selected supply year]},Concentration[Year])))','0.000','Risk')
 measure(stage+' HHI range','VAR lo=['+stage+' HHI lower] RETURN IF(ISBLANK(lo),"No source data",FORMAT(lo,"0.000") & " – " & FORMAT(['+stage+' HHI upper],"0.000"))',folder='Risk')
measure('Risk supply lower','CALCULATE(MAX(SupplyRisk[LowerBound]),TREATAS({[Selected supply year]},SupplyRisk[Year]))','0.000','Risk')
measure('Risk supply upper','CALCULATE(MAX(SupplyRisk[UpperBound]),TREATAS({[Selected supply year]},SupplyRisk[Year]))','0.000','Risk')
measure('Risk supply status','CALCULATE(SELECTEDVALUE(SupplyRisk[Availability]),TREATAS({[Selected supply year]},SupplyRisk[Year]))',folder='Risk')
for basis,col in [('Value','ValueHHILower'),('Mass','MassHHILower')]:
 measure(basis+' exposure HHI','IF([One product] && [One reporter],CALCULATE(MAX(Sensitivity['+col+']),TREATAS({[Selected trade year]},Sensitivity[Year])))','0.000','Risk')
measure('Basis sensitivity result','CALCULATE(SELECTEDVALUE(Sensitivity[SensitivityResult]),TREATAS({[Selected trade year]},Sensitivity[Year]))',folder='Risk')
measure('Demand kt','IF([One definition],DIVIDE(CALCULATE(SUM(Outlook[QuantityTonnes]),Outlook[SeriesKind]="demand_reported_end_uses_sum"),1000))','#,0.0','Outlook')
measure('Demand endpoint kt','CALCULATE([Demand kt],TREATAS({[Selected endpoint]},Outlook[Year]),TREATAS({[Selected scenario]},Outlook[Scenario]))','#,0.0','Outlook')
measure('Demand growth','IF([One definition],CALCULATE(MAX(Outlook[Growth]),Outlook[SeriesKind]="demand_reported_end_uses_sum",TREATAS({[Selected endpoint]},Outlook[Year]),TREATAS({[Selected scenario]},Outlook[Scenario])))','0.0%','Outlook')
measure('Demand CAGR','IF([One definition],CALCULATE(MAX(Outlook[CAGR]),Outlook[SeriesKind]="demand_reported_end_uses_sum",TREATAS({[Selected endpoint]},Outlook[Year]),TREATAS({[Selected scenario]},Outlook[Scenario])))','0.0%','Outlook')
measure('Demand growth label','IF(ISBLANK([Demand growth]),"Not available",FORMAT([Demand growth],"+0.0%;-0.0%;0.0%"))',folder='Outlook')
measure('Demand CAGR label','IF(ISBLANK([Demand CAGR]),"Not available",FORMAT([Demand CAGR],"0.0%"))',folder='Outlook')
measure('Demand endpoint label','IF(ISBLANK([Demand endpoint kt]),"Not available",FORMAT([Demand endpoint kt],"#,0.0") & " kt")',folder='Outlook')
measure('Demand end use kt','IF([One definition],DIVIDE(CALCULATE(SUM(Outlook[QuantityTonnes]),Outlook[SeriesKind]="demand_end_use",TREATAS({[Selected endpoint]},Outlook[Year]),TREATAS({[Selected scenario]},Outlook[Scenario]),TREATAS(VALUES(EndUses[EndUse]),Outlook[EndUse])),1000))','#,0.0; -#,0.0; 0','Outlook')
measure('Supply outlook kt','IF([One definition],DIVIDE(CALCULATE(SUM(Outlook[QuantityTonnes]),Outlook[SeriesKind]="supply_panel_output"),1000))','#,0.0','Outlook')
measure('Outlook context','"Native 2025 baseline → " & FORMAT([Selected endpoint],"0") & " · " & SELECTEDVALUE(ScenarioChoice[ScenarioShort],"STEPS")',folder='Context')


# Paired-stage visuals keep mining and refining in independent contexts.
for stage in ['Mining','Refining']:
 for suffix,base,fmt in [('country share','Country share','0.0%'),('output kt','Supply trend kt','#,0.0'),('output label','Supply volume label',None),('concentration label','Supply HHI label',None),('top3 label','Supply top3 label',None)]:
  measure(stage+' '+suffix,'CALCULATE(['+base+'],REMOVEFILTERS(Stages),Stages[Stage]="'+stage+'")',fmt,'Paired stages')
 measure(stage+' HHI interval width','VAR lo=['+stage+' HHI lower] VAR hi=['+stage+' HHI upper] RETURN IF(NOT ISBLANK(lo) && NOT ISBLANK(hi),hi-lo)','0.000','Risk')
 measure(stage+' outlook kt','CALCULATE([Supply outlook kt],Outlook[Stage]="'+stage+'")','#,0.0','Outlook')
# Scenario-specific measures share one fixed colour/order contract across visuals.
for short,scenario in [('CPS','Current Policies Scenario'),('STEPS','Stated Policies Scenario'),('HDS','High Demand Scenario')]:
 for suffix,base,fmt in [('demand kt','Demand kt','#,0.0'),('endpoint label','Demand endpoint label',None),('growth label','Demand growth label',None),('CAGR label','Demand CAGR label',None),('end use kt','Demand end use kt','#,0.0;-#,0.0;0')]:
  measure(short+' '+suffix,'CALCULATE(['+base+'],REMOVEFILTERS(ScenarioChoice),TREATAS({"'+scenario+'"},ScenarioChoice[Scenario]),REMOVEFILTERS(Outlook[Scenario]),REMOVEFILTERS(Outlook[ScenarioShort]),TREATAS({"'+scenario+'"},Outlook[Scenario]))',fmt,'Scenario comparison')
measure('Map country','SELECTEDVALUE(Supply[Country])',folder='Supply')
measure('Map stage','SELECTEDVALUE(Supply[Stage])',folder='Supply')
# Shared family selector narrows both exact native definitions and traded forms.
measure('Material tile label','SELECTEDVALUE(Materials[MaterialName])')
measure('Material tile color','SELECTEDVALUE(Materials[CategoryColor],"#DDEBDD")')
measure('End use status','IF(NOT [One definition],"Select one material",IF(ISBLANK([Demand end use kt]),"Not returned by source",IF([Demand end use kt]=0,"Reported zero","Reported value")))',folder='Outlook')
measure('Map share','IF([One definition],CALCULATE(MAX(Supply[Share]),Supply[Share]>0,Supply[EntityType]="country_or_territory",TREATAS({[Selected supply year]},Supply[Year])))','0.0%','Supply')
measure('Map color','IF(SELECTEDVALUE(Supply[Stage])="Refining","#479A67","#183323")',folder='Supply')
measure('Map latitude','IF(NOT ISBLANK([Map share]),AVERAGE(Supply[DisplayLatitude]))',folder='Supply')
measure('Map longitude','IF(NOT ISBLANK([Map share]),AVERAGE(Supply[DisplayLongitude]))',folder='Supply')
# Apply a compatible exact definition to every base expression. Never add graphite
# and all-grades graphite; the disconnected choice only controls that family.
for spec in MEASURES.values():
 expr=spec['expression']
 if any(t+'[' in expr for t in ['Definitions','Supply','Concentration','Outlook','SupplyRisk','OutlookRisk']):
  spec['expression']='CALCULATE('+expr+',KEEPFILTERS(FILTER(ALL(Definitions[Material]),IF(SELECTEDVALUE(DefinitionChoice[GraphiteScope],"Graphite")="All grades",Definitions[Material]<>"Graphite",Definitions[Material]<>"Graphite: all grades"))))'

# An unsupported selected slice is a dash in a visual; the footer explains the reason.
for spec in MEASURES.values():
 spec['expression']=spec['expression'].replace('"Not available"','"—"')


def build_model(root,manifest,data_folder):
 model=root/'GlobalCriticalMaterials.SemanticModel';definition=model/'definition';tables=definition/'tables';tables.mkdir(parents=True,exist_ok=True)
 save(root/'GlobalCriticalMaterials.pbip',{'$schema':BASE+'pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'GlobalCriticalMaterials.Report'}}],'settings':{'enableAutoRecovery':True}})
 save(model/'definition.pbism',{'$schema':BASE+'item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{}})
 (definition/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1604\n')
 param='expression DataFolder = '+('"'+data_folder.replace('\\','/').replace('"','""')+'"')+' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tlineageTag: '+ident('DataFolder')+'\n\tannotation PBI_ResultType = Text\n'
 (definition/'expressions.tmdl').write_text(param)
 refs=[];relations=[]
 for table,meta in manifest['tables'].items():
  refs.append('ref table '+table);lines=['/// Reviewed DuckDB business-layer export. See export_manifest.json for exact source SQL and snapshot selection.','table '+table,'\tlineageTag: '+ident(table)]
  mtypes=[]
  for col in meta['columns']:
   name,dt=col['name'],col['duckdb_type'];typ='double' if dt in ['DOUBLE','FLOAT','DECIMAL'] or dt.startswith('DECIMAL') else 'int64' if dt in ['INTEGER','BIGINT','SMALLINT','HUGEINT','UBIGINT','UINTEGER'] else 'boolean' if dt=='BOOLEAN' else 'string'
   lines+=['','\tcolumn '+name,'\t\tdataType: '+typ,'\t\tlineageTag: '+ident(table+'/'+name),'\t\tsummarizeBy: none','\t\tsourceColumn: '+name]
   if name.endswith('Key') or name in ['DefinitionScope','QuantityBasis','SnapshotKey','ComparisonContractKey','ClassificationStatus']:lines+=['\t\tisHidden']
   if name=='CountryISO3':lines+=['\t\tdataCategory: Country']
   if table in ['Materials','EndUses','PartnerDisplay'] and name in ['Symbol','MaterialName','EndUse','PartnerDisplay']:lines+=['\t\tsortByColumn: SortOrder']
   if name in ['DisplayLatitude','DisplayLongitude']:lines+=['\t\tdataCategory: '+('Latitude' if name=='DisplayLatitude' else 'Longitude')]
   if typ=='int64':lines+=['\t\tformatString: 0']
   mtype={'double':'type number','int64':'Int64.Type','boolean':'type logical','string':'type text'}[typ];mtypes.append('{"'+name+'", '+mtype+'}')
  pretype=['\t\t\t\tWithMapPoint = if Table.HasColumns(Headers, \"MapPoint\") then Headers else Table.AddColumn(Headers, \"MapPoint\", each [Country] & \" / \" & [Stage], type text),'] if table=='Supply' else []
  input_step='WithMapPoint' if table=='Supply' else 'Headers'
  lines+=['','\tpartition '+table+' = m','\t\tmode: import','\t\tsource =','\t\t\tlet','\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/'+table+'.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),','\t\t\t\tHeaders = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),',*pretype,'\t\t\t\tTyped = Table.TransformColumnTypes('+input_step+',{'+', '.join(mtypes)+'},"en-US")','\t\t\tin','\t\t\t\tTyped','']
  (tables/(table+'.tmdl')).write_text('\n'.join(lines))
  names={x['name'] for x in meta['columns']}
  for col,target in [('DefinitionKey','Definitions'),('ProductCode','Products'),('ReporterKey','Reporters'),('Stage','Stages')]:
   if col in names and table!=target and table not in ['Outlook','OutlookRisk','SupplyRisk','TradeRisk'] or (col=='DefinitionKey' and table in ['Outlook','OutlookRisk','SupplyRisk']) or (col=='Stage' and table=='SupplyRisk') or (col=='ProductCode' and table=='TradeRisk') or (col=='ReporterKey' and table=='TradeRisk'):
    if col not in names or table==target:continue
    relation='relationship '+ident(table+'/'+col+'/relationship')+'\n\tfromColumn: '+table+'.'+col+'\n\ttoColumn: '+target+'.'+col+'\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n'
    relations.append(relation)
 # Unidirectional presentation dimensions avoid ambiguous filter paths.
 for ft,fc,tt,tc in [('Definitions','Family','Materials','Family'),('Products','Family','Materials','Family'),('Partners','PartnerDisplay','PartnerDisplay','PartnerDisplay')]:
  relations.append('relationship '+ident(ft+'/'+fc+'/presentation')+'\n\tfromColumn: '+ft+'.'+fc+'\n\ttoColumn: '+tt+'.'+tc+'\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n')
 # Measures are guarded; default summarisation of every imported numeric column is disabled.
 lines=['table ReportMeasures','\tlineageTag: '+ident('ReportMeasures'),'','\tcolumn Placeholder','\t\tdataType: string','\t\tisHidden','\t\tsourceColumn: Placeholder','\t\tsummarizeBy: none']
 for name,spec in MEASURES.items():
  lines+=['',"\tmeasure '"+name+"' = "+spec['expression'],'\t\tlineageTag: '+ident('measure/'+name),'\t\tdisplayFolder: '+spec['folder']]
  if spec['format']:lines+=['\t\tformatString: '+spec['format']]
 lines+=['','\tpartition ReportMeasures = m','\t\tmode: import','\t\tsource = #table(type table [Placeholder=text],{{"measure_container"}})','']
 (tables/'ReportMeasures.tmdl').write_text('\n'.join(lines));refs.append('ref table ReportMeasures')
 (definition/'relationships.tmdl').write_text('\n'.join(relations))
 (definition/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tdiscourageImplicitMeasures\n\tsourceQueryCulture: en-US\n\tannotation __PBI_TimeIntelligenceEnabled = 0\n\n'+'\n'.join(refs)+'\n')
 return model

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'dashboards/powerbi');parser.add_argument('--data-folder',default='C:/GlobalCriticalMaterials/data');parser.add_argument('--display-font',choices=[FONT_STACK,'Avenir Next','Arial Narrow','Arial'],default=FONT_STACK);args=parser.parse_args()
 manifest=json.loads((args.output/'data/export_manifest.json').read_text());build_model(args.output,manifest,args.data_folder)
 from powerbi_report import build_report
 build_report(args.output,manifest,display_font=args.display_font)
 print(json.dumps({'status':'authored_pending_Desktop_validation','tables':len(manifest['tables'])+1,'measures':len(MEASURES),'pages':4}))
