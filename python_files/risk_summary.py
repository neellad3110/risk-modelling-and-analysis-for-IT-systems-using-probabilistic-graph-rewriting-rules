from pathlib import Path
from risk_estimation import load_rules, summarize_risk
from groove_lts_parser import parse_groove_lts, parse_groove_lts_with_outcomes
import argparse
import json
from math import exp 


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


def print_report(per_rule: dict, rules_loaded: dict, raw_meta_by_id: dict, horizon_years: float, rate_mode: str, display_basis: str, matches_by_rule: dict, emit, outcomes_by_rule: dict):
    emit("=== Phase 3 Risk Report ===")
    emit(f"Time Horizon: {horizon_years} years")
    emit(f"Rate Mode: {rate_mode} (campaign=per-rule Λ, per-match=λ × matches)")
    if rate_mode == "campaign":
        if display_basis == "none":
            note = "rate-per-match hidden"
        elif display_basis == "cap":
            note = "rate-per-match uses cap: K_disp = min(matches, ceil(Λ·T))"
        else:
            note = "rate-per-match uses naive Λ/matches"
        emit(f"Display: {note}")
        emit("")
    else:
        emit("Display: per-match mode shows raw λ and λ_total = λ × matches")
        emit("")
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

        # Determine effective lambda according to rate mode
        matches = int(row.get("matches") or 0)
        # Compute unique initial states enabling this attack (unique sources of parent edges)
        match_list = matches_by_rule.get(rid, []) or []
        unique_sources = len({m.get("from_node") for m in match_list if m.get("from_node")})
        Lambda_r = float(meta_loaded.get("lambda") or 0.0)
        if rate_mode == "campaign":
            lambda_total = Lambda_r
            # Display-only per-match rate
            if display_basis == "none":
                lambda_per_match = None
            elif display_basis == "cap":
                K_disp = max(1, min(matches, math.ceil(Lambda_r * horizon_years)))
                lambda_per_match = Lambda_r / K_disp
            else:  # naive
                lambda_per_match = (Lambda_r / matches) if matches > 0 else Lambda_r
        else:
            lambda_total = float(row.get("lambda_total") or 0.0)
            lambda_per_match = float(row.get("lambda_per_match") or 0.0)

        # Recompute core metrics for clarity under this mode
        Ecost = float(row.get("Ecost") or row.get("Ecost", 0.0) or 0.0)
        ALE = lambda_total * Ecost
        try:
            from math import exp
            p_one = 1.0 - exp(-lambda_total * horizon_years)
        except Exception:
            p_one = row.get("prob_at_least_one_in_T", 0.0)
        expected_loss_T = ALE * horizon_years
        # NEW: expected counts in T (events and harmful events)
        expected_events_T = lambda_total * horizon_years
        pi_r = 0.0
        if outcomes:
            pi_r = sum(float(o.get("probability") or 0.0) for o in outcomes if float(o.get("cost") or 0.0) > 0.0)
        expected_harm_events_T = lambda_total * pi_r * horizon_years

        emit("------------------------------------------------------------")
        emit(f"Attack: {rid} — {title}")
        emit(f"MITRE ATT&CK: {mitre}")
        emit(f"Tags: {tags}")
        if preconds:
            emit("Preconditions:")
            for p in preconds:
                emit(f"  - {p}")
        if postconds:
            emit("Postconditions:")
            for p in postconds:
                emit(f"  - {p}")
        # Outcomes section directly after postconditions (pretty formatting)
        if outcomes:
            emit("Outcomes:")
            for o in outcomes:
                name = o.get("name") or o.get("label") or "(unnamed)"
                p = o.get("probability") if isinstance(o.get("probability"), (int, float)) else None
                c = float(o.get("cost", 0) or 0)
                if p is None and outcomes:
                    p = 1.0 / len(outcomes)
                emit(f"  - {name}")
                emit(f"    | p = {p:.3f}")
                emit(f"    | cost = ${c:.2f}")

        obs = outcomes_by_rule.get(rid, [])
        if obs:
            # Flatten outcome labels and count
            from collections import Counter
            labels = []
            for m in obs:
                for o in m.get("outcomes", []):
                    labels.append(o.get("label") or "")
            cnt = Counter(labels)
            emit("Observed outcomes in LTS (justification):")
            for lbl, k in cnt.most_common():
                emit(f"  - {lbl}  (count={k})")
        else:
            emit("Observed outcomes in LTS (justification): none")

        emit("")
        # Remaining details
        emit(f"Unique initial states enabling this attack: {unique_sources}")
        emit(f"Matches found in LTS (unique targets): {matches}")
        if lambda_per_match is not None:
            emit(f"Rate per match (λ): {lambda_per_match:.4f} per year  # display basis")
        emit(f"Total rate (Λ or λ_total): {lambda_total:.4f} per year")
        emit(f"Expected cost per occurrence: ${Ecost:.2f}")
        emit(f"ALE (per year): ${ALE:.2f}")
        emit(f"P(at least one in T): {p_one:.3f}")
        emit(f"Expected loss over T: ${expected_loss_T:.2f}")
        emit(f"Expected count in T (events): {expected_events_T:.3f}")          
        emit(f"Expected count in T (harmful events): {expected_harm_events_T:.3f}")
        emit("")


