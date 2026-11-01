with ranked as (
select *,row_number() over(partition by product_key,reporter_key,flow_key,snapshot_key,measure_basis order by measure_value desc nulls last,partner_key) as r
from {{ ref('int_trade_measures') }} where partner_scope_eligible and partner_entity_type in ('country_or_territory','geopolitical_area')
), summary as (
select product_key,reporter_key,flow_key,snapshot_key,measure_basis,
    sum(pow(measure_value,2) order by partner_key) as named_squared_amount,
    max(measure_value) as largest_named_amount,
    max(measure_value) filter(where r=2) as second_named_amount,
    arg_max(partner_key,struct_pack(amount:=coalesce(measure_value,-1),tie:=partner_key)) as largest_named_partner_key,
    coalesce(sum(measure_value order by partner_key) filter(where r<=2),0) as named_top2,
    coalesce(sum(measure_value order by partner_key) filter(where r<=3),0) as named_top3,
    coalesce(sum(measure_value order by partner_key) filter(where r<=4),0) as named_top4,
    coalesce(sum(measure_value order by partner_key) filter(where r<=5),0) as named_top5,
    count(*)::integer as reported_named_partner_count
from ranked group by all
), metrics as (
select d.*,s.named_squared_amount,s.largest_named_amount,s.second_named_amount,s.largest_named_partner_key,
    coalesce(s.reported_named_partner_count,0)::integer as reported_named_partner_count,
    s.named_top2,s.named_top3,s.named_top4,s.named_top5,
    d.denominator_status='valid_source_denominator' as eligible
from {{ ref('int_trade_denominators') }} d
left join summary s using(product_key,reporter_key,flow_key,snapshot_key,measure_basis)
where flow_name='Import'
)
select {{ sk(['product_key','reporter_key','snapshot_key','measure_basis','c.source_selection_key']) }} as dependency_key,
    c.source_selection_key,material_key,product_key,reporter_key,period_key,source_release_key,snapshot_key,
    reference_year,product_code,measure_basis,measure_unit,reference_total,named_partner_total,
    reported_special_partner_total,unallocated_amount,native_reconciliation_delta,numeric_tolerance,
    missing_named_measure_count,flagged_measure_count,reported_named_partner_count,denominator_scope,
    denominator_status,classification_status,largest_named_partner_key,
    case when eligible then unallocated_amount/reference_total end as unallocated_share,
    case when eligible then coalesce(named_squared_amount,0)/pow(reference_total,2) end as hhi_lower,
    case when eligible then {{ trade_hhi_upper('coalesce(named_squared_amount,0)','coalesce(largest_named_amount,0)','unallocated_amount','reference_total') }} end as hhi_upper,
    case when eligible then coalesce(largest_named_amount,0)/reference_total end as top_supplier_share_lower,
    case when eligible then least(reference_total,coalesce(largest_named_amount,0)+unallocated_amount)/reference_total end as top_supplier_share_upper,
    case when eligible then coalesce(named_top3,0)/reference_total end as top3_share_lower,
    case when eligible then least(reference_total,coalesce(named_top3,0)+unallocated_amount)/reference_total end as top3_share_upper,
    case when eligible then coalesce(named_top5,0)/reference_total end as top5_share_lower,
    case when eligible then least(reference_total,coalesce(named_top5,0)+unallocated_amount)/reference_total end as top5_share_upper,
    case when eligible then coalesce(largest_named_amount,0)>=coalesce(second_named_amount,0)+unallocated_amount end as named_leader_guaranteed,
    'historical_trade_statistics_status_unverified' as evidence_class,
    cast(null as double) as import_dependency,
    'unavailable_compatible_domestic_output_and_consumption_denominator' as import_dependency_status
from metrics cross join {{ ref('int_analysis_context') }} c
