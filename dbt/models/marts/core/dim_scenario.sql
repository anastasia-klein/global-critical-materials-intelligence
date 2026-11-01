select distinct {{ sk(['edition','scenario_name','case_name']) }} as scenario_key,
    edition,scenario_name,case_name,'scenario_model' as scenario_kind
from {{ ref('stg_iea_observations') }}
union all
select {{ sk(["'not_applicable'","'not_applicable'","'not_applicable'"]) }},
    'not_applicable','not_applicable','not_applicable','not_applicable'
