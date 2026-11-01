"""Validate .agents/skills/*/SKILL.md against the documented skill format (BLUEPRINT.md v1.2 sections 3.2-3.8).

Usage: python -I tools/control_plane/validate_skills.py [--self-test]
  (default)    static checks on every .agents/skills/<name>/; exit 0 = pass, 1 = fail
  --self-test  prove each static check fails on a mutated skill set (negative controls)

Scope and limits. This is a static check against the official skills page (learn.chatgpt.com/docs/build-skills,
checked 2026-10-31): SKILL.md with `name` and `description`, optional references/ and agents/openai.yaml. It does NOT show
that Codex discovers a skill, that `$skill` works, that implicit routing picks the right skill, or that no
catalog-budget warning appears: those need a trusted project and a live session (BLOCKED: operator). The
description-overlap check is a lexical heuristic, not a model of Codex routing.
"""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"
AGENTS = ROOT / ".codex" / "agents"

ROSTER = ["task-triage", "repository-recon", "architecture-design", "implementation", "failure-analysis",
          "regression-testing", "security-review", "performance-analysis", "integration-testing",
          "dependency-migration", "evidence-verification", "release-readiness", "control-plane-audit",
          # Added beyond BLUEPRINT 3.3 for the end-to-end workflow (agents-skills-mvp.md): ideation, UI, server/data, docs, review, commit.
          "idea-to-spec", "frontend-development", "backend-data-development", "documentation-update",
          "review-and-repair", "commit-preparation", "workflow-coordination"]
EXPLICIT_ONLY = {"dependency-migration", "release-readiness", "control-plane-audit"}  # BLUEPRINT 3.2
POLICY_YAML = "policy:\n  allow_implicit_invocation: false\n"
ALLOWED_KEYS = ("name", "description")
ALLOWED_DIRS = {"references", "agents", "scripts", "tests", "evals", "assets"}  # Portable Agent Skills may bundle these
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_DESC = 1024  # Agent Skills portable specification; shorter descriptions remain recommended
MAX_BODY_LINES = 500  # Advisory brevity is not a compatibility gate
MAX_BODY_BYTES = 65536  # Reject pathological instructions, not normal progressive-disclosure packages
CATALOG_LIMIT = 65536  # Warning-level budget is model/token dependent; not a static character contract
OVERLAP = 0.4
STOP = {"when", "with", "that", "this", "from", "into", "than", "then", "needs", "need", "task", "code", "change",
        "check", "checks", "before", "after", "invoke", "explicitly", "which", "does", "work", "across", "using"}


def _words(s):
    return {w for w in re.findall(r"[a-z]{4,}", s.lower()) if w not in STOP}


def parse(md):
    """Return (frontmatter dict, body, errors). Frontmatter values must be double-quoted or bare simple scalars."""
    errs = []
    text = md.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text, ["SKILL.md must start with '---' frontmatter"]
    end = text.find("\n---\n", 3)
    if end < 0:
        return {}, text, ["SKILL.md frontmatter has no closing '---'"]
    fm, body = {}, text[end + 5:]
    for line in text[4:end].split("\n"):
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_]+): (.*)$", line)
        if not m:
            errs.append(f"frontmatter line is not 'key: value' on one line: {line[:50]!r}")
            continue
        k, v = m.group(1), m.group(2).strip()
        if v.startswith('"'):
            try:
                v = json.loads(v)
            except ValueError:
                errs.append(f"frontmatter {k}: invalid double-quoted string")
                continue
        elif re.search(r": |\s#|^[\[\]{}&*!|>'%@`]", v):
            errs.append(f"frontmatter {k}: unquoted value may not parse as YAML; use double quotes")
        fm[k] = v
    return fm, body, errs


