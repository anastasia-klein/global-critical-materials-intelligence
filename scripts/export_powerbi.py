"""Export source-aware business views to portable UTF-8 CSV for Power BI Import."""
import argparse,csv,hashlib,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.common import dumps

QUERIES={
'Definitions':"""select d.material_definition_key as DefinitionKey,d.native_material as Material,
 case d.native_material when 'Copper' then 'Cu · Copper' when 'Cobalt' then 'Co · Cobalt' when 'Lithium' then 'Li · Lithium' when 'Nickel' then 'Ni · Nickel' when 'Graphite' then 'C · Graphite' when 'Graphite: all grades' then 'C · All grades' else 'REE · Magnets' end as MaterialButton,
 m.material_family as Family,d.definition_scope as DefinitionScope,d.quantity_basis as QuantityBasis
 from gold.dim_material_definition d join gold.dim_material m using(material_key)""",
'Products':"""select distinct product_code as ProductCode,product_label as Product, product_code||' · '||case product_code when '28369100' then 'Lithium carbonates' when '28220000' then 'Cobalt oxides / hydroxides' when '26030000' then 'Copper ores / concentrates' when '26040000' then 'Nickel ores / concentrates' when '25041000' then 'Natural graphite powder / flakes' else 'Rare-earth-containing magnets' end as ProductLabel,
 case product_code when '28369100' then 'Lithium carbonates' when '28220000' then 'Cobalt oxides / hydroxides' when '26030000' then 'Copper ores / concentrates' when '26040000' then 'Nickel ores / concentrates' when '25041000' then 'Natural graphite powder / flakes' else 'Rare-earth-containing magnets' end as ProductShort,
 case product_code when '28369100' then 'Li carbonate · 28369100' when '28220000' then 'Co oxides · 28220000' when '26030000' then 'Cu ores · 26030000' when '26040000' then 'Ni ores · 26040000' when '25041000' then 'Graphite · 25041000' else 'REE magnets · 85051110' end as ProductButton,
 replace(product_form,'_',' ') as ProductForm,definition_scope as DefinitionScope,replace(quantity_basis,'_',' ') as QuantityBasis
 from gold.dim_product""",
'Reporters':"""select distinct g.geography_key as ReporterKey,g.canonical_name as Reporter,
 case when g.geography_id='COMEXT:EU27_2020' then 'EU27 · Extra-EU' else g.canonical_name end as ReporterLabel,
 case when g.geography_id='COMEXT:EU27_2020' then 'EU27_2020' else g.iso_alpha2 end as ReporterCode,
 case when g.geography_id='COMEXT:EU27_2020' then 'Extra-EU27 only · fixed 2020 membership' else 'All partners · including intra-EU' end as TradeScope,
 g.entity_type as ReporterType
 from gold.fct_trade_flows f join gold.dim_geography g on f.reporter_key=g.geography_key""",
'Stages':"select stage_name as Stage from gold.dim_supply_chain_stage",
'SupplyYears':"select distinct reference_year as Year from gold.fct_material_supply",
'TradeYears':"select distinct reference_year as Year from gold.fct_trade_flows",
'FutureYears':"select distinct reference_year as Year from gold.fct_material_demand",
'ScenarioChoice':"""select scenario_name as Scenario,edition as Edition,case_name as ScenarioCase,
 case when scenario_name='Stated Policies Scenario' then 'STEPS' when scenario_name='Current Policies Scenario' then 'CPS' else 'HDS' end as ScenarioShort
 from gold.dim_scenario where scenario_kind='scenario_model'""",
'BasisChoice':"""select distinct measure_basis as Basis,
 case when measure_basis='trade_value' then 'Value · EUR' else 'Product mass · t' end as BasisLabel
 from analytics.mart_country_material_dependency""",
'Supply':"""select f.supply_share_key as RowKey,f.source_selection_key as SelectionKey,f.material_definition_key as DefinitionKey,
 f.reference_year as Year,s.stage_name as Stage,g.canonical_name as Country,g.iso_alpha3 as CountryISO3,
 f.geography_entity_type as EntityType,f.supply_native_scope_tonnes as QuantityTonnes,
 f.supply_share as Share,f.panel_output_tonnes as PanelTonnes,f.evidence_class as Evidence,
 f.snapshot_key as SnapshotKey,f.source_record_id as SourceRecordKey,f.quantity_basis as QuantityBasis
 from analytics.mart_supply_country_shares f join gold.dim_supply_chain_stage s using(stage_key)
 join gold.dim_geography g using(geography_key)""",
'Concentration':"""select f.concentration_key as RowKey,f.source_selection_key as SelectionKey,f.material_definition_key as DefinitionKey,
 f.reference_year as Year,s.stage_name as Stage,f.hhi_lower as HHILower,f.hhi_upper as HHIUpper,
 f.top3_share_lower as Top3Lower,f.top3_share_upper as Top3Upper,f.top5_share_lower as Top5Lower,f.top5_share_upper as Top5Upper,
 f.residual_share as ResidualShare,f.metric_status as MetricStatus,f.evidence_class as Evidence,f.snapshot_key as SnapshotKey
 from analytics.mart_global_supply_concentration f join gold.dim_supply_chain_stage s using(stage_key)""",
'Trade':"""select f.trade_analysis_key as RowKey,f.source_selection_key as SelectionKey,f.product_code as ProductCode,
 f.reporter_key as ReporterKey,f.reference_year as Year,f.measure_basis as Basis,f.measure_unit as Unit,
 f.denominator_scope as DenominatorScope,f.imports as Imports,f.exports as Exports,f.trade_balance as Balance,f.import_unallocated_amount as ImportUnallocated,
 f.export_unallocated_amount as ExportUnallocated,f.balance_status as BalanceStatus,f.classification_status as ClassificationStatus,
 f.evidence_class as Evidence,f.snapshot_key as SnapshotKey
 from analytics.mart_european_trade_analysis f""",
'Partners':"""select f.partner_share_key as RowKey,f.source_selection_key as SelectionKey,f.product_code as ProductCode,
 f.reporter_key as ReporterKey,f.reference_year as Year,f.flow_name as Flow,f.partner_key as PartnerKey,
 f.partner_name as Partner,f.partner_entity_type as PartnerType,f.measure_basis as Basis,f.measure_value as Amount,
 f.denominator_scope as DenominatorScope,f.partner_share as Share,f.source_status as SourceStatus,f.source_record_id as SourceRecordKey,
 f.evidence_class as Evidence,f.snapshot_key as SnapshotKey
 from analytics.mart_trade_partner_shares f""",
'Exposure':"""select f.dependency_key as RowKey,f.source_selection_key as SelectionKey,f.product_code as ProductCode,
 f.reporter_key as ReporterKey,f.reference_year as Year,f.measure_basis as Basis,f.reference_total as Imports,
 f.denominator_scope as DenominatorScope,f.hhi_lower as HHILower,f.hhi_upper as HHIUpper,f.top_supplier_share_lower as TopSupplierLower,f.top_supplier_share_upper as TopSupplierUpper,
 f.top3_share_lower as Top3Lower,f.top3_share_upper as Top3Upper,f.unallocated_share as UnallocatedShare,
 f.denominator_status as DenominatorStatus,f.import_dependency as ImportDependency,f.import_dependency_status as ImportDependencyStatus,
 f.snapshot_key as SnapshotKey
 from analytics.mart_country_material_dependency f""",
'Sensitivity':"""select f.sensitivity_key as RowKey,f.source_selection_key as SelectionKey,p.product_code as ProductCode,
 f.reporter_key as ReporterKey,f.reference_year as Year,f.value_hhi_lower as ValueHHILower,f.value_hhi_upper as ValueHHIUpper,
 f.mass_hhi_lower as MassHHILower,f.mass_hhi_upper as MassHHIUpper,f.sensitivity_result as SensitivityResult,
 f.external_reconciliation_caveat as ExternalReconciliationCaveat,f.snapshot_key as SnapshotKey
 from analytics.mart_supplier_basis_sensitivity f join gold.dim_product p using(product_key)""",
'Composition':"""select f.composition_change_key as RowKey,f.source_selection_key as SelectionKey,f.product_code as ProductCode,
 f.reporter_key as ReporterKey,f.base_year as BaseYear,f.end_year as EndYear,g.canonical_name as Partner,f.measure_basis as Basis,
 f.base_share as BaseShare,f.end_share as EndShare,f.conditional_share_change_pp as ConditionalChangePP,
 f.verified_share_change_pp as VerifiedChangePP,f.presence_pattern as PresencePattern,f.comparison_status as ComparisonStatus,
 f.base_snapshot_key as BaseSnapshotKey,f.end_snapshot_key as EndSnapshotKey
 from analytics.mart_supplier_composition_changes f join gold.dim_geography g on f.partner_key=g.geography_key""",
'Outlook':"""select f.outlook_key as RowKey,f.source_selection_key as SelectionKey,f.material_definition_key as DefinitionKey,
 f.reference_year as Year,f.base_year as BaseYear,coalesce(st.stage_name,'Not applicable') as Stage,
 sc.scenario_name as Scenario,sc.edition as Edition,sc.case_name as ScenarioCase,
 case when sc.scenario_name='Stated Policies Scenario' then 'STEPS' when sc.scenario_name='Current Policies Scenario' then 'CPS' else 'HDS' end as ScenarioShort,
 f.series_kind as SeriesKind,coalesce(e.end_use_name,'Not applicable') as EndUse,
 f.native_scope_tonnes as QuantityTonnes,f.base_native_scope_tonnes as BaseTonnes,f.growth_fraction as Growth,
 f.cagr_fraction as CAGR,f.growth_status as GrowthStatus,f.physical_supply_demand_gap as PhysicalGap,
 f.physical_gap_status as PhysicalGapStatus,f.nameplate_capacity as NameplateCapacity,f.capacity_status as CapacityStatus,
 f.evidence_class as Evidence,f.quantity_basis as QuantityBasis,f.comparison_contract_key as ComparisonContractKey,f.snapshot_key as SnapshotKey
 from analytics.mart_material_outlook f join gold.dim_scenario sc using(scenario_key)
 left join gold.dim_supply_chain_stage st using(stage_key) left join gold.dim_end_use e using(end_use_key)""",
}
RISK="""select f.risk_component_key as RowKey,f.source_selection_key as SelectionKey,{scope} as {scope_alias},
 f.reference_year as Year,f.base_year as BaseYear,f.end_year as EndYear,coalesce(st.stage_name,'Not applicable') as Stage,
 sc.scenario_name as Scenario,sc.case_name as ScenarioCase,sc.edition as Edition,f.measure_basis as Basis,
 f.component_name as Component,f.component_unit as Unit,f.component_value as Value,f.component_lower as LowerBound,f.component_upper as UpperBound,
 f.availability as Availability,f.availability_reason as AvailabilityReason,f.evidence_class as Evidence,
 f.comparison_contract_key as ComparisonContractKey,f.lineage_snapshot_key as SnapshotKey
 from analytics.mart_material_supply_risk f join gold.dim_scenario sc using(scenario_key)
 left join gold.dim_supply_chain_stage st using(stage_key) {join}
 where {where}"""
