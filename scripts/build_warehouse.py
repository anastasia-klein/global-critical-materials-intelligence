"""Build and document the DuckDB/dbt warehouse from one audited full source capture."""
import argparse
from pathlib import Path
import os
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.common import dumps,loads,digest,utc_now
from warehouse.load_bronze import load_bronze


def main():
    project=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--database',type=Path,default=project/'data/warehouse/gcm.duckdb')
    parser.add_argument('--config',type=Path,default=project/'config/sources.json')
    parser.add_argument('--output',type=Path,default=project/'work/validation')
    parser.add_argument('--run-id')
    parser.add_argument('--historical-snapshot',action='store_true',help='Skip freshness check explicitly for fixed historical or CI source fixtures')
    args=parser.parse_args();args.database=args.database.resolve();args.output.mkdir(parents=True,exist_ok=True)
    executable=shutil.which('dbt',path=str(Path(sys.executable).parent))
    if not executable:raise RuntimeError('Install requirements-warehouse.lock.txt into this Python environment')
    target=project/'dbt/target'
    env=dict(os.environ,GCM_DUCKDB_PATH=str(args.database),DBT_SEND_ANONYMOUS_USAGE_STATS='false',DBT_PARTIAL_PARSE='false')
    report={'started_at_utc':utc_now(),'platform':'DuckDB','cloud_target':None,'historical_snapshot':args.historical_snapshot}
    loaded=load_bronze(args.data_root,args.database,args.config,args.run_id)
    (args.output/'load_report.json').write_text(dumps(loaded)+'\n')
    report['source_records']=loaded['records'];report['source_snapshots']=loaded['snapshots'];report['selected_run_id']=loaded['selected_run_id']
    commands=[['build']]
    if not args.historical_snapshot:commands.append(['source','freshness'])
    commands.append(['docs','generate','--static'])
    logs=project/'data/build_logs';logs.mkdir(parents=True,exist_ok=True)
    for command in commands:
        name='_'.join(command).replace('--','')
        full=[executable]+command+['--project-dir',str(project/'dbt'),'--profiles-dir',str(project/'dbt'),'--no-use-colors']
        result=subprocess.run(full,cwd=project,env=env,text=True,capture_output=True)
        (logs/(name+'.log')).write_text(result.stdout+result.stderr)
        if result.returncode:
            report['status']='failed';report['failed_command']=command
            (args.output/'build_report.json').write_text(dumps(report)+'\n')
            raise RuntimeError(f'dbt {command} failed; inspect {logs/(name+".log")}')
        if command==['build']:
            shutil.copy2(target/'run_results.json',args.output/'dbt_build_results.json')
        if command==['source','freshness']:
            shutil.copy2(target/'sources.json',args.output/'source_freshness.json')
    manifest=loads((target/'manifest.json').read_bytes());results=loads((args.output/'dbt_build_results.json').read_bytes())
    report['dbt_tests']={status:sum(r['status']==status for r in results['results'] if r['unique_id'].startswith('test.')) for status in ['pass','fail','error','warn']}
    report['models_built']=sum(r['unique_id'].startswith('model.') and r['status']=='success' for r in results['results'])
    report['seed_tables']=sum(r['unique_id'].startswith('seed.') and r['status']=='success' for r in results['results'])
    report['freshness']='not_run_historical_reproduction' if args.historical_snapshot else 'executed_see_source_freshness'
    import duckdb
    connection=duckdb.connect(str(args.database),read_only=True)
    report['model_rows']={f'{schema}.{name}':connection.execute(f'SELECT count(*) FROM "{schema}"."{name}"').fetchone()[0]
                          for schema,name in connection.execute("select table_schema,table_name from information_schema.tables where table_schema in ('silver','gold','quality','analytics') order by 1,2").fetchall()}
    report['blocking_quality_rows']=connection.execute('select count(*) from quality.dq_observation_issues').fetchone()[0]
    report['semantic_gates']=[dict(zip(['source','gate','affected_records','required_policy'],row)) for row in connection.execute('select * from quality.dq_semantic_gates order by source,gate').fetchall()]
    connection.close()
    if report['blocking_quality_rows'] or not report['dbt_tests']['pass'] or any(report['dbt_tests'][x] for x in ['fail','error','warn']):
        raise RuntimeError('Warehouse did not satisfy its quality acceptance criteria')
    report['documented_model_columns']=sum(len(node.get('columns',{})) for node in manifest['nodes'].values() if node['resource_type']=='model')
    report['versions']={'duckdb':duckdb.__version__,'dbt_core':results['metadata']['dbt_version']}
    report['finished_at_utc']=utc_now();report['status']='passed_with_explicit_semantic_gates'
    (args.output/'build_report.json').write_text(dumps(report)+'\n')
    shutil.copy2(target/'catalog.json',args.output/'catalog.json')
    static=target/'static_index.html'
    if static.exists():shutil.copy2(static,args.output.parent/'dbt_docs.html')
    print(dumps({'status':report['status'],'models':report['models_built'],'tests':report['dbt_tests'],'records':report['source_records']}))

if __name__=='__main__':main()
