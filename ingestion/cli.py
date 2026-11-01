"""CLI: inspect plan, acquire live snapshots or replay checked local captures."""
import argparse
import logging
import os
from pathlib import Path
from .common import dumps
from .extractors.http import HttpClient, CurlHttpClient
from .pipeline import run
from .plan import build_plan
from .store import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['plan','run'])
    parser.add_argument('--config',type=Path,default=Path('config/sources.json'))
    parser.add_argument('--source',choices=['all','iea','comext'],default='all')
    parser.add_argument('--data-root',type=Path,default=Path(os.environ.get('GCM_DATA_ROOT','data/raw')))
    parser.add_argument('--years',type=int,nargs='+',help='Refresh only these approved Comext years; IEA reference years remain source-native')
    parser.add_argument('--reporters',nargs='+',help='Refresh only these reviewed Comext reporter codes')
    parser.add_argument('--transport',choices=['urllib','system-curl'],default='urllib')
    parser.add_argument('--offline',action='store_true',help='Replay only previously accepted captures; no network fallback')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    plan = build_plan(args.config,args.source,args.years,args.reporters)
    if args.command == 'plan':
        print(dumps(plan))
        return 0
    client_class=CurlHttpClient if args.transport=='system-curl' else HttpClient
    client = None if args.offline else client_class(
        timeout=float(os.environ.get('GCM_HTTP_TIMEOUT_SECONDS','45')),
        attempts=int(os.environ.get('GCM_HTTP_ATTEMPTS','4')),
        min_interval=float(os.environ.get('GCM_HTTP_MIN_INTERVAL_SECONDS','1')))
    store = Store(args.data_root)
    try:
        summary = run(plan,store,client,args.offline)
    finally:
        store.close()
    print(dumps({key:value for key,value in summary.items() if key!='slices'}))
    return 1 if summary['transport_failed'] or summary['rejected'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
