"""Audit the expanded reporter population and EU bloc scope without a BI engine."""
import argparse,csv,json
from pathlib import Path

def validate(database, output):
    import duckdb
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    c=duckdb.connect(str(Path(database).resolve()),read_only=True);c.execute("set TimeZone='UTC'")
    checks=[]
    def check(name,ok,**details):
        checks.append(dict(check=name,passed=bool(ok),**details))
        assert ok,(name,details)
    def table(name,sql):
        cursor=c.execute(sql);columns=[x[0] for x in cursor.description];rows=cursor.fetchall()
        with (output/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(columns);w.writerows(rows)
        return [dict(zip(columns,r)) for r in rows]
    coverage=table('reporter_capture_coverage',"""select
      manifest->>'$.request.contract.coordinates.reporter' as reporter,
      count(*) as requested_slices,
      count(*) filter(where cast(manifest->>'$.validation.observations' as integer)=0) as empty_slices,
      sum(cast(manifest->>'$.validation.observations' as integer)) as native_cells,
      cast(min(first_retrieved_at_utc) as varchar) as first_capture_utc,
      cast(max(first_retrieved_at_utc) as varchar) as last_capture_utc
      from bronze.active_snapshots where source='comext' group by 1 order by 1""")
    expected={'DE','FR','IT','ES','PL','NL','EU27_2020'}
    check('all_seven_reviewed_reporting_areas',set(r['reporter'] for r in coverage)==expected)
    check('42_requested_product_year_slices_per_area',all(r['requested_slices']==42 for r in coverage))
    table('trade_fact_coverage',"""select g.canonical_name as reporting_area,
      f.reference_year,p.product_code,count(*) as native_partner_flow_rows,
      count(*) filter(where f.product_mass_tonnes=0 and f.trade_value_eur>0) as positive_value_reported_zero_mass
      from gold.fct_trade_flows f join gold.dim_geography g on f.reporter_key=g.geography_key
      join gold.dim_product p using(product_key) group by 1,2,3 order by 1,2,3""")
    denominators=table('denominator_availability',"""select g.canonical_name as reporting_area,
      d.denominator_scope,d.denominator_status,count(*) as panels
      from silver.int_trade_denominators d join gold.dim_geography g on d.reporter_key=g.geography_key
      group by 1,2,3 order by 1,2,3""")
    # Test the official raw EU sample's Extra-EU value, not a national sum.
    eu=c.execute("""select t.imports,t.exports from analytics.mart_european_trade_analysis t
      join gold.dim_geography g on t.reporter_key=g.geography_key
      where g.geography_id='COMEXT:EU27_2020' and t.product_code='28369100'
      and t.reference_year=2024 and t.measure_basis='trade_value'""").fetchone()
    check('EU_lithium_2024_matches_inspected_native_Extra_EU_sample',eu==(182113259.0,51611973.0))
    members="'AT','BE','BG','CY','CZ','DE','DK','EE','ES','FI','FR','GR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK'"
    leaks=c.execute("""select count(*) from analytics.mart_trade_partner_shares p
      join gold.dim_geography r on p.reporter_key=r.geography_key
      join gold.dim_geography g on p.partner_key=g.geography_key
      where r.geography_id='COMEXT:EU27_2020' and g.iso_alpha2 in ("""+members+")").fetchone()[0]
    check('EU_members_not_counted_as_external_suppliers',leaks==0,leaked_rows=leaks)
    zero=c.execute("""select count(*) from silver.int_trade_denominators d
      join analytics.mart_european_trade_analysis t using(reporter_key,product_key,snapshot_key,measure_basis)
      where d.reference_total=0 and d.denominator_row_count=1
      and ((d.flow_name='Import' and t.imports is distinct from 0.0)
      or (d.flow_name='Export' and t.exports is distinct from 0.0))""").fetchone()[0]
    check('reported_zero_amounts_retained_in_trade_totals',zero==0)
    invalid_hhi=c.execute("""select count(*) from analytics.mart_country_material_dependency
      where denominator_status!='valid_source_denominator' and (hhi_lower is not null or hhi_upper is not null)""").fetchone()[0]
    check('nonpositive_or_missing_denominator_never_produces_HHI',invalid_hhi==0)
    table('example_lithium_carbonate_2024',"""select g.canonical_name as reporting_area,t.denominator_scope,
      t.imports,t.exports,t.trade_balance from analytics.mart_european_trade_analysis t
      join gold.dim_geography g on t.reporter_key=g.geography_key
      where t.product_code='28369100' and t.reference_year=2024 and t.measure_basis='trade_value'
      order by 1""")
    c.close()
    report=dict(status='passed',mode='read_only_scope_checks_not_Desktop',checks=checks,
                denominators=denominators,source_sample_note='EU native Extra-EU sample captured 1 Nov 2026; no World total invented')
    (output/'reporting_area_validation.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();r=validate(args.database,args.output)
    print(json.dumps(dict(status=r['status'],checks=len(r['checks']))))
