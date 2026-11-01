"""One reporter/product/year, native flow and partner categories; no sparse zero filling."""
from collections import defaultdict
import math
from ..common import ContractError
from ..validators.jsonstat import axes, cells

DIMENSIONS = {'freq','reporter','partner','product','flow','indicators','time'}
AGGREGATES = {'WORLD','EXT_EA','EXT_EA21','EXT_EU','EXT_EU27_2020','INT_EA','INT_EA21','INT_EU','INT_EU27_2020'}
INDICATORS = {'VALUE_IN_EUROS','QUANTITY_IN_100KG','SUPPLEMENTARY_QUANTITY'}


def validate(data, spec):
    contract = spec['contract']
    if not isinstance(data, dict) or data.get('class') != 'dataset' or data.get('version') != '2.0':
        raise ContractError('Expected a synchronous JSON-stat 2.0 dataset, not an async/error envelope')
    if data.get('source') != 'ESTAT' or data.get('extension', {}).get('id') != 'DS-045409':
        raise ContractError('Wrong Comext source/dataset')
    ids, sizes, categories = axes(data)
    if set(ids) != DIMENSIONS:
        raise ContractError('Unreviewed Comext dimensions')
    for name, expected in contract['coordinates'].items():
        if categories[name] != [expected]:
            raise ContractError(f'Comext {name} does not match requested slice')
    if set(categories['flow']) != {'1','2'}:
        raise ContractError('Import/export categories need review before acquisition')
    if set(categories['indicators']) != INDICATORS:
        raise ContractError('Unreviewed Comext indicators')
    if any(len(code) != 2 and code not in AGGREGATES for code in categories['partner']):
        raise ContractError('Unreviewed aggregate or geography code; inspect before partner reconciliation')
    label = data['dimension']['product']['category'].get('label', {}).get(contract['coordinates']['product'], '')
    if any(token.lower() not in label.lower() for token in contract['label_contains']):
        raise ContractError(f'Product label does not match inspected form: {label}')
    if not isinstance(data.get('updated'), str):
        raise ContractError('Comext release timestamp is absent')
    observations, counts = cells(data)
    for _, observation in observations:
        observation['source_updated'] = data['updated']
        observation['dataset'] = 'DS-045409'
    # Totals are checked separately, never summed together with their own components.
    grouped = defaultdict(dict)
    warnings, coverage = [], []
    for _, record in observations:
        coord = record['coordinates']
        grouped[(coord['flow'],coord['indicators'])][coord['partner']] = record
        coverage.append({'source':'comext','source_release':data['updated'],
                         'material_or_product':coord['product'],'product_label':label,
                         'material_family_context':contract['material_context'],'measure':coord['indicators'],
                         'stage_or_flow':coord['flow'],'year':int(coord['time']),'geography':coord['reporter'],
                         'partner':coord['partner'],
                         'partner_kind':'aggregate' if coord['partner'] in AGGREGATES else 'native_nonaggregate_unmapped',
                         'scenario':'not_applicable','case':'not_applicable','unit':coord['indicators'],
                         'basis':'traded_product_not_contained_metal','native_observations':1,
                         'value_missing':record['value'] is None,'source_status':record['status'],
                         'classification_revision_status':'reference_year_queried_concordance_not_verified',
                         'publication_eligibility':'reviewed_EU_reporter_attributed_reuse',
                         'metric_readiness':'source_native_product_only; longitudinal_mapping_and_partner_review_pending'})
    reconciliation = []
    for (flow, indicator), partners in sorted(grouped.items()):
        total = partners.get('WORLD', {}).get('value')
        components = [record['value'] for partner, record in partners.items()
                      if partner not in AGGREGATES and record['value'] is not None]
        component_sum = math.fsum(components)
        residual = None if total is None else total - component_sum
        reconciliation.append({'flow':flow,'indicator':indicator,'world_value':total,
                               'native_nonaggregate_sum':component_sum,'world_minus_components':residual,
                               'nonaggregate_cells':len(components),
                               'status':'not_testable_missing_world' if total is None else
                                        'matches_at_source_precision' if abs(residual) <= max(1e-6,abs(total)*1e-9) else 'unresolved_residual'})
    if any(row['status'] != 'matches_at_source_precision' for row in reconciliation):
        warnings.append('Some native partner totals need reconciliation; no supplier denominator promoted')
    if any(record['status'] is not None for _, record in observations):
        warnings.append('Source observation statuses retained; semantic review required')
    return observations, dict(counts, observations=len(observations), source_release=data['updated'],
                              structure=data['extension'].get('datastructure'), product_label=label,
                              native_partner_categories=len(categories['partner']),
                              flows_present=sorted({record['coordinates']['flow'] for _,record in observations}),
                              warnings=warnings, coverage=coverage, reconciliation=reconciliation)
