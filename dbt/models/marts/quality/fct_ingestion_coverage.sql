select snapshot_id as coverage_key,run_id,source,request_id,source_release,
    source_observations,validation_status,first_retrieved_at_utc,
    source_release_timestamp,source_observations=0 as empty_source_response,
    case when source_observations=0 then 'no_observations_returned_not_zero_market_activity'
         else 'native_observations_available' end as coverage_state
from {{ ref('stg_source_snapshots') }}
