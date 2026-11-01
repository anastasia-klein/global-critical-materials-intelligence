with outputs as (
select risk_component_key as row_key,source_selection_key,lineage_snapshot_key as snapshot_key from {{ ref('mart_material_supply_risk') }}
union all select partner_share_key,source_selection_key,snapshot_key from {{ ref('mart_trade_partner_shares') }}
union all select outlook_key,source_selection_key,snapshot_key from {{ ref('mart_material_outlook') }}
)
select o.row_key from outputs o cross join {{ ref('int_analysis_context') }} c
left join {{ ref('dim_snapshot') }} s on o.snapshot_key=s.snapshot_key
where o.source_selection_key!=c.source_selection_key or o.source_selection_key is null or s.snapshot_key is null

union all
select r.risk_component_key from {{ ref('mart_material_supply_risk') }} r
left join {{ ref('dim_material_definition') }} d on r.scope_key=d.material_definition_key
left join {{ ref('dim_product') }} p on r.scope_key=p.product_key
where (r.scope_kind='native_material_definition' and d.material_definition_key is null)
or (r.scope_kind='annual_traded_product' and p.product_key is null)
or r.scope_kind not in ('native_material_definition','annual_traded_product')
