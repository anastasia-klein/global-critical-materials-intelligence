"""JSON-stat cells and statuses decoded from native dimension positions."""
from math import prod
from ..common import ContractError, number


def axes(data):
    ids, sizes = data.get('id'), data.get('size')
    if not isinstance(ids, list) or not isinstance(sizes, list) or len(ids) != len(sizes) or len(set(ids)) != len(ids):
        raise ContractError('Invalid dimension layout')
    if any(isinstance(size, bool) or not isinstance(size, int) or size < 0 for size in sizes):
        raise ContractError('Invalid dimension sizes')
    result = {}
    for name, size in zip(ids, sizes):
        category = data['dimension'][name]['category']
        index = category['index']
        index = {code: position for position, code in enumerate(index)} if isinstance(index, list) else index
        if not isinstance(index, dict) or len(index) != size or set(index.values()) != set(range(size)):
            raise ContractError(f'Incomplete or duplicate {name} positions')
        result[name] = [None] * size
        for code, position in index.items():
            result[name][position] = code
    return ids, sizes, result


def sparse_map(values, total, name, retain_null=False):
    if values is None:
        return {}
    if isinstance(values, list):
        if len(values) != total:
            raise ContractError(f'Dense {name} size mismatch')
        return {i: value for i, value in enumerate(values) if value is not None or retain_null}
    if not isinstance(values, dict):
        raise ContractError(f'Invalid {name} encoding')
    result = {}
    for key, value in values.items():
        try:
            offset = int(key)
        except (ValueError, TypeError) as exc:
            raise ContractError(f'Invalid {name} offset') from exc
        if str(offset) != str(key) or not 0 <= offset < total:
            raise ContractError(f'Out-of-range {name} offset')
        if value is not None or retain_null:
            result[offset] = value
    return result


def cells(data):
    ids, sizes, categories = axes(data)
    total = prod(sizes)
    values = sparse_map(data.get('value'), total, 'value', retain_null=True)
    statuses = sparse_map(data.get('status'), total, 'status')
    if any(value is not None and not number(value) for value in values.values()):
        raise ContractError('Non-finite or non-numeric JSON-stat value')
    observations = []
    for offset in sorted(set(values) | set(statuses)):
        remaining, coordinates = offset, {}
        for name, size in reversed(list(zip(ids, sizes))):
            position = remaining % size
            remaining //= size
            coordinates[name] = categories[name][position]
        coordinates = {name: coordinates[name] for name in ids}
        labels = {name: data['dimension'][name]['category'].get('label', {}).get(code) for name, code in coordinates.items()}
        record = {'coordinates': coordinates, 'labels': labels,
                  'value': values.get(offset), 'status': statuses.get(offset), 'source_offset': offset}
        if record['value'] is None:
            record['missingness'] = 'explicit_null' if offset in values else 'status_without_value'
        observations.append((f'/value/{offset}' if offset in values else f'/status/{offset}', record))
    return observations, {'potential_cells': total, 'numeric_cells': sum(value is not None for value in values.values()),
                          'explicit_null_cells': sum(value is None for value in values.values()),
                          'status_only_cells': len(set(statuses) - set(values)),
                          'unreturned_cells': total - len(set(values) | set(statuses))}
