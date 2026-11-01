with metrics as (
select dependency_key as row_key,hhi_lower,hhi_upper,top3_share_lower,top3_share_upper,top5_share_lower,top5_share_upper from {{ ref('mart_country_material_dependency') }} where denominator_status='valid_source_denominator'
union all
select concentration_key,hhi_lower,hhi_upper,top3_share_lower,top3_share_upper,top5_share_lower,top5_share_upper from {{ ref('mart_global_supply_concentration') }} where metric_status!='unavailable_invalid_panel'
)
select * from metrics where hhi_lower is null or hhi_upper is null or hhi_lower< -1e-10 or hhi_upper>1+1e-10 or hhi_lower>hhi_upper+1e-10
or top3_share_lower< -1e-10 or top5_share_upper>1+1e-10 or top3_share_lower>top3_share_upper+1e-10 or top5_share_lower>top5_share_upper+1e-10
or top5_share_lower<top3_share_lower-1e-10 or top5_share_upper<top3_share_upper-1e-10