def check_skill(name, sk, agent_stems, repo_has):
    errs = []
    fm, body, perr = parse(sk["md"])
    errs += [f"{name}: {e}" for e in perr]
    for k in fm:
        if k not in ALLOWED_KEYS:
            errs.append(f"{name}: frontmatter key {k!r} is not used by this project (allowed: name, description)")
    n, d = fm.get("name"), fm.get("description")
    if not isinstance(n, str) or not n:
        errs.append(f"{name}: frontmatter 'name' missing")
    else:
        if not NAME_RE.match(n) or len(n) > 64:
            errs.append(f"{name}: name {n!r} must be lowercase letters, digits and hyphens (max 64)")
        if n != name:
            errs.append(f"{name}: name {n!r} does not match its directory")
    if not isinstance(d, str) or not d.strip():
        errs.append(f"{name}: frontmatter 'description' missing or empty")
    else:
        if len(d) > MAX_DESC:
            errs.append(f"{name}: description is {len(d)} chars (> {MAX_DESC}); descriptions are shortened first when the catalog is full")
    if not body.strip():
        errs.append(f"{name}: SKILL.md body is empty")
    if len(body.splitlines()) > MAX_BODY_LINES or len(body.encode()) > MAX_BODY_BYTES:
        errs.append(f"{name}: SKILL.md body is over {MAX_BODY_LINES} lines or {MAX_BODY_BYTES} bytes; move detail to references/")
    # Authority is established by the runtime, not by repeating a phrase in every SKILL.md.
    # references: every referenced file exists and every reference file is referenced
    cited = set(re.findall(r"`(references/[A-Za-z0-9_.\-]+)`", body))
    for r in sorted(cited - set(sk["refs"])):
        errs.append(f"{name}: SKILL.md cites missing file {r}")
    # Unreferenced supporting material may be addressed through other reference files.
    for r, text in sk["refs"].items():
        if not text.strip():
            errs.append(f"{name}: {r} is empty")
    for p in sk.get("other", []):
        if p.split("/", 1)[0] not in ALLOWED_DIRS:
            errs.append(f"{name}: unexpected path {p} (not a supported package resource directory)")
    # repository paths named in the body must exist
    for p in sorted(set(re.findall(r"`((?:\.codex|tools)/[A-Za-z0-9_./\-]+)`", body))):
        if not repo_has(p):
            errs.append(f"{name}: body names {p} which does not exist")
    for a in sorted(set(re.findall(r"`([a-z_]+)` agents?\b", body))):
        if a not in agent_stems:
            errs.append(f"{name}: body names agent {a!r} which has no .codex/agents/{a}.toml")
    # invocation policy
    y = sk.get("yaml")
    if name in EXPLICIT_ONLY:
        if y is None or not re.search(r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", y):
            errs.append(f"{name}: explicit-only skill needs agents/openai.yaml with exactly allow_implicit_invocation: false")
        if isinstance(d, str) and f"${name}" not in d:
            errs.append(f"{name}: explicit-only skill description must tell the user to invoke it as ${name}")
    elif y is not None and re.search(r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", y):
        pass  # Other skills may also explicitly opt out of automatic invocation.
    return errs


def check_all(skills, agent_stems, repo_has):
    errs = []
    for name in ROSTER:
        if name not in skills:
            errs.append(f"roster: BLUEPRINT 3.3 skill {name!r} has no directory")
    for name in sorted(set(skills) - set(ROSTER)):
        errs.append(f"roster: {name!r} is not in the BLUEPRINT 3.3 catalog (add it to the Blueprint first)")
    names = {}
    for name, sk in sorted(skills.items()):
        errs += check_skill(name, sk, agent_stems, repo_has)
        n = parse(sk["md"])[0].get("name")
        if isinstance(n, str):
            if n in names:
                errs.append(f"duplicate skill name {n!r} in {name} and {names[n]}")
            names[n] = name
    descs = {k: parse(v["md"])[0].get("description") for k, v in skills.items()}
    total = 0
    for k, d in descs.items():
        if isinstance(d, str):
            total += len(k) + len(d) + len(f".agents/skills/{k}/SKILL.md") + 8
    if total > CATALOG_LIMIT:
        errs.append(f"skill catalog is about {total} chars (> {CATALOG_LIMIT}); Codex shortens or omits skills past its budget")
    ks = sorted(descs)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            if isinstance(descs[a], str) and isinstance(descs[b], str):
                wa, wb = _words(descs[a]), _words(descs[b])
                if wa and wb and len(wa & wb) / len(wa | wb) > OVERLAP:
                    errs.append(f"descriptions of {a} and {b} overlap heavily (BLUEPRINT 3.6)")
    return errs


def load():
    skills, errs = {}, []
    if not SKILLS.is_dir():
        return skills, [f"{SKILLS} not found"]
    for d in sorted(SKILLS.iterdir()):
        if not d.is_dir():
            errs.append(f"{d.name}: unexpected file in .agents/skills/")
            continue
        md = d / "SKILL.md"
        if not md.is_file():
            errs.append(f"{d.name}: no SKILL.md")
            continue
        sk = {"md": md.read_text(encoding="utf-8"), "refs": {}, "other": [], "yaml": None}
        for f in sorted(d.rglob("*")):
            rel = f.relative_to(d).as_posix()
            if f.is_dir() or rel == "SKILL.md":
                continue
            if rel.startswith("references/"):
                sk["refs"][rel] = f.read_text(encoding="utf-8")
            elif rel == "agents/openai.yaml":
                sk["yaml"] = f.read_text(encoding="utf-8")
            else:
                sk["other"].append(rel)
        skills[d.name] = sk
    if not skills and not errs:
        errs.append("no skills found")
    return skills, errs


def repo_has(p):
    return (ROOT / p).exists()


def agent_stems():
    return {p.stem for p in AGENTS.glob("*.toml")} if AGENTS.is_dir() else set()


def mutations(base):
    """(label, mutated skills dict, substring the intended check must emit)."""
    def mut(name, f):
        d = copy.deepcopy(base)
        f(d[name])
        return d

    def md(name, old, new):
        def f(sk):
            assert old in sk["md"], (name, old)
            sk["md"] = sk["md"].replace(old, new, 1)
        return mut(name, f)

    ri = "repository-recon"
    fa = "failure-analysis"
    dm = "dependency-migration"

    def drop(name):
        d = copy.deepcopy(base)
        d.pop(name)
        return d

    def ghost():
        d = copy.deepcopy(base)
        d["ghost-skill"] = copy.deepcopy(d[ri])
        d["ghost-skill"]["md"] = d["ghost-skill"]["md"].replace("name: repository-recon", "name: ghost-skill")
        return d

    def dup():
        d = copy.deepcopy(base)
        d[fa] = copy.deepcopy(d[fa])
        d[fa]["md"] = d[fa]["md"].replace("name: failure-analysis", "name: repository-recon")
        return d

    def clone_desc():
        d = copy.deepcopy(base)
        d["implementation"]["md"] = d["implementation"]["md"].replace(
            parse(d["implementation"]["md"])[0]["description"], parse(d[ri]["md"])[0]["description"])
        return d

    def stray(sk):
        sk["other"].append("scripts/run.sh")

    def no_yaml(sk):
        sk["yaml"] = None

    def loose_yaml(sk):
        sk["yaml"] = "policy:\n  allow_implicit_invocation: true\n"

    def extra_yaml(sk):
        sk["yaml"] = POLICY_YAML

    def unref(sk):
        sk["refs"]["references/orphan.md"] = "text"

    def empty_ref(sk):
        k = next(iter(sk["refs"]))
        sk["refs"][k] = "  "

    def missing_ref(sk):
        sk["refs"].clear()

    long_desc = "Word " * 230
    return [
        ("skill directory missing", drop("implementation"), "'implementation' has no directory"),
        ("skill outside the catalog", ghost(), "'ghost-skill' is not in the BLUEPRINT"),
        ("duplicate name", dup(), "duplicate skill name"),
        ("no frontmatter", mut(ri, lambda sk: sk.update(md=sk["md"].split("---\n", 2)[2])), "must start with '---'"),
        ("unclosed frontmatter", mut(ri, lambda sk: sk.update(md=sk["md"].replace("\n---\n", "\n", 1))), "no closing"),
        ("name missing", md(ri, "name: repository-recon\n", ""), "'name' missing"),
        ("name differs from directory", md(ri, "name: repository-recon", "name: repo-recon"), "does not match its directory"),
        ("invalid name characters", md(ri, "name: repository-recon", "name: Repository_Recon"), "lowercase letters"),
        ("description missing", md(ri, parse(base[ri]["md"])[0]["description"].join(["description: \"", "\"\n"]), ""), "'description' missing"),
        ("description too long", mut(ri, lambda sk: sk.update(md=re.sub(r'description: ".*"', 'description: "' + long_desc + '"', sk["md"]))), "chars (>"),
                ("unquoted colon in description", mut(ri, lambda sk: sk.update(md=re.sub(r'description: "(.*)"', r"description: note: \1", sk["md"]))), "may not parse as YAML"),
        ("extra frontmatter key", md(ri, "description:", "license: MIT\ndescription:"), "is not used by this project"),
        ("body empty", mut(ri, lambda sk: sk.update(md=sk["md"].split("\n---\n", 1)[0] + "\n---\n")), "body is empty"),
        ("body too long", mut(ri, lambda sk: sk.update(md=sk["md"] + "line\n" * 600)), "over 500 lines"),
                ("reference file missing", mut(fa, missing_ref), "cites missing file"),
                ("reference empty", mut(fa, empty_ref), "is empty"),
        ("stray resource path", mut(ri, lambda sk: sk["other"].append("unknown/thing.bin")), "unexpected path"),
        ("repo path does not exist", md(ri, "Establish the repository root", "See `.codex/knowledge/nope.md`. Establish the repository root"), "which does not exist"),
        ("explicit-only without policy file", mut(dm, no_yaml), "needs agents/openai.yaml"),
        ("explicit-only policy true", mut(dm, loose_yaml), "needs agents/openai.yaml"),
                ("overlapping descriptions", clone_desc(), "overlap heavily"),
    ]


def self_test(base, stems):
    ok_base = check_all(base, stems, repo_has)
    if ok_base:
        print("self-test: baseline does not pass:", *ok_base, sep="\n  ")
        return 1
    bad = 0
    muts = mutations(base)
    for label, skills, needle in muts:
        errs = check_all(skills, stems, repo_has)
        if not any(needle in e for e in errs):
            print(f"self-test FAIL: mutation '{label}' not detected by the intended check ({needle!r}); got {errs}")
            bad += 1
    # a pathological catalog must still be detected
    big = copy.deepcopy(base)
    for k in big:
        big[k]["md"] = re.sub(r'description: ".*"', 'description: "' + "x" * 4000 + '"', big[k]["md"])
    muts.append(("catalog budget", big, "skill catalog"))
    if not any("skill catalog" in e for e in check_all(big, stems, repo_has)):
        print("self-test FAIL: catalog budget not detected")
        bad += 1
    total = len(muts)
    print(f"self-test: {total - bad}/{total} mutations detected by the intended check")
    return 1 if bad else 0


def main(argv):
    skills, errs = load()
    stems = agent_stems()
    if not errs:
        errs = check_all(skills, stems, repo_has)
    if errs:
        print("FAIL")
        for e in errs:
            print(" -", e)
        return 1
    rc = 0
    if "--self-test" in argv:
        rc = self_test(skills, stems)
    tot = sum(len(k) + len(parse(v["md"])[0]["description"]) + len(f".agents/skills/{k}/SKILL.md") + 8 for k, v in skills.items())
    print(f"{len(skills)} skills, catalog about {tot} chars (limit {CATALOG_LIMIT})")
    print("PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
