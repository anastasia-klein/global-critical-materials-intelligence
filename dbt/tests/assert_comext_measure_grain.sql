select source_release,reporter_native,partner_native,product_code,reference_year,flow_code,indicator,count(*) as records
from {{ ref('stg_comext_cells') }}
group by all
having count(*)>1
