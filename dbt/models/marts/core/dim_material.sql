select {{ sk(['family_id']) }} as material_key,family_id,material_family,definition_note
from {{ ref('material_families') }}
