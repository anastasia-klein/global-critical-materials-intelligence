select distinct {{ sk(['end_use_native']) }} as end_use_key,end_use_native as end_use_name
from {{ ref('stg_iea_observations') }} where category='Material demand'
