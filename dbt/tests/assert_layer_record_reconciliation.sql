with counts as (
 select
   (select count(*) from {{ source('bronze','active_records') }} where source='iea') as raw_iea,
   (select count(*) from {{ ref('stg_iea_observations') }}) as staged_iea,
   (select count(*) from {{ source('bronze','active_records') }} where source='comext') as raw_trade,
   (select count(*) from {{ ref('stg_comext_cells') }}) as staged_trade,
   (select count(*) from {{ ref('stg_iea_observations') }} where category='Material demand') as staged_demand,
   (select count(*) from {{ ref('stg_iea_observations') }} where category='Material supply') as staged_supply,
   (select count(*) from {{ ref('fct_material_demand') }}) as fact_demand,
   (select count(*) from {{ ref('fct_material_supply') }}) as fact_supply,
   (select sum(source_observations) from {{ ref('fct_ingestion_coverage') }}) as covered_records,
   (select count(*) from {{ source('bronze','active_records') }}) as raw_all
)
select * from counts
where raw_iea!=staged_iea or raw_trade!=staged_trade
   or staged_demand!=fact_demand or staged_supply!=fact_supply
   or covered_records!=raw_all or raw_iea=0 or raw_trade=0
