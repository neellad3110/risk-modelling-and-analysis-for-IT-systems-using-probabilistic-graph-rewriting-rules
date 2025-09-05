from __future__ import annotations
from pathlib import Path
import json

def load_rules(rs_path: Path) -> dict:
    data = json.loads(Path(rs_path).read_text(encoding="utf-8"))
    out = {}
    for r in (data.get("risk_specification") or {}).get("rules") or []:
        rid = r.get("id")
        if not rid:
            continue
        lam = float((r.get("attack_rate") or {}).get("rate_per_year") or 0.0)

        outs = r.get("outcomes") or []
        # parse numeric probabilities if present
        raw_ps = []
        for o in outs:
            v = o.get("probability")
            try:
                raw_ps.append(float(v))
            except Exception:
                raw_ps.append(None)

        s = sum(v for v in raw_ps if isinstance(v, (int, float)))
        if outs:
            if s and s > 0:
                probs = [float(v) / s if isinstance(v, (int, float)) else 0.0 for v in raw_ps]
            else:
                # uniform if missing/invalid
                probs = [1.0 / len(outs)] * len(outs)
        else:
            probs = []

        outs_norm = []
        for o, p in zip(outs, probs):
            outs_norm.append({
                "name": o.get("name") or o.get("label") or "",
                "probability": float(p),
                "cost": float(o.get("cost") or 0.0),
            })

        out[rid] = {
            "id": rid,
            "title": r.get("title", rid),
            "lambda": lam,
            "outcomes": outs_norm
        }
    return out

def summarize_risk(rules_loaded: dict, matches_by_rule: dict, horizon_years: float = 1.0) -> dict:
    from math import exp
    per_rule = {}
    total_lambda = 0.0
    ALE_total = 0.0
    expected_loss_in_T = 0.0
    p_no = 1.0
    for rid, meta in rules_loaded.items():
        Lam = float(meta.get("lambda") or 0.0)
        outs = meta.get("outcomes") or []
        Ecost = sum(float(o["probability"]) * float(o["cost"]) for o in outs)
        per_rule[rid] = {
            "title": meta.get("title", rid),
            "matches": len(matches_by_rule.get(rid, [])),
            "Ecost": Ecost,
        }
        total_lambda += Lam
        ALE_total += Lam * Ecost
        expected_loss_in_T += Lam * Ecost * horizon_years
        p_no *= exp(-Lam * horizon_years)
    return {
        "per_rule": per_rule,
        "lambda_total": total_lambda,
        "ALE_total": ALE_total,
        "expected_loss_in_T": expected_loss_in_T,
        "P_any_event_in_T": 1.0 - p_no,
    }