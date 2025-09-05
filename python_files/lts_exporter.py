from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import json, re, xml.etree.ElementTree as ET

# ---------- XML helpers (namespace-agnostic) ----------
def _detect_ns(elem):
    t = getattr(elem, "tag", "")
    return t[1:t.find("}")] if t.startswith("{") else None

def _q(ns, tag):
    return f"{{{ns}}}{tag}" if ns else tag

def _edge_label_ns(e, ns) -> str:
    for a in e.findall(_q(ns, "attr")):
        if a.get("name") == "label":
            s = a.find(_q(ns, "string"))
            if s is not None and s.text:
                return s.text.strip()
    a = e.find('attr[@name="label"]')
    if a is not None:
        s = a.find("string")
        if s is not None and s.text:
            return s.text.strip()
    return ""

def parse_gxl_lts(gxl_path: Path) -> Tuple[List[str], List[Dict], str | None]:
    """Return (nodes_in_order, edges[{src,dst,label}], initial_node_id)."""
    root = ET.parse(str(gxl_path)).getroot()
    ns = _detect_ns(root)
    graph = root.find(_q(ns, "graph")) or root.find("graph")
    if graph is None:
        return [], [], None
    nodes = [n.get("id") for n in graph.findall(_q(ns, "node"))] or [n.get("id") for n in graph.findall("node")]
    edges: List[Dict] = []
    for e in graph.findall(_q(ns, "edge")) or graph.findall("edge"):
        edges.append({
            "src": e.get("from") or e.get("source") or "",
            "dst": e.get("to") or e.get("target") or "",
            "label": _edge_label_ns(e, ns),
        })
    init = nodes[0] if nodes else None
    return nodes, edges, init

# ---------- Label normalization and parent mapping ----------
_NON_ALNUM = re.compile(r"[^a-z0-9]+")

def outcome_key(s: str) -> str:
    """Loose key for matching outcome labels."""
    return _NON_ALNUM.sub(" ", (s or "").strip().lower()).strip()

def _base_before_paren(label: str) -> str:
    s = (label or "").strip()
    i = s.find("(")
    return (s if i < 0 else s[:i]).strip()

def _norm(s: str) -> str:
    return _NON_ALNUM.sub("", (s or "").strip().lower())

# Map GROOVE parent base names (before '(') -> rule id
_PARENT_BASE_TO_RULE: Dict[str, str] = {
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
    _norm("dosAttack"): "RISK010",  # tolerate case variant
}

def is_parent_edge(label: str) -> bool:
    base = _norm(_base_before_paren(label))
    return base in _PARENT_BASE_TO_RULE

def rule_id_from_parent(label: str) -> str | None:
    base = _norm(_base_before_paren(label))
    return _PARENT_BASE_TO_RULE.get(base)

# ---------- Rules loader (Λ and normalized outcomes) ----------
def load_rules(rs_path: Path) -> Dict[str, Dict]:
    """
    Expect JSON:
      risk_specification: { rules: [ { id, title, attack_rate: {rate_per_year}, outcomes:[{name,probability,cost}] } ... ] }
    Produces:
      { rid: { id, title, lambda, outcomes:[{name,p,cost}] } }
    """
    data = json.loads(Path(rs_path).read_text(encoding="utf-8"))
    rules = {}
    rules_arr = (data.get("risk_specification") or {}).get("rules") or []
    for r in rules_arr:
        rid = r.get("id")
        if not rid:
            continue
        Lam = float((r.get("attack_rate") or {}).get("rate_per_year") or 0.0)
        outs = r.get("outcomes") or []
        # normalize probabilities
        raw = []
        for o in outs:
            v = o.get("probability")
            try:
                raw.append(float(v))
            except Exception:
                raw.append(None)
        total = sum(v for v in raw if isinstance(v, (int, float, float)))
        if outs:
            if total and total > 0:
                ps = [float(v)/total if isinstance(v, (int, float, float)) else 0.0 for v in raw]
            else:
                ps = [1.0/len(outs)] * len(outs)
        else:
            ps = []
        outs_norm = []
        for o, p in zip(outs, ps):
            outs_norm.append({
                "name": o.get("name") or o.get("label") or "",
                "p": float(p),
                "cost": float(o.get("cost") or 0.0),
            })
        rules[rid] = {
            "id": rid,
            "title": r.get("title", rid),
            "lambda": Lam,
            "outcomes": outs_norm,
        }
    return rules
