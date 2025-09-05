"""
GROOVE LTS Parser for Risk Estimation Integration

This module parses a GROOVE LTS (.gpr, GXL XML) and extracts the attack surface
(matches for the LHS of each rule) by looking for parent attack edges and
returning their destination node as a match id.
"""
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import re
import xml.etree.ElementTree as ET

NS = {"gxl": "http://www.gupro.de/GXL/gxl-1.0.dtd"}
_NON_ALNUM = re.compile(r"[^a-z0-9]+")

def _norm(s: str) -> str:
    return _NON_ALNUM.sub("", (s or "").strip().lower())

def _fn_base(label: str) -> str:
    # "phishingAttack(n15)" -> "phishingAttack"
    s = (label or "").strip()
    i = s.find("(")
    return s if i < 0 else s[:i]

PARENT_BASE_TO_RULE: Dict[str, str] = {
    _norm("phishingAttack"): "RISK001",
    _norm("privilegeEscalation"): "RISK002",
    _norm("credentialDumping"): "RISK003",
    _norm("UnauthorizedScriptExecution"): "RISK004",
    _norm("remoteServiceExploitation"): "RISK005",
    _norm("passTheHash_lateralMovement"): "RISK006",
    _norm("maliciousUSBDevice"): "RISK007",
    _norm("ransomwareDeployment"): "RISK008",
    _norm("trustedRelationship"): "RISK009",
    _norm("DOSAttack"): "RISK010",
}
def _detect_ns(elem):
    t = getattr(elem, "tag", "")
    return t[1:t.find("}")] if t.startswith("{") else None

def _q(ns, tag):
    return f"{{{ns}}}{tag}" if ns else tag

def _edge_label_ns(e, ns) -> str:
    # namespaced <attr name="label"><string>...</string></attr>
    for a in e.findall(_q(ns, "attr")):
        if a.get("name") == "label":
            s = a.find(_q(ns, "string"))
            if s is not None and s.text:
                return s.text.strip()
    # fallback non-namespaced
    a = e.find('attr[@name="label"]')
    if a is not None:
        s = a.find("string")
        if s is not None and s.text:
            return s.text.strip()
    return ""

def _load_graph(gxl_path: Path) -> Tuple[List[str], List[Dict[str, str]], str | None]:
    root = ET.parse(str(gxl_path)).getroot()
    ns = _detect_ns(root)
    graph = root.find(_q(ns, "graph")) or root.find("graph")
    if graph is None:
        return [], [], None
    nodes = [n.get("id") for n in graph.findall(_q(ns, "node"))] or [n.get("id") for n in graph.findall("node")]
    edges = []
    for e in graph.findall(_q(ns, "edge")) or graph.findall("edge"):
        edges.append({
            "src": e.get("from") or e.get("source") or "",
            "dst": e.get("to") or e.get("target") or "",
            "label": _edge_label_ns(e, ns),
        })
    init = nodes[0] if nodes else None
    return nodes, edges, init

def debug_parents(lts_file_path: Path, limit: int = 10):
    nodes, edges, _ = _load_graph(lts_file_path)
    print(f"Parsed LTS: |S|={len(nodes)} |E|={len(edges)}")
    shown = 0
    for e in edges:
        base = _norm(_fn_base(e["label"]))
        rid = PARENT_BASE_TO_RULE.get(base)
        if rid:
            print(f"parent rid={rid} base={base} src={e['src']} fork={e['dst']} label={e['label']}")
            shown += 1
            if shown >= limit:
                break
            
def parse_groove_lts_with_outcomes(lts_file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns: { rid: [ { from_node, fork_node, parent_label, outcomes:[{label,to_node}...] } ... ] }
    Parent edges are like phishingAttack(...). Outcomes are edges out of the fork_node.
    """
    _, edges, _ = _load_graph(lts_file_path)
    by_src: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for e in edges:
        by_src[e["src"]].append(e)

    out: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in edges:
        base = _norm(_fn_base(e["label"]))
        rid = PARENT_BASE_TO_RULE.get(base)
        if not rid:
            continue
        fork = e["dst"]
        outcomes = [{"label": oe["label"], "to_node": oe["dst"]} for oe in by_src.get(fork, [])]
        out[rid].append({
            "from_node": e["src"],
            "fork_node": fork,
            "parent_label": e["label"],
            "outcomes": outcomes
        })

    # Deduplicate by fork_node per rule
    for rid, arr in list(out.items()):
        seen, uniq = set(), []
        for m in arr:
            f = m["fork_node"]
            if f in seen: continue
            seen.add(f); uniq.append(m)
        out[rid] = uniq
    return dict(out)

def parse_groove_lts(lts_file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
  
    with_outs = parse_groove_lts_with_outcomes(lts_file_path)
    simple = {}
    for rid, arr in with_outs.items():
        simple[rid] = [{
            "from_node": m["from_node"],
            "target_node": m["fork_node"],
            "edge_label": m["parent_label"],
        } for m in arr]
    return simple


def analyze_lts_structure(lts_file_path: Path):
    nodes, edges, _ = _load_graph(lts_file_path)
    print(f"States={len(nodes)}, Transitions={len(edges)}")
    
