with imports as (
select * from {{ ref('mart_trade_partner_shares') }} where flow_name='Import'
), pairs as (
select b.product_code,b.reporter_key,b.measure_basis,b.reference_year as base_year,e.reference_year as end_year,
    b.product_key as base_product_key,e.product_key as end_product_key,
    b.snapshot_key as base_snapshot_key,e.snapshot_key as end_snapshot_key,b.source_selection_key,
    b.reference_total as base_reference_total,e.reference_total as end_reference_total
from {{ ref('mart_country_material_dependency') }} b
join {{ ref('mart_country_material_dependency') }} e
on b.product_code=e.product_code and b.reporter_key=e.reporter_key and b.measure_basis=e.measure_basis
and e.reference_year=b.reference_year+1 and b.source_selection_key=e.source_selection_key
), partners as (
select p.*,s.partner_key from pairs p join imports s on s.snapshot_key=p.base_snapshot_key and s.measure_basis=p.measure_basis
union
select p.*,s.partner_key from pairs p join imports s on s.snapshot_key=p.end_snapshot_key and s.measure_basis=p.measure_basis
)
select {{ sk(['p.source_selection_key','p.reporter_key','p.base_product_key','p.end_product_key','p.partner_key','p.measure_basis','p.base_snapshot_key','p.end_snapshot_key']) }} as composition_change_key,
    p.*,b.partner_share as base_share,e.partner_share as end_share,
    b.measure_value as base_amount,e.measure_value as end_amount,
    case when b.partner_share is not null and e.partner_share is not null then (e.partner_share-b.partner_share)*100 end as conditional_share_change_pp,
    case when b.partner_share_key is null then 'end_only_reported'
         when e.partner_share_key is null then 'base_only_reported' else 'both_reported' end as presence_pattern,
    'same_CN8_code_continuity_unverified_no_absent_partner_zero' as comparison_status,
    cast(null as double) as verified_share_change_pp,
    'not_established_query_presence_is_not_market_entry_exit' as entry_exit_status
from partners p
left join imports b on b.snapshot_key=p.base_snapshot_key and b.partner_key=p.partner_key and b.measure_basis=p.measure_basis
left join imports e on e.snapshot_key=p.end_snapshot_key and e.partner_key=p.partner_key and e.measure_basis=p.measure_basis