QUERIES['SupplyRisk']=RISK.format(scope='f.scope_key',scope_alias='DefinitionKey',join='',where="f.scope_kind='native_material_definition' and f.component_name='supply_geographic_hhi'")
QUERIES['TradeRisk']=RISK.format(scope='p.product_code',scope_alias='ProductCode',join='join gold.dim_product p on f.scope_key=p.product_key',where="f.scope_kind='annual_traded_product'")
QUERIES['TradeRisk']=QUERIES['TradeRisk'].replace('f.reference_year as Year','f.geography_key as ReporterKey,f.reference_year as Year')
QUERIES['OutlookRisk']=RISK.format(scope='f.scope_key',scope_alias='DefinitionKey',join='',where="f.scope_kind='native_material_definition' and f.component_name!='supply_geographic_hhi'")


# Presentation dimensions are explicit and independent of the warehouse facts.
QUERIES['Materials']="""select * from (values
 ('Copper','Cu','Copper',29,'Transition metal','#DDEBDD',1),
 ('Cobalt','Co','Cobalt',27,'Transition metal','#DDEBDD',2),
 ('Lithium','Li','Lithium',3,'Alkali metal','#F2E5CD',3),
 ('Nickel','Ni','Nickel',28,'Transition metal','#DDEBDD',4),
 ('Graphite','C','Graphite',6,'Nonmetal','#E1E8ED',5),
 ('Magnet rare earth context','REE','Rare earths',NULL,'Element group','#E9E1EF',6)
 ) as t(Family,Symbol,MaterialName,AtomicNumber,Category,CategoryColor,SortOrder)"""
