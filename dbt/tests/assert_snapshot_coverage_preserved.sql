select s.snapshot_id
from {{ source('bronze','active_snapshots') }} s
left join {{ ref('fct_ingestion_coverage') }} c on s.snapshot_id=c.coverage_key
left join (select snapshot_id,count(*) as records from {{ source('bronze','active_records') }} group by snapshot_id) r
  on r.snapshot_id=s.snapshot_id
where c.coverage_key is null or c.source_observations!=coalesce(r.records,0)
   or c.empty_source_response is distinct from (c.source_observations=0)
