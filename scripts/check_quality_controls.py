"""Deliberately violate business rules in disposable database copies, never source data."""
import argparse
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.common import digest,dumps,loads,utc_now


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--phase',choices=['native','business','all'],default='native')
    args=parser.parse_args();database=args.database.resolve();project=Path(__file__).resolve().parents[1]
    executable=shutil.which('dbt',path=str(Path(sys.executable).parent))
    if not executable:raise RuntimeError('dbt executable is not in the active Python environment')
    if Path(str(database)+'.wal').exists():raise RuntimeError('Close/checkpoint the source warehouse before copy tests')
    before=digest(database.read_bytes());results=[]
    controls=[('mass_scale','assert_mass_scale_and_missingness',
       '''update gold.fct_trade_flows set product_mass_tonnes=product_mass_tonnes*1000
          where trade_flow_key=(select trade_flow_key from gold.fct_trade_flows where product_mass_tonnes>0 order by product_mass_tonnes desc limit 1)'''),
       ('semantic_duplicate','assert_fact_natural_grains',
        "insert into gold.fct_material_demand select * replace(demand_key || '_negative_control' as demand_key) from gold.fct_material_demand limit 1")]
    business_controls=[('trade_balance','assert_business_trade_balance',
        'update analytics.mart_european_trade_analysis set trade_balance=trade_balance+1 where trade_analysis_key=(select min(trade_analysis_key) from analytics.mart_european_trade_analysis)'),
       ('risk_semantic_duplicate','assert_risk_component_grain_and_availability',
        "insert into analytics.mart_material_supply_risk select * replace(risk_component_key || '_negative_control' as risk_component_key) from analytics.mart_material_supply_risk limit 1")]
    if args.phase=='business':controls=business_controls
    elif args.phase=='all':controls+=business_controls
    import duckdb
    with tempfile.TemporaryDirectory(prefix='gcm-controls-') as temporary:
        for name,test,mutation in controls:
            directory=Path(temporary)/name;directory.mkdir()
            clone=directory/database.name;shutil.copy2(database,clone)
            connection=duckdb.connect(str(clone));connection.execute(mutation);connection.close()
            env=dict(os.environ,GCM_DUCKDB_PATH=str(clone),DBT_SEND_ANONYMOUS_USAGE_STATS='false',DBT_PARTIAL_PARSE='false')
            target=directory/'target'
            command=[executable,'test','--project-dir',str(project/'dbt'),'--profiles-dir',str(project/'dbt'),
                     '--target-path',str(target),'--select',test,'--no-use-colors']
            process=subprocess.run(command,cwd=project,env=env,text=True,capture_output=True)
            result=loads((target/'run_results.json').read_bytes())
            failures=[r for r in result['results'] if r['status']=='fail' and test in r['unique_id']]
            valid=process.returncode==1 and len(failures)==1 and failures[0].get('failures',0)>0
            results.append({'control':name,'test':test,'expected_test_failure_detected':valid,
                            'return_code':process.returncode,'failing_rows':failures[0].get('failures') if failures else None})
            if not valid:raise RuntimeError('Negative control did not fail for the expected business-rule reason: '+process.stdout+process.stderr)
    unchanged=digest(database.read_bytes())==before
    if not unchanged:raise RuntimeError('The production warehouse changed during disposable-copy controls')
    report={'checked_at_utc':utc_now(),'status':'passed','database_unchanged':unchanged,
            'modified_observations_are':'temporary_test_controls_not_source_data','controls':results}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(dumps(report)+'\n')
    print(dumps(report))

if __name__=='__main__':main()
