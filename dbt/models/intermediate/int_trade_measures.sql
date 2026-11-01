select f.trade_flow_key,f.material_key,f.product_key,f.reporter_key,f.partner_key,f.period_key,
    f.flow_key,f.source_release_key,f.snapshot_key,f.reference_year,f.partner_entity_type,
    r.geography_id as reporter_id,g.geography_id as partner_geography_id,
    case when r.geography_id='COMEXT:EU27_2020' then 'EU27_2020_extra_EU' else 'national_all_partners' end as trade_scope,
    case when r.geography_id='COMEXT:EU27_2020' then 'COMEXT:EXT_EU27_2020' else 'WORLD' end as denominator_partner_id,
    not (r.geography_id='COMEXT:EU27_2020' and coalesce(g.iso_alpha2,'') in ({{ eu27_member_codes() }})) as partner_scope_eligible,
    f.evidence_class,p.product_code,p.classification_status,g.canonical_name as partner_name,
    g.iso_alpha2 as partner_iso_alpha2,d.flow_name,
    m.measure_basis,m.measure_unit,m.measure_value,m.source_status,m.source_record_id
from {{ ref('fct_trade_flows') }} f
join {{ ref('dim_product') }} p using(product_key)
join {{ ref('dim_geography') }} g on f.partner_key=g.geography_key
join {{ ref('dim_trade_flow') }} d using(flow_key)
join {{ ref('dim_geography') }} r on f.reporter_key=r.geography_key
cross join lateral (values
    ('trade_value','EUR',f.trade_value_eur,f.value_source_status,f.value_record_id),
    ('product_mass','tonnes_product',f.product_mass_tonnes,f.quantity_source_status,f.quantity_record_id)
) m(measure_basis,measure_unit,measure_value,source_status,source_record_id)
