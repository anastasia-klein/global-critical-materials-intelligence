with restored as (
    select value_record_id as record_id,trade_value_eur as native_value,value_source_status as source_status
    from {{ ref('fct_trade_flows') }} where value_record_id is not null
    union all
    select quantity_record_id,native_quantity_100kg,quantity_source_status
    from {{ ref('fct_trade_flows') }} where quantity_record_id is not null
    union all
    select supplementary_record_id,supplementary_quantity,supplementary_source_status
    from {{ ref('fct_trade_flows') }} where supplementary_record_id is not null
)
select coalesce(s.record_id,r.record_id) as record_id
from {{ ref('stg_comext_cells') }} s full outer join restored r using(record_id)
where s.record_id is null or r.record_id is null or s.native_value is distinct from r.native_value
   or s.source_status is distinct from r.source_status
