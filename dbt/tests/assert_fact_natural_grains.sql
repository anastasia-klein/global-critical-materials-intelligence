select 'demand' as fact,material_definition_key,geography_key,period_key,scenario_key,
       end_use_key as qualifier,source_release_key,count(*) as observations
from {{ ref('fct_material_demand') }} group by all having count(*)>1
union all
select 'supply',material_definition_key,geography_key,period_key,scenario_key,
       stage_key,source_release_key,count(*)
from {{ ref('fct_material_supply') }} group by all having count(*)>1