QUERIES['DefinitionChoice']="select * from (values ('Graphite'),('All grades')) as t(GraphiteScope)"
QUERIES['EndUses']="""select * from (values
 ('Electric vehicles',1),('Grid battery storage',2),('Electricity networks',3),
 ('Wind',4),('Solar PV',5),('Hydrogen technologies',6),
 ('Other low emissions power generation',7),('Other uses',8)
 ) as t(EndUse,SortOrder)"""
QUERIES['Products']="select p.*,case ProductCode when '26030000' then 'Copper' when '28220000' then 'Cobalt' when '28369100' then 'Lithium' when '26040000' then 'Nickel' when '25041000' then 'Graphite' else 'Magnet rare earth context' end as Family from ("+QUERIES['Products']+") p"
# Frozen reference union: leading country for each reporter/product, 2024 EUR imports.
# Ranking stays within each native reporter scope; no country/bloc totals are added.
partner_reference="""select distinct partner_name as Partner
 from analytics.mart_trade_partner_shares
 where reference_year=2024 and flow_name='Import' and measure_basis='trade_value'
 and partner_entity_type='country_or_territory'
 qualify row_number() over(partition by reporter_key,product_code order by measure_value desc,partner_name)=1"""
QUERIES['PartnerDisplay']="select Partner as PartnerDisplay,row_number() over(order by Partner)::integer as SortOrder from ("+partner_reference+") union all select 'Other partners',1000"
QUERIES['Partners']="select p.*,case when Partner in (select Partner from ("+partner_reference+")) then Partner else 'Other partners' end as PartnerDisplay from ("+QUERIES['Partners']+") p"
# Natural Earth label anchors are cartographic positions, never mine/refinery locations.
# The paired longitude shift is a display-only separation; original country IDs stay intact.
import json as _json
_world=Path(__file__).resolve().parents[1]/'dashboards/assets/ne_world_110m.geojson'
_anchors=[]
for _f in _json.loads(_world.read_text())['features']:
 _p=_f['properties'];_iso=_p.get('ISO_A3_EH')
 if _iso and _iso!='-99' and _p.get('LABEL_X') is not None:
  _anchors.append("('"+_iso+"',"+str(_p['LABEL_X'])+","+str(_p['LABEL_Y'])+")")
