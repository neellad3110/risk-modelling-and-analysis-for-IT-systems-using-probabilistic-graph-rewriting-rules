import json
from pathlib import Path

def get_attr_prefix(attr_name, attr_type):
    typ = attr_type.lower()
    if typ == "string":
        return "string", attr_name
    elif typ in ("bool", "boolean"):
        return "bool", attr_name
    elif typ in ("int", "integer"):
        return "int", attr_name
    elif typ in ("real", "float", "number"):
        return "real", attr_name
    else:
        return "flag", attr_name  # fallback

def write_gty(json_data, gty_path):
    node_types = json_data['nodes']
    edge_types = json_data['edges']

    # Assign node ids
    node_id_map = {nt['type']: f"n{i}" for i, nt in enumerate(node_types)}
    nodes_xml = []
    edges_xml = []

    # Nodes and self-loop type/attribute edges
    for nt in node_types:
        nid = node_id_map[nt['type']]
        nodes_xml.append(f'        <node id="{nid}"/>')
        # type edge
        edges_xml.append(f'''        <edge from="{nid}" to="{nid}">
            <attr name="label">
                <string>type:{nt["type"]}</string>
            </attr>
        </edge>''')
        # attribute edges
        for attr_name, attr_type in nt.get('attributes', {}).items():
            prefix, attr_name2 = get_attr_prefix(attr_name, attr_type)
            edges_xml.append(f'''        <edge from="{nid}" to="{nid}">
            <attr name="label">
                <string>{prefix}:{attr_name2}</string>
            </attr>
        </edge>''')
        # generalization (inheritance) edge    
        if 'isSubTypeOf' in nt:
            supertype = nt['isSubTypeOf']
            if supertype in node_id_map:
                super_id = node_id_map[supertype]
                edges_xml.append(f'''        <edge from="{nid}" to="{super_id}">
            <attr name="label">
                <string>sub:</string>
            </attr>
        </edge>''')    

    # Edge types between nodes
    for et in edge_types:
        src = et.get('source')
        tgt = et.get('target')
        if src and tgt and src in node_id_map and tgt in node_id_map:
            src_id = node_id_map[src]
            tgt_id = node_id_map[tgt]
            # Handle self-looping edge with layout for GUI clarity
            if src == tgt:
                edges_xml.append(f'''        <edge from="{src_id}" to="{src_id}">
            <attr name="label">
                <string>{et["type"]}</string>
            </attr>
            <attr name="layout">
                <string>1 1 1 1 1 1 1 1 1 1</string>
            </attr>
        </edge>''')
            else:
                edges_xml.append(f'''        <edge from="{src_id}" to="{tgt_id}">
            <attr name="label">
                <string>{et["type"]}</string>
            </attr>
        </edge>''')

    # Write XML
    with open(gty_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write('<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">\n')
        f.write('    <graph role="type" edgeids="false" edgemode="directed" id="type">\n')
        f.write('        <attr name="$version">\n            <string>curly</string>\n        </attr>\n')
        for n in nodes_xml:
            f.write(n + '\n')
        for e in edges_xml:
            f.write(e + '\n')
        f.write('    </graph>\n</gxl>\n')

if __name__ == "__main__":
    base = Path(__file__).parent.parent
    json_path = base / "json_files/type_graph.json"
    gty_path = base / "groove_model/RiskModelling.gps/type.gty"
    with open(json_path) as f:
        data = json.load(f)
    write_gty(data, gty_path)