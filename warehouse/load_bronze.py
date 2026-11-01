"""Transactional, version-preserving load of one complete accepted capture run into DuckDB."""
import argparse
from datetime import datetime
from pathlib import Path
from ingestion.audit import audit
from ingestion.common import digest, dumps, loads, stable_id, utc_now
from ingestion.plan import build_plan
from ingestion.pipeline import VALIDATORS


def load_bronze(data_root, database, config, run_id=None):
    import duckdb
    root, database = Path(data_root).resolve(), Path(database).resolve()
    run_path = root/'runs'/f'{run_id}.json' if run_id else root/loads((root/'latest_run.json').read_bytes())['run_path']
    result = audit(root,run_path)
    if result['status'] != 'passed':
        raise ValueError(f'Source audit failed: {result["issues"]}')
    run = loads(run_path.read_bytes())
    current_specs = {stable_id({'source':spec['source'],'url':spec['url']}):spec for spec in build_plan(Path(config))}
    expected = set(current_specs)
    selected = {item['request_id'] for item in run['slices']}
    if selected != expected or len(run['slices']) != len(expected):
        raise ValueError('Warehouse selection requires one complete approved plan; consolidate partial refreshes with a full offline replay first')
    if run['rejected'] or run['transport_failed']:
        raise ValueError('A failed acquisition cannot be selected')
    for item in run['slices']:
        manifest=loads((root/item['manifest_path']).read_bytes())
        raw=(root/manifest['object_path']).read_bytes()
        VALIDATORS[item['source']](loads(raw),current_specs[item['request_id']])
    database.parent.mkdir(parents=True,exist_ok=True)
    connection=duckdb.connect(str(database))
    try:
        connection.execute('BEGIN TRANSACTION')
        connection.execute('CREATE SCHEMA IF NOT EXISTS bronze')
        connection.execute('''CREATE TABLE IF NOT EXISTS bronze.records (
          record_id VARCHAR PRIMARY KEY, source VARCHAR NOT NULL, request_id VARCHAR NOT NULL,
          snapshot_id VARCHAR NOT NULL, source_locator VARCHAR NOT NULL, payload_sha256 VARCHAR NOT NULL,
          source_object_path VARCHAR NOT NULL, ingested_at_utc TIMESTAMPTZ NOT NULL, source_record JSON NOT NULL)''')
        connection.execute('''CREATE TABLE IF NOT EXISTS bronze.snapshots (
          snapshot_id VARCHAR PRIMARY KEY, source VARCHAR NOT NULL, request_id VARCHAR NOT NULL,
          payload_sha256 VARCHAR NOT NULL, source_release VARCHAR NOT NULL,
          source_release_timestamp TIMESTAMPTZ, first_retrieved_at_utc TIMESTAMPTZ NOT NULL,
          manifest JSON NOT NULL)''')
        connection.execute('''CREATE TABLE IF NOT EXISTS bronze.runs (
          run_id VARCHAR PRIMARY KEY, acquisition_started_at_utc TIMESTAMPTZ NOT NULL,
          checked_at_utc TIMESTAMPTZ NOT NULL, run_metadata JSON NOT NULL)''')
        connection.execute('''CREATE TABLE IF NOT EXISTS bronze.run_snapshots (
          run_id VARCHAR NOT NULL, snapshot_id VARCHAR NOT NULL, PRIMARY KEY(run_id,snapshot_id))''')
        connection.execute('CREATE TABLE IF NOT EXISTS bronze.selection (singleton BOOLEAN PRIMARY KEY CHECK(singleton), run_id VARCHAR NOT NULL)')
        connection.execute('INSERT INTO bronze.runs VALUES (?,?,?,?) ON CONFLICT DO NOTHING',
                           [run['run_id'],run['started_at_utc'],utc_now(),dumps(run)])
        record_count=0
        for item in run['slices']:
            manifest=loads((root/item['manifest_path']).read_bytes())
            released_at = item['source_release'] if item['source']=='comext' else None
            connection.execute('INSERT INTO bronze.snapshots VALUES (?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING',
                [manifest['snapshot_id'],item['source'],manifest['request_id'],manifest['payload_sha256'],
                 item['source_release'],released_at,manifest['first_retrieved_at_utc'],dumps(manifest)])
            connection.execute('INSERT INTO bronze.run_snapshots VALUES (?,?) ON CONFLICT DO NOTHING',
                               [run['run_id'],manifest['snapshot_id']])
            rows=[]
            for line in (root/item['bronze_path']).read_text().splitlines():
                record=loads(line)
                existing=connection.execute('SELECT source_record,source,request_id,snapshot_id,source_locator,payload_sha256,source_object_path,ingested_at_utc FROM bronze.records WHERE record_id=?',[record['record_id']]).fetchone()
                expected_metadata=tuple(record[key] for key in ['source','request_id','snapshot_id','source_locator','payload_sha256','source_object_path'])
                if existing and (loads(existing[0])!=record['source_record'] or tuple(existing[1:7])!=expected_metadata or existing[7]!=datetime.fromisoformat(record['ingested_at_utc'])):
                    raise ValueError('Immutable Bronze record conflicts with existing warehouse content')
                rows.append([record[key] for key in ['record_id','source','request_id','snapshot_id','source_locator',
                                                     'payload_sha256','source_object_path','ingested_at_utc']]+[dumps(record['source_record'])])
            if rows:
                connection.executemany('INSERT INTO bronze.records VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING',rows)
            record_count+=len(rows)
        loaded=connection.execute('''SELECT count(*) FROM bronze.records r JOIN bronze.run_snapshots s USING(snapshot_id)
                                    WHERE s.run_id=?''',[run['run_id']]).fetchone()[0]
        if loaded!=run['observations'] or loaded!=record_count:
            raise ValueError('Selected snapshot record count does not reconcile')
        connection.execute('INSERT INTO bronze.selection VALUES (true,?) ON CONFLICT(singleton) DO UPDATE SET run_id=excluded.run_id',[run['run_id']])
        connection.execute('''CREATE OR REPLACE VIEW bronze.active_snapshots AS
          SELECT s.*,sel.run_id FROM bronze.snapshots s JOIN bronze.run_snapshots rs USING(snapshot_id)
          JOIN bronze.selection sel ON rs.run_id=sel.run_id''')
        connection.execute('''CREATE OR REPLACE VIEW bronze.active_records AS
          SELECT r.*,s.source_release,s.source_release_timestamp FROM bronze.records r
          JOIN bronze.active_snapshots s USING(snapshot_id)''')
        for source,name in [('iea','iea_records'),('comext','comext_cells')]:
            connection.execute(f"""CREATE OR REPLACE VIEW bronze.{name} AS
              SELECT r.*,(SELECT min(first_retrieved_at_utc) FROM bronze.active_snapshots
                          WHERE source='{source}') AS oldest_selected_source_ingestion_at
              FROM bronze.active_records r WHERE r.source='{source}'""")
        connection.execute('COMMIT')
        return {'status':'passed','selected_run_id':run['run_id'],'records':loaded,'snapshots':len(run['slices']),
                'database_name':database.name,'source_audit':result}
    except Exception:
        connection.execute('ROLLBACK')
        raise
    finally:
        connection.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--config',type=Path,default=Path('config/sources.json'))
    parser.add_argument('--run-id')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    result=load_bronze(args.data_root,args.database,args.config,args.run_id)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(dumps(result)+'\n')
    print(dumps({key:value for key,value in result.items() if key!='source_audit'}))
