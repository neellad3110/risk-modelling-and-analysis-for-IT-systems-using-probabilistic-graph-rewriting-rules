# import json
# import math
# from pathlib import Path
# from collections import defaultdict

# def load_rules(rs_path):
#     rs = json.loads(Path(rs_path).read_text(encoding="utf-8"))
#     rules = {}
#     for r in rs["risk_specification"]["rules"]:
#         rid = r["id"]
#         lam = r.get("attack_rate", {}).get("rate_per_year", 0.0) or 0.0
#         outcomes = r.get("outcomes", [])
#         # Expected cost per occurrence = sum p_i * cost_i
#         exp_cost = 0.0
#         for oc in outcomes:
#             p = float(oc.get("probability", 0.0) or 0.0)
#             c = float(oc.get("cost", 0.0) or 0.0)
#             exp_cost += p * c
#         rules[rid] = {
#             "title": r.get("title", rid),
#             "lambda_per_match": float(lam),
#             "expected_cost_per_occurrence": exp_cost,
#         }
#     return rules

# def summarize_risk(rules, matches_by_rule, horizon_years=1.0):
#     """
#     matches_by_rule: dict { rule_id: [match1, match2, ...] }
#     Each match is one independent potential occurrence (per your LHS match).
#     """
#     summary = {"per_rule": {}, "totals": {}}
#     total_ALE = 0.0
#     total_prob_at_least_one = 0.0  # not strictly additive; we report per-rule probs and overall via independence assumption below
#     total_expected_loss_horizon = 0.0

#     # For an overall probability under independence: P_any = 1 - Π (1 - P_r)
#     overall_no_event_prob = 1.0

#     for rid, meta in rules.items():
#         lam_match = meta["lambda_per_match"]
#         C = meta["expected_cost_per_occurrence"]
#         count = len(matches_by_rule.get(rid, []))
#         lam_total = lam_match * count  # λ_total = λ_per_match × number_of_matches

#         # Per-rule metrics
#         ALE = lam_total * C  # expected annual loss
#         P_at_least_one = 1.0 - math.exp(-lam_total * horizon_years)
#         expected_loss_horizon = ALE * horizon_years  # if repeats allowed (Poisson)

#         summary["per_rule"][rid] = {
#             "title": meta["title"],
#             "matches": count,
#             "lambda_per_match": lam_match,
#             "lambda_total": lam_total,
#             "expected_cost_per_occurrence": C,
#             "ALE_per_year": ALE,
#             "prob_at_least_one_in_T": P_at_least_one,
#             "expected_loss_in_T": expected_loss_horizon,
#         }

#         total_ALE += ALE
#         total_expected_loss_horizon += expected_loss_horizon
#         overall_no_event_prob *= (1.0 - P_at_least_one)

#     summary["totals"] = {
#         "ALE_per_year": total_ALE,
#         "expected_loss_in_T": total_expected_loss_horizon,
#         "prob_any_event_in_T_assuming_independence": 1.0 - overall_no_event_prob,
#         "horizon_years": horizon_years,
#     }
#     return summary

# if __name__ == "__main__":
#     base = Path(__file__).parent.parent
#     rs_path = base / "json_files/risk_rules_new.json"

#     # 1) Load rules
#     rules = load_rules(rs_path)

#     # 2) Plug in matches exported from GROOVE (example structure below).
#     # Replace this with your real matches-by-rule dictionary.
#     # Key = rule id, value = list of match dicts (the content is not used here, only the count).
#     matches_by_rule = {
#         # "RISK001": [ { "victimEmail": "email_EMP001" }, { "victimEmail": "email_EMP004" } ],
#         # "RISK005": [ { "targetHost": "host1" } ],
#     }

#     # 3) Compute risk for a 1-year horizon
#     summary = summarize_risk(rules, matches_by_rule, horizon_years=1.0)

