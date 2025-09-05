import json
import tempfile
import unittest
from pathlib import Path


def make_minimal_gxl(edges):
    # edges: list of (src, dst, label)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">',
        '<graph id="G" edgeids="false" edgemode="directed">',
    ]
    # nodes (derive from edges)
    nodes = set()
    for s, d, _ in edges:
        nodes.add(s)
        nodes.add(d)
    for n in nodes:
        parts.append(f'<node id="{n}"/>')
    # edges with label attribute
    for s, d, label in edges:
        parts.append(f'<edge from="{s}" to="{d}">')
        parts.append('<attr name="label"><string>' + label + '</string></attr>')
        parts.append('</edge>')
    parts.append('</graph></gxl>')
    return "".join(parts)


class TestOfflineCTMC(unittest.TestCase):
    def setUp(self):
        here = Path(__file__).resolve()
        py_root = here.parents[1]
        import sys
        if str(py_root) not in sys.path:
            sys.path.insert(0, str(py_root))

    def test_parent_outcome_collapse_and_campaign_split(self):
        # Build tiny LTS: s0 --parentA--> s1, s0 --parentA--> s2 (K=2 at s0)
        # Then s1 --OutcomeX--> s3, s2 --OutcomeX--> s4
        # Parent function label matches RISK001 default: phishingAttack
        edges = [
            ("s0", "s1", "phishingAttack(x)"),
            ("s0", "s2", "phishingAttack(y)"),
            ("s1", "s3", "User_clicked_link_and_entered_credentials()"),
            ("s2", "s4", "User_clicked_link_and_entered_credentials()"),
        ]
        gxl = make_minimal_gxl(edges)
        with tempfile.TemporaryDirectory() as td:
            lts_path = Path(td) / "test.gpr"
            lts_path.write_text(gxl, encoding="utf-8")

            # Rules: RISK001 with Λ=10/yr, outcome label maps to above; prob=1.0, cost 100
            rules = {
                "risk_specification": {
                    "rules": [
                        {
                            "id": "RISK001",
                            "attack_rate": {"rate_per_year": 10.0},
                            "outcomes": [
                                {"name": "User clicked link and entered credentials", "probability": 1.0, "cost": 100.0}
                            ],
                        }
                    ]
                }
            }
            rs_path = Path(td) / "risk_rules.json"
            rs_path.write_text(json.dumps(rules), encoding="utf-8")

            from offline_lts_ctmc import load_rule_specs, parse_gxl_lts, build_ctmc_from_lts

            specs = load_rule_specs(rs_path)
            lts = parse_gxl_lts(lts_path)
            ctmc, start = build_ctmc_from_lts(lts, specs)

            # At s0, K=2 for RISK001, so lam_eff = 10/2 = 5 per parent edge
            # Each outcome has p=1, so q=5. We should have two transitions out of s0 totalizing 10.
            outs = ctmc.get("s0", [])
            self.assertEqual(len(outs), 2)
            rates = sorted(round(tr.rate, 6) for tr in outs)
            self.assertEqual(rates, [5.0, 5.0])
            self.assertAlmostEqual(sum(tr.rate for tr in outs), 10.0, places=6)
            self.assertTrue(all(tr.cost == 100.0 for tr in outs))


if __name__ == "__main__":
    unittest.main()
