"""Offline source-fixture import for CI; no fabricated observations or live requests."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.common import atomic_write,dumps,loads,digest,utc_now
from ingestion.plan import build_plan
from ingestion.pipeline import VALIDATORS
from ingestion.store import Store
import uuid


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    project=Path(__file__).resolve().parents[1];root=args.output.resolve();root.mkdir(parents=True,exist_ok=True)
    config=loads((project/'config/sources.json').read_bytes())
    config['comext']['reporters']=['DE']
    config['comext']['years']=[2023]
    config['comext']['products']=[p for p in config['comext']['products'] if p['code']=='28220000']
    config_path=root/'fixture_config.json';config_path.write_text(dumps(config)+'\n')
    store=Store(root/'capture');run_id='fixture_'+uuid.uuid4().hex
    run={'run_id':run_id,'started_at_utc':utc_now(),'finished_at_utc':None,'offline':True,'mode':'fixture_import',
         'requested_slices':0,'accepted':0,'accepted_empty':0,'rejected':0,'transport_failed':0,'observations':0,'slices':[]}
    try:
        for spec in build_plan(config_path):
            if spec['source']=='iea':
                native=spec['contract']['equals']['material'].lower().replace(':','').replace(' ','_')
                kind=spec['contract']['equals']['category'].split()[-1]
                raw=(project/f'data/sample/iea/iea_{native}_{kind}.json').read_bytes()
            else:
                raw=(project/'tests/fixtures/comext_cobalt_2023.json').read_bytes()
                expected=loads((project/'tests/fixtures/comext_cobalt_2023.meta.json').read_bytes())['payload_sha256']
                if digest(raw)!=expected:raise ValueError('Original fixture fingerprint mismatch')
            manifest=store.capture(spec,raw,{},spec['url'],mode='fixture_import')
            observations,validation=VALIDATORS[spec['source']](loads(raw),spec)
            bronze,count=store.bronze(manifest,observations);state='accepted' if count else 'accepted_empty'
            path,_=store.finish(manifest,state,validation)
            run['requested_slices']+=1;run[state]+=1;run['observations']+=count
            run['slices'].append({'name':spec['name'],'source':spec['source'],'status':state,'manifest_path':str(path),
                                  'request_id':manifest['request_id'],'snapshot_id':manifest['snapshot_id'],
                                  'payload_sha256':manifest['payload_sha256'],'bronze_path':bronze,'observations':count,
                                  'source_release':validation['source_release']})
        run['finished_at_utc']=utc_now();run['status']='fixture_import_not_live_acquisition'
        path=Path('runs')/(run_id+'.json');atomic_write(store.root/path,(dumps(run)+'\n').encode())
        atomic_write(store.root/'latest_run.json',(dumps({'run_id':run_id,'run_path':str(path)})+'\n').encode())
    finally:store.close()
    print(dumps({'data_root':str(root/'capture'),'config':str(config_path),'observations':run['observations']}))

if __name__=='__main__':main()
