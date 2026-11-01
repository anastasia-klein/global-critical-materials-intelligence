select record_id as supply_key,material_key,material_definition_key,geography_key,period_key,scenario_key,
    {{ sk(['stage_code']) }} as stage_key,source_release_key,snapshot_id as snapshot_key,
    record_id as source_record_id,native_value as native_supply,native_unit,
    native_scope_tonnes as supply_native_scope_tonnes,quantity_basis,evidence_class,conversion_status,
    reference_year,geography_entity_type,quality_state,'expected_output_not_capacity' as supply_measure_kind
from {{ ref('int_iea_observations') }} where category='Material supply'
