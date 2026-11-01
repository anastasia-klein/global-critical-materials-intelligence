select {{ sk(['flow_code']) }} as flow_key,flow_code,flow_name
from {{ ref('trade_flow_mapping') }}
