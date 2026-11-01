-- name: lithium_stage_concentration
select d.Material,c.Year,c.Stage,c.HHILower,c.HHIUpper
from Concentration c join Definitions d using(DefinitionKey)
where d.Material='Lithium' and c.Year=2030 order by c.Stage;

-- name: graphite_stage_concentration
select d.Material,c.Year,c.Stage,c.HHILower,c.HHIUpper
from Concentration c join Definitions d using(DefinitionKey)
where d.Material='Graphite' and c.Year=2030 order by c.Stage;

-- name: nickel_stage_concentration
select d.Material,c.Year,c.Stage,c.HHILower,c.HHIUpper
from Concentration c join Definitions d using(DefinitionKey)
where d.Material='Nickel' and c.Year=2030 order by c.Stage;

-- name: german_lithium_carbonate_suppliers
select p.Partner,p.Year,p.Basis,p.Share
from Partners p join Reporters r using(ReporterKey)
where r.Reporter='Germany' and p.ProductCode='28369100'
  and p.Year=2024 and p.Basis='trade_value' and p.Flow='Import'
  and p.Partner in ('Chile','Belgium','United States')
order by p.Share desc;

-- name: lithium_ev_demand_share
with scoped as (
 select o.* from Outlook o join Definitions d using(DefinitionKey)
 where d.Material='Lithium' and o.Year=2040 and o.ScenarioShort='STEPS'
), parts as (
 select max(case when SeriesKind='demand_end_use' and EndUse='Electric vehicles' then QuantityTonnes end) as EVTonnes,
 max(case when SeriesKind='demand_reported_end_uses_sum' then QuantityTonnes end) as ReturnedEndUseTonnes from scoped
)
select EVTonnes/1000 as EVKT,ReturnedEndUseTonnes/1000 as TotalKT,
 EVTonnes/nullif(ReturnedEndUseTonnes,0) as EVShare from parts;
