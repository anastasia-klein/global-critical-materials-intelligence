import copy
from pathlib import Path
import tempfile
import unittest
import urllib.error
from ingestion.common import ContractError, digest, dumps, loads
from ingestion.audit import audit
from ingestion.extractors.http import HttpClient
from ingestion.pipeline import run
from ingestion.plan import build_plan
from ingestion.sources import iea, comext
from ingestion.store import Store
from ingestion.validators.jsonstat import cells

ROOT = Path(__file__).resolve().parents[1]
PLAN = build_plan(ROOT / 'config/sources.json')
SPEC = next(s for s in PLAN if s['name'] == 'Copper demand')
IEA = loads((ROOT / 'data/sample/iea/iea_copper_demand.json').read_bytes())

class FakeClient:
    def __init__(self,data):
        self.raw=(dumps(data)+'\n').encode(); self.calls=0
    def get(self,url):
        self.calls+=1
        return self.raw,{'content-type':'application/json'},url

def grid():
    return {'id':['partner','time'],'size':[2,2],
            'dimension':{'partner':{'category':{'index':{'CN':0,'US':1}}},
                         'time':{'category':{'index':['2022','2023']}}},
            'value':{'1':0,'2':17},'status':{'0':'c'}}

class SourceTests(unittest.TestCase):
    def test_selective_refresh_does_not_backfill_other_years(self):
        selected=build_plan(ROOT/'config/sources.json','comext',[2024])
        self.assertEqual(len(selected),42)
        self.assertTrue(all(s['contract']['coordinates']['time']=='2024' for s in selected))
        with self.assertRaises(ValueError):build_plan(ROOT/'config/sources.json','comext',[1900])

    def test_selective_reporters_preserve_other_scopes(self):
        selected=build_plan(ROOT/'config/sources.json','comext',[2024],['FR','EU27_2020'])
        self.assertEqual(len(selected),12)
        self.assertEqual({s['contract']['coordinates']['reporter'] for s in selected},{'FR','EU27_2020'})
        with self.assertRaises(ValueError):build_plan(ROOT/'config/sources.json','comext',[2024],['AT'])

    def test_all_saved_iea_slices_match_contracts(self):
        for spec in [s for s in PLAN if s['source']=='iea']:
            stem=spec['contract']['equals']['material'].lower().replace(':','').replace(' ','_')
            kind=spec['contract']['equals']['category'].split()[-1]
            data=loads((ROOT/f'data/sample/iea/iea_{stem}_{kind}.json').read_bytes())
            observations,_=iea.validate(data,spec)
            self.assertEqual(len(observations),len(data))
            if not data: self.assertTrue(spec['contract']['allow_empty'])
    def test_unreviewed_edition_is_rejected(self):
        data=copy.deepcopy(IEA);data[0]['mcm']='UNREVIEWED'
        with self.assertRaises(ContractError):iea.validate(data,SPEC)
    def test_duplicate_identity_is_rejected(self):
        with self.assertRaises(ContractError):iea.validate(IEA+[IEA[0]],SPEC)
    def test_empty_required_slice_is_not_success(self):
        with self.assertRaises(ContractError):iea.validate([],SPEC)
    def test_sparse_absence_status_and_zero_differ(self):
        records,report=cells(grid());records={r['source_offset']:r for _,r in records}
        self.assertIsNone(records[0]['value']);self.assertEqual(records[0]['status'],'c')
        self.assertEqual(records[1]['value'],0);self.assertNotIn(3,records)
        self.assertEqual(report['unreturned_cells'],1)
    def test_explicit_null_is_not_an_absent_sparse_cell(self):
        data=grid();data['value']['3']=None
        observations,report=cells(data);records={r['source_offset']:r for _,r in observations}
        self.assertEqual(records[3]['missingness'],'explicit_null')
        self.assertEqual(records[0]['missingness'],'status_without_value')
        self.assertEqual(report['explicit_null_cells'],1)
        self.assertEqual(report['unreturned_cells'],0)
    def test_reordered_dimensions_preserve_coordinates(self):
        other=grid();other['id']=['time','partner'];other['value']={'2':0,'1':17}
        def values(data):return {tuple(sorted(r['coordinates'].items())):(r['value'],r['status']) for _,r in cells(data)[0]}
        self.assertEqual(values(grid()),values(other))
    def test_duplicate_category_positions_and_bad_offsets_fail(self):
        data=grid();data['dimension']['partner']['category']['index']['US']=0
        with self.assertRaises(ContractError):cells(data)
        data=grid();data['value']['4']=1
        with self.assertRaises(ContractError):cells(data)
    def test_dense_values_are_not_padded(self):
        data=grid();data['value']=[None,0,17,None]
        self.assertEqual(cells(data)[1]['numeric_cells'],2)
        data['value']=[1]
        with self.assertRaises(ContractError):cells(data)
    def test_nonfinite_json_is_rejected(self):
        with self.assertRaises(ValueError):loads('{"value":NaN}')
        with self.assertRaises(ValueError):dumps({'value':float('inf')})

