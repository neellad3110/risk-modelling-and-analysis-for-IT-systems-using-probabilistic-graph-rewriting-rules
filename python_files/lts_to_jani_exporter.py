from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from typing import List, Dict, Any

def parse_gxl_lts(gxl_path: Path) -> Dict[str, Any]:
    """Parse GROOVE LTS (GXL) into dict with nodes and edges."""
    root = ET.parse(str(gxl_path)).getroot()
    ns = root.tag.split("}")[0].strip("{") if "}" in root.tag else None
    def q(tag): return f"{{{ns}}}{tag}" if ns else tag

    graph = root.find(q("graph"))
    if graph is None:
        raise ValueError("No <graph> element found in GXL.")

    nodes = [n.get("id") for n in graph.findall(q("node"))]

    edges = []
    for e in graph.findall(q("edge")):
        lbl = ""
        for a in e.findall(q("attr")):
            if a.get("name") == "label":
                s = a.find(q("string"))
                if s is not None and s.text:
                    lbl = s.text.strip()
        edges.append({"src": e.get("from"), "dst": e.get("to"), "label": lbl})

    return {"nodes": nodes, "edges": edges, "init": nodes[0] if nodes else None}

def bfs_attack_patterns(gxl_data: Dict[str, Any], max_depth: int = 3) -> List[List[str]]:
    """BFS exploration to extract attack sequences (labels)."""
    edges_by_src = defaultdict(list)
    for e in gxl_data["edges"]:
        edges_by_src[e["src"]].append(e)

    patterns = []
    queue = deque()
    queue.append( (gxl_data["init"], [], 0) )  # node, path_so_far, depth

    while queue:
        node, path, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for e in edges_by_src.get(node, []):
            new_path = path + [e["label"]]
            patterns.append(new_path)
            queue.append( (e["dst"], new_path, depth+1) )

    return patterns

def save_patterns_to_file(patterns, filepath: Path):
    with open(filepath, "w", encoding="utf-8") as f:
        for p in patterns:
            f.write(" -> ".join(p) + "\n")

if __name__ == "__main__":
    base = Path(__file__).parent.parent
    gxl_file = base / "groove_LTS" /"RiskModelling@host.gxl"
    gxl_data = parse_gxl_lts(gxl_file)

    print("Nodes:", len(gxl_data["nodes"]))
    print("Edges:", len(gxl_data["edges"]))
    print("Initial node:", gxl_data["init"])

    output_file = base / "results" / "bfs_patterns.txt"
    patterns = bfs_attack_patterns(gxl_data, max_depth=5)
    save_patterns_to_file(patterns, output_file)
