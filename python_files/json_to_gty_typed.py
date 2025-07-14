import json
from pathlib import Path

def get_attr_prefix(attr):
    # If attribute is a string, default to string type
    if isinstance(attr, str):
        return "string", attr
    # If attribute is an object with type info
    name = attr.get("name")
    typ = attr.get("type", "string").lower()
    if typ in ("string",):
        return "string", name
    elif typ in ("bool", "boolean"):
        return "bool", name
    elif typ in ("int", "integer"):
        return "int", name
    elif typ in ("real", "float"):
        return "real", name
    else:
        return "flag", name  # fallback

def write_gty(json_data, gty_path):
    node_types = json_data['type_graph']['node_types']
    edge_types = json_data['type_graph']['edge_types']

    # Assign node ids
    node_id_map = {nt['name']: f"n{i}" for i, nt in enumerate(node_types)}
    nodes_xml = []
    edges_xml = []

    # Nodes and self-loop type/attribute edges
    for nt in node_types:
        nid = node_id_map[nt['name']]
        nodes_xml.append(f'        <node id="{nid}"/>')
        # type edge
        edges_xml.append(f'''        <edge from="{nid}" to="{nid}">
            <attr name="label">
                <string>type:{nt["name"]}</string>
            </attr>
        </edge>''')
        # attribute edges
        for attr in nt.get('attributes', []):
            prefix, attr_name = get_attr_prefix(attr)
            edges_xml.append(f'''        <edge from="{nid}" to="{nid}">
            <attr name="label">
                <string>{prefix}:{attr_name}</string>
            </attr>
        </edge>''')

    # Edge types between nodes
    for et in edge_types:
        src = et.get('source')
        tgt = et.get('target')
        if src and tgt and src in node_id_map and tgt in node_id_map:
            src_id = node_id_map[src]
            tgt_id = node_id_map[tgt]
            if src == tgt:
                edges_xml.append(f'''        <edge from="{src_id}" to="{src_id}">
                <attr name="label">
                    <string>{et["name"]}</string>
                </attr>
                <attr name="layout">
                    <string>1 1 1 1 1 1 1 1 1 1</string>
                </attr>
            </edge>''')
            else:
                edges_xml.append(f'''        <edge from="{src_id}" to="{tgt_id}">
                <attr name="label">
                    <string>{et["name"]}</string>
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
    json_path = base / "json_files/typed_graph.json"
    gty_path = base / "groove_model/RiskModelling.gps/type.gty"
    with open(json_path) as f:
        data = json.load(f)
    write_gty(data, gty_path)