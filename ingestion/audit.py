"""Audit a completed local ingestion run against original bytes and Bronze identities."""
import argparse
from collections import Counter
from pathlib import Path
from .common import atomic_write, digest, dumps, loads, utc_now
from .pipeline import VALIDATORS


def audit(data_root, run_path=None):
    root = Path(data_root).resolve()
    if run_path is None:
        run_path = root / loads((root/'latest_run.json').read_bytes())['run_path']
    run = loads(Path(run_path).read_bytes())
    issues, identifiers, totals, releases = [], set(), Counter(), set()
    numeric_cells = missing_cells = 0
    for item in run['slices']:
        if item['status'] not in {'accepted','accepted_empty'}:
            issues.append(f'Failed slice: {item["name"]}')
            continue
        manifest = loads((root/item['manifest_path']).read_bytes())
        raw = (root/manifest['object_path']).read_bytes()
        if digest(raw) != manifest['payload_sha256']:
            issues.append(f'Corrupt object: {item["name"]}')
        observations, validation = VALIDATORS[item['source']](loads(raw),manifest['request'])
        expected = {locator:record for locator,record in observations}
        bronze = [loads(line) for line in (root/item['bronze_path']).read_text().splitlines()]
        if len(bronze) != len(expected) or len(bronze) != item['observations']:
            issues.append(f'Bronze count mismatch: {item["name"]}')
        for record in bronze:
            if record['record_id'] in identifiers:
                issues.append('Duplicate record_id within selected run')
            identifiers.add(record['record_id'])
            if record['source_record'] != expected.get(record['source_locator']):
                issues.append(f'Native record mismatch: {item["name"]}')
            if record['payload_sha256'] != manifest['payload_sha256'] or record['snapshot_id'] != manifest['snapshot_id']:
                issues.append('Lineage mismatch')
            if record['source_record'].get('value') is None:
                missing_cells += 1
            else:
                numeric_cells += 1
        totals[item['source']] += len(bronze)
        releases.add((item['source'],validation['source_release']))
    report = {'audited_at_utc':utc_now(),'run_id':run['run_id'],'status':'failed' if issues else 'passed',
              'slices':len(run['slices']),'observations':sum(totals.values()),'unique_record_ids':len(identifiers),
              'observations_by_source':dict(totals),'source_releases':[list(x) for x in sorted(releases)],
              'numeric_observations':numeric_cells,'explicit_null_observations':missing_cells,
              'empty_slices':[item['name'] for item in run['slices'] if item['status']=='accepted_empty'],
              'checks':['object_sha256','revalidation','record_count','unique_record_id','native_record_equality','lineage'],
              'issues':issues}
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--run-path',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=audit(args.data_root,args.run_path)
    atomic_write(args.output,(dumps(report)+'\n').encode())
    print(dumps(report))
    raise SystemExit(0 if not report['issues'] else 1)
