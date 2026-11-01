"""Acquire original source bytes, validate source contracts, materialise versioned Bronze."""
import logging
from pathlib import Path
import uuid
from .common import atomic_write, dumps, loads, utc_now
from .sources import comext, iea

LOG = logging.getLogger(__name__)
VALIDATORS = {'iea':iea.validate,'comext':comext.validate}


def run(plan, store, client=None, offline=False):
    run_id = uuid.uuid4().hex
    summary = {'run_id':run_id,'started_at_utc':utc_now(),'offline':offline,
               'requested_slices':len(plan),'accepted':0,'accepted_empty':0,'rejected':0,
               'transport_failed':0,'observations':0,'slices':[]}
    coverage = []
    for spec in plan:
        LOG.info('Source %s; slice %s', spec['source'],spec['name'])
        try:
            if offline:
                raw, previous = store.latest(store.request_id(spec))
                manifest = store.capture(spec,raw,previous['headers'],previous['final_url'],mode='offline_replay',
                                         replay_of=previous['snapshot_id'])
            else:
                if client is None:
                    raise ValueError('A transport is required for live ingestion')
                raw, headers, final_url = client.get(spec['url'])
                manifest = store.capture(spec,raw,headers,final_url)
        except Exception as exc:
            path, _ = store.failure(spec,exc)
            summary['transport_failed'] += 1
            summary['slices'].append({'name':spec['name'],'source':spec['source'],'status':'transport_failed',
                                      'manifest_path':str(path),'error':str(exc)})
            LOG.error('Transport failed for %s: %s',spec['name'],exc)
            continue
        try:
            data = loads(raw)
            observations, validation = VALIDATORS[spec['source']](data,spec)
            bronze_path, count = store.bronze(manifest,observations)
            state = 'accepted' if count else 'accepted_empty'
            path, _ = store.finish(manifest,state,validation)
            summary[state] += 1
            summary['observations'] += count
            summary['slices'].append({'name':spec['name'],'source':spec['source'],'status':state,
                                      'request_id':manifest['request_id'],'snapshot_id':manifest['snapshot_id'],
                                      'payload_sha256':manifest['payload_sha256'],'manifest_path':str(path),
                                      'bronze_path':bronze_path,'observations':count,
                                      'source_release':validation['source_release'],
                                      'validation':{key:value for key,value in validation.items() if key!='coverage'}})
            for row in validation['coverage']:
                coverage.append(dict(row,request_id=manifest['request_id'],snapshot_id=manifest['snapshot_id']))
        except Exception as exc:
            path, _ = store.finish(manifest,'rejected',{},error={'type':type(exc).__name__,'message':str(exc)})
            summary['rejected'] += 1
            summary['slices'].append({'name':spec['name'],'source':spec['source'],'status':'rejected',
                                      'manifest_path':str(path),'payload_sha256':manifest['payload_sha256'],
                                      'error':str(exc)})
            LOG.error('Source contract rejected %s: %s',spec['name'],exc)
    summary['finished_at_utc'] = utc_now()
    summary['status'] = 'failed_slices_present' if summary['transport_failed'] or summary['rejected'] else 'accepted_with_semantic_gates'
    summary['coverage_rows'] = len(coverage)
    path = Path('runs') / (run_id + '.json')
    atomic_write(store.root / path,(dumps(summary)+'\n').encode())
    atomic_write(store.root / 'runs' / (run_id + '.coverage.jsonl'),
                 ''.join(dumps(row)+'\n' for row in coverage).encode())
    if not summary['transport_failed'] and not summary['rejected']:
        atomic_write(store.root / 'latest_run.json',(dumps({'run_id':run_id,'run_path':str(path)})+'\n').encode())
    return summary
