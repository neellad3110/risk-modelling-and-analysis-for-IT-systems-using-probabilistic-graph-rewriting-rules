# Offline LTS-driven Risk Simulation

This flow consumes a GROOVE-exported LTS (.gpr) and your rules JSON to build a CTMC via q = λ · p for outcome-labelled edges, then runs Monte Carlo.

- Input:
  - json_files/risk_rules_new.json
  - groove_LTS/RiskModelling-gts.gpr (exported from GROOVE with BFS bound)
  - Optional: json_files/risk_outcome_label_map.json to map JSON outcome names to GROOVE function labels.

- Runner:
  - python_files/run_offline_lts.py

## Label Mapping
If GROOVE outcome edge labels differ from JSON outcome names, add:

```
{
  "RISK001": {
    "User clicked and entered credentials": "phishingAttack_User_clicked_link_and_entered_credentials"
  },
  "RISK004": {
    "Script executed successfully": "UnauthorizedScriptExecution_Script_is_executed_successfully"
  }
}
```

## How it works
1. Parse rules and normalize probabilities per rule (uniform if missing).
2. Parse LTS, collect edges and labels.
3. Match outcome edges by normalized label to the rule’s outcome set.
4. Create CTMC transitions with rate q = λ(rule) · p(outcome) and attach outcome cost.
5. Simulate many runs over a time horizon with race-of-exponentials; sum costs.

## CLI
```
python d:\Dessertation\nvl2\python_files\run_offline_lts.py --rules d:\Dessertation\nvl2\json_files\risk_rules_new.json --lts d:\Dessertation\nvl2\groove_LTS\RiskModelling-gts.gpr --horizon 1.0 --runs 2000 --seed 123
```

Results include mean loss and p05/p50/p95 quantiles.
