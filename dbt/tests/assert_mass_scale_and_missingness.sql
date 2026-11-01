select trade_flow_key as observation_key,'comext' as source
from {{ ref('fct_trade_flows') }}
where (product_mass_tonnes is null)!=(native_quantity_100kg is null)
   or abs(product_mass_tonnes*1000.0-native_quantity_100kg*100.0)>greatest(1e-8,abs(native_quantity_100kg*100.0)*1e-12)
   or quantity_basis!='traded_product_mass'
union all
select demand_key,'iea_demand'
from {{ ref('fct_material_demand') }}
where (demand_native_scope_tonnes is null)!=(native_demand is null)
   or abs(demand_native_scope_tonnes/1000.0-native_demand)>greatest(1e-8,abs(native_demand)*1e-12)
   or quantity_basis!='unverified_native_equivalent'
union all
select supply_key,'iea_supply'
from {{ ref('fct_material_supply') }}
where (supply_native_scope_tonnes is null)!=(native_supply is null)
   or abs(supply_native_scope_tonnes/1000.0-native_supply)>greatest(1e-8,abs(native_supply)*1e-12)
   or quantity_basis!='unverified_native_equivalent'
