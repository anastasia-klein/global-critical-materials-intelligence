select record_id as source_record_id,'iea' as source,quality_state as issue_code
from {{ ref('int_iea_observations') }} where quality_state!='structurally_valid_with_semantic_gates'
union all
select trade_flow_key,'comext',quality_state
from {{ ref('int_trade_flows') }} where quality_state!='structurally_valid_with_semantic_gates'