class ComextTests(unittest.TestCase):
    def dataset(self):
        data=loads((ROOT/'data/sample/comext/comext_cobalt.json').read_bytes())
        # Test-only layout extension: the export category exists but no export cell is supplied.
        data['size'][data['id'].index('flow')]=2
        data['dimension']['flow']['category']['index']={'1':0,'2':1}
        data['dimension']['flow']['category']['label']={'1':'IMPORT','2':'EXPORT'}
        return data
    def spec(self):
        return next(s for s in PLAN if s['name']=='28220000 2023')
    def test_inspected_eu_sample_retains_native_external_total_without_world(self):
        data=loads((ROOT/'data/sample/comext/comext_eu27_lithium_2024.json').read_bytes())
        spec=next(s for s in PLAN if s['source']=='comext' and s['contract']['coordinates']=={'freq':'A','reporter':'EU27_2020','product':'28369100','time':'2024'})
        records,_=comext.validate(data,spec)
        values={tuple(r['coordinates'][k] for k in ['partner','flow','indicators']):r['value'] for _,r in records}
        self.assertEqual(values[('EXT_EU27_2020','1','VALUE_IN_EUROS')],182113259)
        self.assertNotIn(('WORLD','1','VALUE_IN_EUROS'),values)

    def test_missing_export_cells_are_not_zero_records(self):
        records,report=comext.validate(self.dataset(),self.spec())
        self.assertEqual(report['flows_present'],['1'])
        self.assertEqual(len(records),2)
        self.assertEqual(report['unreturned_cells'],4)
    def test_wrong_reporter_is_rejected(self):
        data=self.dataset();data['dimension']['reporter']['category']['index']={'FR':0}
        with self.assertRaises(ContractError):comext.validate(data,self.spec())
    def test_renamed_indicator_order_keeps_eur_and_mass(self):
        data=self.dataset()
        data['dimension']['indicators']['category']['index']={'QUANTITY_IN_100KG':0,'VALUE_IN_EUROS':1,'SUPPLEMENTARY_QUANTITY':2}
        data['value']={'0':2.35,'1':68472}
        records,_=comext.validate(data,self.spec())
        result={r['coordinates']['indicators']:r['value'] for _,r in records}
        self.assertEqual(result['VALUE_IN_EUROS'],68472)
        self.assertEqual(result['QUANTITY_IN_100KG'],2.35)
    def test_aggregate_is_not_a_bilateral_component(self):
        data=self.dataset();data['size'][data['id'].index('partner')]=2
        data['dimension']['partner']['category']['index']={'CN':0,'WORLD':1}
        data['dimension']['partner']['category']['label']={'CN':'China','WORLD':'All countries of the world'}
        data['value']={'0':68472,'1':2.35,'6':68472,'7':2.35}
        _,report=comext.validate(data,self.spec())
        for row in report['reconciliation']:
            self.assertEqual(row['nonaggregate_cells'],1)
            self.assertEqual(row['world_minus_components'],0)

