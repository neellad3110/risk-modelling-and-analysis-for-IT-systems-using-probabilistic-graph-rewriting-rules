from pathlib import Path
from offline_lts_ctmc import run_offline_lts
import argparse


def main():
    base = Path(__file__).parent.parent
    parser = argparse.ArgumentParser(description="Offline GROOVE LTS CTMC Monte Carlo")
    parser.add_argument("--rules", type=str, default=str(base / "json_files" / "risk_rules_new.json"), help="Path to risk_rules_new.json")
    parser.add_argument("--lts", type=str, default=str(base / "groove_LTS" / "RiskModelling-gts.gpr"), help="Path to GROOVE LTS .gpr")
    parser.add_argument("--horizon", type=float, default=1.0, help="Time horizon in years")
    parser.add_argument("--runs", type=int, default=1000, help="Monte Carlo runs")
    parser.add_argument("--seed", type=int, default=123, help="Random seed")
    args = parser.parse_args()

    rs_path = Path(args.rules)
    lts_path = Path(args.lts)
    if not rs_path.exists():
        print(f"Rules JSON not found: {rs_path}")
        return
    if not lts_path.exists():
        print(f"LTS not found: {lts_path}")
        return

    summary = run_offline_lts(rs_path, lts_path, horizon_years=args.horizon, runs=args.runs, seed=args.seed)
    print("Offline LTS CTMC Monte Carlo summary:")
    print(summary)


if __name__ == "__main__":
    main()
