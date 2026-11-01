select min(risk_component_key) as row_key
from {{ ref('mart_material_supply_risk') }} group by source_selection_key,scope_kind,scope_key,geography_key,scenario_key,reference_year,component_name,comparison_contract_key
having count(*)>1
union all
select risk_component_key from {{ ref('mart_material_supply_risk') }}
where composite_risk_score is not null or availability_reason is null
or (availability='unavailable' and (component_value is not null or component_lower is not null or component_upper is not null))
or (availability='available' and (component_value is null or component_lower is null or component_upper is null))
or (availability='bounded' and (component_value is not null or component_lower is null or component_upper is null))
or component_lower>component_upper+1e-10
or (availability='available' and (abs(component_value-component_lower)>1e-10 or abs(component_value-component_upper)>1e-10))
or (component_name in ('import_dependency','capacity_growth','physical_supply_demand_gap') and availability!='unavailable')
