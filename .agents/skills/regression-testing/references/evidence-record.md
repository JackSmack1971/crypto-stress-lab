# Optional machine-readable evidence manifest

Use a JSON object with `contracts`, `commands`, `baseline_status`, and `conclusion` for auditability. Record only observations from executed checks. The validator checks internal consistency, **not** test quality or external truth.

```json
{
  "baseline_status": "not_established",
  "contracts": [
    {"id": "C1", "status": "passed", "command_ids": ["run1"]}
  ],
  "commands": [
    {"id": "run1", "command": "python -m pytest tests/test_example.py", "status": "passed", "exit_code": 0}
  ],
  "conclusion": "verified"
}
```

Allowed contract statuses: `passed`, `failed`, `blocked`, `not_run`. Allowed command statuses: `passed`, `failed`, `blocked`, `not_run`. Baseline: `established`, `not_established`, `not_applicable`. Conclusion: `verified`, `not_verified`, `inconclusive`. A `verified` claim needs every contract passed and referenced by an actual passing command; it does **not** prove that the chosen contracts are comprehensive. Preserve baseline evidence and failure analysis in the human-readable report.
