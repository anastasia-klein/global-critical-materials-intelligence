select
    record_id, request_id, snapshot_id, payload_sha256, source_locator, ingested_at_utc,
    source_release,
    source_record->>'$.dataset' as dataset_code,
    source_record->>'$.coordinates.reporter' as reporter_native,
    source_record->>'$.coordinates.partner' as partner_native,
    source_record->>'$.labels.reporter' as reporter_label,
    source_record->>'$.labels.partner' as partner_label,
    source_record->>'$.coordinates.product' as product_code,
    source_record->>'$.labels.product' as product_label,
    source_record->>'$.coordinates.flow' as flow_code,
    source_record->>'$.coordinates.indicators' as indicator,
    source_record->>'$.coordinates.freq' as frequency,
    cast(source_record->>'$.coordinates.time' as integer) as reference_year,
    cast(source_record->>'$.value' as double) as native_value,
    source_record->>'$.status' as source_status,
    source_record->>'$.missingness' as source_missingness,
    'CN8' as native_classification,
    'reference_year_native_not_concorded' as classification_status,
    'historical_trade_statistics_status_unverified' as evidence_class
from {{ source('bronze','comext_cells') }}
where source='comext'
