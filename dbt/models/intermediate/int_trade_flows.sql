with measurements as (
    select s.*,p.family_id,p.product_form,p.definition_scope,p.basis,p.concordance_status,
        r.geography_id as reporter_id,r.mapping_status as reporter_mapping_status,
        g.geography_id as partner_id,g.entity_type as partner_entity_type,g.mapping_status as partner_mapping_status
    from {{ ref('stg_comext_cells') }} s
    left join {{ ref('trade_product_mapping') }} p using(product_code)
    left join {{ ref('geography_mapping') }} r on r.source='comext' and r.native_id=s.reporter_native
    left join {{ ref('geography_mapping') }} g on g.source='comext' and g.native_id=s.partner_native
), pivoted as (
    select snapshot_id,request_id,payload_sha256,source_release,reporter_native,partner_native,
        reporter_id,partner_id,partner_entity_type,reporter_mapping_status,partner_mapping_status,
        product_code,product_label,native_classification,classification_status,reference_year,flow_code,
        family_id,product_form,definition_scope,basis,concordance_status,evidence_class,
        min(ingested_at_utc) as ingested_at_utc,
        max(case when indicator='VALUE_IN_EUROS' then native_value end) as trade_value_eur,
        max(case when indicator='QUANTITY_IN_100KG' then native_value end) as native_quantity_100kg,
        max(case when indicator='SUPPLEMENTARY_QUANTITY' then native_value end) as supplementary_quantity,
        max(case when indicator='VALUE_IN_EUROS' then record_id end) as value_record_id,
        max(case when indicator='QUANTITY_IN_100KG' then record_id end) as quantity_record_id,
        max(case when indicator='SUPPLEMENTARY_QUANTITY' then record_id end) as supplementary_record_id,
        max(case when indicator='VALUE_IN_EUROS' then source_status end) as value_source_status,
        max(case when indicator='QUANTITY_IN_100KG' then source_status end) as quantity_source_status,
        max(case when indicator='SUPPLEMENTARY_QUANTITY' then source_status end) as supplementary_source_status,
        count(*) as source_cell_count
    from measurements
    group by all
)
select *,
    native_quantity_100kg * 0.1 as product_mass_tonnes,
    'traded_product_mass' as quantity_basis,
    'source_100kg_scaled_to_tonnes' as conversion_status,
    {{ sk(['snapshot_id','reporter_native','partner_native','product_code','reference_year','flow_code']) }} as trade_flow_key,
    {{ sk(['family_id']) }} as material_key,
    {{ sk(['native_classification','product_code','reference_year']) }} as product_key,
    {{ sk(['reporter_id']) }} as reporter_key,
    {{ sk(['partner_id']) }} as partner_key,
    {{ sk(['reference_year']) }} as period_key,
    {{ sk(["'comext'",'source_release']) }} as source_release_key,
    case when reporter_id is null or partner_id is null or family_id is null then 'unmapped_reference'
         else 'structurally_valid_with_semantic_gates' end as quality_state
from pivoted
