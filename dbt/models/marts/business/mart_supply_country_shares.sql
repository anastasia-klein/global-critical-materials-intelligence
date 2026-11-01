with panel as (
select *,sum(supply_native_scope_tonnes) over(partition by material_definition_key,period_key,scenario_key,stage_key,snapshot_key,quantity_basis order by geography_key rows between unbounded preceding and unbounded following) as panel_output_tonnes,
    count(*) filter(where supply_native_scope_tonnes is null or supply_native_scope_tonnes<0) over(partition by material_definition_key,period_key,scenario_key,stage_key,snapshot_key,quantity_basis)::integer as invalid_panel_observations
from {{ ref('fct_material_supply') }}
)
select {{ sk(['s.supply_key','c.source_selection_key']) }} as supply_share_key,c.source_selection_key,
    s.material_key,s.material_definition_key,s.geography_key,s.period_key,s.scenario_key,s.stage_key,
    s.source_release_key,s.snapshot_key,s.source_record_id,s.reference_year,s.geography_entity_type,
    s.supply_native_scope_tonnes,s.quantity_basis,s.evidence_class,s.panel_output_tonnes,s.invalid_panel_observations,
    case when s.panel_output_tonnes>0 and s.invalid_panel_observations=0 then s.supply_native_scope_tonnes/s.panel_output_tonnes end as supply_share,
    'captured_named_countries_plus_opaque_residual' as denominator_scope,
    'expected_output_not_capacity' as supply_measure_kind
from panel s cross join {{ ref('int_analysis_context') }} c
