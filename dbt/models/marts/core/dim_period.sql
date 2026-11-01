with years as (
    select reference_year from {{ ref('stg_iea_observations') }}
    union select reference_year from {{ ref('stg_comext_cells') }}
)
select {{ sk(['reference_year']) }} as period_key,reference_year,
    make_date(reference_year,1,1) as period_start,
    make_date(reference_year,12,31) as period_end,'A' as frequency
from years
