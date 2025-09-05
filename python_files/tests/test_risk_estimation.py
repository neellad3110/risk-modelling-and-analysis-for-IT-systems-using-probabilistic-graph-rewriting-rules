import json
import math
import os
import tempfile
import unittest
from pathlib import Path


class TestRiskEstimation(unittest.TestCase):
    def setUp(self):
        # Ensure python_files is importable
        here = Path(__file__).resolve()
        py_root = here.parents[1]
        import sys
        if str(py_root) not in sys.path:
            sys.path.insert(0, str(py_root))

    def test_probability_normalization_and_ecost(self):
        from risk_estimation import load_rules, summarize_risk

        # Build a temporary rules JSON with non-normalized probabilities
        data = {
            "risk_specification": {
                "rules": [
                    {
                        "id": "RISKTEST1",
                        "title": "Test Rule",
                        "attack_rate": {"rate_per_year": 2.0},
                        "outcomes": [
                            {"name": "A", "probability": 2, "cost": 100},
                            {"name": "B", "probability": 3, "cost": 200},
                        ],
                    }
                ]
            }
        }
        with tempfile.TemporaryDirectory() as td:
            rules_path = Path(td) / "risk_rules.json"
            rules_path.write_text(json.dumps(data), encoding="utf-8")

            rules = load_rules(rules_path)
            # Normalized probs should be 0.4 and 0.6
            outs = rules["RISKTEST1"]["outcomes"]
            p_norm = [o["probability"] for o in outs]
            self.assertTrue(all(isinstance(p, float) for p in p_norm))
            self.assertAlmostEqual(p_norm[0], 0.4, places=6)
            self.assertAlmostEqual(p_norm[1], 0.6, places=6)

            # One match yields lambda_total = 2.0; with two matches, 4.0
            matches_by_rule = {"RISKTEST1": [{"target_node": "t1"}, {"target_node": "t2"}]}
            summary = summarize_risk(rules, matches_by_rule, horizon_years=1.0)

            # E[cost] = 0.4*100 + 0.6*200 = 160
            per = summary["per_rule"]["RISKTEST1"]
            self.assertAlmostEqual(per["Ecost"], 160.0, places=6)
            # ALE = lambda_total * E[cost] = (2.0*2) * 160 = 640
            self.assertAlmostEqual(per["ALE"], 640.0, places=6)
            # P(any in 1y) = 1 - exp(-4)
            self.assertAlmostEqual(per["prob_at_least_one_in_T"], 1.0 - math.exp(-4.0), places=6)


if __name__ == "__main__":
    unittest.main()
