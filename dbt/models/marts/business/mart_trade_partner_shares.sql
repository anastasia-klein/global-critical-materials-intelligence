select {{ sk(['m.trade_flow_key','m.measure_basis','c.source_selection_key']) }} as partner_share_key,
    c.source_selection_key,m.material_key,m.product_key,m.reporter_key,m.partner_key,m.period_key,
    m.flow_key,m.source_release_key,m.snapshot_key,m.reference_year,m.product_code,m.flow_name,
    m.partner_name,m.partner_iso_alpha2,m.partner_entity_type,m.measure_basis,m.measure_unit,
    m.measure_value,m.source_status,m.source_record_id,m.evidence_class,d.reference_total,
    d.unallocated_amount,d.denominator_scope,d.denominator_status,m.classification_status,
    case when d.denominator_status='valid_source_denominator' then m.measure_value/d.reference_total end as partner_share,
    case when m.measure_value is not null then row_number() over(partition by m.product_key,m.reporter_key,m.flow_key,m.snapshot_key,m.measure_basis order by m.measure_value desc nulls last,m.partner_key) end::integer as reported_partner_rank
from {{ ref('int_trade_measures') }} m
join {{ ref('int_trade_denominators') }} d using(product_key,reporter_key,flow_key,snapshot_key,measure_basis)
cross join {{ ref('int_analysis_context') }} c
where m.partner_scope_eligible and m.partner_entity_type in ('country_or_territory','geopolitical_area')
