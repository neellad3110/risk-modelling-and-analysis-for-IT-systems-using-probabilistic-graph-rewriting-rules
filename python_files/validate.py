import json
from pathlib import Path

def load_json(path):
    """Loads JSON files (typed graph, business graph, risk rules) into Python dictionaries"""
    with open(path, 'r') as f:
        return json.load(f)

def get_typed_graph_info(typed_graph):
    """Extracts node types, relation types, and attributes from the typed graph."""
    tg = typed_graph.get("type_graph", typed_graph)
    node_types = set()
    relation_types = set()
    node_attributes = {}
    for node in tg.get("node_types", []):
        if "name" in node:
            node_types.add(node["name"])
            node_attributes[node["name"]] = set(node.get("attributes", []))
    for rel in tg.get("edge_types", []):
        if "name" in rel:
            relation_types.add(rel["name"])
    return node_types, relation_types, node_attributes

def check_nodes_and_attrs(graph, allowed_types, allowed_attrs, context):
    """
    For each node in business graph:
    Checks if its type is defined in the schema.
    Checks if all its attributes are allowed for that type. 
    Returns a list of errors if any inconsistencies are found.
    """
    errors = []
    for node in graph.get("nodes", []):
        ntype = node.get("type")
        if ntype not in allowed_types:
            errors.append(f"{context}: Node type '{ntype}' not in typed graph.")
        for attr in node.get("attributes", {}).keys():
            if ntype in allowed_attrs and attr not in allowed_attrs[ntype]:
                errors.append(f"{context}: Attribute '{attr}' not allowed for node type '{ntype}'.")
    return errors

def check_relations(graph, allowed_types, context):
    """
    For each relation in business graph:
    Checks if its type is defined in the schema.
    Returns a list of errors if any inconsistencies are found.
    """
    errors = []
    for rel in graph.get("relations", []):
        rtype = rel.get("type")
        if rtype not in allowed_types:
            errors.append(f"{context}: Relation type '{rtype}' not in typed graph.")
    return errors

def check_rules(rules, allowed_node_types, allowed_rel_types, allowed_attrs):
    """
    For each rule in risk rules:
    Checks if all node types, attributes, and relation types in the pattern are defined in the schema.
    Returns a list of errors if any inconsistencies are found.
    """
    errors = []
    for rule in rules:
        rule_id = rule.get("id", "NO_ID")
        lhs = rule.get("risk_pattern", {}).get("lhs", [])
        for pat in lhs:
            ntype = pat.get("node_type")
            if ntype and ntype not in allowed_node_types:
                errors.append(f"Rule {rule_id}: Node type '{ntype}' not in typed graph.")
            for attr in pat.get("attributes", {}).keys():
                if ntype in allowed_attrs and attr not in allowed_attrs[ntype]:
                    errors.append(f"Rule {rule_id}: Attribute '{attr}' not allowed for node type '{ntype}'.")
            rel = pat.get("relation_type")
            if rel and rel not in allowed_rel_types:
                errors.append(f"Rule {rule_id}: Relation type '{rel}' not in typed graph.")
    return errors

def main():
    
    """Main function to     ."""
    base = Path(__file__).parent.parent
    typed_graph = load_json(base/"json_files/typed_graph.json")
    business_graph = load_json(base/"json_files/business_graph.json")
    risk_rules = load_json(base/"json_files/risk_rules.json")["risk_specification"]["rules"]

    allowed_node_types, allowed_rel_types, allowed_attrs = get_typed_graph_info(typed_graph)

    errors = []
    errors += check_nodes_and_attrs(business_graph["business_graph"], allowed_node_types, allowed_attrs, "BusinessGraph")
    errors += check_relations(business_graph["business_graph"], allowed_rel_types, "BusinessGraph")
    errors += check_rules(risk_rules, allowed_node_types, allowed_rel_types, allowed_attrs)

    if errors:
        print("Consistency check failed:")
        for err in errors:
            print(" -", err)
    else:
        print("All checks passed. Business graph and rules are consistent with the typed graph.")

if __name__ == "__main__":
    main()