def main():
    base = Path(__file__).parent.parent
    parser = argparse.ArgumentParser(description="Phase 3 Analytical Risk Estimation Report (per-attack)")
    parser.add_argument("--rules", type=str, default=str(base / "json_files" / "risk_rules.json"), help="Path to risk_rules.json")
    parser.add_argument("--lts", type=str, default=str(base / "groove_LTS" / "RiskModelling@host.gxl"), help="Path to GROOVE LTS .gxl")
    parser.add_argument("--horizon", type=float, default=1.0, help="Time horizon in years")
    parser.add_argument("--rate-mode", choices=["campaign", "per-match"], default="campaign",
                        help="Use per-rule campaign rate (recommended) or multiply λ by matches")
    parser.add_argument("--display-rate-basis", choices=["cap", "naive", "none"], default="none",
                        help="How to display λ per match in campaign mode: cap=min(matches, ceil(Λ·T)); naive=Λ/matches; none=hide")
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
    outcomes_by_rule = parse_groove_lts_with_outcomes(lts_path)
    print("LTS matches detected per rule:", {k: len(v) for k, v in matches_by_rule.items()})
    analytical = summarize_risk(rules_loaded, matches_by_rule, horizon_years=horizon_years)
    
    # Prepare emitter to both print and collect for file export
    report_lines = []
    def emit(line: str = ""):
        print(line)
        report_lines.append(line)

    # Report per attack
    per_rule = analytical.get("per_rule", {})
    print_report(per_rule, rules_loaded, meta_by_id, horizon_years, args.rate_mode, args.display_rate_basis, matches_by_rule, emit, outcomes_by_rule)

    # LTS-only justification (covers attacks present in LTS even if missing in JSON)
    emit("=== LTS-only outcome justification ===")
    for rid, arr in sorted(outcomes_by_rule.items()):
        from collections import Counter
        labels = [o["label"] or "" for m in arr for o in m.get("outcomes", [])]
        cnt = Counter(labels)
        emit(f"{rid}:")
        if cnt:
            for lbl, k in cnt.most_common():
                emit(f"  - {lbl}  (count={k})")
        else:
            emit("  - none")
    emit("")
    # Totals (Analytical)
    emit("--- Overall (Analytical) ---")
    total_lambda = 0.0
    total_ale = 0.0
    total_eloss = 0.0
    p_no = 1.0
    for rid, meta in rules_loaded.items():
        Lam = float(meta.get("lambda") or 0.0)
        outs = meta.get("outcomes", []) or []
        Ecost = sum(float(o.get("probability") or 0.0) * float(o.get("cost") or 0.0) for o in outs)
        total_lambda += Lam
        total_ale += Lam * Ecost
        total_eloss += Lam * Ecost * horizon_years
        p_no *= exp(-Lam * horizon_years)
    emit(f"Total λ: {total_lambda:.4f} per year")
    emit(f"Total ALE/yr: ${total_ale:.2f}")
    emit(f"E[loss over T]: ${total_eloss:.2f}")
    emit(f"P(any event in T): {1.0 - p_no:.3f}")

    # Monte Carlo over LTS (CTMC embedding)
    # mc = run_offline_lts(rs_path, lts_path, horizon_years=horizon_years, runs=args.runs, seed=args.seed)
    # emit("")
    # emit("--- Monte Carlo over LTS (CTMC) ---")
    # emit(f"runs={mc['runs']} | mean_loss=${mc['mean_loss']:.2f} | p05=${mc['p05']:.2f} | p50=${mc['p50']:.2f} | p95=${mc['p95']:.2f} | P(any in T)≈{mc['p_any_event']:.3f}")

    # Export to results/results.txt
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "results.txt").write_text("\n".join(report_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
