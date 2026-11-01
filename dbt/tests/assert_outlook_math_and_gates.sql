select outlook_key as row_key from {{ ref('mart_material_outlook') }}
where (growth_status='available_native_scope_growth' and (growth_fraction is null or cagr_fraction is null or base_year!=2025 or reference_year<=base_year
or abs(growth_fraction-(native_scope_tonnes/base_native_scope_tonnes-1))>1e-10
or abs(pow(1+cagr_fraction,reference_year-base_year)-(1+growth_fraction))>1e-9))
or (growth_status!='available_native_scope_growth' and (growth_fraction is not null or cagr_fraction is not null))
or physical_supply_demand_gap is not null or nameplate_capacity is not null
union all
select scenario_comparison_key from {{ ref('mart_scenario_comparison') }} where comparison_status='available_native_scenario_comparison'
and (relative_difference_fraction is null or abs(relative_difference_fraction-(alternative_amount/reference_amount-1))>1e-10)
