select snapshot_id, source, request_id, payload_sha256, source_release,
    source_release_timestamp, first_retrieved_at_utc, run_id,
    manifest->>'$.validation_status' as validation_status,
    cast(manifest->>'$.validation.observations' as integer) as source_observations,
    manifest->>'$.licensing.licence' as licence_name,
    manifest->>'$.licensing.licence_url' as licence_url,
    manifest->>'$.licensing.publication_status' as publication_status,
    manifest->>'$.requested_url' as request_url
from {{ source('bronze','active_snapshots') }}
