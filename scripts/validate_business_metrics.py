"""Independently recalculate business metrics from native facts using Python Decimal."""
import argparse
from collections import defaultdict
from decimal import Decimal
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.common import dumps,utc_now

D=lambda x:Decimal(str(x))

def bounds(named,residual,total,residual_can_augment_known=False):
    shares=sorted((D(x)/D(total) for x in named),reverse=True);r=D(residual)/D(total)
    lower=sum((s*s for s in shares),Decimal(0))
    return {'hhi_lower':lower,'hhi_upper':lower+r*r+(2*max(shares,default=Decimal(0))*r if residual_can_augment_known else 0),
            'top3_share_lower':sum(shares[:3]),'top3_share_upper':min(Decimal(1),sum(shares[:3])+r) if residual_can_augment_known else sum(sorted(shares+[r],reverse=True)[:3]),
            'top5_share_lower':sum(shares[:5]),'top5_share_upper':min(Decimal(1),sum(shares[:5])+r) if residual_can_augment_known else sum(sorted(shares+[r],reverse=True)[:5])}


def validate(database):
    import duckdb
    c=duckdb.connect(str(Path(database).resolve()),read_only=True)
    def rows(q):
        cursor=c.execute(q);cols=[x[0] for x in cursor.description]
        return [dict(zip(cols,x)) for x in cursor.fetchall()]
    checked=defaultdict(int);failures=[];max_error=0.0
    def close(actual,expected,label,tolerance=1e-9):
        nonlocal max_error
        checked[label.split(':')[0]]+=1
        if expected is None:
            if actual is not None:failures.append(label+':expected null')
        elif actual is None or not math.isfinite(float(actual)):
            failures.append(label+':missing or nonfinite result')
        else:
            error=abs(float(D(actual)-D(expected)));max_error=max(max_error,error)
            if error>max(tolerance,abs(float(expected))*1e-10):failures.append(label+':numeric mismatch')
    # Test arithmetic against explicit small examples, not synthetic source observations.
    known=bounds([60,25],15,100)
    assert known['hhi_lower']==D('.4225') and known['hhi_upper']==D('.4450')
    assert known['top3_share_lower']==D('.85') and known['top3_share_upper']==1
    assert bounds([60,25],15,100,True)['hhi_upper']==D('.6250')
    groups=defaultdict(list)
    for r in rows('select * from gold.fct_material_supply'):
        key=tuple(r[k] for k in ['material_definition_key','period_key','scenario_key','stage_key','snapshot_key'])
        groups[key].append(r)
    for m in rows('select * from analytics.mart_global_supply_concentration'):
        key=tuple(m[k] for k in ['material_definition_key','period_key','scenario_key','stage_key','snapshot_key'])
        src=groups[key];total=sum((D(r['supply_native_scope_tonnes']) for r in src),Decimal(0))
        named=[r['supply_native_scope_tonnes'] for r in src if r['geography_entity_type']=='country_or_territory']
        residual=sum((D(r['supply_native_scope_tonnes']) for r in src if r['geography_entity_type']=='residual'),Decimal(0))
        close(m['panel_output_tonnes'],total,'supply_panel:total',1e-5)
        for name,v in bounds(named,residual,total).items():close(m[name],v,'supply_concentration:'+name)
    groups=defaultdict(list)
    for r in rows('select f.*,d.flow_name,r.geography_id as reporter_id,g.geography_id as partner_id,g.iso_alpha2 as partner_iso2 from gold.fct_trade_flows f join gold.dim_trade_flow d using(flow_key) join gold.dim_geography r on f.reporter_key=r.geography_key join gold.dim_geography g on f.partner_key=g.geography_key'):
        for basis,column in [('trade_value','trade_value_eur'),('product_mass','product_mass_tonnes')]:
            groups[(r['product_key'],r['reporter_key'],r['snapshot_key'],r['flow_name'],basis)].append((r,r[column]))
    totals={}
    eu27=set('AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK'.split())
    for key,src in groups.items():
        eu=src[0][0]['reporter_id']=='COMEXT:EU27_2020'
        native_total='COMEXT:EXT_EU27_2020' if eu else 'WORLD'
        found=[D(v) for r,v in src if r['partner_id']==native_total and v is not None]
        named=[D(v) for r,v in src if r['partner_entity_type'] in ('country_or_territory','geopolitical_area') and (not eu or r['partner_iso2'] not in eu27) and v is not None]
        total=found[0] if len(found)==1 else None
        delta=None if total is None else total-sum(named,Decimal(0))
        tol=max(D('.01') if key[-1]=='trade_value' else D('.000001'),abs(total or 0)*D('1e-9'))
        residual=None if delta is None or delta < -tol else Decimal(0) if abs(delta)<=tol else delta
        eligible=total is not None and total>0 and delta>=-tol
        totals[key]=(total,named,residual,eligible)
    for m in rows('select * from analytics.mart_country_material_dependency'):
        key=(m['product_key'],m['reporter_key'],m['snapshot_key'],'Import',m['measure_basis']);total,named,residual,eligible=totals[key]
        close(m['reference_total'],total,'supplier_denominator:total',1e-5)
        close(m['unallocated_amount'],residual,'supplier_denominator:residual',1e-5)
        if eligible:
            for name,v in bounds(named,residual,total,True).items():close(m[name],v,'supplier_concentration:'+name)
        else:
            for name in ['hhi_lower','hhi_upper','top3_share_lower','top3_share_upper','top5_share_lower','top5_share_upper']:close(m[name],None,'unavailable_denominator:'+name)
        close(m['import_dependency'],None,'unavailable:import_dependency')
    for m in rows('select * from analytics.mart_european_trade_analysis'):
        key=(m['product_key'],m['reporter_key'],m['snapshot_key'])
        imp=totals.get(key+('Import',m['measure_basis']));exp=totals.get(key+('Export',m['measure_basis']))
        iv=imp[0] if imp and imp[0] is not None and imp[0]>=0 and imp[2] is not None else None;ev=exp[0] if exp and exp[0] is not None and exp[0]>=0 and exp[2] is not None else None
        close(m['imports'],iv,'trade_balance:imports',1e-5);close(m['exports'],ev,'trade_balance:exports',1e-5)
        close(m['trade_balance'],ev-iv if ev is not None and iv is not None else None,'trade_balance:difference',1e-5)
    # Build demand end-use/sum and supply-panel series directly from the facts.
    series={};categories=defaultdict(set)
    for r in rows('select * from gold.fct_material_demand'):
        detail=(r['material_definition_key'],r['scenario_key'],r['snapshot_key'],'demand_end_use',None,r['end_use_key'],r['reference_year'])
        series[detail]=D(r['demand_native_scope_tonnes'])
        aggregate=(r['material_definition_key'],r['scenario_key'],r['snapshot_key'],'demand_reported_end_uses_sum',None,None,r['reference_year'])
        series[aggregate]=series.get(aggregate,Decimal(0))+D(r['demand_native_scope_tonnes']);categories[aggregate].add(r['end_use_key'])
    for r in rows('select * from gold.fct_material_supply'):
        key=(r['material_definition_key'],r['scenario_key'],r['snapshot_key'],'supply_panel_output',r['stage_key'],None,r['reference_year'])
        series[key]=series.get(key,Decimal(0))+D(r['supply_native_scope_tonnes'])
    for m in rows('select * from analytics.mart_material_outlook'):
        key=tuple(m[k] for k in ['material_definition_key','scenario_key','snapshot_key','series_kind','stage_key','end_use_key','reference_year'])
        base=key[:-1]+(2025,);expected=series[key];bv=series[base]
        close(m['native_scope_tonnes'],expected,'outlook_series:source_sum',1e-5)
        close(m['base_native_scope_tonnes'],bv,'outlook_series:base',1e-5)
        if key[-1]>2025 and bv>0 and (m['series_kind']!='demand_reported_end_uses_sum' or categories[key]==categories[base]):
            close(m['growth_fraction'],expected/bv-1,'outlook_growth:fraction')
            close(m['cagr_fraction'],float(expected/bv)**(1/(key[-1]-2025))-1,'outlook_growth:cagr')
        else:close(m['growth_fraction'],None,'outlook_growth:baseline_unavailable')
        close(m['physical_supply_demand_gap'],None,'unavailable:physical_gap');close(m['nameplate_capacity'],None,'unavailable:capacity')
    scenarios={r['scenario_key']:r for r in rows('select * from gold.dim_scenario')}
    for m in rows('select * from analytics.mart_scenario_comparison'):
        keys=[(m['material_definition_key'],m[s+'_scenario_key'],m[s+'_snapshot_key'],m['series_kind'],None,m['end_use_key'],m['reference_year']) for s in ['reference','alternative']]
        ref,alt=[series[k] for k in keys]
        assert scenarios[m['reference_scenario_key']]['scenario_name']=='Current Policies Scenario'
        close(m['reference_amount'],ref,'scenario_comparison:reference',1e-5);close(m['alternative_amount'],alt,'scenario_comparison:alternative',1e-5)
        close(m['relative_difference_fraction'],alt/ref-1 if ref>0 else None,'scenario_comparison:fraction')
    c.close()
    report={'checked_at_utc':utc_now(),'status':'failed' if failures else 'passed','method':'Independent Python Decimal regrouping of native Gold facts; no business mart is used as a denominator oracle','comparison_counts':dict(sorted(checked.items())),'scalar_checks':sum(checked.values()),'max_absolute_numeric_difference_all_units':max_error,'tolerance':'max(1e-9, abs(expected)*1e-10); totals use 1e-5 absolute allowance; source residual zero uses the documented EUR/mass tolerance','arithmetic_reference_cases_passed':2,'failures':failures}
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--database',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=validate(args.database);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(dumps(report)+'\n')
    print(dumps(report));sys.exit(0 if report['status']=='passed' else 1)
