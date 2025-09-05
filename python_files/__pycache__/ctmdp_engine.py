"""
CTMDP Monte Carlo simulation engine for Phase 3.

Uses:
- risk_estimation.load_rules for base rates and expected costs (we'll also read raw outcomes)
- groove_lts_parser.parse_groove_lts for initial matches per rule
- ctmdp_config for enabling predicates and simple state transformers

Does not modify risk rules JSON; only consumes it.
"""
from __future__ import annotations
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any

from ctmdp_config import CTMDPState, ENABLING_PREDICATES, categorize_outcome_label, transform_state


def load_raw_rules(rs_path: Path) -> Dict[str, Any]:
    data = json.loads(rs_path.read_text(encoding="utf-8"))
    rules = {}
    for r in data["risk_specification"]["rules"]:
        rid = r["id"]
        rules[rid] = r
    return rules


def outcome_probabilities(rule: Dict[str, Any]) -> List[Tuple[float, float, Dict[str, Any]]]:
    """Return list of (probability, cost, outcome_obj) for a rule.
    If probabilities missing, assign uniform over provided outcomes with cost entries.
    """
    outs = [oc for oc in rule.get("outcomes", []) if isinstance(oc, dict) and ("cost" in oc or "probability" in oc)]
    if not outs:
        return []
    probs = [oc.get("probability") for oc in outs]
    if any(p is None for p in probs):
        # Uniform if unspecified
        k = len(outs)
        return [(1.0 / k, float(oc.get("cost", 0.0) or 0.0), oc) for oc in outs]
    # Normalize just in case
    total = sum(float(p or 0.0) for p in probs)
    if total <= 0:
        k = len(outs)
        return [(1.0 / k, float(oc.get("cost", 0.0) or 0.0), oc) for oc in outs]
    return [(float(oc.get("probability", 0.0) or 0.0) / total, float(oc.get("cost", 0.0) or 0.0), oc) for oc in outs]


def initial_enabled_actions(matches_by_rule: Dict[str, List[Dict[str, Any]]]) -> List[Tuple[str, str]]:
    """Produce initial list of actions (rule_id, match_id). We derive match_id from match['target_node'] or similar fields.
    """
    enabled: List[Tuple[str, str]] = []
    for rid, matches in matches_by_rule.items():
        for m in matches:
            mid = m.get("target_node") or m.get("id") or m.get("match") or next(iter(m.values()), None)
            if mid:
                enabled.append((rid, str(mid)))
    return enabled


def filter_enabled(state: CTMDPState, actions: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for rid, mid in actions:
        pred = ENABLING_PREDICATES.get(rid, lambda s, m: True)
        if pred(state, mid):
            out.append((rid, mid))
    return out


def simulate_once(raw_rules: Dict[str, Any], init_actions: List[Tuple[str, str]], T: float, seed: int | None = None) -> CTMDPState:
    if seed is not None:
        random.seed(seed)
    state = CTMDPState()
    actions = list(init_actions)
    while state.time < T:
        enabled = filter_enabled(state, actions)
        if not enabled:
            break
        # Compute rates per enabled action
        rates: List[float] = []
        for rid, _ in enabled:
            rule = raw_rules.get(rid, {})
            lam = float(rule.get("attack_rate", {}).get("rate_per_year", 0.0) or 0.0)
            rates.append(lam)
        Lambda = sum(rates)
        if Lambda <= 0:
            break
        # Sample next event time increment
        u = random.random()
        dt = -math.log(1 - u) / Lambda
        state.time += dt
        if state.time > T:
            break
        # Choose which action fires
        r = random.random() * Lambda
        acc = 0.0
        idx = 0
        for i, rate in enumerate(rates):
            acc += rate
            if r <= acc:
                idx = i
                break
        rid, mid = enabled[idx]
        rule = raw_rules[rid]

        # Select outcome
        ops = outcome_probabilities(rule)
        if not ops:
            # No outcomes: zero cost, neutral effect
            cost = 0.0
            category = "neutral"
        else:
            x = random.random()
            accp = 0.0
            chosen = ops[-1]
            for p, c, oc in ops:
                accp += p
                if x <= accp:
                    chosen = (p, c, oc)
                    break
            cost = chosen[1]
            # Try to categorize from any embedded label hint; fallback to heuristic by cost
            label_hint = str(chosen[2].get("label", ""))
            category = categorize_outcome_label(label_hint)
            if category == "neutral":
                category = "success" if cost > 0 else "fail"

        # Apply cost and state transform
        state.cumulative_cost += cost
        transform_state(rid, category, state, mid)
        state.events.append({
            "t": state.time,
            "rule": rid,
            "match": mid,
            "category": category,
            "cost": cost,
        })

        # Optional: continue to allow repeated attempts; we keep actions list as-is
        # In a stricter model, we could remove (rid, mid) if success/detection disables it.

    return state


def monte_carlo(raw_rules: Dict[str, Any], init_actions: List[Tuple[str, str]], T: float, N: int = 1000, seed: int | None = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    losses: List[float] = []
    times: List[float] = []
    for i in range(N):
        s = simulate_once(raw_rules, init_actions, T, seed=rng.randint(0, 2**31 - 1))
        losses.append(s.cumulative_cost)
        times.append(s.time)
    losses_sorted = sorted(losses)
    def pct(vs: List[float], p: float) -> float:
        if not vs:
            return 0.0
        k = max(0, min(len(vs) - 1, int(p * (len(vs) - 1))))
        return vs[k]
    return {
        "mean_loss": sum(losses) / max(1, len(losses)),
        "p05": pct(losses_sorted, 0.05),
        "p50": pct(losses_sorted, 0.50),
        "p95": pct(losses_sorted, 0.95),
        "mean_time": sum(times) / max(1, len(times)),
        "runs": N,
        "horizon": T,
    "p_any_event": (sum(1 for L in losses if L > 0.0) / max(1, len(losses))),
    }

