with ranked as (
select *,row_number() over(partition by material_definition_key,period_key,scenario_key,stage_key,snapshot_key order by supply_share desc nulls last,geography_key) as r
from {{ ref('mart_supply_country_shares') }} where geography_entity_type='country_or_territory'
), named as (
select material_definition_key,period_key,scenario_key,stage_key,snapshot_key,
    sum(pow(supply_share,2) order by geography_key) as named_hhi,max(supply_share) as largest_named_share,
    sum(supply_share order by geography_key) filter(where r<=2) as named_top2,sum(supply_share order by geography_key) filter(where r<=3) as named_top3,
    sum(supply_share order by geography_key) filter(where r<=4) as named_top4,sum(supply_share order by geography_key) filter(where r<=5) as named_top5,
    count(*)::integer as named_country_count
from ranked group by all
), panels as (
select source_selection_key,material_key,material_definition_key,period_key,scenario_key,stage_key,
    source_release_key,snapshot_key,reference_year,quantity_basis,evidence_class,denominator_scope,
    max(panel_output_tonnes) as panel_output_tonnes,
    max(invalid_panel_observations)::integer as invalid_panel_observations,
    sum(supply_share order by geography_key) filter(where geography_entity_type='residual') as residual_share
from {{ ref('mart_supply_country_shares') }} group by all
)
select {{ sk(['material_definition_key','period_key','scenario_key','stage_key','snapshot_key','source_selection_key']) }} as concentration_key,
    p.*,n.named_country_count,n.largest_named_share,
    n.named_hhi as hhi_lower,n.named_hhi+pow(coalesce(p.residual_share,0),2) as hhi_upper,
    n.named_top3 as top3_share_lower,
    greatest(n.named_top3,coalesce(n.named_top2,0)+coalesce(p.residual_share,0)) as top3_share_upper,
    n.named_top5 as top5_share_lower,
    greatest(n.named_top5,coalesce(n.named_top4,0)+coalesce(p.residual_share,0)) as top5_share_upper,
    case when p.panel_output_tonnes is null or p.panel_output_tonnes<=0 or invalid_panel_observations>0 then 'unavailable_invalid_panel'
         when coalesce(residual_share,0)>0 then 'bounded_opaque_residual' else 'exact_captured_panel' end as metric_status,
    'HHI_0_to_1' as hhi_unit,'expected_output_not_capacity' as supply_measure_kind
from panels p left join named n using(material_definition_key,period_key,scenario_key,stage_key,snapshot_key)
