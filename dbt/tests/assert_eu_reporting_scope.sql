-- Bloc external totals and national all-partner totals must retain distinct scopes.
select cast(d.product_key as varchar) as row_key
from {{ ref('int_trade_denominators') }} d
join {{ ref('dim_geography') }} r on d.reporter_key=r.geography_key
where (r.geography_id='COMEXT:EU27_2020' and
 (d.denominator_partner_id!='COMEXT:EXT_EU27_2020' or d.denominator_scope!='source_EXT_EU27_2020_external_partners_only'))
 or (r.geography_id!='COMEXT:EU27_2020' and
 (d.denominator_partner_id!='WORLD' or d.denominator_scope!='source_World_all_partners_including_intra_EU'))
union all
select p.partner_share_key
from {{ ref('mart_trade_partner_shares') }} p
join {{ ref('dim_geography') }} r on p.reporter_key=r.geography_key
join {{ ref('dim_geography') }} g on p.partner_key=g.geography_key
where r.geography_id='COMEXT:EU27_2020' and g.iso_alpha2 in ({{ eu27_member_codes() }})
union all
select t.trade_analysis_key
from {{ ref('mart_european_trade_analysis') }} t
join {{ ref('dim_geography') }} r on t.reporter_key=r.geography_key
where (r.geography_id='COMEXT:EU27_2020' and t.denominator_scope!='source_EXT_EU27_2020_external_partners_only')
 or (r.geography_id!='COMEXT:EU27_2020' and t.denominator_scope!='source_World_all_partners_including_intra_EU')
