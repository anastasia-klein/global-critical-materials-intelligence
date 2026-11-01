"""Inspected IEA GCMO2026 public explorer contracts; source semantics stay native."""
from collections import Counter
from ..common import ContractError, number

KEY = ['mcm','scenario','category','unit','region','product','year','material','case','flow']
FIELDS = set(KEY + ['value'])


def validate(data, spec):
    contract = spec['contract']
    if not isinstance(data, list):
        raise ContractError('Expected an array, not an API error or pagination envelope')
    if not data and not contract.get('allow_empty', False):
        raise ContractError('Required IEA slice unexpectedly empty')
    seen, warnings, observations = set(), set(), []
    for index, record in enumerate(data):
        if not isinstance(record, dict) or not FIELDS <= set(record):
            raise ContractError('Missing IEA fields')
        for field in KEY:
            expected_type = int if field == 'year' else str
            if isinstance(record[field], bool) or not isinstance(record[field], expected_type):
                raise ContractError(f'Unexpected IEA type: {field}')
        if record['value'] is not None and not number(record['value']):
            raise ContractError('Invalid IEA value')
        for field, expected in contract['equals'].items():
            if record[field] != expected:
                raise ContractError(f'IEA {field} does not match query contract')
        for field, expected in contract['accepted'].items():
            if record[field] not in expected:
                raise ContractError(f'Unreviewed IEA {field}: {record[field]}')
        key = tuple(record[field] for field in KEY)
        if key in seen:
            raise ContractError('Duplicate IEA natural identity')
        seen.add(key)
        if set(record) != FIELDS:
            warnings.add('Additive fields preserved; schema extension requires review')
        if record['value'] is None:
            warnings.add('Missing source values retained as null')
        observations.append((f'/{index}', record))
    coverage = Counter((record['mcm'],record['material'],record['category'],record['flow'],
                        record['year'],record['region'],record['scenario'],record['case'],record['unit']) for record in data)
    rows = [{'source': 'iea', 'source_release': key[0], 'material_or_product': key[1],
             'measure': key[2], 'stage_or_flow': key[3], 'year': key[4], 'geography': key[5],
             'scenario': key[6], 'case': key[7], 'unit': key[8], 'basis': 'native_equivalent_basis_unverified',
             'native_observations': count, 'historical_status': 'baseline_status_unverified' if key[4] == 2025 else 'scenario_projection',
             'publication_eligibility': 'attribution_required',
             'metric_readiness': 'native_levels_candidate; basis_and_status_review_required; no_physical_gap_or_capacity'}
            for key, count in sorted(coverage.items())]
    expected_years = set(contract['accepted']['year'])
    observed_years = {record['year'] for record in data}
    missing = sorted(expected_years - observed_years) if data else []
    if missing:
        warnings.add(f'Unreturned reference years: {missing}')
    return observations, {'source_release': contract['equals']['mcm'], 'observations': len(data),
                          'natural_keys_unique': True, 'warnings': sorted(warnings),
                          'basis_status': 'not_independently_verified',
                          'coverage': rows, 'native_product_labels': sorted({record['product'] for record in data})}
