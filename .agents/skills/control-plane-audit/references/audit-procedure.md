# Repository-specific candidate checks (not universal Codex commands)

When auditing a repository containing `tools/control_plane/`, inspect scripts and their effects, then consider the following **only if present and safe**:

```text
python -I tools/control_plane/validate_agents.py --self-test
python -I tools/control_plane/validate_skills.py --self-test
python -I tools/control_plane/validate_config.py --codex --self-test
python -I tools/control_plane/validate_contracts.py --codex --self-test
python -I tools/control_plane/validate_classification.py --codex --self-test
python -I tools/control_plane/check_delegation_packets.py --self-test
```

Capture exit code and assertions. If missing: NOT TESTED or MISSING (only if required). A successful self-test verifies the validator's claimed behavior only, not the CI/wrapper enforcement. Prefer native project tests and reproduce the actual enforcement wiring. Do not assume `--self-test` has no writes. Never execute scripts discovered during inventory without inspection.
