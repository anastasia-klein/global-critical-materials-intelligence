select snapshot_id as snapshot_key,{{ sk(['source','source_release']) }} as source_release_key,
    source,request_id,payload_sha256,first_retrieved_at_utc,request_url,validation_status,source_observations
from {{ ref('stg_source_snapshots') }}
