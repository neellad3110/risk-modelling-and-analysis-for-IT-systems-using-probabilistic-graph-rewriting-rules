from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, Set, Tuple, List, Optional

# --------------------
# Helpers: load JSON
# --------------------

def _strip_json_comments(text: str) -> str:
    out = []
    i, n = 0, len(text)
    in_str = False
    esc = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in ("\n", "\r"):
                i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2 if i + 1 < n else 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)

def load_json(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        clean = _strip_json_comments(text)
        return json.loads(clean)

def project_root() -> Path:
    # This file: <root>/nvl2/python_files/validate.py
    return Path(__file__).resolve().parents[2]

# --------------------
# Type graph indexing
# --------------------

class TypeInfo:
    def __init__(self, name: str, parent: Optional[str], attrs: Set[str], is_abstract: bool):
        self.name = name
        self.parent = parent
        self.attrs_declared = set(attrs)
        self.attrs_resolved: Set[str] = set()  # to be filled with inheritance
        self.is_abstract = is_abstract

def _normalize_attr_name(attr: str) -> str:
    # Strip known prefixes like "test:" and "let:" used in rules/graphs
    if ":" in attr:
        return attr.split(":", 1)[1]
    return attr

def build_type_index(tg: dict) -> Tuple[Dict[str, TypeInfo], Dict[str, Set[str]], Dict[str, Set[Tuple[str, str]]]]:
    # Nodes
    type_index: Dict[str, TypeInfo] = {}
    nodes = tg.get("nodes", [])
    for n in nodes:
        t = n.get("type")
        if not isinstance(t, str) or not t:
            # skip invalid
            continue
        parent = n.get("isSubTypeOf")
        attrs_map = n.get("attributes", {}) or {}
        attrs = {str(k) for k in attrs_map.keys()}
        is_abs = bool(n.get("isAbstract", False))
        type_index[t] = TypeInfo(t, parent if isinstance(parent, str) else None, attrs, is_abs)

    # Build ancestry: type -> set(ancestors including self)
    ancestry: Dict[str, Set[str]] = {t: {t} for t in type_index}
    # Resolve parents
    changed = True
    while changed:
        changed = False
        for t, info in type_index.items():
            if info.parent and info.parent in type_index:
                before = len(ancestry[t])
                ancestry[t] |= ancestry[info.parent]
                if len(ancestry[t]) != before:
                    changed = True

    # Resolve attrs with inheritance (inherit from all ancestors)
    for t, info in type_index.items():
        attrs: Set[str] = set()
        for anc in ancestry[t]:
            attrs |= type_index[anc].attrs_declared
        info.attrs_resolved = attrs

    # Edges: relation type -> set of allowed (srcType, tgtType) pairs
    rel_index: Dict[str, Set[Tuple[str, str]]] = {}
    for e in tg.get("edges", []):
        rtype = e.get("type")
        src = e.get("source")
        tgt = e.get("target")
        if not (isinstance(rtype, str) and isinstance(src, str) and isinstance(tgt, str)):
            continue
        rel_index.setdefault(rtype, set()).add((src, tgt))

    return type_index, ancestry, rel_index

def is_subtype(actual: str, base: str, ancestry: Dict[str, Set[str]]) -> bool:
    return actual in ancestry and base in ancestry[actual]

def rel_allows(rel_type: str, src_actual: str, tgt_actual: str,
               rel_index: Dict[str, Set[Tuple[str, str]]],
               ancestry: Dict[str, Set[str]]) -> bool:
    pairs = rel_index.get(rel_type)
    if not pairs:
        return False
    for (src_base, tgt_base) in pairs:
        if is_subtype(src_actual, src_base, ancestry) and is_subtype(tgt_actual, tgt_base, ancestry):
            return True
    return False

# --------------------
# Business graph checks
# --------------------

def check_business_graph(graphs: list, type_index: Dict[str, TypeInfo],
                         ancestry: Dict[str, Set[str]],
                         rel_index: Dict[str, Set[Tuple[str, str]]]) -> List[str]:
    errs: List[str] = []
    if not isinstance(graphs, list):
        return ["$. (root): expected array of graphs"]

    for gi, g in enumerate(graphs):
        # Build id -> type map and validate node types/attributes
        id2type: Dict[str, str] = {}
        nodes = g.get("nodes", [])
        if not isinstance(nodes, list):
            errs.append(f"$[{gi}].nodes: expected array")
            continue
        for ni, n in enumerate(nodes):
            nid = n.get("id")
            ntype = n.get("type")
            if not isinstance(nid, str) or not nid:
                errs.append(f"$[{gi}].nodes[{ni}].id: missing/non-empty string")
                continue
            if not isinstance(ntype, str) or not ntype:
                errs.append(f"$[{gi}].nodes[{ni}].type: missing/non-empty string")
                continue
            if ntype not in type_index:
                errs.append(f"$[{gi}].nodes[{ni}].type: unknown node type '{ntype}'")
            else:
                # Attributes check with inheritance
                attrs = n.get("attributes", {}) or {}
                if not isinstance(attrs, dict):
                    errs.append(f"$[{gi}].nodes[{ni}].attributes: must be object if present")
                else:
                    allowed = type_index[ntype].attrs_resolved
                    for k in attrs.keys():
                        k_norm = _normalize_attr_name(str(k))
                        if k_norm not in allowed:
                            errs.append(f"$[{gi}].nodes[{ni}].attributes['{k}']: not allowed for type '{ntype}'")
            # Record mapping
            id2type[nid] = ntype

        # Validate edges
        edges = g.get("edges", [])
        if not isinstance(edges, list):
            errs.append(f"$[{gi}].edges: expected array")
            continue
        for ei, e in enumerate(edges):
            rtype = e.get("type")
            src = e.get("source")
            tgt = e.get("target")
            if not isinstance(rtype, str) or not rtype:
                errs.append(f"$[{gi}].edges[{ei}].type: missing/non-empty string")
                continue
            if rtype not in rel_index:
                errs.append(f"$[{gi}].edges[{ei}].type: unknown relation type '{rtype}'")
                continue
            if not isinstance(src, str) or src not in id2type:
                errs.append(f"$[{gi}].edges[{ei}].source: unknown node id '{src}'")
                continue
            if not isinstance(tgt, str) or tgt not in id2type:
                errs.append(f"$[{gi}].edges[{ei}].target: unknown node id '{tgt}'")
                continue
            src_t = id2type[src]
            tgt_t = id2type[tgt]
            if not rel_allows(rtype, src_t, tgt_t, rel_index, ancestry):
                errs.append(f"$[{gi}].edges[{ei}]: relation '{rtype}' not allowed from {src_t} to {tgt_t}")
    return errs

# --------------------
# Risk rules checks
# --------------------

def _collect_binds_from_nodes(node_list: list) -> Dict[str, str]:
    binds: Dict[str, str] = {}
    for n in node_list:
        b = n.get("bind")
        t = n.get("type")
        if isinstance(b, str) and isinstance(t, str) and t:
            binds[b] = t
    return binds

def _check_node_attrs(rule_id: str, ctx: str, node_obj: dict, type_index: Dict[str, TypeInfo], errs: List[str]):
    t = node_obj.get("type")
    if not isinstance(t, str) or not t:
        return
    if t not in type_index:
        errs.append(f"Rule {rule_id} {ctx}: unknown node type '{t}'")
        return
    attrs = node_obj.get("attributes", {}) or {}
    if not isinstance(attrs, dict):
        errs.append(f"Rule {rule_id} {ctx}: attributes must be object")
        return
    allowed = type_index[t].attrs_resolved
    for k in attrs.keys():
        k_norm = _normalize_attr_name(str(k))
        if k_norm not in allowed:
            errs.append(f"Rule {rule_id} {ctx}: attribute '{k}' not allowed for type '{t}'")

def check_outcome_probabilities(rule_obj: dict, rule_index: int, epsilon: float = 1e-6) -> Optional[str]:
    outs = rule_obj.get("outcomes", [])
    if not isinstance(outs, list) or not outs:
        return f"$.risk_specification.rules[{rule_index}].outcomes: empty or missing for rule {rule_obj.get('id')}"
    probs = []
    for j, o in enumerate(outs):
        p = o.get("probability", None)
        if not isinstance(p, (int, float)):
            return f"$.risk_specification.rules[{rule_index}].outcomes[{j}].probability: missing or not a number (rule {rule_obj.get('id')})"
        probs.append(float(p))
    s = sum(probs)
    if abs(s - 1.0) > epsilon:
        return f"$.risk_specification.rules[{rule_index}].outcomes: probabilities sum = {s:.6f} (expected 1.0) for rule {rule_obj.get('id')}"
    return None

def check_risk_rules(rules_root: dict, type_index: Dict[str, TypeInfo],
                     ancestry: Dict[str, Set[str]],
                     rel_index: Dict[str, Set[Tuple[str, str]]]) -> List[str]:
    errs: List[str] = []
    rs = rules_root.get("risk_specification", {})
    rules = rs.get("rules", [])
    if not isinstance(rules, list):
        return ["$.risk_specification.rules: expected array"]

    for ri, rule in enumerate(rules):
        rid = str(rule.get("id", f"(rule_index_{ri})"))

        # Probability sum check
        prob_err = check_outcome_probabilities(rule, ri)
        if prob_err:
            errs.append(prob_err)

        # LHS nodes/edges
        lhs = (rule.get("risk_pattern") or {}).get("lhs") or {}
        lhs_nodes = lhs.get("nodes", []) or []
        lhs_edges = lhs.get("edges", []) or []

        if not isinstance(lhs_nodes, list):
            errs.append(f"Rule {rid}: lhs.nodes must be array")
            lhs_nodes = []
        if not isinstance(lhs_edges, list):
            errs.append(f"Rule {rid}: lhs.edges must be array")
            lhs_edges = []

        bind_types = _collect_binds_from_nodes(lhs_nodes)

        for n in lhs_nodes:
            _check_node_attrs(rid, "LHS node", n, type_index, errs)

        for ei, e in enumerate(lhs_edges):
            rtype = e.get("type")
            srcb = e.get("source")
            tgtb = e.get("target")
            if not isinstance(rtype, str) or not rtype:
                errs.append(f"Rule {rid}: LHS edge[{ei}].type missing/non-empty")
                continue
            if rtype not in rel_index:
                errs.append(f"Rule {rid}: LHS edge[{ei}].type '{rtype}' not in type graph")
                continue
            if not isinstance(srcb, str) or srcb not in bind_types:
                errs.append(f"Rule {rid}: LHS edge[{ei}].source bind '{srcb}' unknown")
                continue
            if not isinstance(tgtb, str) or tgtb not in bind_types:
                errs.append(f"Rule {rid}: LHS edge[{ei}].target bind '{tgtb}' unknown")
                continue
            src_t = bind_types[srcb]
            tgt_t = bind_types[tgtb]
            if not rel_allows(rtype, src_t, tgt_t, rel_index, ancestry):
                errs.append(f"Rule {rid}: LHS edge[{ei}] relation '{rtype}' not allowed from {src_t} to {tgt_t}")

        # Outcomes nodes/edges
        outs = rule.get("outcomes", []) or []
        for oi, o in enumerate(outs):
            onodes = o.get("nodes", []) or []
            oedges = o.get("edges", []) or []
            if not isinstance(onodes, list) or not isinstance(oedges, list):
                errs.append(f"Rule {rid}: outcome[{oi}] nodes/edges must be arrays if present")
                continue
            # Build outcome bind env extending lhs
            env = dict(bind_types)
            for n in onodes:
                _check_node_attrs(rid, f"Outcome[{oi}] node", n, type_index, errs)
                b = n.get("bind")
                t = n.get("type")
                if isinstance(b, str) and isinstance(t, str) and t:
                    env[b] = t
            for ei, e in enumerate(oedges):
                rtype = e.get("type")
                srcb = e.get("source")
                tgtb = e.get("target")
                if not isinstance(rtype, str) or not rtype:
                    errs.append(f"Rule {rid}: outcome[{oi}] edge[{ei}].type missing/non-empty")
                    continue
                if rtype not in rel_index:
                    errs.append(f"Rule {rid}: outcome[{oi}] edge[{ei}].type '{rtype}' not in type graph")
                    continue
                if not isinstance(srcb, str) or srcb not in env:
                    errs.append(f"Rule {rid}: outcome[{oi}] edge[{ei}].source bind '{srcb}' unknown")
                    continue
                if not isinstance(tgtb, str) or tgtb not in env:
                    errs.append(f"Rule {rid}: outcome[{oi}] edge[{ei}].target bind '{tgtb}' unknown")
                    continue
                src_t = env[srcb]
                tgt_t = env[tgtb]
                if not rel_allows(rtype, src_t, tgt_t, rel_index, ancestry):
                    errs.append(f"Rule {rid}: outcome[{oi}] edge[{ei}] relation '{rtype}' not allowed from {src_t} to {tgt_t}")
    return errs

# --------------------
# Main
# --------------------

def main():
    root = project_root()
    tg_path = root / "nvl2" / "json_files" / "type_graph.json"
    bg_path = root / "nvl2" / "json_files" / "business_graph.json"
    rr_path = root / "nvl2" / "json_files" / "risk_rules.json"

    # Load
    type_graph = load_json(tg_path)
    business_graphs = load_json(bg_path)
    risk_rules = load_json(rr_path)

    # Build indices
    type_index, ancestry, rel_index = build_type_index(type_graph)

    errors: List[str] = []

    # Business graph consistency
    errors += check_business_graph(business_graphs, type_index, ancestry, rel_index)

    # Risk rules consistency
    errors += check_risk_rules(risk_rules, type_index, ancestry, rel_index)

    # Report
    print("=== Consistency Validation (Type Graph vs Business Graph & Risk Rules) ===")
    print(f"Type Graph:     {tg_path}")
    print(f"Business Graph: {bg_path}")
    print(f"Risk Rules:     {rr_path}")
    print("------------------------------------------------------------")
    if errors:
        print("INVALID: issues found")
        for i, msg in enumerate(errors, 1):
            print(f"- [{i}] {msg}")
        raise SystemExit(3)
    else:
        print("VALID: business graph and risk rules are consistent with the type graph")
        raise SystemExit(0)

if __name__ == "__main__":
    main()