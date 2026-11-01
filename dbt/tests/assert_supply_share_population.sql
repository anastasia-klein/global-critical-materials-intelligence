select snapshot_key||scenario_key||stage_key||cast(reference_year as varchar) as row_key
from {{ ref('mart_supply_country_shares') }} group by all
having abs(sum(supply_share)-1)>1e-10 or count(*) filter(where geography_entity_type not in ('country_or_territory','residual'))>0
or count(*) filter(where invalid_panel_observations>0)>0
union all
select supply_share_key from {{ ref('mart_supply_country_shares') }} where supply_share is null or supply_share<0
or abs(supply_share-supply_native_scope_tonnes/panel_output_tonnes)>1e-10
