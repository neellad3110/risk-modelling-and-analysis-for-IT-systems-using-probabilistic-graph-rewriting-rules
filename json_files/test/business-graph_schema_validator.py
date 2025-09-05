from pathlib import Path
import sys
from typing import List, Set, Dict

def strip_json_comments(text: str) -> str:
    out = []
    i, n = 0, len(text)
    in_str = False
    esc = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in ("\n", "\r"):
                i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2 if i + 1 < n else 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)

def load_json_like(path: Path):
    import json
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        clean = strip_json_comments(text)
        return json.loads(clean)

def project_root() -> Path:
    # this file: <root>/nvl2/json_files/test/business-graph_schema_validator.py
    return Path(__file__).resolve().parents[3]

def default_paths() -> tuple[Path, Path]:
    root = project_root()
    schema_path = root / "nvl2" / "json_files" / "schema" / "jtsa_BusinessGraphs.schema.json"
    json_path = root / "nvl2" / "json_files" / "business_graph.json"
    return schema_path, json_path

def semantic_checks(instance: list, json_dir: Path) -> List[str]:
    errs: List[str] = []
    if not isinstance(instance, list):
        errs.append("$. (root): expected array of graphs")
        return errs
    for gi, graph in enumerate(instance):
        # typedOver file existence (optional)
        typed_over = graph.get("typedOver")
        if isinstance(typed_over, str) and typed_over.strip():
            # resolve relative to same directory as JSON
            tg_path = (json_dir / typed_over).resolve()
            if not tg_path.exists():
                errs.append(f"$[{gi}].typedOver: referenced file not found: {tg_path}")

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        if not isinstance(nodes, list):
            errs.append(f"$[{gi}].nodes: expected array")
            continue
        if not isinstance(edges, list):
            errs.append(f"$[{gi}].edges: expected array")
            continue

        # Node id uniqueness and presence
        node_ids: Set[str] = set()
        for ni, n in enumerate(nodes):
            nid = n.get("id")
            if not isinstance(nid, str) or not nid:
                errs.append(f"$[{gi}].nodes[{ni}].id: missing or not a non-empty string")
                continue
            if nid in node_ids:
                errs.append(f"$[{gi}].nodes[{ni}].id: duplicate node id '{nid}'")
            else:
                node_ids.add(nid)

        # Optional: type is often expected in your data; warn if missing but not error (schema doesn't require it)
        for ni, n in enumerate(nodes):
            if "type" in n:
                t = n.get("type")
                if not isinstance(t, str) or not t:
                    errs.append(f"$[{gi}].nodes[{ni}].type: must be a non-empty string when present")

        # Edge endpoints must reference known node ids; edge id uniqueness
        edge_ids: Set[str] = set()
        for ei, e in enumerate(edges):
            eid = e.get("id")
            if not isinstance(eid, str) or not eid:
                errs.append(f"$[{gi}].edges[{ei}].id: missing or not a non-empty string")
            elif eid in edge_ids:
                errs.append(f"$[{gi}].edges[{ei}].id: duplicate edge id '{eid}'")
            else:
                edge_ids.add(eid)

            src = e.get("source")
            tgt = e.get("target")
            if not isinstance(src, str) or src not in node_ids:
                errs.append(f"$[{gi}].edges[{ei}].source: unknown or invalid node id '{src}'")
            if not isinstance(tgt, str) or tgt not in node_ids:
                errs.append(f"$[{gi}].edges[{ei}].target: unknown or invalid node id '{tgt}'")

            if "type" in e:
                et = e.get("type")
                if not isinstance(et, str) or not et:
                    errs.append(f"$[{gi}].edges[{ei}].type: must be a non-empty string when present")

            # attributes if present should not contain nulls (schema enforces); minimal sanity done by schema

    return errs

def main():
    schema_path, json_path = default_paths()

    try:
        from jsonschema import Draft202012Validator, exceptions as js_exceptions
    except Exception:
        print("ERROR: jsonschema is not installed. Install with:", file=sys.stderr)
        print("  py -m pip install jsonschema", file=sys.stderr)
        sys.exit(1)

    # Load files
    try:
        schema = load_json_like(schema_path)
    except Exception as e:
        print(f"ERROR: Failed to parse schema '{schema_path}': {e}", file=sys.stderr)
        sys.exit(2)

    try:
        instance = load_json_like(json_path)
    except Exception as e:
        print(f"ERROR: Failed to parse JSON '{json_path}': {e}", file=sys.stderr)
        sys.exit(2)

    # Validate schema itself
    try:
        Draft202012Validator.check_schema(schema)
    except js_exceptions.SchemaError as e:
        print(f"ERROR: Provided schema is not a valid JSON Schema (2020-12): {e}", file=sys.stderr)
        sys.exit(4)

    # Schema validation
    validator = Draft202012Validator(schema)
    js_errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    # Semantic checks
    json_dir = json_path.parent
    sem_errors = semantic_checks(instance, json_dir)

    print(f"Schema: {schema_path}")
    print(f"JSON:   {json_path}")

    if not js_errors and not sem_errors:
        print(f"VALID: {json_path.name} conforms to schema and semantic checks")
        sys.exit(0)

    print(f"INVALID: {json_path.name} has issues")
    for idx, err in enumerate(js_errors, 1):
        path = "$" + "".join(f"[{repr(p)}]" if isinstance(p, int) else f".{p}" for p in err.path)
        print(f"- [S{idx}] {path}: {err.message}")
        if err.context:
            for sub in err.context:
                subpath = "$" + "".join(f"[{repr(p)}]" if isinstance(p, int) else f".{p}" for p in sub.path)
                print(f"    note: {subpath}: {sub.message}")
    for idx, msg in enumerate(sem_errors, 1):
        print(f"- [M{idx}] {msg}")
    sys.exit(3)

if __name__ == "__main__":
    main()