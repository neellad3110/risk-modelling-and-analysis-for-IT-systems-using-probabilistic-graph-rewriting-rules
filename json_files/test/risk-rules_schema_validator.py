from pathlib import Path
import sys

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
    # this file: <root>/nvl2/json_files/test/risk-rules_schema_validator.py
    base = Path(__file__).resolve()
    # parents: [test, json_files, nvl2, <root>, ...]
    return base.parents[3]

def default_paths() -> tuple[Path, Path]:
    root = project_root()
    schema_path = root / "nvl2" / "json_files" / "schema" / "Riskrule.schema.json"
    json_path = root / "nvl2" / "json_files" / "risk_rules.json"
    return schema_path, json_path

def check_outcome_probabilities(instance: dict, epsilon: float = 1e-6) -> list[str]:
    errs: list[str] = []
    try:
        rs = instance.get("risk_specification", {})
        rules = rs.get("rules", [])
        if not isinstance(rules, list):
            errs.append("$.risk_specification.rules: expected array")
            return errs
        for i, rule in enumerate(rules):
            rid = rule.get("id", f"(rule_index_{i})")
            outcomes = rule.get("outcomes", [])
            if not isinstance(outcomes, list) or len(outcomes) == 0:
                errs.append(f"$.risk_specification.rules[{i}].outcomes: empty or missing for rule {rid}")
                continue
            probs = []
            missing_idx = []
            for j, o in enumerate(outcomes):
                p = o.get("probability", None)
                if isinstance(p, (int, float)):
                    probs.append(float(p))
                else:
                    missing_idx.append(j)
            if missing_idx:
                idxs = ", ".join(str(j) for j in missing_idx)
                errs.append(f"$.risk_specification.rules[{i}].outcomes: missing 'probability' at indices [{idxs}] for rule {rid}")
                continue
            s = sum(probs)
            if abs(s - 1.0) > epsilon:
                errs.append(f"$.risk_specification.rules[{i}].outcomes: probabilities sum = {s:.6f} (expected 1.0) for rule {rid}")
    except Exception as e:
        errs.append(f"Custom probability check failed with error: {e}")
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

    # Custom probability-sum check
    custom_errors = check_outcome_probabilities(instance)

    print(f"Schema: {schema_path}")
    print(f"JSON:   {json_path}")

    if not js_errors and not custom_errors:
        print(f"VALID: {json_path.name} conforms to schema {schema_path.name} and outcome probabilities of all attacks is sum to 1.")
        sys.exit(0)

    print(f"INVALID: {json_path.name} has issues")
    for idx, err in enumerate(js_errors, 1):
        path = "$" + "".join(f"[{repr(p)}]" if isinstance(p, int) else f".{p}" for p in err.path)
        print(f"- [S{idx}] {path}: {err.message}")
        if err.context:
            for sub in err.context:
                subpath = "$" + "".join(f"[{repr(p)}]" if isinstance(p, int) else f".{p}" for p in sub.path)
                print(f"    note: {subpath}: {sub.message}")
    for idx, msg in enumerate(custom_errors, 1):
        print(f"- [P{idx}] {msg}")
    sys.exit(3)

if __name__ == "__main__":
    main()