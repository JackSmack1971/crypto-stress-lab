#!/usr/bin/env python3
"""Check structural consistency of a regression evidence record (stdlib only)."""
import json
import sys
from pathlib import Path

STATUSES = {"passed", "failed", "blocked", "not_run"}


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if data.get("baseline_status") not in {"established", "not_established", "not_applicable"}:
        errors.append("invalid baseline_status")
    if data.get("conclusion") not in {"verified", "not_verified", "inconclusive"}:
        errors.append("invalid conclusion")
    contracts, commands = data.get("contracts"), data.get("commands")
    if not isinstance(contracts, list) or not contracts:
        errors.append("contracts must be a nonempty list")
        contracts = []
    if not isinstance(commands, list):
        errors.append("commands must be a list")
        commands = []
    by_id = {}
    for index, cmd in enumerate(commands):
        if not isinstance(cmd, dict):
            errors.append(f"commands[{index}] must be an object")
            continue
        identifier, status, code = cmd.get("id"), cmd.get("status"), cmd.get("exit_code")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in by_id:
            errors.append(f"commands[{index}] missing or duplicate id")
        else:
            by_id[identifier] = cmd
        if not isinstance(cmd.get("command"), str) or not cmd["command"].strip():
            errors.append(f"commands[{index}] missing command")
        if status not in STATUSES:
            errors.append(f"commands[{index}] invalid status")
        if status == "passed" and (type(code) is not int or code != 0):
            errors.append(f"commands[{index}] passing command must have exit_code 0")
        if status == "failed" and (type(code) is not int or code == 0):
            errors.append(f"commands[{index}] failed command needs nonzero exit_code")
        if status in {"blocked", "not_run"} and code is not None:
            errors.append(f"commands[{index}] non-executed command cannot have exit_code")
    contract_ids = set()
    for index, contract in enumerate(contracts):
        if not isinstance(contract, dict):
            errors.append(f"contracts[{index}] must be an object")
            continue
        identifier, status = contract.get("id"), contract.get("status")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in contract_ids:
            errors.append(f"contracts[{index}] missing or duplicate id")
        else:
            contract_ids.add(identifier)
        if status not in STATUSES:
            errors.append(f"contracts[{index}] invalid status")
        refs = contract.get("command_ids")
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            errors.append(f"contracts[{index}] command_ids must be a list of strings")
            continue
        if len(set(refs)) != len(refs):
            errors.append(f"contracts[{index}] duplicate command reference")
        if any(ref not in by_id for ref in refs):
            errors.append(f"contracts[{index}] references unknown command")
        if status == "passed" and (not refs or not all(ref in by_id and by_id[ref].get("status") == "passed" for ref in refs)):
            errors.append(f"contracts[{index}] pass requires passing command evidence")
    if data.get("conclusion") == "verified" and (not contracts or any(not isinstance(c, dict) or c.get("status") != "passed" for c in contracts)):
        errors.append("verified conclusion requires all contracts passed")
    if data.get("conclusion") == "not_verified" and not any(isinstance(c, dict) and c.get("status") == "failed" for c in contracts):
        errors.append("not_verified conclusion requires failed contract")
    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: validate_evidence.py EVIDENCE.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Cannot read evidence: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    print("VALID" if not errors else f"INVALID ({len(errors)} issue(s))")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
