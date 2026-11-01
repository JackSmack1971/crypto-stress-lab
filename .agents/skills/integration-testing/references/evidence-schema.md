# Optional machine-checkable evidence record

`python scripts/check_evidence.py path/to/evidence.json` checks that an integration-evidence record is syntactically coherent, that each boundary has a recognized status, and that `verified` is supported by recorded passing assertions and an independent observation. It **does not execute tests or authenticate evidence**.

Example:

```json
{
  "boundaries": [
    {
      "id": "api-to-db",
      "contract": "POST writes one row or rolls back",
      "environment": "local-ephemeral",
      "status": "verified",
      "command": "pytest tests/integration/test_write.py -q",
      "exit_code": 0,
      "assertion": "client received 201 and database query found exactly one row",
      "observation": "independent SELECT after request returned the expected row",
      "real_components": ["HTTP application", "SQL driver", "ephemeral database"],
      "simulated_components": [],
      "cleanup": "verified"
    }
  ]
}
```

For `failed`, `blocked`, or `not tested`, supply a nonempty `reason`; include a command and exit code for `failed` when a command ran. Each boundary needs a stable unique `id`, `contract`, `environment`, `status`, `real_components`, `simulated_components`, and `cleanup` (`verified`, `not-applicable`, `unverified`). `verified` requires an executable command, zero exit code, assertion, observation and verified/applicable cleanup. This is a reporting integrity check, not a coverage measurement or substitute for code review.
