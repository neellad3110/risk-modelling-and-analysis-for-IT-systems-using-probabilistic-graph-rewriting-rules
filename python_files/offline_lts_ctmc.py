"""
Offline LTS-driven CTMC simulator.

Purpose:
- Parse a GROOVE-exported LTS (.gpr, GXL XML) once.
- Use risk_rules_new.json to annotate outcome-labeled edges with rates and costs.
- Collapse (attack -> outcome) to a CTMC embedding via q = lambda(rule) * p(outcome).
- Run Monte Carlo directly on the fixed CTMC to estimate time-bounded expected loss.

Notes:
- We do not re-run GROOVE during simulation.
- We do not modify your rules JSON.
- Outcome probabilities are normalized per rule; if missing we assume uniform.
- If an outcome cost is missing, we treat it as 0.

Output:
- Summary dict with mean loss and quantiles over the horizon.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import xml.etree.ElementTree as ET
import json
import math
import random
import re


# ---------------------------
# Utilities
# ---------------------------

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _norm(s: str) -> str:
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    return _NON_ALNUM.sub("", s.strip().lower())


# ---------------------------
# Rules and outcomes
# ---------------------------

@dataclass
class OutcomeSpec:
    label_norm: str
    prob: float
    cost: float
    raw: Dict[str, Any]


@dataclass
class RuleSpec:
    rule_id: str
    lam: float
    outcomes: List[OutcomeSpec]


def load_rule_specs(rs_path: Path) -> Dict[str, RuleSpec]:
    data = json.loads(rs_path.read_text(encoding="utf-8"))
    # Optional sidecar mapping to override outcome labels: { "RISK001": { "Outcome Name": "GROOVE_Function_Label" }, ... }
    label_map_path = rs_path.parent / "risk_outcome_label_map.json"
    label_map: Dict[str, Dict[str, str]] = {}
    if label_map_path.exists():
        try:
            label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
        except Exception:
            label_map = {}
    rule_specs: Dict[str, RuleSpec] = {}
    rules = data.get("risk_specification", {}).get("rules", [])
    for r in rules:
        rid = r.get("id")
        if not rid:
            continue
        lam = float((r.get("attack_rate") or {}).get("rate_per_year") or 0.0)
        outs_raw = r.get("outcomes", []) or []
        # Determine labels and probabilities
        # Prefer 'label' field for matching to GROOVE edge labels; fallback to 'name'.
        probs = []
        for o in outs_raw:
            p = o.get("probability")
            if isinstance(p, (int, float)):
                probs.append(float(p))
        p_sum = sum(probs)
        outcomes: List[OutcomeSpec] = []
        if outs_raw:
            if p_sum > 0:
                # normalize provided probs
                norm_ps = [float((o.get("probability") or 0.0)) / p_sum for o in outs_raw]
            else:
                # uniform if missing
                k = len(outs_raw)
                norm_ps = [1.0 / k] * k
            for o, p in zip(outs_raw, norm_ps):
                # Allow override via mapping file keyed by outcome name
                o_name = o.get("name") or ""
                override = label_map.get(rid, {}).get(o_name)
                label = override or o.get("label") or o_name or ""
                cost = float(o.get("cost", 0.0) or 0.0)
                outcomes.append(OutcomeSpec(label_norm=_norm(label), prob=float(p), cost=cost, raw=o))
        rule_specs[rid] = RuleSpec(rule_id=rid, lam=lam, outcomes=outcomes)
    return rule_specs


# ---------------------------
# LTS parsing
# ---------------------------

@dataclass
class LTSEdge:
    src: str
    dst: str
    label: str


@dataclass
class LTSGraph:
    nodes: List[str]
    edges: List[LTSEdge]


def parse_gxl_lts(lts_file_path: Path) -> LTSGraph:
    tree = ET.parse(lts_file_path)
    root = tree.getroot()

    # Try namespace-aware first, then fallback
    ns = {"gxl": "http://www.gupro.de/GXL/gxl-1.0.dtd"}
    graph_elem = root.find("gxl:graph", ns) or root.find(".//graph")
    if graph_elem is None:
        raise RuntimeError(f"No <graph> element found in {lts_file_path}")

    # Collect nodes
    nodes = []
    node_elems = graph_elem.findall("gxl:node", ns) or graph_elem.findall("node") or []
    for n in node_elems:
        nid = n.get("id")
        if nid:
            nodes.append(nid)

    # Collect edges and labels
    edges = []
    edge_elems = graph_elem.findall("gxl:edge", ns)
    if not edge_elems:
        edge_elems = graph_elem.findall("edge") or []
    for e in edge_elems:
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
        edges.append(LTSEdge(src=src, dst=dst, label=label))

    # If nodes list is empty, derive from edges
    if not nodes:
        seen = set()
        for e in edges:
            if e.src:
                seen.add(e.src)
            if e.dst:
                seen.add(e.dst)
        nodes = list(seen)

    return LTSGraph(nodes=nodes, edges=edges)


# ---------------------------
# Build CTMC from LTS and rules
# ---------------------------

@dataclass
class CTMCTransition:
    dst: str
    rate: float
    cost: float
    rule_id: Optional[str] = None
    outcome_label: Optional[str] = None


CTMC = Dict[str, List[CTMCTransition]]  # adjacency list: state -> transitions


def build_outcome_index(rule_specs: Dict[str, RuleSpec]) -> Dict[str, Tuple[str, OutcomeSpec]]:
    """Map normalized outcome labels to (rule_id, OutcomeSpec)."""
    idx: Dict[str, Tuple[str, OutcomeSpec]] = {}
    for rid, rs in rule_specs.items():
        for oc in rs.outcomes:
            if oc.label_norm:
                idx[oc.label_norm] = (rid, oc)
    return idx


def _extract_fn_name(label: str) -> str:
    """Extract function-like name from a GROOVE edge label e.g., foo_bar(x,y) -> foo_bar."""
    if not label:
        return ""
    i = label.find("(")
    return (label if i < 0 else label[:i]).strip()


def build_ctmc_from_lts(lts: LTSGraph, rule_specs: Dict[str, RuleSpec]) -> Tuple[CTMC, str]:
    """
    Build a CTMC by collapsing two-step (attack -> outcome) in the GROOVE LTS:
    - Identify parent attack edges (labels like phishingAttack(...), privilegeEscalation(...)).
    - For each parent edge s --attack--> s', find outgoing outcome edges s' --outcome--> s''.
    - Create CTMC transition s --[q=λ·p, cost]--> s''.

    Returns (ctmc, start_state), where start_state is a node with in-degree 0 if found, else an arbitrary node.
    """
    # Parent function label to rule-id mapping (normalized). Allow override from optional JSON sidecar.
    parent_map_default: Dict[str, str] = {
        _norm("phishingAttack"): "RISK001",
        _norm("privilegeEscalation"): "RISK002",
        _norm("credentialDumping"): "RISK003",
        _norm("UnauthorizedScriptExecution"): "RISK004",
        _norm("remoteServiceExploitation"): "RISK005",
        _norm("passTheHash_lateralMovement"): "RISK006",
        _norm("maliciousUSBDevice"): "RISK007",
        _norm("ransomwareDeployment"): "RISK008",
    # Note: RISK009=Trusted Relationship, RISK010=Denial of Service
    _norm("trustedRelationship"): "RISK009",
    _norm("DOSAttack"): "RISK010",
    }

    # Allow user to override/augment mapping via json_files/risk_parent_label_map.json
    # We infer json_files folder from presence of rules JSON nearby. If not available, defaults are used.
    parent_override: Dict[str, str] = {}
    # Try to find the rules json path from any loaded spec to locate the folder
    # (Not perfect; if unavailable, skip overrides)
    try:
        # Heuristic: take folder two levels up from first edge label path assumption is not reliable here.
        pass
    except Exception:
        pass

    # Build fast lookups
    outcome_idx_by_rule: Dict[str, Dict[str, OutcomeSpec]] = {}
    for rid, spec in rule_specs.items():
        inner: Dict[str, OutcomeSpec] = {}
        for oc in spec.outcomes:
            inner[oc.label_norm] = oc
        outcome_idx_by_rule[rid] = inner

    # Compute indegrees to pick a start state
    indeg: Dict[str, int] = {n: 0 for n in lts.nodes}
    for e in lts.edges:
        if e.dst in indeg:
            indeg[e.dst] += 1
    start_node = None
    for n, d in indeg.items():
        if d == 0:
            start_node = n
            break
    if start_node is None:
        start_node = lts.nodes[0] if lts.nodes else ""

    # Group edges by source for quick traversal
    edges_by_src: Dict[str, List[LTSEdge]] = {}
    for e in lts.edges:
        edges_by_src.setdefault(e.src, []).append(e)

    ctmc: CTMC = {n: [] for n in lts.nodes}
    dedupe = set()  # (src,dst,rid,label)

    # Primary: collapse parent->outcome pairs
    for e1 in lts.edges:
        # Consider only parent attack edges
        fn1 = _extract_fn_name(e1.label)
        rid = parent_map_default.get(_norm(fn1))
        if not rid:
            continue
        spec = rule_specs.get(rid)
        if not spec or spec.lam <= 0.0:
            continue
        # Outcomes leaving intermediate node
        for e2 in edges_by_src.get(e1.dst, []):
            fn2 = _extract_fn_name(e2.label)
            oc = outcome_idx_by_rule.get(rid, {}).get(_norm(fn2))
            if not oc:
                continue
            q = float(spec.lam) * float(oc.prob)
            if q <= 0:
                continue
            key = (e1.src, e2.dst, rid, _norm(fn2))
            if key in dedupe:
                continue
            dedupe.add(key)
            ctmc.setdefault(e1.src, []).append(
                CTMCTransition(dst=e2.dst, rate=q, cost=float(oc.cost), rule_id=rid, outcome_label=fn2)
            )

    # Fallback: directly use outcome-labeled edges if parent labels not present
    if all(len(v) == 0 for v in ctmc.values()):
        for e in lts.edges:
            fn = _extract_fn_name(e.label)
            norm = _norm(fn)
            # Find which rule has this outcome label
            for rid, ocmap in outcome_idx_by_rule.items():
                oc = ocmap.get(norm)
                if not oc:
                    continue
                spec = rule_specs.get(rid)
                if not spec or spec.lam <= 0.0:
                    continue
                q = float(spec.lam) * float(oc.prob)
                if q <= 0:
                    continue
                key = (e.src, e.dst, rid, norm)
                if key in dedupe:
                    continue
                dedupe.add(key)
                ctmc.setdefault(e.src, []).append(
                    CTMCTransition(dst=e.dst, rate=q, cost=float(oc.cost), rule_id=rid, outcome_label=fn)
                )

    return ctmc, start_node


# ---------------------------
# Monte Carlo on CTMC
# ---------------------------

def simulate_ctmc_once(ctmc: CTMC, start: str, horizon_years: float, rng: random.Random) -> Tuple[float, float]:
    """Simulate one trajectory: return (total_cost, time_elapsed)."""
    s = start
    t = 0.0
    loss = 0.0
    # If start is empty or not in CTMC, early out
    if not s or s not in ctmc:
        return (0.0, 0.0)
    while t < horizon_years:
        outs = ctmc.get(s, [])
        rates = [tr.rate for tr in outs]
        Lambda = sum(rates)
        if Lambda <= 0.0:
            break
        # Sample sojourn
        u = max(rng.random(), 1e-12)
        dt = -math.log(u) / Lambda
        t += dt
        if t > horizon_years:
            break
        # Pick transition
        r = rng.random() * Lambda
        acc = 0.0
        chosen = outs[-1]
        for tr in outs:
            acc += tr.rate
            if r <= acc:
                chosen = tr
                break
        loss += chosen.cost
        s = chosen.dst
    return (loss, t)


def monte_carlo_ctmc(ctmc: CTMC, start_state: str, horizon_years: float, runs: int = 1000, seed: int = 42) -> Dict[str, Any]:
    rng = random.Random(seed)
    losses: List[float] = []
    times: List[float] = []
    for _ in range(runs):
        # Use different seeds per run for variety
        loss, t = simulate_ctmc_once(ctmc, start_state, horizon_years, rng)
        losses.append(loss)
        times.append(t)
    losses_sorted = sorted(losses)

    def quantile(vs: List[float], p: float) -> float:
        if not vs:
            return 0.0
        k = max(0, min(len(vs) - 1, int(p * (len(vs) - 1))))
        return vs[k]

    return {
        "runs": runs,
        "horizon_years": horizon_years,
        "mean_loss": sum(losses) / max(1, len(losses)),
        "p05": quantile(losses_sorted, 0.05),
        "p50": quantile(losses_sorted, 0.50),
        "p95": quantile(losses_sorted, 0.95),
        "mean_time": sum(times) / max(1, len(times)),
    "p_any_event": (sum(1 for L in losses if L > 0.0) / max(1, len(losses))),
    }


# ---------------------------
# Convenience end-to-end
# ---------------------------

def run_offline_lts(rs_path: Path, lts_path: Path, horizon_years: float = 1.0, runs: int = 1000, seed: int = 42) -> Dict[str, Any]:
    rule_specs = load_rule_specs(rs_path)
    lts = parse_gxl_lts(lts_path)
    ctmc, start = build_ctmc_from_lts(lts, rule_specs)
    return monte_carlo_ctmc(ctmc, start, horizon_years, runs=runs, seed=seed)
