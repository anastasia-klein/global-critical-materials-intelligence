with expected as (
select s.snapshot_id,cast(y.value as integer) as reference_year,st.stage_key
from {{ source('bronze','active_snapshots') }} s
cross join json_each(s.manifest,'$.request.contract.accepted.year') y
cross join json_each(s.manifest,'$.request.contract.accepted.flow') f
join {{ ref('dim_supply_chain_stage') }} st on st.stage_name=json_extract_string(f.value,'$')
where s.source='iea' and s.manifest->>'$.request.contract.equals.category'='Material supply'
and cast(s.manifest->>'$.validation.observations' as integer)=0
)
select e.* from expected e left join {{ ref('mart_material_supply_risk') }} r
on e.snapshot_id=r.lineage_snapshot_key and e.reference_year=r.reference_year and e.stage_key=r.stage_key
and r.component_name='supply_geographic_hhi'
where r.risk_component_key is null or r.availability!='unavailable' or r.component_value is not null
or r.availability_reason!='no_observations_returned_not_zero_output'
