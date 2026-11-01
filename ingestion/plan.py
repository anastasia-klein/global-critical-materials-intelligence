"""Build bounded requests from inspected material and product contracts."""
from urllib.parse import urlencode
from .common import loads


def build_plan(config_path, only='all', years=None, reporters=None):
    config = loads(config_path.read_bytes())
    if only not in {'all','iea','comext'}:
        raise ValueError('Unknown source selection')
    if years is not None and (only == 'iea' or not set(years) <= set(config['comext']['years'])):
        raise ValueError('Selective years must be approved Comext years and cannot be used for an IEA-only run')
    if reporters is not None and only=='iea':
        raise ValueError('Reporter selection applies to Comext, not IEA')
    result = []
    if only in {'all','iea'}:
        iea = config['iea']
        for material in iea['materials']:
            for kind in ['demand','supply']:
                category = 'Material ' + kind
                query = {'material': material, 'category': category, 'case': 'Base Case'}
                equals = {'material':material,'category':category,'mcm':iea['edition'],'case':'Base Case','unit':'Thousand tonnes'}
                accepted = {'year':iea[kind+'_years'], 'scenario':iea[kind+'_scenarios']}
                if kind == 'demand':
                    query['flow'] = 'IDLE'
                    equals.update(flow='IDLE', region='World')
                else:
                    accepted['flow'] = ['Mining','Refining']
                result.append({'source':'iea','name':material+' '+kind,
                               'url':iea['endpoint']+'?'+urlencode(sorted(query.items())),
                               'contract':{'equals':equals,'accepted':accepted,
                                           'allow_empty':material=='Graphite: all grades' and kind=='supply'},
                               'licensing':iea['licensing']})
    if only in {'all','comext'}:
        comext = config['comext']
        approved=comext.get('reporters',[comext.get('reporter','DE')])
        reviewed={'DE','FR','IT','ES','PL','NL','EU27_2020'}
        if len(approved)!=len(set(approved)) or not set(approved)<=reviewed:
            raise ValueError('Reporter outside the reviewed licensing/geography scope')
        if reporters is not None and not set(reporters)<=set(approved):
            raise ValueError('Selective reporters must belong to the approved plan')
        for reporter in (reporters if reporters is not None else approved):
            for product in comext['products']:
                for year in sorted(set(years)) if years is not None else comext['years']:
                    coordinates = {'freq':'A','reporter':reporter,'product':product['code'],'time':str(year)}
                    query = dict(coordinates, lang='en')
                    result.append({'source':'comext','name':('' if reporter=='DE' else reporter+' ')+product['code']+' '+str(year),
                                   'url':comext['endpoint']+'?'+urlencode(sorted(query.items())),
                                   'contract':{'coordinates':coordinates,'label_contains':product['label_contains'],
                                               'material_context':product['material_context'],
                                               'scope_note':product['scope_note']},
                                   'licensing':comext['licensing']})
    return result
