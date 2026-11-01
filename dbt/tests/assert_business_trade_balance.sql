select trade_analysis_key from {{ ref('mart_european_trade_analysis') }}
where (valid_flow_count=2 and (imports is null or exports is null or trade_balance is null))
or abs(trade_balance-(exports-imports))>1e-8
or (valid_flow_count!=2 and trade_balance is not null)
