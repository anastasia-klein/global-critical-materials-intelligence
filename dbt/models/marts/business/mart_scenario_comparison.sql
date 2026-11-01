select {{ sk(['a.outlook_key','b.outlook_key']) }} as scenario_comparison_key,
    a.source_selection_key,a.material_key,a.material_definition_key,a.geography_key,a.reference_year,
    a.series_kind,a.end_use_key,a.quantity_basis,a.measure_unit,
    b.scenario_key as reference_scenario_key,a.scenario_key as alternative_scenario_key,
    b.snapshot_key as reference_snapshot_key,a.snapshot_key as alternative_snapshot_key,
    b.native_scope_tonnes as reference_amount,a.native_scope_tonnes as alternative_amount,
    case when b.native_scope_tonnes>0 and a.missing_value_count=0 and b.missing_value_count=0
          and a.category_set_key=b.category_set_key then a.native_scope_tonnes/b.native_scope_tonnes-1 end as relative_difference_fraction,
    case when a.category_set_key!=b.category_set_key then 'unavailable_changed_end_use_scope'
         when a.missing_value_count>0 or b.missing_value_count>0 or b.native_scope_tonnes is null or b.native_scope_tonnes<=0 then 'unavailable_reference_value'
         else 'available_native_scenario_comparison' end as comparison_status,
    a.evidence_class
from {{ ref('mart_material_outlook') }} a
join {{ ref('dim_scenario') }} sa on a.scenario_key=sa.scenario_key
join {{ ref('mart_material_outlook') }} b on a.material_definition_key=b.material_definition_key
and a.geography_key=b.geography_key and a.reference_year=b.reference_year and a.series_kind=b.series_kind
and a.end_use_key is not distinct from b.end_use_key and a.quantity_basis=b.quantity_basis
and a.source_selection_key=b.source_selection_key and a.source_release_key=b.source_release_key
join {{ ref('dim_scenario') }} sb on b.scenario_key=sb.scenario_key
and sa.edition=sb.edition and sa.case_name=sb.case_name
where a.series_kind like 'demand_%' and sb.scenario_name='Current Policies Scenario'
and sa.scenario_name!='Current Policies Scenario'
