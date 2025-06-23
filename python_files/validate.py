import json
from pathlib import Path

def check_consistency(business_graph, typed_graph):
    # Build lookup tables
    node_types = {nt['name']: nt for nt in typed_graph['type_graph']['node_types'] if 'name' in nt}
    edge_types = {et['name']: et for et in typed_graph['type_graph']['edge_types'] if 'name' in et}
    node_id_to_type = {n['id']: n['type'] for n in business_graph['business_graph']['nodes'] if 'id' in n and 'type' in n}

    errors = []

    # 1. Node type check
    for node in business_graph['business_graph']['nodes']:
        ntype = node.get('type')
        if ntype not in node_types:
            errors.append(f"Node {node.get('id')} has unknown type '{ntype}'.")

    # 2. Node attribute check
    for node in business_graph['business_graph']['nodes']:
        ntype = node.get('type')
        attrs = node.get('attributes', {})
        allowed_attrs = set(node_types.get(ntype, {}).get('attributes', []))
        for attr in attrs:
            if allowed_attrs and attr not in allowed_attrs:
                errors.append(f"Node {node.get('id')} of type '{ntype}' has unknown attribute '{attr}'.")

    # 3. Edge type check
    for rel in business_graph['business_graph']['relations']:
        rtype = rel.get('type')
        if rtype not in edge_types:
            errors.append(f"Relation {rel} has unknown type '{rtype}'.")

    # 4. Relation endpoint check
    node_ids = set(node_id_to_type.keys())
    for rel in business_graph['business_graph']['relations']:
        if rel.get('source') not in node_ids:
            errors.append(f"Relation {rel} source '{rel.get('source')}' not found among nodes.")
        if rel.get('target') not in node_ids:
            errors.append(f"Relation {rel} target '{rel.get('target')}' not found among nodes.")

    return errors

# Usage:

base = Path(__file__).parent.parent  # code/nvl2

with open( base/'json_files/business_graph.json') as f:
    business_graph = json.load(f)
with open( base/'json_files/typed_graph.json') as f:
    typed_graph = json.load(f)
errors = check_consistency(business_graph, typed_graph)
if errors:
    for e in errors:
        print(e)
else:
    print("Business graph is consistent with typed graph!")