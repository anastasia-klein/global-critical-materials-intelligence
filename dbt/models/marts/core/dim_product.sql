select distinct product_key,material_key,product_code,product_label,reference_year as classification_reference_year,
    native_classification,product_form,definition_scope,quantity_basis,classification_status
from {{ ref('int_trade_flows') }}
