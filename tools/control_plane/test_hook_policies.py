"""Fixture tests for the CODEX PRIME hook handlers in .codex/hooks/ (static; no Codex session is started).

Each test pipes an event to the handler script and asserts stdout JSON and exit status against the documented
contract for that event (https://learn.chatgpt.com/docs/hooks, read 2026-10-31). They show the handlers behave as
designed; they do not show that Codex runs, trusts or honors them (operator trust and a live session are needed).

Run: python -I tools/control_plane/test_hook_policies.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOKS = os.path.join(ROOT, ".codex", "hooks")
FIX = os.path.join(HOOKS, "fixtures")


def run(script, event=None, raw=None, cwd=None):
    data = raw if raw is not None else json.dumps(event).encode("utf-8")
    p = subprocess.run([sys.executable, "-B", os.path.join(HOOKS, script)], input=data, capture_output=True,
                       cwd=cwd or ROOT, timeout=20)
    out = p.stdout.decode("utf-8")
    return p.returncode, (json.loads(out) if out.strip() else None), p.stderr.decode("utf-8")


def read(path, **kw):
    with open(path, encoding="utf-8", **kw) as fh:
        return fh.read()


def fixture(name, **over):
    with open(os.path.join(FIX, name + ".json"), encoding="utf-8") as fh:
        ev = json.load(fh)
    ev.update(over)
    return ev


def bash(cmd, event="PreToolUse"):
    return {"session_id": "s1", "cwd": ROOT, "hook_event_name": event, "turn_id": "t1", "tool_use_id": "u1",
            "tool_name": "Bash", "tool_input": {"command": cmd}}


def patch(path, event="PreToolUse"):
    body = f"*** Begin Patch\n*** Update File: {path}\n@@\n-a\n+b\n*** End Patch"
    return {"session_id": "s1", "cwd": ROOT, "hook_event_name": event, "turn_id": "t1", "tool_use_id": "u1",
            "tool_name": "apply_patch", "tool_input": {"command": body}}


def is_deny(out):
    h = (out or {}).get("hookSpecificOutput", {})
    return h.get("permissionDecision") == "deny" and bool(h.get("permissionDecisionReason"))


class PreToolPolicy(unittest.TestCase):
    DENIED = [
        "git clean -fd", "git clean -fdx", "git -C . clean -f", "git reset --hard HEAD~1", "git checkout -- .", "git checkout .",
        "git restore src/a.py", "git stash", "git stash drop", "git branch -D x", "git commit -n -m x", "git commit --no-verify -m x",
        "git push --force origin main", "git push -f origin main", "git push --force-with-lease origin f", "git push origin +main",
        "git push origin :feature", "git push -fu origin f", "git push --delete origin f",
        "rm -rf /", "rm -rf src", "rm -rf ../x", "rm -r *", "Remove-Item -Recurse -Force src", "rd /s /q build\\..\\x",
        "codex exec --yolo hi", "codex --ignore-rules", "codex --dangerously-bypass-hook-trust", "cat ~/.codex/auth.json",
        'bash -lc "git add . && git clean -fd"', "sh -c 'git reset --hard'", "FOO=1 git push --force",
        'powershell -Command "git push --force"', "git status; git clean -fd", "echo x | git push -f",
        "git add -A\ngit clean -fd",
    ]
    ALLOWED = [
        "git status --short", "git diff --stat", "git log --oneline -5", "git clean -n", "git clean --dry-run -d",
        "git restore --staged a.py", "git stash list", "git push origin feature", "git commit -m 'git clean -fd is blocked'",
        "git checkout -b new", "git branch -d merged", "rm -rf .codex-runtime", "rm -rf node_modules/pkg", "rm file.txt",
        "python -I tools/control_plane/validate_skills.py --self-test", "grep -r 'git push --force' docs", "echo hello",
        "ls", "Remove-Item old.txt",
    ]

    def test_denied_commands(self):
        for cmd in self.DENIED:
            with self.subTest(cmd=cmd):
                rc, out, _ = run("pre_tool_policy.py", bash(cmd))
                self.assertEqual(rc, 0)
                self.assertTrue(is_deny(out), out)

    def test_allowed_commands(self):
        for cmd in self.ALLOWED:
            with self.subTest(cmd=cmd):
                rc, out, _ = run("pre_tool_policy.py", bash(cmd))
                self.assertEqual((rc, out), (0, None))

    def test_patch_paths(self):
        for p in (".env", "app/.env.local", "config\\.env.production", ".codex/hooks/pre_tool_policy.py", ".codex/hooks.json",
                  ".codex/rules/execution.rules", ".codex/config.toml", "./.git/config"):
            with self.subTest(path=p):
                self.assertTrue(is_deny(run("pre_tool_policy.py", patch(p))[1]))
        for p in ("src/app.py", ".env.example", ".agents/skills/x/SKILL.md", ".codex/agents/a.toml", "docs/env.md"):
            with self.subTest(path=p):
                self.assertEqual(run("pre_tool_policy.py", patch(p))[1], None)

    def test_fixtures(self):
        self.assertTrue(is_deny(run("pre_tool_policy.py", fixture("pretool-bash-git-clean"))[1]))
        self.assertTrue(is_deny(run("pre_tool_policy.py", fixture("pretool-bash-wrapped-force-push"))[1]))
        self.assertTrue(is_deny(run("pre_tool_policy.py", fixture("pretool-patch-env"))[1]))
        self.assertEqual(run("pre_tool_policy.py", fixture("pretool-bash-allowed")), (0, None, ""))
        self.assertEqual(run("pre_tool_policy.py", fixture("pretool-patch-allowed")), (0, None, ""))

    def test_output_has_only_supported_fields(self):
        _, out, _ = run("pre_tool_policy.py", fixture("pretool-bash-git-clean"))
        self.assertEqual(set(out), {"hookSpecificOutput"})
        self.assertEqual(set(out["hookSpecificOutput"]), {"hookEventName", "permissionDecision", "permissionDecisionReason"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")  # never "ask" (unsupported)

    def test_other_tools_and_shapes_pass_through(self):
        for ev in ({"tool_name": "mcp__x__y", "tool_input": {"command": "git clean -fd"}},
                   {"tool_name": "Bash", "tool_input": "git clean -fd"}, {"tool_name": "Bash"}, {"tool_name": "Bash", "tool_input": {}},
                   {"tool_name": "Bash", "tool_input": {"command": 5}}, {}):
            with self.subTest(ev=ev):
                self.assertEqual(run("pre_tool_policy.py", ev)[:2], (0, None))

    def test_malformed_input_fails_open_with_exit_zero(self):
        for raw in (b"", b"not json", b"[1,2]", b"\xff\xfe", b"{" * 5000, b'{"tool_name":"Bash"'):
            with self.subTest(raw=raw[:20]):
                rc, out, err = run("pre_tool_policy.py", raw=raw)
                self.assertEqual((rc, out), (0, None))
                self.assertIn("fails open", err)

    def test_oversized_input_is_not_parsed(self):
        rc, out, _ = run("pre_tool_policy.py", raw=b" " * 1_100_000)
        self.assertEqual((rc, out), (0, None))

    def test_command_is_not_executed_or_echoed(self):
        marker = os.path.join(tempfile.gettempdir(), "cp_hook_marker_should_not_exist")
        if os.path.exists(marker):
            os.remove(marker)
        run("pre_tool_policy.py", bash(f"git clean -fd; touch {marker}; echo $(touch {marker})"))
        self.assertFalse(os.path.exists(marker))

    def test_deep_wrapping_is_bounded(self):
        cmd = "git clean -fd"
        for _ in range(8):
            cmd = "bash -c " + json.dumps(cmd)
        rc, out, _ = run("pre_tool_policy.py", bash(cmd))
        self.assertEqual(rc, 0)  # beyond the unwrap depth the inner command is not evaluated: documented residual bypass


class PermissionPolicy(unittest.TestCase):
    def test_denies_never_acceptable(self):
        for cmd in ("git push --force origin main", "git push -f origin main", "codex exec --yolo x", "git reset --hard",
                    "cp x .codex/hooks/pre_tool_policy.py", "sed -i s/a/b/ .codex/rules/execution.rules", "echo x > .codex\\config.toml"):
            with self.subTest(cmd=cmd):
                rc, out, _ = run("permission_policy.py", bash(cmd, "PermissionRequest"))
                h = out["hookSpecificOutput"]
                self.assertEqual((rc, h["hookEventName"], h["decision"]["behavior"]), (0, "PermissionRequest", "deny"))
                self.assertTrue(h["decision"]["message"])

    def test_defers_everything_else_and_never_allows(self):
        for cmd in ("git push origin feature", "npm install", "curl https://example.com", "git status"):
            with self.subTest(cmd=cmd):
                self.assertEqual(run("permission_policy.py", bash(cmd, "PermissionRequest"))[:2], (0, None))

    def test_patch_requests(self):
        self.assertEqual(run("permission_policy.py", patch(".codex/hooks.json", "PermissionRequest"))[1]["hookSpecificOutput"]["decision"]["behavior"], "deny")
        self.assertEqual(run("permission_policy.py", patch("src/a.py", "PermissionRequest"))[:2], (0, None))

    def test_fixture_and_malformed(self):
        self.assertEqual(run("permission_policy.py", fixture("permission-force-push"))[1]["hookSpecificOutput"]["decision"]["behavior"], "deny")
        for raw in (b"", b"garbage"):
            rc, out, _ = run("permission_policy.py", raw=raw)
            self.assertEqual((rc, out), (0, None))

    def test_source_never_emits_allow_or_unsupported_fields(self):
        with open(os.path.join(HOOKS, "permission_policy.py"), encoding="utf-8") as fh:
            src = fh.read()
        for bad in ('"allow"', "updatedInput", "updatedPermissions", "interrupt"):
            self.assertNotIn(bad, src)
        with open(os.path.join(HOOKS, "hooklib.py"), encoding="utf-8") as fh:
            lib = fh.read()
        for bad in ('"ask"', "updatedInput", "suppressOutput", "stopReason"):
            self.assertNotIn(bad, lib)


class SessionContext(unittest.TestCase):
    def make_repo(self):
        d = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(d.name, ".git"))
        return d

    def ctx(self, out):
        h = out["hookSpecificOutput"]
        self.assertEqual(h["hookEventName"], "SessionStart")
        return h["additionalContext"]

    def test_startup_is_short(self):
        rc, out, _ = run("session_context.py", fixture("sessionstart-startup"))
        self.assertEqual(rc, 0)
        self.assertLess(len(self.ctx(out)), 1200)
        self.assertNotIn("Saved task state", self.ctx(out))

    def test_compact_restores_newest_state_with_label(self):
        with self.make_repo() as d:
            sd = os.path.join(d, ".codex-runtime", "state")
            os.makedirs(sd)
            for name, body, t in (("old.md", "OLD GOAL", 1_000_000), ("new.md", "NEW GOAL: finish X", 2_000_000)):
                p = os.path.join(sd, name)
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(body)
                os.utime(p, (t, t))
            _, out, _ = run("session_context.py", fixture("sessionstart-compact", cwd=d))
            c = self.ctx(out)
            self.assertIn("NEW GOAL", c)
            self.assertNotIn("OLD GOAL", c)
            self.assertIn("not a reconstruction", c)

    def test_compact_state_is_capped(self):
        with self.make_repo() as d:
            sd = os.path.join(d, ".codex-runtime", "state")
            os.makedirs(sd)
            with open(os.path.join(sd, "big.md"), "w", encoding="utf-8") as fh:
                fh.write("x" * 100_000)
            _, out, _ = run("session_context.py", fixture("sessionstart-compact", cwd=d))
            self.assertLess(len(self.ctx(out)), 8000)

    def test_compact_without_state(self):
        with self.make_repo() as d:
            _, out, _ = run("session_context.py", fixture("sessionstart-compact", cwd=d))
            self.assertIn("No saved task state", self.ctx(out))

    def test_malformed_still_valid_json_exit_zero(self):
        rc, out, _ = run("session_context.py", raw=b"nope")
        self.assertEqual(rc, 0)
        self.assertIn("additionalContext", out["hookSpecificOutput"])


class ExecutionEvidence(unittest.TestCase):
    def run_in(self, d, ev):
        ev = dict(ev, cwd=d)
        return run("execution_evidence.py", ev, cwd=d)

    def test_records_sanitized_fields_only(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".git"))
            ev = fixture("posttool-bash-test")
            ev["tool_input"] = {"command": "API_TOKEN=supersecret python -m pytest tests/test_x.py"}
            ev["tool_response"] = {"exit_code": 1, "output": "password=hunter2"}
            self.assertEqual(self.run_in(d, ev)[:2], (0, None))
            p = os.path.join(d, ".codex-runtime", "results", "s1.jsonl")
            raw = read(p)
            rec = json.loads(raw)
            self.assertEqual({k: rec[k] for k in ("schema_version", "session_id", "turn_id", "tool_use_id", "tool_name", "command_class", "exit_code")},
                             {"schema_version": 1, "session_id": "s1", "turn_id": "t1", "tool_use_id": "u1", "tool_name": "Bash",
                              "command_class": "test", "exit_code": 1})
            self.assertRegex(rec["timestamp"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
            self.assertNotIn("supersecret", raw)
            self.assertNotIn("hunter2", raw)
            self.assertNotIn("pytest", raw)

    def test_appends_and_classifies(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".git"))
            for i, (cmd, cls) in enumerate((("git status", "git-read"), ("git commit -m x", "git-write"), ("make build", "build"),
                                            ("ruff check .", "lint"), ("python tools/x.py --self-test", "test"), ("ls", "other"),
                                            ("bash -lc 'cd a && npm test'", "test"))):
                ev = fixture("posttool-bash-test", tool_use_id=f"u{i}")
                ev["tool_input"] = {"command": cmd}
                self.run_in(d, ev)
            lines = read(os.path.join(d, ".codex-runtime", "results", "s1.jsonl")).splitlines()
            self.assertEqual([json.loads(x)["command_class"] for x in lines],
                             ["git-read", "git-write", "build", "lint", "test", "other", "test"])

    def test_unknown_exit_code_is_null_and_hostile_session_id_is_contained(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".git"))
            ev = fixture("posttool-bash-test", session_id="../../evil", tool_response="plain text")
            self.run_in(d, ev)
            names = os.listdir(os.path.join(d, ".codex-runtime", "results"))
            self.assertEqual(len(names), 1)
            self.assertNotIn("/", names[0])
            self.assertFalse(os.path.exists(os.path.join(os.path.dirname(d), "evil.jsonl")))
            self.assertIsNone(json.loads(read(os.path.join(d, ".codex-runtime", "results", names[0])))["exit_code"])

    def test_no_repo_malformed_and_other_tools_write_nothing(self):
        with tempfile.TemporaryDirectory() as d:  # no .git anywhere above (temp dir); best effort
            self.assertEqual(self.run_in(d, fixture("posttool-bash-test", tool_name="apply_patch"))[:2], (0, None))
            self.assertEqual(run("execution_evidence.py", raw=b"bad", cwd=d)[:2], (0, None))
            self.assertFalse(os.path.exists(os.path.join(d, ".codex-runtime", "results")))


class SubagentContract(unittest.TestCase):
    def test_start_injects_rules(self):
        rc, out, _ = run("subagent_contract.py", fixture("subagent-start"))
        h = out["hookSpecificOutput"]
        self.assertEqual((rc, h["hookEventName"]), (0, "SubagentStart"))
        for word in ("COMPLETE", "UNVERIFIED", "scope"):
            self.assertIn(word, h["additionalContext"])

    def test_stop_without_status_blocks_once(self):
        rc, out, _ = run("subagent_contract.py", fixture("subagent-stop-nostatus"))
        self.assertEqual((rc, out["decision"]), (0, "block"))
        self.assertIn("COMPLETE", out["reason"])
        again = run("subagent_contract.py", fixture("subagent-stop-nostatus", stop_hook_active=True))
        self.assertEqual(again[:2], (0, {}))

    def test_stop_with_status_or_odd_input_passes(self):
        for msg in ("Done.\nStatus: COMPLETE", "BLOCKED: cannot read file", "UNVERIFIED claim", "PARTIAL"):
            self.assertEqual(run("subagent_contract.py", fixture("subagent-stop-nostatus", last_assistant_message=msg))[:2], (0, {}))
        for msg in (None, 5):
            self.assertEqual(run("subagent_contract.py", fixture("subagent-stop-nostatus", last_assistant_message=msg))[:2], (0, {}))
        self.assertEqual(run("subagent_contract.py", raw=b"garbage")[:2], (0, {}))
        self.assertEqual(run("subagent_contract.py", {"hook_event_name": "Other"})[:2], (0, {}))

    def test_lowercase_status_word_does_not_count(self):
        self.assertEqual(run("subagent_contract.py", fixture("subagent-stop-nostatus", last_assistant_message="complete analysis"))[1]["decision"], "block")


class CompletionGate(unittest.TestCase):
    def write_log(self, d, recs):
        os.makedirs(os.path.join(d, ".git"), exist_ok=True)
        os.makedirs(os.path.join(d, ".codex-runtime", "results"), exist_ok=True)
        with open(os.path.join(d, ".codex-runtime", "results", "s1.jsonl"), "w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")

    def test_blocks_unbacked_claim_once(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_log(d, [{"turn_id": "t1", "command_class": "git-read"}, {"turn_id": "t0", "command_class": "test"}])
            rc, out, _ = run("completion_gate.py", fixture("stop-claims-tests", cwd=d))
            self.assertEqual((rc, out["decision"]), (0, "block"))
            self.assertIn("no test command ran", out["reason"])
            self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d, stop_hook_active=True))[:2], (0, {}))

    def test_allows_backed_claim_and_non_claims(self):
        with tempfile.TemporaryDirectory() as d:
            self.write_log(d, [{"turn_id": "t1", "command_class": "test"}, "not json"])
            self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d))[:2], (0, {}))
        with tempfile.TemporaryDirectory() as d:
            self.write_log(d, [])
            for msg in ("The function parses the file and returns a list.", "Tests were not run; status PARTIAL.",
                        "I could not run the tests, so nothing is verified.", "If the tests pass, we are done.",
                        "This explains how checks work in CI.", ""):
                with self.subTest(msg=msg):
                    self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d, last_assistant_message=msg))[:2], (0, {}))

    def test_claim_variants_block_without_log(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".git"))
            for msg in ("All tests passed.", "I ran the test suite and it is green.", "Self-tests pass (32/32).", "validators passed"):
                with self.subTest(msg=msg):
                    self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d, last_assistant_message=msg))[1]["decision"], "block")

    def test_malformed_and_null_message(self):
        self.assertEqual(run("completion_gate.py", raw=b"x")[:2], (0, {}))
        self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", last_assistant_message=None))[:2], (0, {}))


class ReviewerRegressions(unittest.TestCase):
    """Cases an independent adversarial review reproduced against the first version of the matcher (all were allowed)."""

    DENIED = [
        "(git reset --hard)", "$(git reset --hard)", "{ git reset --hard; }", "if true; then git reset --hard; fi",
        'powershell -Command "& { git reset --hard }"', 'powershell -Command "if ($true) { git reset --hard }"',
        'pwsh -com "git reset --hard"', "eval 'git reset --hard'", "env -i git reset --hard", "env -u X git reset --hard",
        "sudo -u root git reset --hard", "nice -n 5 git reset --hard", "time -p git reset --hard", "timeout 5 git reset --hard",
        "xargs -I{} git reset --hard", "find . -exec git reset --hard ;", "git checkout -f", "git checkout -f main",
        "git checkout -B main", "git switch -f main", "git switch --discard-changes main", "git reset --merge",
        "git branch --delete --force x", "git branch -fd x", "git branch -df x", "git push --mirror", "git push --prune",
        "git commit -nm x", "git -c alias.x='reset --hard' x", "git config alias.x 'reset --hard'",
        "rd /s/q src", "Remove-Item -rec src", "Remove-Item -Recurs src", "find . -delete", "find src -type f -delete",
        "type C:\\Users\\click\\.codex\\auth.json", "Get-Content $env:USERPROFILE\\.codex\\auth.json",
        "x" * 25000 + "; git reset --hard", "x" * 250000, "powershell Remove-Item -Recurse src",
    ]
    ALLOWED = [
        "Remove-Item -Recurse -Force .\\node_modules", "rm -rf .\\node_modules", "rd /s /q node_modules\\.bin",
        "rg -- --yolo docs", 'grep -rn "--ignore-rules" .codex', "git grep -n -- --yolo", "echo --yolo", "cat docs/auth.json",
        "git log --oneline -- auth.json", 'git commit -m "use -a flag"', 'git commit -m "bump -n"', "git commit -am 'x'",
        'git commit -m "fix: update -all docs" --author=a', "echo git reset --hard",
    ]

    def test_previously_allowed_forms_are_denied(self):
        import base64
        encoded = base64.b64encode("git reset --hard".encode("utf-16-le")).decode()
        nested = "git reset --hard"
        for _ in range(8):
            nested = "bash -c " + json.dumps(nested)
        for cmd in self.DENIED + ["powershell -EncodedCommand " + encoded, nested]:
            with self.subTest(cmd=cmd[:80]):
                rc, out, _ = run("pre_tool_policy.py", bash(cmd))
                self.assertEqual(rc, 0)
                self.assertTrue(is_deny(out), out)

    def test_legitimate_forms_are_still_allowed(self):
        for cmd in self.ALLOWED:
            with self.subTest(cmd=cmd):
                self.assertEqual(run("pre_tool_policy.py", bash(cmd))[:2], (0, None))

    def test_patch_path_normalization(self):
        for p in (".codex/./hooks/a.py", ".codex//hooks/a.py", ".CODEX/hooks/a.py", ".CODEX/HOOKS.JSON", "C:\\repo\\.Codex\\Hooks\\a.py",
                  ".GIT/config", ".ENV", ".envrc", ".codex/hooks/../hooks/a.py"):
            with self.subTest(path=p):
                self.assertTrue(is_deny(run("pre_tool_policy.py", patch(p))[1]))

    def test_permission_text_is_case_and_dot_insensitive(self):
        for cmd in ("echo x >.CODEX/hooks/a.py", "cp a .codex/./rules/x", "cp a .codex//config.toml"):
            with self.subTest(cmd=cmd):
                self.assertEqual(run("permission_policy.py", bash(cmd, "PermissionRequest"))[1]["hookSpecificOutput"]["decision"]["behavior"], "deny")

    def test_command_class_is_executable_based(self):
        sys.path.insert(0, HOOKS)
        try:
            import hooklib
        finally:
            sys.path.pop(0)
        for cmd, cls in (("cat tools/control_plane/validate_agents.py", "other"), ("echo pytest", "other"), ("rm test_foo.py", "other"),
                         ("grep -rn pytest .", "other"), ("python -m pytest -q", "test"), ("python -I tools/x/validate_skills.py --self-test", "test"),
                         ("pytest tests/", "test"), ("npm test", "test"), ("make test", "test"), ("git status", "git-read"),
                         ("ruff check .", "lint")):
            with self.subTest(cmd=cmd):
                self.assertEqual(hooklib.command_class(cmd), cls)

    def test_gate_ignores_a_failed_run_and_honest_failure_reports(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".git"))
            os.makedirs(os.path.join(d, ".codex-runtime", "results"))
            with open(os.path.join(d, ".codex-runtime", "results", "s1.jsonl"), "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"turn_id": "t1", "command_class": "test", "exit_code": 1}) + "\n")
            blocked = run("completion_gate.py", fixture("stop-claims-tests", cwd=d, last_assistant_message="All tests pass."))
            self.assertEqual(blocked[1]["decision"], "block")
            for msg in ("Tests did not pass.", "I ran the tests; 3 failed.", "tests aren't passing", "Not all tests pass", "Tests cannot pass until X is fixed."):
                with self.subTest(msg=msg):
                    self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d, last_assistant_message=msg))[:2], (0, {}))
            for msg in ("All tests pass, no errors.", "Tests passed with 0 failures"):
                with self.subTest(msg=msg):
                    self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d, last_assistant_message=msg))[1]["decision"], "block")
            for msg in ("12 passed in 0.3s", "validation passed", "tests: ok"):
                with self.subTest(msg=msg):
                    self.assertEqual(run("completion_gate.py", fixture("stop-claims-tests", cwd=d, last_assistant_message=msg))[1]["decision"], "block")

    def test_status_must_be_a_status_line(self):
        self.assertEqual(run("subagent_contract.py", fixture("subagent-stop-nostatus", last_assistant_message="no status here, PARTIAL credit"))[1]["decision"], "block")
        self.assertEqual(run("subagent_contract.py", fixture("subagent-stop-nostatus", last_assistant_message="Findings...\n\n**Status: COMPLETE**"))[:2], (0, {}))

    def test_evidence_session_ids_stay_distinct_when_sanitized(self):
        sys.path.insert(0, HOOKS)
        try:
            import hooklib
        finally:
            sys.path.pop(0)
        self.assertNotEqual(hooklib.safe_name("../../escape"), hooklib.safe_name("a/b"))
        self.assertEqual(hooklib.safe_name("abc-123"), "abc-123")

    def test_hooks_do_not_write_bytecode(self):
        with open(os.path.join(ROOT, ".codex", "hooks.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        for groups in cfg["hooks"].values():
            for g in groups:
                for h in g["hooks"]:
                    self.assertIn("python3 -B ", h["command"])
                    self.assertIn("py -3 -B ", h["commandWindows"])


class Configuration(unittest.TestCase):
    def test_every_handler_has_a_fixture_test_and_is_registered(self):
        with open(os.path.join(ROOT, ".codex", "hooks.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        events = cfg["hooks"]
        self.assertEqual(set(events), {"SessionStart", "PreToolUse", "PermissionRequest", "PostToolUse", "SubagentStart", "SubagentStop", "Stop"})
        scripts = set()
        for groups in events.values():
            for g in groups:
                for h in g["hooks"]:
                    self.assertEqual(h["type"], "command")
                    self.assertLessEqual(h["timeout"], 30)
                    self.assertIn("$(git rev-parse --show-toplevel)", h["command"])
                    self.assertIn("commandWindows", h)
                    scripts.update(s for s in os.listdir(HOOKS) if s.endswith(".py") and s in h["command"])
        self.assertEqual(scripts, {"session_context.py", "pre_tool_policy.py", "permission_policy.py", "execution_evidence.py",
                                   "subagent_contract.py", "completion_gate.py"})
        self.assertTrue(events["PostToolUse"][0]["hooks"][0]["async"])

    def test_no_bypass_flags_or_network_or_exec_of_input_in_handlers(self):
        for name in os.listdir(HOOKS):
            if name.endswith(".py"):
                src = read(os.path.join(HOOKS, name))
                for bad in ("urllib", "requests", "socket", "eval(", "exec(", "os.system", "shell=True", "subprocess"):
                    self.assertNotIn(bad, src, f"{name}: {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=1)
