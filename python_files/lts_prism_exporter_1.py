from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import argparse, json

from lts_exporter import (
    load_rules, parse_gxl_lts, is_parent_edge, rule_id_from_parent, outcome_key
)

def build_collapsed_ctmc(gxl_path: Path, rules: Dict, outcome_label_map: Dict | None = None):
    nodes, edges, init = parse_gxl_lts(gxl_path)
    if not nodes or not edges:
        raise RuntimeError("Empty LTS. Re-export the GXL with labeled edges.")
    idx = {n: i for i, n in enumerate(nodes)}
    by_src: Dict[str, List[Dict]] = {}
    for e in edges:
        by_src.setdefault(e["src"], []).append(e)

    trans: List[Tuple[int,int,float,float,str,str,int]] = []

    for s in nodes:
        parents = [e for e in by_src.get(s, []) if is_parent_edge(e["label"])]
        by_rule: Dict[str, List[Dict]] = {}
        for p in parents:
            rid = rule_id_from_parent(p["label"])
            if rid:
                by_rule.setdefault(rid, []).append(p)
        for rid, plist in by_rule.items():
            spec = rules.get(rid)
            if not spec:
                continue
            Lambda_r = float(spec.get("lambda", 0.0))
            if Lambda_r <= 0:
                continue
            K = max(1, len(plist))
            per_match_rate = Lambda_r / K
            for p in plist:
                fork = p["dst"]
                for out in by_src.get(fork, []):
                    on_lbl = out["label"]
                    oname, p_out, cost = None, None, 0.0
                    if outcome_label_map and rid in outcome_label_map:
                        rev = {v.lower(): k for k, v in (outcome_label_map[rid] or {}).items()}
                        key = outcome_key(on_lbl)
                        if key in rev:
                            oname = rev[key]
                    if oname is None:
                        low = outcome_key(on_lbl)
                        best = None
                        for o in spec.get("outcomes", []):
                            if o["name"].lower() in low:
                                best = o; break
                        if best is None and spec.get("outcomes"):
                            best = spec["outcomes"][0]
                        if best:
                            oname = best["name"]; p_out = float(best["p"]); cost = float(best["cost"])
                    else:
                        for o in spec.get("outcomes", []):
                            if o["name"] == oname:
                                p_out = float(o["p"]); cost = float(o["cost"]); break
                    if p_out is None:
                        n = max(1, len(spec.get("outcomes", [])))
                        p_out = 1.0 / n
                    q = per_match_rate * p_out
                    if q <= 0:
                        continue
                    harm = 1 if cost > 0 else 0
                    trans.append((idx[s], idx[out["dst"]], q, cost, rid, oname or "outcome", harm))
    s0_idx = idx.get(init, 0)
    return nodes, trans, s0_idx

def write_prism_ctmc(out_model: Path, S: List[str], trans, s_init_idx: int):
    lines: List[str] = []
    lines.append("ctmc\n\n")
    lines.append("module risk\n")
    lines.append(f"  s : [0..{len(S)-1}] init {s_init_idx};\n")
    lines.append("  h : [0..1] init 0;\n\n")
    for i, (src, dst, q, cost, rid, oname, harm) in enumerate(trans):
        set_h = "1" if harm == 1 else "h"
        lines.append(f"  [{rid}_{i}] (s={src}) -> {q:.10g} : (s'={dst}) & (h'={set_h});\n")
    lines.append("endmodule\n\n")
    lines.append('rewards "cost"\n')
    for i, (_, _, _, cost, rid, _, _) in enumerate(trans):
        if abs(cost) > 0:
            lines.append(f"  [{rid}_{i}] true : {cost};\n")
    lines.append("endrewards\n\n")
    lines.append('label "harm" = (h=1);\n')
    Path(out_model).write_text("".join(lines), encoding="utf-8")

def write_props(out_props: Path, T: float = 1.0):
    Path(out_props).write_text(f'P=? [ F<={T} "harm" ]\nR{{"cost"}}=? [ C<={T} ]\n', encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Export PRISM CTMC from GROOVE LTS with Λ/K · p rates and cost rewards")
    base = Path(__file__).parent.parent
    ap.add_argument("--rules", default=str(base / "json_files" / "risk_rules.json"))
    ap.add_argument("--lts", default=str(base / "groove_LTS" / "RiskModelling@host.gxl"))
    ap.add_argument("--out-model", default=str(base / "results" / "model_ctmc.prism"))
    ap.add_argument("--out-props", default=str(base / "results" / "props.props"))
    ap.add_argument("--outcome-map", default=str(base / "json_files" / "risk_outcome_label_map.json"))
    ap.add_argument("--horizon", type=float, default=1.0)
    args = ap.parse_args()

    Path(args.out_model).parent.mkdir(parents=True, exist_ok=True)
    rules = load_rules(Path(args.rules))
    if not rules:
        raise RuntimeError("risk_rules.json has no rules. Populate Λ and outcomes.")
    outcome_map = {}
    p = Path(args.outcome_map)
    if p.exists():
        try: outcome_map = json.loads(Path(args.outcome_map).read_text(encoding="utf-8"))
        except Exception: outcome_map = {}

    S, trans, s0 = build_collapsed_ctmc(Path(args.lts), rules, outcome_map)
    if not trans:
        raise RuntimeError("No transitions constructed. Check label mapping and rules JSON.")
    write_prism_ctmc(Path(args.out_model), S, trans, s0)
    write_props(Path(args.out_props), args.horizon)
    print(f"Wrote PRISM CTMC: {args.out_model}\nWrote props: {args.out_props}")

if __name__ == "__main__":
    main()