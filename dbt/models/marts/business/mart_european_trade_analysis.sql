with totals as (
select material_key,product_key,reporter_key,period_key,source_release_key,snapshot_key,reference_year,
    product_code,measure_basis,measure_unit,classification_status,denominator_scope,
    max(reference_total) filter(where flow_name='Import' and denominator_row_count=1 and reference_total>=0 and negative_measure_count=0 and native_reconciliation_delta>=-numeric_tolerance) as imports,
    max(reference_total) filter(where flow_name='Export' and denominator_row_count=1 and reference_total>=0 and negative_measure_count=0 and native_reconciliation_delta>=-numeric_tolerance) as exports,
    max(unallocated_amount) filter(where flow_name='Import') as import_unallocated_amount,
    max(unallocated_amount) filter(where flow_name='Export') as export_unallocated_amount,
    sum(flagged_measure_count)::integer as flagged_measure_count,
    count(*) filter(where denominator_row_count=1 and reference_total>=0 and negative_measure_count=0 and native_reconciliation_delta>=-numeric_tolerance)::integer as valid_flow_count
from {{ ref('int_trade_denominators') }} group by all
)
select {{ sk(['product_key','reporter_key','snapshot_key','measure_basis','c.source_selection_key']) }} as trade_analysis_key,
    c.source_selection_key,t.*,exports-imports as trade_balance,
    case when valid_flow_count=2 then 'available_native_scoped_flows' else 'unavailable_missing_or_invalid_flow' end as balance_status,
    'CIF_imports_FOB_exports_not_consumption_or_origin' as interpretation_status,
    'historical_trade_statistics_status_unverified' as evidence_class
from totals t cross join {{ ref('int_analysis_context') }} c
