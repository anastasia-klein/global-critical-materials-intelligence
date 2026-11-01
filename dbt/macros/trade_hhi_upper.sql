{% macro trade_hhi_upper(named_squared_amount, largest_named_amount, residual_amount, world_total) -%}
(({{ named_squared_amount }}) + 2*({{ largest_named_amount }})*({{ residual_amount }}) + pow(({{ residual_amount }}),2)) / pow(({{ world_total }}),2)
{%- endmacro %}
