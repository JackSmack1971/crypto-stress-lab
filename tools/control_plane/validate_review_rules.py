"""Validate the repository's code-review guidance and the PR-review documentation (static).

Usage: python -I tools/control_plane/validate_review_rules.py [--self-test]

Checks, against https://learn.chatgpt.com/docs/third-party/github (read 2026-10-31):
  - the root AGENTS.md and each nested AGENTS.md that carries review rules have a `## Code Review Rules` section grouped with `###` headings,
    rules that start with "Flag", a stated safe path or exception, no mechanical checks (formatting, lint), and a concise size
  - .codex/knowledge/code-review.md states the operator setting, the manual trigger, and that rules do not replace tests or approvals
  - no repository workflow claims to enable the Codex account setting (the repository cannot control it)
  - a PR template exists and asks for evidence, not for a reviewer's approval

It does not show that Codex cloud review runs, follows these rules, or is enabled: that is an account setting (BLOCKED: operator).
"""
import copy
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE_FILES = ["AGENTS.md", ".codex/hooks/AGENTS.md"]
DOC = ".codex/knowledge/code-review.md"
TEMPLATE = ".github/pull_request_template.md"
MAX_SECTION_BYTES = 3000
MECHANICAL = re.compile(r"\b(formatting|whitespace|indentation|lint(ing)?|prettier|black|eslint|code style|import order)\b", re.I)
DOC_NEEDLES = ["chatgpt.com/settings/code-review", "Automatic review", "@codex review", "operator", "AGENTS.md",
               "Code Review Rules", "P0", "not replace tests"]
TEMPLATE_NEEDLES = ["evidence", "commands", "unverified"]
WORKFLOW_CLAIM = re.compile(r"codex|chatgpt\.com/settings|automatic review", re.I)


