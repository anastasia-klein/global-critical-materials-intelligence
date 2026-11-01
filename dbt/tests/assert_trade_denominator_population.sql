select cast(product_key as varchar) as row_key from {{ ref('int_trade_denominators') }}
where denominator_status='valid_source_denominator' and
 (denominator_row_count!=1 or reference_total<=0
 or abs(reference_total-named_partner_total-native_reconciliation_delta)>numeric_tolerance
 or abs(reference_total-named_partner_total-unallocated_amount)>numeric_tolerance)
union all
select partner_share_key from {{ ref('mart_trade_partner_shares') }}
where partner_entity_type not in ('country_or_territory','geopolitical_area')
 or partner_share< -1e-10 or partner_share>1+1e-10
 or (denominator_status='valid_source_denominator' and abs(partner_share-measure_value/reference_total)>1e-10)
 or (denominator_status!='valid_source_denominator' and partner_share is not null)
