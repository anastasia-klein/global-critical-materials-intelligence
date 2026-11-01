select distinct {{ sk(['geography_id']) }} as geography_key,
    geography_id,canonical_name,iso_alpha2,iso_alpha3,entity_type
from {{ ref('geography_mapping') }}
