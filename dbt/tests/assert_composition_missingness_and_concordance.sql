select composition_change_key from {{ ref('mart_supplier_composition_changes') }}
where verified_share_change_pp is not null or comparison_status!='same_CN8_code_continuity_unverified_no_absent_partner_zero'
or end_year!=base_year+1 or entry_exit_status!='not_established_query_presence_is_not_market_entry_exit'
or ((base_share is null or end_share is null) and conditional_share_change_pp is not null)
or (base_share is not null and end_share is not null and abs(conditional_share_change_pp-(end_share-base_share)*100)>1e-10)
