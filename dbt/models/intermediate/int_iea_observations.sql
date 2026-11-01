select
    s.*,
    m.family_id,
    g.geography_id,
    g.entity_type as geography_entity_type,
    g.mapping_status as geography_mapping_status,
    case when s.category='Material supply' then lower(s.native_flow) end as stage_code,
    {{ sk(['m.family_id']) }} as material_key,
    {{ sk(['s.material_definition']) }} as material_definition_key,
    {{ sk(['g.geography_id']) }} as geography_key,
    {{ sk(['s.edition','s.scenario_name','s.case_name']) }} as scenario_key,
    {{ sk(['s.reference_year']) }} as period_key,
    {{ sk(["'iea'",'s.source_release']) }} as source_release_key,
    {{ sk(['s.end_use_native']) }} as end_use_key,
    case when g.geography_id is null or m.family_id is null then 'unmapped_reference'
         when s.native_unit != 'Thousand tonnes' then 'unreviewed_unit'
         when s.native_value < 0 then 'negative_physical_quantity'
         else 'structurally_valid_with_semantic_gates' end as quality_state
from {{ ref('stg_iea_observations') }} s
left join {{ ref('iea_material_mapping') }} m on s.material_definition=m.native_material
left join {{ ref('geography_mapping') }} g on g.source='iea' and g.native_id=s.geography_native
