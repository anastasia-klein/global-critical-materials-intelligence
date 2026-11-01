select record_id as demand_key,material_key,material_definition_key,geography_key,period_key,scenario_key,
    end_use_key,source_release_key,snapshot_id as snapshot_key,record_id as source_record_id,
    native_value as native_demand,native_unit,native_scope_tonnes as demand_native_scope_tonnes,
    quantity_basis,evidence_class,conversion_status,reference_year,quality_state
from {{ ref('int_iea_observations') }} where category='Material demand'
