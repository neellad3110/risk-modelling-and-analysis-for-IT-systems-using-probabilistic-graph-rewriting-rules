"""
GROOVE LTS Parser for Risk Estimation Integration

This module parses GROOVE LTS (.gpr) files to extract initial pattern matches
and converts them to the format expected by the CTMDP simulation.
It is defensive: returns an empty mapping if the file is missing or malformed.
"""

from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import xml.etree.ElementTree as ET


"""
GROOVE LTS Parser for Risk Estimation Integration

This module parses a GROOVE LTS (.gpr, GXL XML) and extracts the attack surface
(matches for the LHS of each rule) by looking for parent attack edges and
returning their destination node as a match id. The result feeds the Phase 3
risk estimation (analytical ALE and CTMDP Monte Carlo).
"""
from pathlib import Path
from collections import defaultdict
import re
import xml.etree.ElementTree as ET

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _norm(s: str) -> str:
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    return _NON_ALNUM.sub("", s.strip().lower())


PARENT_LABEL_TO_RULE = {
    _norm("phishingAttack"): "RISK001",
    _norm("privilegeEscalation"): "RISK002",
    _norm("credentialDumping"): "RISK003",
    _norm("UnauthorizedScriptExecution"): "RISK004",
    _norm("remoteServiceExploitation"): "RISK005",
    _norm("passTheHash_lateralMovement"): "RISK006",
    _norm("maliciousUSBDevice"): "RISK007",
    _norm("ransomwareDeployment"): "RISK008",
    _norm("DOSAttack"): "RISK009",
    _norm("trustedRelationship"): "RISK010",
}


def _fn_name(label: str) -> str:
    if not label:
        return ""
    i = label.find("(")
    return (label if i < 0 else label[:i]).strip()


def parse_groove_lts(lts_file_path: Path):
    """
    Parse GROOVE LTS (.gpr) file to extract pattern matches for risk rules.

    Returns dict: { rule_id: [ { target_node, edge_label, from_node, to_node }, ... ] }
    """
    tree = ET.parse(lts_file_path)
    root = tree.getroot()

    ns = {"gxl": "http://www.gupro.de/GXL/gxl-1.0.dtd"}
    graph_elem = root.find("gxl:graph", ns) or root.find(".//graph")
    if graph_elem is None:
        return {}

    edges = graph_elem.findall("gxl:edge", ns)
    if not edges:
        edges = graph_elem.findall("edge") or []

    matches_by_rule = defaultdict(list)
    for e in edges:
        src = e.get("from") or e.get("source") or ""
        dst = e.get("to") or e.get("target") or ""
        label = ""
        attr = e.find('gxl:attr[@name="label"]', ns)
        if attr is None:
            attr = e.find('attr[@name="label"]')
        if attr is not None:
            sval = attr.find("gxl:string", ns)
            if sval is None:
                sval = attr.find("string")
            if sval is not None and sval.text:
                label = sval.text.strip()
        parent = _norm(_fn_name(label))
        rid = PARENT_LABEL_TO_RULE.get(parent)
        if not rid:
            continue
        matches_by_rule[rid].append({
            "target_node": dst or "unknown",
            "edge_label": label,
            "from_node": src,
            "to_node": dst,
        })

    # Deduplicate by target_node
    for rid, arr in list(matches_by_rule.items()):
        seen = set()
        uniq = []
        for m in arr:
            t = m.get("target_node")
            if t and t not in seen:
                seen.add(t)
                uniq.append(m)
        matches_by_rule[rid] = uniq

    return dict(matches_by_rule)


def analyze_lts_structure(lts_file_path: Path):
    """Optional: quick stats on the LTS (states, transitions)."""
    tree = ET.parse(lts_file_path)
    root = tree.getroot()
    ns = {"gxl": "http://www.gupro.de/GXL/gxl-1.0.dtd"}
    graph_elem = root.find("gxl:graph", ns) or root.find(".//graph")
    if graph_elem is None:
        print("Warning: No graph element found")
        return
    nodes = graph_elem.findall("gxl:node", ns) or graph_elem.findall("node") or []
    edges = graph_elem.findall("gxl:edge", ns) or graph_elem.findall("edge") or []
    print(f"LTS Analysis for: {lts_file_path}")
    print(f"Total states: {len(nodes)}")
    print(f"Total transitions: {len(edges)}")
    
