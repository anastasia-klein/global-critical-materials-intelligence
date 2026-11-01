select
    record_id, request_id, snapshot_id, payload_sha256, source_locator, ingested_at_utc,
    source_release,
    source_record->>'$.mcm' as edition,
    source_record->>'$.material' as material_definition,
    source_record->>'$.scenario' as scenario_name,
    source_record->>'$.case' as case_name,
    source_record->>'$.category' as category,
    source_record->>'$.flow' as native_flow,
    source_record->>'$.region' as geography_native,
    source_record->>'$.product' as end_use_native,
    cast(source_record->>'$.year' as integer) as reference_year,
    source_record->>'$.unit' as native_unit,
    cast(source_record->>'$.value' as double) as native_value,
    cast(source_record->>'$.value' as double) * 1000.0 as native_scope_tonnes,
    'unverified_native_equivalent' as quantity_basis,
    case when cast(source_record->>'$.year' as integer)=2025
         then 'baseline_status_unverified' else 'scenario_projection' end as evidence_class,
    'native_mass_scale_only' as conversion_status
from {{ source('bronze','iea_records') }}
where source='iea'
