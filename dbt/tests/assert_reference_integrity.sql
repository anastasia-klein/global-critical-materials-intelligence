select 'noncountry_iso_assignment' as issue,geography_id as identifier
from {{ ref('dim_geography') }}
where entity_type in ('world','residual','regional_aggregate','special_trade_partner','geopolitical_area')
  and (iso_alpha2 is not null or iso_alpha3 is not null)
union all
select 'namibia_iso_lost',geography_id
from {{ ref('dim_geography') }} where geography_id='ISO:NAM' and iso_alpha2 is distinct from 'NA'
union all
select 'serbia_source_alias',native_id
from {{ ref('geography_mapping') }} where source='comext' and native_id='XS' and iso_alpha2 is distinct from 'RS'
union all
select 'opaque_residual_remapped',native_id
from {{ ref('geography_mapping') }} where source='iea' and native_id='Other countries' and entity_type!='residual'
