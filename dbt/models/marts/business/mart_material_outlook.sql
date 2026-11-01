with matched as (
select e.*,b.reference_year as base_year,b.native_scope_tonnes as base_native_scope_tonnes,
    b.evidence_class as base_evidence_class,b.category_set_key as base_category_set_key,
    b.missing_value_count as base_missing_value_count,b.source_observation_count as base_observation_count,
    case when b.reference_year is null then 'unavailable_2025_baseline'
         when b.native_scope_tonnes is null or b.native_scope_tonnes<=0 then 'unavailable_nonpositive_base'
         when e.native_scope_tonnes is null or e.native_scope_tonnes<0 then 'unavailable_end_value'
         when b.missing_value_count>0 or e.missing_value_count>0 then 'unavailable_missing_components'
         when b.category_set_key!=e.category_set_key then 'unavailable_changed_end_use_scope'
         when e.reference_year=b.reference_year then 'baseline_only'
         else 'available_native_scope_growth' end as growth_status
from {{ ref('int_outlook_series') }} e
left join {{ ref('int_outlook_series') }} b
on e.material_definition_key=b.material_definition_key and e.geography_key=b.geography_key
and e.scenario_key=b.scenario_key and e.stage_key is not distinct from b.stage_key
and e.end_use_key is not distinct from b.end_use_key and e.series_kind=b.series_kind
and e.quantity_basis=b.quantity_basis and e.source_release_key=b.source_release_key
and e.snapshot_key=b.snapshot_key and b.reference_year=2025
)
select {{ sk(['material_definition_key','geography_key','scenario_key','stage_key','end_use_key','series_kind','snapshot_key','reference_year','c.source_selection_key']) }} as outlook_key,
    c.source_selection_key,m.*,
    {{ sk(['series_kind','base_year','reference_year','stage_key','quantity_basis','denominator_scope']) }} as comparison_contract_key,
    case when growth_status='available_native_scope_growth' then native_scope_tonnes/base_native_scope_tonnes-1 end as growth_fraction,
    case when growth_status='available_native_scope_growth' then pow(native_scope_tonnes/base_native_scope_tonnes,1.0/(reference_year-base_year))-1 end as cagr_fraction,
    'tonnes_native_scope_unverified_equivalent' as measure_unit,
    cast(null as double) as physical_supply_demand_gap,
    'unavailable_matched_primary_requirements_and_equivalent_basis' as physical_gap_status,
    cast(null as double) as nameplate_capacity,
    'unavailable_supply_is_expected_output_not_capacity' as capacity_status
from matched m cross join {{ ref('int_analysis_context') }} c