#     # 4) Print concise report
#     print("=== Risk Estimation Summary ===")
#     for rid, row in summary["per_rule"].items():
#         print(f'{rid} | matches={row["matches"]} | λ_total={row["lambda_total"]:.3f} '
#               f'| ALE/yr={row["ALE_per_year"]:.2f} '
#               f'| P(at least one in T)={row["prob_at_least_one_in_T"]:.3f} '
#               f'| E[loss in T]={row["expected_loss_in_T"]:.2f}')
#     t = summary["totals"]
#     print(f'\nTOTAL | ALE/yr={t["ALE_per_year"]:.2f} | E[loss in T]={t["expected_loss_in_T"]:.2f} '
#           f'| P(any event in T)≈{t["prob_any_event_in_T_assuming_independence"]:.3f} '
#           f'| T={t["horizon_years"]}y')

from __future__ import annotations
from pathlib import Path
import json
from math import exp

def load_rules(rs_path: Path):
    """Load rules and normalize outcome probabilities if present."""
    if not rs_path.exists():
        return {}
    data = json.loads(rs_path.read_text(encoding="utf-8"))
    rules = {}
    for r in data.get("risk_specification", {}).get("rules", []):
        rid = r.get("id")
        if not rid:
            continue
        lam = (r.get("attack_rate") or {}).get("rate_per_year")
        outs = r.get("outcomes", []) or []
        title = r.get("title", rid)
        # Normalize probabilities if available; otherwise leave as-is (uniform handled by consumers)
        ps = [o.get("probability") for o in outs if isinstance(o.get("probability"), (int, float))]
        s = sum(ps) if ps else 0.0
        if s > 0:
            for o in outs:
                if isinstance(o.get("probability"), (int, float)):
                    o["probability"] = float(o["probability"]) / s
        rules[rid] = {"lambda": lam, "outcomes": outs, "title": title}
    return rules

def summarize_risk(rules: dict, matches_by_rule: dict, horizon_years: float = 1.0):
    """Baseline ALE (analytical) for comparison with Monte Carlo.

    Returns per-rule: title, matches, lambda_per_match, lambda_total, Ecost, ALE,
    prob_at_least_one_in_T, expected_loss_in_T. And overall totals.
    """
    total_lambda = 0.0
    total_ale = 0.0
    total_expected_loss = 0.0
    overall_no_event_prob = 1.0
    per_rule = {}
    for rid, info in rules.items():
        lam = float(info.get("lambda") or 0.0)
        title = info.get("title", rid)
        k = len(matches_by_rule.get(rid, []))
        if lam > 0 and k > 0:
            outs = info.get("outcomes", [])
            if outs:
                # If probs missing, assume uniform
                probs = [o.get("probability") if isinstance(o.get("probability"), (int, float)) else 1.0/len(outs) for o in outs]
                costs = [float(o.get("cost", 0) or 0) for o in outs]
                ecost = sum(p * c for p, c in zip(probs, costs))
            else:
                ecost = 0.0
            lam_tot = k * lam
            ale = lam_tot * ecost
            p_one = 1.0 - exp(-lam_tot * horizon_years)
            e_loss_T = ale * horizon_years
            total_lambda += lam_tot
            total_ale += ale
            total_expected_loss += e_loss_T
            overall_no_event_prob *= (1.0 - p_one)
            per_rule[rid] = {
                "title": title,
                "matches": k,
                "lambda_per_match": lam,
                "lambda_total": lam_tot,
                "Ecost": ecost,
                "ALE": ale,
                "prob_at_least_one_in_T": p_one,
                "expected_loss_in_T": e_loss_T,
            }
    return {
        "ALE_total": total_ale,
        "lambda_total": total_lambda,
        "expected_loss_in_T": total_expected_loss,
        "P_any_event_in_T": (1.0 - overall_no_event_prob),
        "horizon_years": horizon_years,
        "per_rule": per_rule,
    }