_anchor_sql="select * from (values "+','.join(_anchors)+") a(ISO3,AnchorLongitude,AnchorLatitude)"
QUERIES['Supply']="select s.*,s.Country||' / '||s.Stage as MapPoint,a.AnchorLatitude as DisplayLatitude,a.AnchorLongitude+case s.Stage when 'Mining' then -3.0 else 3.0 end as DisplayLongitude from ("+QUERIES['Supply']+") s left join ("+_anchor_sql+") a on s.CountryISO3=a.ISO3"

def export(database,output):
 import duckdb
 output=Path(output);output.mkdir(parents=True,exist_ok=True);c=duckdb.connect(str(Path(database).resolve()),read_only=True);c.execute("set TimeZone='UTC'")
 capture=c.execute("select source,cast(min(first_retrieved_at_utc) as varchar),cast(max(first_retrieved_at_utc) as varchar) from bronze.active_snapshots group by source order by source").fetchall()
 from datetime import datetime
 def captured_label(source):
  row=next((r for r in capture if r[0]==source),None)
  if row is None:return 'NO CAPTURE'
  first,last=[datetime.fromisoformat(x[:10]).strftime('%d %b %Y').upper() for x in row[1:]]
  return first if first==last else first+'–'+last
 capture_label='IEA: '+captured_label('iea')+' / TRADE: '+captured_label('comext')
 manifest={'source_captures':{source:{'first':first,'last':last} for source,first,last in capture},'source_capture_label':capture_label,'warehouse':'DuckDB','mode':'portable_Import_from_reviewed_marts','source_selection_key':c.execute('select source_selection_key from silver.int_analysis_context').fetchone()[0],'tables':{}}
 for table,sql in QUERIES.items():
  cursor=c.execute('select * from ('+sql+') as exported order by all');description=list(cursor.description);cols=[x[0] for x in description];rows=cursor.fetchall()
  if 'RowKey' in cols:assert len({r[cols.index('RowKey')] for r in rows})==len(rows),table
  types=[{'name':a,'duckdb_type':str(b)} for a,b,*_ in description]
  path=output/(table+'.csv')
  with path.open('w',encoding='utf-8',newline='') as f:
   writer=csv.writer(f,lineterminator='\n');writer.writerow(cols);writer.writerows(rows)
  manifest['tables'][table]={'rows':len(rows),'columns':types,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_sql':sql}
  # Round-trip independently using DuckDB's all-text reader; retain blank versus nonblank values.
  count=c.execute('select count(*) from read_csv(?,header=true,all_varchar=true)',[str(path.resolve())]).fetchone()[0];assert count==len(rows)
 assert sum(manifest['tables'][n]['rows'] for n in ['SupplyRisk','TradeRisk','OutlookRisk'])==c.execute('select count(*) from analytics.mart_material_supply_risk').fetchone()[0]
 c.close();(output/'export_manifest.json').write_text(dumps(manifest)+'\n');return manifest

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--database',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 result=export(args.database,args.output);print(dumps({'status':'passed','tables':{k:v['rows'] for k,v in result['tables'].items()}}))
