{% macro sk(fields) -%}
md5(cast(json_array({% for field in fields %}cast({{ field }} as varchar){% if not loop.last %}, {% endif %}{% endfor %}) as varchar))
{%- endmacro %}
