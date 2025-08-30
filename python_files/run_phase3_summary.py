from pathlib import Path
from risk_estimation import load_rules, summarize_risk
from groove_lts_parser import parse_groove_lts
from offline_lts_ctmc import run_offline_lts
import argparse
import json


def _load_rule_metadata(rs_path: Path) -> dict:
    """Load raw rules JSON to access full titles and metadata (tags, MITRE, pre/postconditions)."""
    try:
        return json.loads(rs_path.read_text(encoding="utf-8"))
    except Exception:
        return {"risk_specification": {"rules": []}}


def _meta_by_id(raw_rules: dict) -> dict:
    by_id = {}
    for r in raw_rules.get("risk_specification", {}).get("rules", []):
        rid = r.get("id")
        if rid:
            by_id[rid] = r
    return by_id


def print_report(per_rule: dict, rules_loaded: dict, raw_meta_by_id: dict, horizon_years: float):
    print("=== Phase 3 Risk Report ===")
    print(f"Time Horizon: {horizon_years} years\n")
    for rid in sorted(per_rule.keys()):
        row = per_rule[rid]
        meta_loaded = rules_loaded.get(rid, {})  # normalized probs, title, lambda
        meta_raw = raw_meta_by_id.get(rid, {})   # full metadata
        title = meta_raw.get("title") or row.get("title") or rid
        mitre = meta_raw.get("mitre_attack_id") or "-"
        tags = ", ".join(meta_raw.get("tags", []) or []) or "-"
        preconds = meta_raw.get("preconditions", []) or []
        postconds = meta_raw.get("postconditions", []) or []
        outcomes = meta_loaded.get("outcomes", []) or []

        print(f"Attack: {rid} — {title}")
        print(f"MITRE ATT&CK: {mitre}")
        print(f"Tags: {tags}")
        if preconds:
            print("Preconditions:")
            for p in preconds:
                print(f"  - {p}")
        if postconds:
            print("Postconditions:")
            for p in postconds:
                print(f"  - {p}")
        print(f"Matches found in LTS: {row['matches']}")
        print(f"Rate per match (λ): {row['lambda_per_match']:.4f} per year")
        print(f"Total rate (λ_total): {row['lambda_total']:.4f} per year")
        print(f"Expected cost per occurrence: ${row['Ecost']:.2f}")
        print(f"ALE (per year): ${row['ALE']:.2f}")
        print(f"P(at least one in T): {row['prob_at_least_one_in_T']:.3f}")
        print(f"Expected loss over T: ${row['expected_loss_in_T']:.2f}")
        if outcomes:
            print("Outcomes (normalized):")
            for o in outcomes:
                name = o.get("name") or o.get("label") or "(unnamed)"
                p = o.get("probability") if isinstance(o.get("probability"), (int, float)) else None
                c = float(o.get("cost", 0) or 0)
                if p is None and outcomes:
                    p = 1.0 / len(outcomes)
                print(f"  - {name} — p={p:.3f}, cost=${c:.2f}")
        print("")


def main():
    base = Path(__file__).parent.parent
    parser = argparse.ArgumentParser(description="Phase 3 Risk Estimation Report (per-attack) + LTS Monte Carlo summary")
    parser.add_argument("--rules", type=str, default=str(base / "json_files" / "risk_rules_new.json"), help="Path to risk_rules_new.json")
    parser.add_argument("--lts", type=str, default=str(base / "groove_LTS" / "RiskModelling-gts.gpr"), help="Path to GROOVE LTS .gpr")
    parser.add_argument("--horizon", type=float, default=1.0, help="Time horizon in years")
    parser.add_argument("--runs", type=int, default=2000, help="Monte Carlo runs for LTS CTMC")
    parser.add_argument("--seed", type=int, default=123, help="Random seed")
    args = parser.parse_args()

    rs_path = Path(args.rules)
    lts_path = Path(args.lts)
    horizon_years = args.horizon

    if not rs_path.exists():
        print(f"Rules JSON not found: {rs_path}")
        return
    if not lts_path.exists():
        print(f"LTS not found: {lts_path}")
        return

    # Load data
    rules_loaded = load_rules(rs_path)              # normalized outcomes + title + lambda
    raw_rules = _load_rule_metadata(rs_path)        # full metadata
    meta_by_id = _meta_by_id(raw_rules)
    matches_by_rule = parse_groove_lts(lts_path)
    analytical = summarize_risk(rules_loaded, matches_by_rule, horizon_years=horizon_years)

    # Report per attack
    per_rule = analytical.get("per_rule", {})
    print_report(per_rule, rules_loaded, meta_by_id, horizon_years)

    # Totals (Analytical)
    print("--- Overall (Analytical) ---")
    print(f"Total λ: {analytical['lambda_total']:.4f} per year")
    print(f"Total ALE/yr: ${analytical['ALE_total']:.2f}")
    print(f"E[loss over T]: ${analytical['expected_loss_in_T']:.2f}")
    print(f"P(any event in T): {analytical['P_any_event_in_T']:.3f}")

    # Monte Carlo over LTS (CTMC embedding)
    mc = run_offline_lts(rs_path, lts_path, horizon_years=horizon_years, runs=args.runs, seed=args.seed)
    print("\n--- Monte Carlo over LTS (CTMC) ---")
    print(f"runs={mc['runs']} | mean_loss=${mc['mean_loss']:.2f} | p05=${mc['p05']:.2f} | p50=${mc['p50']:.2f} | p95=${mc['p95']:.2f} | P(any in T)≈{mc['p_any_event']:.3f}")


if __name__ == "__main__":
    main()
