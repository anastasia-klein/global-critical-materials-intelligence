select {{ sk(['native_material']) }} as material_definition_key,
    {{ sk(['family_id']) }} as material_key,native_material,definition_scope,
    'unverified_native_equivalent' as quantity_basis
from {{ ref('iea_material_mapping') }}
