-- name: copper_stage_country_shares
select d.Material,s.Year,s.Country,s.Stage,s.Share,s.EntityType
from Supply s join Definitions d using(DefinitionKey)
where d.Material='Copper' and s.Year=2025 and s.Country in ('Chile','China')
order by s.Country,s.Stage;

-- name: material_stage_concentration
select d.Material,c.Year,c.Stage,c.HHILower,c.HHIUpper
from Concentration c join Definitions d using(DefinitionKey)
where d.Material in ('Copper','Cobalt','Lithium','Nickel','Graphite','Magnet rare earth elements') and c.Year=2025
order by d.Material,c.Stage;

-- name: german_graphite_trade
select r.Reporter,t.ProductCode,t.Year,t.Basis,t.Imports,t.Exports,t.Balance
from Trade t join Reporters r using(ReporterKey)
where r.Reporter='Germany' and t.ProductCode='25041000'
  and t.Year=2024 and t.Basis='trade_value';

-- name: german_graphite_suppliers
select r.Reporter,p.ProductCode,p.Partner,p.Year,p.Basis,p.Share
from Partners p join Reporters r using(ReporterKey)
where r.Reporter='Germany' and p.ProductCode='25041000'
  and p.Year=2024 and p.Basis='trade_value' and p.Flow='Import'
  and p.Partner in ('China','Belgium','Netherlands','Brazil')
order by p.Share desc;

-- name: german_concentration_by_basis
select r.Reporter,p.ProductShort,s.Year,s.ValueHHILower,s.ValueHHIUpper,
 s.MassHHILower,s.MassHHIUpper
from Sensitivity s join Reporters r using(ReporterKey)
join Products p using(ProductCode)
where r.Reporter='Germany' and s.Year=2024
  and s.ProductCode in ('25041000','26030000')
order by p.ProductShort;

-- name: nickel_demand_scenarios
select d.Material,o.Year,o.ScenarioShort,o.QuantityTonnes/1000 as DemandKT,
 o.Growth,o.CAGR
from Outlook o join Definitions d using(DefinitionKey)
where d.Material='Nickel' and o.Year=2035
 and o.SeriesKind='demand_reported_end_uses_sum'
order by case o.ScenarioShort when 'CPS' then 1 when 'STEPS' then 2 else 3 end;

-- name: nickel_end_use_mix
with scoped as (
 select o.* from Outlook o join Definitions d using(DefinitionKey)
 where d.Material='Nickel' and o.Year=2035 and o.ScenarioShort='STEPS'
), total as (
 select max(QuantityTonnes) as ReturnedEndUseTonnes from scoped
 where SeriesKind='demand_reported_end_uses_sum'
)
select o.EndUse,o.QuantityTonnes/1000 as DemandKT,
 o.QuantityTonnes/nullif(t.ReturnedEndUseTonnes,0) as ReturnedEndUseShare
from scoped o cross join total t
where o.SeriesKind='demand_end_use'
order by o.QuantityTonnes desc;
