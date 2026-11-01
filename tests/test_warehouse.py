"""DuckDB persistence/reference checks using actual bounded source fixtures."""
import copy
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
from ingestion.common import dumps,loads
from ingestion.pipeline import run
from ingestion.plan import build_plan
from ingestion.store import Store

HAS_DUCKDB=importlib.util.find_spec('duckdb') is not None
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(HAS_DUCKDB,'Install the warehouse lock requirements to run DuckDB checks')
class WarehouseTests(unittest.TestCase):
    def make_capture(self,directory):
        config=loads((ROOT/'config/sources.json').read_bytes())
        config['iea']['materials']=['Copper'];config['comext']['products']=[]
        config_path=Path(directory)/'config.json';config_path.write_text(dumps(config))
        plan=build_plan(config_path)
        class FixtureClient:
            def get(self,url):
                kind='demand' if 'demand' in url else 'supply'
                return (ROOT/f'data/sample/iea/iea_copper_{kind}.json').read_bytes(),{},url
        store=Store(Path(directory)/'capture');result=run(plan,store,FixtureClient());store.close()
        return config_path,plan,result,FixtureClient
    def test_repeat_load_preserves_records_and_snapshot_selection(self):
        import duckdb
        from warehouse.load_bronze import load_bronze
        with tempfile.TemporaryDirectory() as directory:
            config,_,first,_=self.make_capture(directory);database=Path(directory)/'warehouse.duckdb'
            a=load_bronze(Path(directory)/'capture',database,config)
            b=load_bronze(Path(directory)/'capture',database,config)
            c=duckdb.connect(str(database));count=c.execute('select count(*) from bronze.records').fetchone()[0]
            selected=c.execute('select run_id from bronze.selection').fetchone()[0];c.close()
            self.assertEqual(a['records'],216);self.assertEqual(a['records'],b['records'])
            self.assertEqual(count,216);self.assertEqual(selected,first['run_id'])
    def test_partial_run_cannot_replace_complete_selection(self):
        import duckdb
        from warehouse.load_bronze import load_bronze
        with tempfile.TemporaryDirectory() as directory:
            config,plan,first,client=self.make_capture(directory);database=Path(directory)/'warehouse.duckdb'
            load_bronze(Path(directory)/'capture',database,config)
            store=Store(Path(directory)/'capture');run(plan[:1],store,client());store.close()
            with self.assertRaisesRegex(ValueError,'complete approved plan'):
                load_bronze(Path(directory)/'capture',database,config)
            c=duckdb.connect(str(database));self.assertEqual(c.execute('select run_id from bronze.selection').fetchone()[0],first['run_id']);c.close()
    def test_newer_slice_cannot_mask_old_source_capture_freshness(self):
        import duckdb
        from warehouse.load_bronze import load_bronze
        with tempfile.TemporaryDirectory() as directory:
            config,_,_,_=self.make_capture(directory);database=Path(directory)/'warehouse.duckdb'
            load_bronze(Path(directory)/'capture',database,config)
            c=duckdb.connect(str(database))
            c.execute("update bronze.snapshots set first_retrieved_at_utc='2020-01-01T00:00:00+00:00' where snapshot_id=(select snapshot_id from bronze.snapshots limit 1)")
            oldest=c.execute('select max(oldest_selected_source_ingestion_at) from bronze.iea_records').fetchone()[0]
            self.assertEqual(oldest.year,2020)
            c.close()
    def test_current_edition_contract_must_match_selected_capture(self):
        from warehouse.load_bronze import load_bronze
        with tempfile.TemporaryDirectory() as directory:
            config,_,_,_=self.make_capture(directory)
            data=loads(config.read_bytes());data['iea']['edition']='UNREVIEWED'
            config.write_text(dumps(data))
            with self.assertRaisesRegex(ValueError,'IEA mcm'):
                load_bronze(Path(directory)/'capture',Path(directory)/'warehouse.duckdb',config)
    def test_existing_immutable_lineage_conflict_is_rejected(self):
        import duckdb
        from warehouse.load_bronze import load_bronze
        with tempfile.TemporaryDirectory() as directory:
            config,_,_,_=self.make_capture(directory);database=Path(directory)/'warehouse.duckdb'
            load_bronze(Path(directory)/'capture',database,config)
            c=duckdb.connect(str(database));c.execute("update bronze.records set payload_sha256='corrupt' where record_id=(select record_id from bronze.records limit 1)");c.close()
            with self.assertRaisesRegex(ValueError,'Immutable Bronze'):
                load_bronze(Path(directory)/'capture',database,config)
    def test_seed_iso_codes_match_locked_reference(self):
        import pycountry
        with (ROOT/'dbt/seeds/geography_mapping.csv').open() as stream:
            for row in csv.DictReader(stream):
                if row['iso_alpha2']:
                    country=pycountry.countries.get(alpha_2=row['iso_alpha2'])
                    self.assertIsNotNone(country);self.assertEqual(row['iso_alpha3'],country.alpha_3)
                else:self.assertEqual(row['iso_alpha3'],'')

if __name__=='__main__':unittest.main()
