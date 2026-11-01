select {{ sk(['source','source_release']) }} as source_release_key,
    source,source_release,source_release_timestamp,licence_name,licence_url,
    string_agg(distinct publication_status,' | ' order by publication_status) as publication_status,
    case when source_release_timestamp is null then 'source_timestamp_not_supplied' else 'source_timestamp_available' end as source_timestamp_status
from {{ ref('stg_source_snapshots') }}
group by source,source_release,source_release_timestamp,licence_name,licence_url
