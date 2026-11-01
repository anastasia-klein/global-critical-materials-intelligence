select {{ sk(['stage_code']) }} as stage_key,stage_code,stage_name,measure_kind
from {{ ref('supply_chain_stages') }}
