from pathlib import Path
from groove_lts_parser import parse_groove_lts
from ctmdp_engine import load_raw_rules, initial_enabled_actions, monte_carlo


def main():
    base = Path(__file__).parent.parent
    rs_path = base / "json_files" / "risk_rules_new.json"
    lts_path = base / "groove_LTS" / "RiskModelling-gts.gpr"

    raw_rules = load_raw_rules(rs_path)
    matches_by_rule = parse_groove_lts(lts_path)
    init_actions = initial_enabled_actions(matches_by_rule)

    # Run Monte Carlo for 1-year horizon
    summary = monte_carlo(raw_rules, init_actions, T=1.0, N=200, seed=42)
    print("CTMDP Monte Carlo summary:")
    print(summary)


if __name__ == "__main__":
    main()
