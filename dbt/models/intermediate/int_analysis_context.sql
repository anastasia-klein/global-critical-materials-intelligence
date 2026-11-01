select md5(string_agg(snapshot_id,'|' order by snapshot_id)) as source_selection_key,
    count(*)::integer as selected_snapshot_count
from {{ source('bronze','active_snapshots') }}