class PersistenceTests(unittest.TestCase):
    def test_audit_detects_changed_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory);result=run([SPEC],store,FakeClient(IEA))
            self.assertEqual(audit(store.root)['status'],'passed')
            manifest=loads((store.root/result['slices'][0]['manifest_path']).read_bytes())
            changed=copy.deepcopy(IEA);changed[0]['value']+=1
            (store.root/manifest['object_path']).write_bytes(FakeClient(changed).raw)
            self.assertEqual(audit(store.root)['status'],'failed')
            store.close()

    def test_live_repeat_and_offline_replay_are_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory);client=FakeClient(IEA)
            first=run([SPEC],store,client)
            before={str(p):digest(p.read_bytes()) for p in (store.root/'bronze').rglob('*.jsonl')}
            second=run([SPEC],store,client);replay=run([SPEC],store,offline=True)
            after={str(p):digest(p.read_bytes()) for p in (store.root/'bronze').rglob('*.jsonl')}
            self.assertEqual(before,after);self.assertEqual(client.calls,2)
            self.assertEqual(first['slices'][0]['snapshot_id'],second['slices'][0]['snapshot_id'])
            self.assertEqual(first['slices'][0]['snapshot_id'],replay['slices'][0]['snapshot_id'])
            store.close()
    def test_source_revision_keeps_both_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory);first=run([SPEC],store,FakeClient(IEA))
            data=copy.deepcopy(IEA);data[0]['value']+=1
            second=run([SPEC],store,FakeClient(data))
            self.assertNotEqual(first['slices'][0]['snapshot_id'],second['slices'][0]['snapshot_id'])
            self.assertEqual(len(list((store.root/'bronze').rglob('*.jsonl'))),2)
            self.assertEqual(store.latest(store.request_id(SPEC))[0],FakeClient(data).raw)
            store.close()
    def test_rejected_source_preserved_without_replacing_latest(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory);first=run([SPEC],store,FakeClient(IEA))
            before=store.latest(store.request_id(SPEC))[0]
            data=copy.deepcopy(IEA);data[0]['mcm']='UNREVIEWED'
            bad=run([SPEC],store,FakeClient(data));self.assertEqual(bad['rejected'],1)
            self.assertEqual(before,store.latest(store.request_id(SPEC))[0])
            manifest=loads((store.root/bad['slices'][0]['manifest_path']).read_bytes())
            self.assertEqual((store.root/manifest['object_path']).read_bytes(),FakeClient(data).raw)
            self.assertEqual(loads((store.root/'latest_run.json').read_bytes())['run_id'],first['run_id'])
            store.close()
    def test_offline_missing_cache_never_fetches(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory);client=FakeClient(IEA)
            result=run([SPEC],store,client,offline=True)
            self.assertEqual(result['transport_failed'],1);self.assertEqual(client.calls,0)
            store.close()

class HttpTests(unittest.TestCase):
    def test_retry_after_429(self):
        waits=[];attempts=[]
        class Response:
            status=200;url='https://example.test/data';headers={'Content-Type':'application/json'}
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):return b'[]'
        def opener(request,timeout):
            attempts.append(1)
            if len(attempts)==1:raise urllib.error.HTTPError(request.full_url,429,'rate',{'Retry-After':'3'},None)
            return Response()
        self.assertEqual(HttpClient(opener=opener,sleep=waits.append,min_interval=0).get('https://example.test/data')[0],b'[]')
        self.assertIn(3,waits);self.assertEqual(len(attempts),2)
    def test_permanent_400_is_not_retried(self):
        calls=[]
        def opener(request,timeout):
            calls.append(1);raise urllib.error.HTTPError(request.full_url,400,'bad',{},None)
        with self.assertRaises(urllib.error.HTTPError):HttpClient(opener=opener,sleep=lambda _:None).get('https://example.test/data')
        self.assertEqual(len(calls),1)
    def test_long_retry_after_is_not_shortened(self):
        def opener(request,timeout):raise urllib.error.HTTPError(request.full_url,429,'rate',{'Retry-After':'120'},None)
        with self.assertRaises(RuntimeError):HttpClient(opener=opener,sleep=lambda _:None).get('https://example.test/data')

if __name__=='__main__':unittest.main()
