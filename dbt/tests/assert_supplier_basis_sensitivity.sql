select sensitivity_key from {{ ref('mart_supplier_basis_sensitivity') }}
where abs(mass_minus_value_hhi_lower-(mass_hhi_lower-value_hhi_upper))>1e-10
or abs(mass_minus_value_hhi_upper-(mass_hhi_upper-value_hhi_lower))>1e-10
or mass_minus_value_hhi_lower>mass_minus_value_hhi_upper+1e-10
or (sensitivity_result='mass_more_concentrated_under_all_residual_allocations' and mass_minus_value_hhi_lower<=0)
or (sensitivity_result='value_more_concentrated_under_all_residual_allocations' and mass_minus_value_hhi_upper>=0)
