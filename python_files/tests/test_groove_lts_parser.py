import tempfile
import unittest
from pathlib import Path


def make_minimal_gxl(edges):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">',
        '<graph id="G" edgeids="false" edgemode="directed">',
    ]
    nodes = set()
    for s, d, _ in edges:
        nodes.add(s)
        nodes.add(d)
    for n in nodes:
        parts.append(f'<node id="{n}"/>')
    for s, d, label in edges:
        parts.append(f'<edge from="{s}" to="{d}">')
        parts.append('<attr name="label"><string>' + label + '</string></attr>')
        parts.append('</edge>')
    parts.append('</graph></gxl>')
    return "".join(parts)


class TestGrooveLTSParser(unittest.TestCase):
    def setUp(self):
        here = Path(__file__).resolve()
        py_root = here.parents[1]
        import sys
        if str(py_root) not in sys.path:
            sys.path.insert(0, str(py_root))

    def test_label_normalization_and_unique_counts(self):
        # Two parent edges into two different targets but from same source, mixed case and params
        edges = [
            ("n0", "n1", "PhishingAttack(u=1)"),
            ("n0", "n2", "phishingAttack(u=2)"),
            # Some unrelated edge should be ignored
            ("n1", "n3", "otherLabel()"),
        ]
        gxl = make_minimal_gxl(edges)
        with tempfile.TemporaryDirectory() as td:
            lts_path = Path(td) / "x.gpr"
            lts_path.write_text(gxl, encoding="utf-8")

            from groove_lts_parser import parse_groove_lts
            matches_by_rule = parse_groove_lts(lts_path)

            # Should map to RISK001 via normalized parent label
            self.assertIn("RISK001", matches_by_rule)
            matches = matches_by_rule["RISK001"]
            # Unique targets: n1 and n2 -> 2
            self.assertEqual(len(matches), 2)
            # Unique initial sources (from_node) -> {n0} -> 1
            unique_sources = {m.get("from_node") for m in matches if m.get("from_node")}
            self.assertEqual(len(unique_sources), 1)


if __name__ == "__main__":
    unittest.main()
