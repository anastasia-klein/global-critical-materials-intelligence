select f.material_key,f.material_definition_key,f.geography_key,f.scenario_key,
    cast(null as varchar) as stage_key,f.end_use_key,f.source_release_key,f.snapshot_key,
    f.reference_year,f.quantity_basis,f.evidence_class,
    'demand_end_use' as series_kind,'native_end_use' as denominator_scope,
    f.demand_native_scope_tonnes as native_scope_tonnes,1::integer as source_observation_count,
    case when f.demand_native_scope_tonnes is null then 1 else 0 end::integer as missing_value_count,
    f.end_use_key as category_set_key
from {{ ref('fct_material_demand') }} f
union all
select material_key,material_definition_key,geography_key,scenario_key,cast(null as varchar),cast(null as varchar),
    source_release_key,snapshot_key,reference_year,quantity_basis,evidence_class,
    'demand_reported_end_uses_sum','sum_of_returned_end_uses_not_primary_requirements',
    sum(demand_native_scope_tonnes order by end_use_key),count(*)::integer,count(*) filter(where demand_native_scope_tonnes is null)::integer,
    md5(string_agg(end_use_key,'|' order by end_use_key))
from {{ ref('fct_material_demand') }} group by all
union all
select material_key,material_definition_key,(select geography_key from {{ ref('dim_geography') }} where geography_id='WORLD'),
    scenario_key,stage_key,cast(null as varchar),source_release_key,snapshot_key,reference_year,quantity_basis,evidence_class,
    'supply_panel_output','captured_named_countries_plus_opaque_residual',sum(supply_native_scope_tonnes order by geography_key),
    count(*)::integer,count(*) filter(where supply_native_scope_tonnes is null)::integer,
    'named_and_residual_panel_membership_may_change'
from {{ ref('fct_material_supply') }} group by all
