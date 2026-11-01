with components as (
select s.source_selection_key,s.material_key,'native_material_definition' as scope_kind,
    s.material_definition_key as scope_key,g.geography_key,s.scenario_key,s.reference_year,
    s.reference_year as base_year,s.reference_year as end_year,s.stage_key,
    'native_scope_output' as measure_basis,s.quantity_basis,s.denominator_scope,
    'supply_geographic_hhi' as component_name,'HHI_0_to_1' as component_unit,
    case when s.residual_share=0 then s.hhi_lower end as component_value,
    s.hhi_lower as component_lower,s.hhi_upper as component_upper,
    case when s.metric_status='unavailable_invalid_panel' then 'unavailable'
         when s.residual_share>0 then 'bounded' else 'available' end as availability,
    s.metric_status as availability_reason,s.evidence_class,s.snapshot_key as lineage_snapshot_key,
    'level_no_growth_comparison' as comparison_kind
from {{ ref('mart_global_supply_concentration') }} s
cross join (select geography_key from {{ ref('dim_geography') }} where geography_id='WORLD') g
union all
select d.source_selection_key,d.material_key,'annual_traded_product',d.product_key,d.reporter_key,
    s.scenario_key,d.reference_year,d.reference_year,d.reference_year,cast(null as varchar),
    d.measure_basis,case when d.measure_basis='trade_value' then 'native_EUR' else 'traded_product_mass' end,
    d.denominator_scope,'import_supplier_hhi','HHI_0_to_1',
    case when d.unallocated_amount=0 then d.hhi_lower end,d.hhi_lower,d.hhi_upper,
    case when d.denominator_status!='valid_source_denominator' then 'unavailable'
         when d.unallocated_amount>0 then 'bounded' else 'available' end,d.denominator_status,
    d.evidence_class,d.snapshot_key,'level_no_growth_comparison'
from {{ ref('mart_country_material_dependency') }} d
cross join (select scenario_key from {{ ref('dim_scenario') }} where scenario_kind='not_applicable') s
union all
select d.source_selection_key,d.material_key,'annual_traded_product',d.product_key,d.reporter_key,
    s.scenario_key,d.reference_year,d.reference_year,d.reference_year,cast(null as varchar),
    'compatible_consumption','coherent_material_form',d.denominator_scope,'import_dependency','fraction',
    cast(null as double),cast(null as double),cast(null as double),'unavailable',d.import_dependency_status,
    d.evidence_class,d.snapshot_key,'level_no_growth_comparison'
from {{ ref('mart_country_material_dependency') }} d
cross join (select scenario_key from {{ ref('dim_scenario') }} where scenario_kind='not_applicable') s
where d.measure_basis='trade_value'
union all
select o.source_selection_key,o.material_key,'native_material_definition',o.material_definition_key,
    o.geography_key,o.scenario_key,o.reference_year,o.base_year,o.reference_year,o.stage_key,
    'native_scope_output',o.quantity_basis,o.denominator_scope,
    case when o.series_kind='supply_panel_output' then 'supply_output_growth' else 'demand_growth' end,
    'fraction',o.growth_fraction,o.growth_fraction,o.growth_fraction,
    case when o.growth_status='available_native_scope_growth' then 'available' else 'unavailable' end,
    o.growth_status,o.evidence_class,o.snapshot_key,'growth_from_native_2025_baseline'
from {{ ref('mart_material_outlook') }} o
where o.series_kind in ('demand_reported_end_uses_sum','supply_panel_output') and o.reference_year>2025
union all
select o.source_selection_key,o.material_key,'native_material_definition',o.material_definition_key,
    o.geography_key,o.scenario_key,o.reference_year,o.base_year,o.reference_year,o.stage_key,
    'native_scope_output',o.quantity_basis,o.denominator_scope,
    case when o.series_kind='supply_panel_output' then 'capacity_growth' else 'physical_supply_demand_gap' end,
    case when o.series_kind='supply_panel_output' then 'fraction' else 'tonnes_native_scope_unverified_equivalent' end,
    cast(null as double),cast(null as double),cast(null as double),'unavailable',
    case when o.series_kind='supply_panel_output' then o.capacity_status else o.physical_gap_status end,
    o.evidence_class,o.snapshot_key,'growth_from_native_2025_baseline'
from {{ ref('mart_material_outlook') }} o
where o.series_kind in ('demand_reported_end_uses_sum','supply_panel_output') and o.reference_year>2025
union all
select c.source_selection_key,m.material_key,'native_material_definition',m.material_definition_key,
    g.geography_key,sc.scenario_key,cast(y.value as integer),cast(y.value as integer),cast(y.value as integer),st.stage_key,
    'native_scope_output',m.quantity_basis,'captured_named_countries_plus_opaque_residual',
    'supply_geographic_hhi','HHI_0_to_1',cast(null as double),cast(null as double),cast(null as double),
    'unavailable','no_observations_returned_not_zero_output','no_source_observations',s.snapshot_id,'level_no_growth_comparison'
from {{ source('bronze','active_snapshots') }} s
cross join json_each(s.manifest,'$.request.contract.accepted.year') y
cross join json_each(s.manifest,'$.request.contract.accepted.flow') f
cross join json_each(s.manifest,'$.request.contract.accepted.scenario') scenario
join {{ ref('dim_material_definition') }} m on m.native_material=s.manifest->>'$.request.contract.equals.material'
join {{ ref('dim_scenario') }} sc on sc.edition=s.manifest->>'$.request.contract.equals.mcm'
and sc.case_name=s.manifest->>'$.request.contract.equals.case'
and sc.scenario_name=json_extract_string(scenario.value,'$')
join {{ ref('dim_supply_chain_stage') }} st on st.stage_name=json_extract_string(f.value,'$')
cross join (select geography_key from {{ ref('dim_geography') }} where geography_id='WORLD') g
cross join {{ ref('int_analysis_context') }} c
where s.source='iea' and s.manifest->>'$.request.contract.equals.category'='Material supply'
and cast(s.manifest->>'$.validation.observations' as integer)=0
), contracted as (
select *,{{ sk(['comparison_kind','base_year','end_year','stage_key','measure_basis','quantity_basis','denominator_scope']) }} as comparison_contract_key
from components
)
select {{ sk(['source_selection_key','scope_kind','scope_key','geography_key','scenario_key','reference_year','component_name','comparison_contract_key','lineage_snapshot_key']) }} as risk_component_key,
    *,cast(null as double) as composite_risk_score,
    'unweighted_components_no_composite_or_arbitrary_thresholds' as risk_policy
from contracted
