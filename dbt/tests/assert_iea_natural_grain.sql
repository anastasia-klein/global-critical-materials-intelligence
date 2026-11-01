select edition,material_definition,geography_native,reference_year,scenario_name,case_name,
       category,native_flow,end_use_native,native_unit,count(*) as records
from {{ ref('stg_iea_observations') }}
group by all
having count(*)>1
