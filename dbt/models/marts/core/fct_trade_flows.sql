select trade_flow_key,material_key,product_key,reporter_key,partner_key,period_key,
    {{ sk(['flow_code']) }} as flow_key,source_release_key,snapshot_id as snapshot_key,
    value_record_id,quantity_record_id,supplementary_record_id,
    trade_value_eur,native_quantity_100kg,product_mass_tonnes,supplementary_quantity,
    value_source_status,quantity_source_status,supplementary_source_status,quantity_basis,conversion_status,classification_status,
    evidence_class,reference_year,partner_entity_type,source_cell_count,quality_state,
    'unknown_product_specific_unit' as supplementary_unit_status
from {{ ref('int_trade_flows') }}