def section(text):
    m = re.search(r"^## Code Review Rules\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def check_rules(name, text):
    errs = []
    body = section(text)
    if body is None:
        return [f"{name}: no '## Code Review Rules' section"]
    if len(body.encode("utf-8")) > MAX_SECTION_BYTES:
        errs.append(f"{name}: review rules exceed {MAX_SECTION_BYTES} bytes; keep them to consequential, repository-specific checks")
    groups = re.findall(r"^### .+$", body, re.M)
    if len(groups) < 1:
        errs.append(f"{name}: group rules under at least one '###' heading")
    bullets = re.findall(r"^- (.*(?:\n  .*)*)", body, re.M)
    if not 2 <= len(bullets) <= 12:
        errs.append(f"{name}: {len(bullets)} rules; start with a few concise ones (2 to 12)")
    for b in bullets:
        flat = " ".join(b.split())
        if not flat.startswith("Flag"):
            errs.append(f"{name}: rule does not say what to flag: {flat[:60]!r}")
        if MECHANICAL.search(flat):
            errs.append(f"{name}: mechanical check in a review rule (leave it to CI): {flat[:60]!r}")
    if not any("Safe path" in b or "safe path" in b for b in bullets):
        errs.append(f"{name}: no rule states a safe path or exception")
    if re.search(r"claude", body, re.I):
        errs.append(f"{name}: review rules must not reference Claude")
    return errs


def check_doc(text):
    errs = [f"{DOC}: missing {n!r}" for n in DOC_NEEDLES if n not in text]
    if re.search(r"\b(guarantee[sd]?|ensures?|enforces?)\b[^.\n]{0,40}\breview", text, re.I):
        errs.append(f"{DOC}: overclaims what review rules do")
    if not re.search(r"BLOCKED: operator", text):
        errs.append(f"{DOC}: must mark enabling automatic review as BLOCKED: operator")
    return errs


def check_template(text):
    errs = [f"{TEMPLATE}: missing {n!r}" for n in TEMPLATE_NEEDLES if n not in text.lower()]
    if re.search(r"(?i)approved by (codex|ai|the model)|codex approved", text):
        errs.append(f"{TEMPLATE}: a model approval must not be a merge criterion")
    return errs


def check_workflows(files):
    """files: {relative path: text} for .github/workflows."""
    return [f"{p}: a repository workflow cannot enable the Codex account setting; remove the claim" for p, t in files.items()
            if WORKFLOW_CLAIM.search(t)]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8") if (ROOT / rel).is_file() else None


def gather():
    data = {"rules": {}, "doc": read(DOC), "template": read(TEMPLATE), "workflows": {}}
    for rel in RULE_FILES:
        data["rules"][rel] = read(rel)
    wf = ROOT / ".github" / "workflows"
    if wf.is_dir():
        for p in wf.iterdir():
            if p.is_file():
                data["workflows"][f".github/workflows/{p.name}"] = p.read_text(encoding="utf-8")
    return data


def run_all(data):
    errs = []
    for rel, text in data["rules"].items():
        errs += [f"{rel}: missing"] if text is None else check_rules(rel, text)
    errs += [f"{DOC}: missing"] if data["doc"] is None else check_doc(data["doc"])
    errs += [f"{TEMPLATE}: missing"] if data["template"] is None else check_template(data["template"])
    errs += check_workflows(data["workflows"])
    return errs


def mutations(data):
    def sub(path, a, b):
        def fn(d):
            d = copy.deepcopy(d)
            tgt = d["rules"] if path[0] == "rules" else d
            key = path[1] if path[0] == "rules" else path[0]
            assert a in tgt[key], (path, a)
            tgt[key] = tgt[key].replace(a, b, 1)
            return d
        return fn
    def inject(d, text):
        d = copy.deepcopy(d)
        d["rules"]["AGENTS.md"] = d["rules"]["AGENTS.md"].replace("## Code Review Rules\n", "## Code Review Rules\n" + text, 1)
        return d

    root = data["rules"]["AGENTS.md"]
    first_rule = re.search(r"^- (Flag [^\n]*)", section(root), re.M).group(1)[:30]
    return {
        "section removed": sub(("rules", "AGENTS.md"), "## Code Review Rules", "## Review"),
        "headings removed": lambda d: {**d, "rules": {**d["rules"], "AGENTS.md": d["rules"]["AGENTS.md"].replace("### ", "#### ")}},
        "rule that flags nothing": sub(("rules", "AGENTS.md"), first_rule, "Remember to be careful about " + first_rule[5:]),
        "mechanical rule added": lambda d: inject(d, "- Flag inconsistent formatting and lint errors.\n"),
        "safe paths removed": lambda d: {**d, "rules": {**d["rules"], "AGENTS.md": d["rules"]["AGENTS.md"].replace("Safe path", "Instead")}},
        "oversized rules": lambda d: inject(d, "<!-- " + "x" * 3200 + " -->\n"),
        "claude reference": lambda d: inject(d, "- Flag Claude Code edits.\n"),
        "nested rules file missing": lambda d: {**d, "rules": {**d["rules"], ".codex/hooks/AGENTS.md": None}},
        "operator setting removed from the doc": sub(("doc",), "chatgpt.com/settings/code-review", "the settings page"),
        "operator block removed from the doc": lambda d: {**d, "doc": d["doc"].replace("BLOCKED: operator", "done")},
        "doc overclaims": lambda d: {**d, "doc": d["doc"] + "\nCodex review guarantees every review catches regressions.\n"},
        "template asks for model approval": lambda d: {**d, "template": d["template"] + "\n- [ ] Approved by Codex\n"},
        "template missing": lambda d: {**d, "template": None},
        "workflow claims to enable the setting": lambda d: {**d, "workflows": {".github/workflows/x.yml": "name: enable codex automatic review\n"}},
    }


EXPECTED = {
    "section removed": "no '## Code Review Rules'", "headings removed": "at least one", "rule that flags nothing": "does not say what to flag",
    "mechanical rule added": "mechanical check", "safe paths removed": "safe path", "oversized rules": "exceed",
    "claude reference": "must not reference Claude", "nested rules file missing": "missing",
    "operator setting removed from the doc": "chatgpt.com/settings/code-review", "operator block removed from the doc": "BLOCKED: operator",
    "doc overclaims": "overclaims", "template asks for model approval": "model approval", "template missing": "missing",
    "workflow claims to enable the setting": "cannot enable",
}


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = gather()
    errs = run_all(data)
    for e in errs:
        print("FAIL:", e)
    if "--self-test" in argv:
        missed = []
        muts = mutations(data)
        for name, fn in muts.items():
            found = run_all(fn(data))
            if not any(EXPECTED[name] in e for e in found):
                missed.append(name)
        for n in missed:
            print("MISSED:", n)
        print(f"self-test: {len(muts) - len(missed)}/{len(muts)} mutations detected by the intended check")
        errs += missed
    print("PASS" if not errs else "FAILED")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
