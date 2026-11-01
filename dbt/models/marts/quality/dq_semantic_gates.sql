select 'iea' as source,'native_equivalent_basis_and_baseline_status_unverified' as gate,
    count(*) as affected_records,'preserve_status_no_physical_gap' as required_policy
from {{ ref('stg_iea_observations') }}
union all
select 'comext','annual_classification_concordance_unverified',count(*),'native_product_year_only'
from {{ ref('fct_trade_flows') }}
union all
select 'comext','source_flags_not_equivalent_to_certified_actual',count(*),'preserve_native_status'
from {{ ref('stg_comext_cells') }}
