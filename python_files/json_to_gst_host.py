import json
from pathlib import Path
import xml.sax.saxutils as sax

def escape(val):
    return sax.escape(str(val))

def main():
    base = Path(__file__).parent.parent
    json_path = base / "json_files/business_graph.json"
    gst_path = base / "groove_model/RiskModelling.gps/host.gst"

    with open(json_path) as f:
        data = json.load(f)["business_graph"]

    # Assign node ids
    node_id_map = {}
    nodes_xml = []
    edges_xml = []
    for idx, node in enumerate(data["nodes"]):
        node_id_map[node["id"]] = f"n{idx}"

    # Nodes and attribute self-loops
    for node in data["nodes"]:
        nid = node_id_map[node["id"]]
        nodes_xml.append(f'        <node id="{nid}"/>')
        # type edge
        edges_xml.append(f'''        <edge from="{nid}" to="{nid}">
            <attr name="label"><string>type:{node["type"]}</string></attr>
        </edge>''')
        # attributes as let:<key>=<value>
        for k, v in node.get("attributes", {}).items():
            # Format value for let
            if isinstance(v, bool):
                v_str = "true" if v else "false"
            elif isinstance(v, (int, float)):
                v_str = str(v)
            else:
                v_str = f'"{escape(v)}"'
            edges_xml.append(f'''        <edge from="{nid}" to="{nid}">
            <attr name="label"><string>let:{k}={v_str}</string></attr>
        </edge>''')

    # Relations as edges
    for rel in data["relations"]:
        src = node_id_map[rel["source"]]
        tgt = node_id_map[rel["target"]]
        label = escape(rel["type"])
        edges_xml.append(f'''        <edge from="{src}" to="{tgt}">
            <attr name="label"><string>{label}</string></attr>
        </edge>''')

    # Write XML
    gst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(gst_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write('<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">\n')
        f.write('    <graph role="host" edgeids="false" edgemode="directed" id="host">\n')
        for n in nodes_xml:
            f.write(n + '\n')
        for e in edges_xml:
            f.write(e + '\n')
        f.write('    </graph>\n</gxl>\n')

if __name__ == "__main__":
    main()