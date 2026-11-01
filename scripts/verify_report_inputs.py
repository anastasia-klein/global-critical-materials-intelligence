"""Verify versioned report inputs without requiring the analytical warehouse."""
import argparse,csv,hashlib,json,re
from pathlib import Path

def verify(project):
    data=Path(project)/'data'
    def reject(value):raise ValueError('Non-standard JSON constant: '+value)
    manifest=json.loads((data/'export_manifest.json').read_text(),parse_constant=reject)
    rows=fields=0
    for table,spec in manifest['tables'].items():
        if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',table):raise ValueError('Unsafe manifest table name')
        path=data/(table+'.csv')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=spec['sha256']:raise ValueError('Fingerprint mismatch: '+table)
        with path.open(encoding='utf-8',newline='') as f:
            reader=csv.reader(f);columns=next(reader)
            if columns!=[c['name'] for c in spec['columns']]:raise ValueError('Column contract mismatch: '+table)
            count=0
            for row in reader:
                if len(row)!=len(columns):raise ValueError('Cell count mismatch: '+table)
                count+=1
            if count!=spec['rows']:raise ValueError('Row count mismatch: '+table)
            rows+=count;fields+=count*len(columns)
    return {'status':'passed','tables':len(manifest['tables']),'rows':rows,'scalar_fields':fields,'source_selection_key':manifest['source_selection_key']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]/'dashboards/powerbi');args=parser.parse_args();print(json.dumps(verify(args.project)))
