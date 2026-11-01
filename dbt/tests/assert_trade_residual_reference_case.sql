-- Hypothetical arithmetic only: known suppliers 60/25, unknown 15, World 100.
-- Unknown may belong to the largest known supplier: 0.75^2 + 0.25^2 = 0.625.
select 'unknown_can_augment_known_supplier' as failure
where abs({{ trade_hhi_upper('4225.0','60.0','15.0','100.0') }}-0.625)>1e-12
union all
select 'no_residual_exact_hhi' where abs({{ trade_hhi_upper('5200.0','60.0','0.0','100.0') }}-0.52)>1e-12
