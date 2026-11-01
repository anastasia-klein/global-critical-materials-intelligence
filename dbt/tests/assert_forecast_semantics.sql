select record_id
from {{ ref('int_iea_observations') }}
where (reference_year=2025 and evidence_class!='baseline_status_unverified')
   or (reference_year>2025 and evidence_class!='scenario_projection')
   or (category='Material supply' and scenario_name!='Stated Policies Scenario')
   or (category='Material supply' and stage_code not in ('mining','refining'))
   or (category='Material supply' and end_use_native!='Total')
   or (category='Material demand' and geography_native!='World')
   or native_value<0
