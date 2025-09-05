from pathlib import Path
import sys
from typing import Set, List

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
    # this file: <root>/nvl2/json_files/test/type-graph_schema_validator.py
    return Path(__file__).resolve().parents[3]

def default_paths() -> tuple[Path, Path]:
    root = project_root()
    schema_path = root / "nvl2" / "json_files" / "schema" / "jtsa_typeGraph.schema.json"
    json_path = root / "nvl2" / "json_files" / "type_graph.json"
    return schema_path, json_path

def semantic_checks(instance: dict) -> List[str]:
    errs: List[str] = []
    try:
        nodes = instance.get("nodes", [])
        edges = instance.get("edges", [])
        if not isinstance(nodes, list):
            errs.append("$.nodes: expected array")
            return errs
        if not isinstance(edges, list):
            errs.append("$.edges: expected array")
            return errs

        # Node type uniqueness and index
        types: Set[str] = set()
        for i, n in enumerate(nodes):
            t = n.get("type")
            if not isinstance(t, str) or not t:
                errs.append(f"$.nodes[{i}].type: missing or not a non-empty string")
                continue
            if t in types:
                errs.append(f"$.nodes[{i}].type: duplicate node type '{t}'")
            else:
                types.add(t)

        # Subtype references must exist
        for i, n in enumerate(nodes):
            if "isSubTypeOf" in n:
                st = n.get("isSubTypeOf")
                if not isinstance(st, str) or not st:
                    errs.append(f"$.nodes[{i}].isSubTypeOf: must be a non-empty string if present")
                elif st not in types:
                    errs.append(f"$.nodes[{i}].isSubTypeOf: references unknown type '{st}'")

        # Edge endpoints must exist; multiplicity sanity if present
        for i, e in enumerate(edges):
            src = e.get("source")
            tgt = e.get("target")
            if not isinstance(src, str) or src not in types:
                errs.append(f"$.edges[{i}].source: unknown or invalid node type '{src}'")
            if not isinstance(tgt, str) or tgt not in types:
                errs.append(f"$.edges[{i}].target: unknown or invalid node type '{tgt}'")
            mult = e.get("multiplicity")
            if isinstance(mult, dict):
                lower = mult.get("lower")
                upper = mult.get("upper")
                if isinstance(lower, int) and lower < 0:
                    errs.append(f"$.edges[{i}].multiplicity.lower: must be >= 0")
                # If both ints, enforce lower <= upper
                if isinstance(lower, int) and isinstance(upper, int):
                    if lower > upper:
                        errs.append(f"$.edges[{i}].multiplicity: lower ({lower}) > upper ({upper})")
                # If upper is "*", accept; schema already enforces types
    except Exception as ex:
        errs.append(f"Semantic checks failed: {ex}")
    return errs

def main():
    schema_path, json_path = default_paths()

    try:
        from jsonschema import Draft202012Validator, exceptions as js_exceptions
    except Exception:
        print("ERROR: jsonschema is not installed. Install with:", file=sys.stderr)
        print("  py -m pip install jsonschema", file=sys.stderr)
        sys.exit(1)

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
    sem_errors = semantic_checks(instance)

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