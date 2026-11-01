"""Reproduce documented findings from the versioned report capture."""
from pathlib import Path
import json,re
from verify_report_inputs import verify

def main():
    import duckdb
    root=Path(__file__).resolve().parents[1];project=root/'dashboards/powerbi'
    verify(project)
    manifest=json.loads((project/'data/export_manifest.json').read_text())
    connection=duckdb.connect(':memory:')
    for table,meta in manifest['tables'].items():
        if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',table):raise ValueError('Unsafe table name')
        types={c['name']:c['duckdb_type'] for c in meta['columns']}
        connection.execute('create table "'+table+'" as select * from read_csv(?,header=true,columns=?)',[str(project/'data'/(table+'.csv')),types])
    parts=re.split(r'(?m)^-- name: ([a-z_]+)\s*$',(root/'docs/business_insights/findings.sql').read_text())
    result={}
    for name,sql in zip(parts[1::2],parts[2::2]):
        cursor=connection.execute(sql);cols=[c[0] for c in cursor.description]
        result[name]=[dict(zip(cols,row)) for row in cursor.fetchall()]
    connection.close()
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
