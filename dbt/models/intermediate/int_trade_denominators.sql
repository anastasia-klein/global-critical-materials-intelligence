with totals as (
select material_key,product_key,reporter_key,period_key,flow_key,source_release_key,snapshot_key,
    reference_year,product_code,classification_status,flow_name,measure_basis,measure_unit,trade_scope,denominator_partner_id,
    count(*) filter(where partner_geography_id=denominator_partner_id)::integer as denominator_row_count,
    max(measure_value) filter(where partner_geography_id=denominator_partner_id) as reference_total,
    coalesce(sum(measure_value order by trade_flow_key) filter(where partner_scope_eligible and partner_entity_type in ('country_or_territory','geopolitical_area')),0) as named_partner_total,
    case when trade_scope='EU27_2020_extra_EU' then null else coalesce(sum(measure_value order by trade_flow_key) filter(where partner_entity_type='special_trade_partner'),0) end as reported_special_partner_total,
    count(*) filter(where partner_scope_eligible and partner_entity_type in ('country_or_territory','geopolitical_area') and measure_value is null)::integer as missing_named_measure_count,
    count(*) filter(where source_status is not null)::integer as flagged_measure_count,
    count(*) filter(where measure_value<0)::integer as negative_measure_count
from {{ ref('int_trade_measures') }} group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
), checked as (
select *,reference_total-named_partner_total as native_reconciliation_delta,
    case when measure_basis='trade_value' then greatest(0.01,abs(reference_total)*1e-9)
         else greatest(1e-6,abs(reference_total)*1e-9) end as numeric_tolerance
from totals
)
select *,case when denominator_row_count!=1 or reference_total is null then 'unavailable_reference_total'
              when reference_total<=0 then 'unavailable_nonpositive_denominator'
              when negative_measure_count>0 or native_reconciliation_delta < -numeric_tolerance then 'unavailable_reconciliation'
              else 'valid_source_denominator' end as denominator_status,
    case when abs(native_reconciliation_delta)<=numeric_tolerance then 0.0
         when native_reconciliation_delta >= -numeric_tolerance then greatest(native_reconciliation_delta,0) end as unallocated_amount,
    case when trade_scope='EU27_2020_extra_EU' then 'source_EXT_EU27_2020_external_partners_only' else 'source_World_all_partners_including_intra_EU' end as denominator_scope
from checked
