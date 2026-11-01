select {{ sk(['v.dependency_key','m.dependency_key']) }} as sensitivity_key,
    v.source_selection_key,v.material_key,v.product_key,v.reporter_key,v.reference_year,v.snapshot_key,
    v.hhi_lower as value_hhi_lower,v.hhi_upper as value_hhi_upper,
    m.hhi_lower as mass_hhi_lower,m.hhi_upper as mass_hhi_upper,
    m.hhi_lower-v.hhi_upper as mass_minus_value_hhi_lower,
    m.hhi_upper-v.hhi_lower as mass_minus_value_hhi_upper,
    v.largest_named_partner_key as value_largest_named_partner_key,
    m.largest_named_partner_key as mass_largest_named_partner_key,
    case when v.denominator_status!='valid_source_denominator' or m.denominator_status!='valid_source_denominator' then 'unavailable_denominator'
         when m.hhi_lower>v.hhi_upper then 'mass_more_concentrated_under_all_residual_allocations'
         when v.hhi_lower>m.hhi_upper then 'value_more_concentrated_under_all_residual_allocations'
         else 'ordering_not_resolved_by_bounds' end as sensitivity_result,
    case when v.named_leader_guaranteed and m.named_leader_guaranteed then v.largest_named_partner_key=m.largest_named_partner_key end as same_guaranteed_leading_partner,
    v.denominator_scope||'_same_product_year_separate_value_and_mass' as sensitivity_scope,
    case when v.product_code='28220000' and v.reporter_key=(select geography_key from {{ ref('dim_geography') }} where geography_id='ISO:DEU') then 'G04_external_cobalt_quantity_discrepancy_unresolved'
         else 'not_independently_cross_source_reconciled' end as external_reconciliation_caveat
from {{ ref('mart_country_material_dependency') }} v
join {{ ref('mart_country_material_dependency') }} m
on v.product_key=m.product_key and v.reporter_key=m.reporter_key and v.snapshot_key=m.snapshot_key
and v.source_selection_key=m.source_selection_key
where v.measure_basis='trade_value' and m.measure_basis='product_mass'
