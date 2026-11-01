"""Shared helpers for CODEX PRIME hook handlers (stdlib only, no network, no file writes).

Guardrail code, not a security boundary: see .codex/knowledge/hooks.md for what each event can and cannot enforce.
The command matcher is a deny list over a best-effort tokenization. It cannot see inside interpreters (python -c,
node -e), variables, aliases defined elsewhere, or files a script writes and then runs.
"""
import base64
import json
import os
import posixpath
import re
import shlex
import sys

MAX_INPUT = 1_000_000
MAX_COMMAND = 200_000
MAX_DEPTH = 5
STATUSES = ("COMPLETE", "PARTIAL", "BLOCKED", "CONFLICTED", "UNVERIFIED")
BYPASS_FLAGS = {
    "--dangerously-bypass-hook-trust", "--dangerously-bypass-approvals-and-sandbox",
    "--yolo", "--ignore-rules", "--skip-git-repo-check",
}
GENERATED_DIRS = {".codex-runtime", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", "target"}
CONTROL_PATH = re.compile(r"(^|/)\.codex/(hooks/|hooks\.json$|rules/|config\.toml$)")
CONTROL_TEXT = re.compile(r"(^|[/\s'\"=<>(])\.codex/(hooks/|hooks\.json|rules/|config\.toml)", re.I)
GIT_DIR_PATH = re.compile(r"(^|/)\.git(/|$)")
ENV_FILE = re.compile(r"(^|/)\.env(rc|\.[^/]*)?$")
ENV_OK_SUFFIX = (".example", ".sample", ".template")
CRED_TEXT = re.compile(r"\.codex[/\\]auth\.json|CODEX_HOME[^\n]{0,40}auth\.json", re.I)
WRAPPERS = {"sudo", "command", "env", "nohup", "time", "exec", "nice", "xargs", "timeout", "setsid", "doas", "stdbuf", "ionice"}
INTRO = WRAPPERS | {"eval", "iex", "invoke-expression", "then", "do", "else", "if", "while", "!", "-exec", "-execdir", "-ok",
                    "call", "start", "foreach-object", "%"}
TARGETS = {"git", "rm", "remove-item", "ri", "rd", "rmdir", "del", "erase", "codex", "find"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
WIN_SHELLS = {"powershell", "pwsh", "cmd"}
GIT_OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
COMMIT_VALUE_FLAGS = {"-m", "-F", "-c", "-C", "--message", "--file", "--author", "--date", "--template", "-t"}


class TooComplex(Exception):
    pass


def read_event():
    """Return the parsed event object, or None when stdin is missing, oversized or not a JSON object."""
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    except Exception:
        return None
    if len(raw) > MAX_INPUT:
        return None
    try:
        event = json.loads(raw.decode("utf-8"))
    except Exception:
        return None
    return event if isinstance(event, dict) else None


def emit(obj):
    sys.stdout.write(json.dumps(obj, separators=(",", ":")))
    sys.stdout.flush()


def deny_pretool(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def deny_permission(message):
    return {"hookSpecificOutput": {"hookEventName": "PermissionRequest",
                                   "decision": {"behavior": "deny", "message": message}}}


def norm_path(p):
    p = str(p).replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def canon_path(p):
    """Lower-case, slash-normalized, dot-segments collapsed: for matching on case-insensitive filesystems."""
    p = str(p).replace("\\", "/").lower()
    m = re.match(r"^([a-z]:)(/.*)?$", p)
    drive, rest = (m.group(1), m.group(2) or "") if m else ("", p)
    return drive + posixpath.normpath(rest) if rest else drive


def find_root(start):
    """Nearest ancestor of start that contains a .git entry, else None."""
    try:
        cur = os.path.abspath(start)
    except Exception:
        return None
    for _ in range(64):
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            return None
        cur = nxt
    return None


def safe_name(value, default="unknown"):
    raw = str(value or "")
    s = re.sub(r"[^A-Za-z0-9._-]", "_", raw)[:96].strip(".")
    if s != raw and s:  # keep distinct ids distinct after sanitizing
        import hashlib
        s = s[:80] + "-" + hashlib.sha1(raw.encode("utf-8", "replace")).hexdigest()[:8]
    return s or default


def _tokens(text, escape=""):
    text = text.replace("\r", " ").replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        lex.escape = escape  # "" treats backslash as a Windows path separator; "\\" as a POSIX escape
        return list(lex)
    except ValueError:
        return text.split()


def _exe(tok):
    base = tok.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return base[:-4] if base.endswith(".exe") else base


def _clean(tok):
    return tok.lstrip("({$`&!").rstrip(")};`")


def _strip(seg):
    seg = list(seg)
    while seg:
        t = seg[0]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
            seg.pop(0)
            continue
        break
    return seg


def _script_of(seg):
    """If seg is an interpreter invocation with an inline script, return that script text."""
    exe = _exe(_clean(seg[0]))
    if exe in SHELLS:
        for i, t in enumerate(seg[1:], 1):
            if t.startswith("-") and not t.startswith("--") and "c" in t[1:] and i + 1 < len(seg):
                return seg[i + 1]
    elif exe in WIN_SHELLS:
        for i, t in enumerate(seg[1:], 1):
            low = t.lower()
            if len(low) >= 2 and low.startswith("-") and "-command".startswith(low) and i + 1 < len(seg):
                return " ".join(seg[i + 1:])
            if low == "/c" and i + 1 < len(seg):
                return " ".join(seg[i + 1:])
            if len(low) >= 2 and low.startswith("-e") and "-encodedcommand".startswith(low) and i + 1 < len(seg):
                try:
                    return base64.b64decode(seg[i + 1]).decode("utf-16-le")
                except Exception:
                    return None
        if exe in ("powershell", "pwsh"):
            return " ".join(seg[1:])  # script text given without -Command
    elif exe in ("eval", "iex", "invoke-expression"):
        return " ".join(seg[1:])
    return None


def split_segments(command, depth=0):
    """Split a shell command into token segments, unwrapping inline scripts. Raises TooComplex past MAX_DEPTH."""
    if depth > MAX_DEPTH:
        raise TooComplex()
    text = command[:MAX_COMMAND]
    # Backslash is a path separator on Windows and an escape in POSIX shells. Only when it escapes a quote (nested quoting) is the
    # command also read the POSIX way and the union evaluated; otherwise Windows paths like .\node_modules would be mangled.
    variants = ["", "\\"] if re.search(r"""\\["']""", text) else [""]
    out, seen = [], set()
    for esc in variants:
        segs, cur = [], []
        for t in _tokens(text, esc):
            if t and set(t) <= set(";&|"):
                if cur:
                    segs.append(cur)
                cur = []
            else:
                cur.append(t)
        if cur:
            segs.append(cur)
        for seg in segs:
            seg = _strip(seg)
            if not seg:
                continue
            script = _script_of(seg)
            if script:
                for inner in split_segments(script, depth + 1):
                    if tuple(inner) not in seen:
                        seen.add(tuple(inner))
                        out.append(inner)
            if tuple(seg) not in seen:
                seen.add(tuple(seg))
                out.append(seg)
    return out


def iter_commands(command):
    """Yield token lists that start at a command word we have rules for, including ones behind wrappers or punctuation."""
    for seg in split_segments(command):
        ex = [_exe(_clean(t)) for t in seg]
        for j, name in enumerate(ex):
            if name not in TARGETS:
                continue
            glued = _clean(seg[j]) != seg[j] and seg[j][:1] in "({$`&!"
            behind = any(ex[k] in INTRO or _clean(seg[k]) == "" for k in range(max(0, j - 6), j))
            if j == 0 or glued or behind:
                yield [_clean(seg[j])] + [t.rstrip(")};`") for t in seg[j + 1:]]


def _git_parts(seg):
    """Return (subcommand, args) for a git segment, skipping global options."""
    i = 1
    while i < len(seg):
        t = seg[i]
        if t in GIT_OPTS_WITH_ARG:
            i += 2
        elif t.startswith("-"):
            i += 1
        else:
            return t, seg[i + 1:]
    return None, []


def _cluster(args, letter):
    """True when a pure short-flag cluster such as -fd or -nm contains the letter."""
    return any(re.fullmatch(r"-[A-Za-z]+", a) and letter in a[1:] for a in args)


def _flags_only(args):
    """Drop the values that follow value-taking commit flags so message text is never read as a flag."""
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a in COMMIT_VALUE_FLAGS:
            skip = True
            continue
        out.append(a)
    return out


def _git_reason(seg):
    # Config-level command smuggling: -c alias.x=... or editing aliases.
    for i, t in enumerate(seg[1:-1], 1):
        if t == "-c" and seg[i + 1].lower().startswith(("alias.", "core.hookspath", "core.sshcommand", "core.fsmonitor")):
            return "git -c alias or hook-path overrides can smuggle commands"
    sub, args = _git_parts(seg)
    flags = _flags_only(args)
    if sub == "config" and any(a.lower().startswith("alias.") for a in args):
        return "git aliases can smuggle destructive commands"
    if sub == "clean":
        dry = "--dry-run" in args or _cluster(args, "n")
        return None if dry else "git clean removes untracked work; ask the user to clean the tree themselves"
    if sub == "reset" and ("--hard" in args or "--merge" in args):
        return "git reset --hard discards work; needs explicit user authorization"
    if sub == "checkout" and ("--" in args or "." in args or "-f" in args or "--force" in args or "-B" in args or _cluster(args, "f")):
        return "git checkout that forces or discards path changes needs explicit user authorization"
    if sub == "switch" and ("-f" in args or "--force" in args or "--discard-changes" in args or _cluster(args, "f")):
        return "git switch that discards changes needs explicit user authorization"
    if sub == "restore" and not ("--staged" in args and "--worktree" not in args):
        return "git restore discards working-tree changes; needs explicit user authorization"
    if sub == "stash" and (not args or args[0] not in ("list", "show")):
        return "git stash hides or drops user work; needs explicit user authorization"
    if sub == "branch" and ("-D" in args or (("--delete" in args or _cluster(args, "d")) and ("--force" in args or _cluster(args, "f")))):
        return "forced branch deletion needs explicit user authorization"
    if sub in ("commit", "push", "merge", "am") and ("--no-verify" in args or (sub == "commit" and _cluster(flags, "n"))):
        return "bypassing git hooks needs explicit user authorization"
    if sub == "push":
        if (any(a in ("--force", "-f", "--force-if-includes", "--delete", "-d", "--mirror", "--prune") or a.startswith("--force-with-lease")
                or a.startswith("+") or a.startswith(":") for a in args) or _cluster(args, "f")):
            return "forced, mirroring or deleting pushes need a separate authorized workflow"
    return None


def _delete_reason(seg):
    exe = _exe(seg[0])
    args = seg[1:]
    low = [a.lower() for a in args]
    if exe == "find":
        return "find -delete removes files recursively; needs explicit user authorization" if "-delete" in low else None
    if exe == "rm":
        recursive = "--recursive" in args or _cluster(args, "r") or _cluster(args, "R")
    elif exe in ("remove-item", "ri"):
        recursive = any(len(a) >= 2 and a.startswith("-") and "-recurse".startswith(a) for a in low)
    elif exe in ("rd", "rmdir", "del", "erase"):
        recursive = any(re.fullmatch(r"(/[a-z])+", a) and "/s" in a for a in low) or any(a in ("-recurse", "/s") for a in low)
    else:
        return None
    if not recursive:
        return None
    slash_flags = exe in ("rd", "rmdir", "del", "erase")
    targets = [a for a in args if not a.startswith("-") and not (slash_flags and re.fullmatch(r"(/[A-Za-z])+", a))]
    if not targets:
        return "recursive delete without an explicit target"
    for t in targets:
        for piece in t.split(","):
            n = norm_path(piece).rstrip("/")
            parts = [p for p in n.split("/") if p]
            bad = (not parts or n.startswith("/") or n.startswith("~") or re.match(r"^[A-Za-z]:", n)
                   or ".." in parts or any(c in n for c in "*?$%") or n in (".", ""))
            if bad or parts[0].lower() not in GENERATED_DIRS:
                return "recursive delete outside generated directories needs explicit user authorization"
    return None


def evaluate_bash(command):
    """Return a denial reason for a narrow list of unsafe shell operations, else None."""
    if not isinstance(command, str):
        return None
    if len(command) > MAX_COMMAND:
        return "command too long to evaluate safely; split it into smaller commands"
    if CRED_TEXT.search(command):
        return "credential files must not be read"
    try:
        cmds = list(iter_commands(command))
    except TooComplex:
        return "command is nested too deeply to evaluate safely; simplify it"
    for seg in cmds:
        exe = _exe(seg[0])
        if exe == "codex" and any(t in BYPASS_FLAGS for t in seg):
            return "approval, sandbox, rule and hook-trust bypass flags are operator-only"
        r = _git_reason(seg) if exe == "git" else _delete_reason(seg)
        if r:
            return r
    return None


def patch_paths(patch):
    if not isinstance(patch, str):
        return []
    pat = r"^\*\*\* (?:Add File|Update File|Delete File|Move to):\s*(.+)$"
    return [m.group(1).strip() for m in re.finditer(pat, patch[:MAX_INPUT], re.M)]


def evaluate_patch(patch):
    for raw in patch_paths(patch):
        p = canon_path(raw)
        if ENV_FILE.search(p) and not p.endswith(ENV_OK_SUFFIX):
            return f"patches must not touch environment files ({raw})"
        if CONTROL_PATH.search(p):
            return f"hooks, rules and project config are changed by the operator, not in-session ({raw})"
        if GIT_DIR_PATH.search(p):
            return f"patches must not touch .git ({raw})"
    return None


def control_text(command):
    """True when raw command text names a hook, rule or project-config path (case-insensitive, dot segments collapsed)."""
    text = re.sub(r"(?:/\./)+", "/", norm_path(command[:MAX_COMMAND]))
    text = re.sub(r"/{2,}", "/", text)
    return bool(CONTROL_TEXT.search(text))


RUNNERS = {"pytest", "py.test", "tox", "nox", "jest", "vitest", "mocha", "rspec", "phpunit"}
PYTHONS = {"python", "python3", "py", "pypy", "pypy3"}
PKG = {"npm", "pnpm", "yarn", "cargo", "go", "dotnet", "mvn", "gradle", "make", "bun", "deno"}
LINTERS = {"ruff", "flake8", "pylint", "eslint", "mypy", "tsc", "black", "prettier", "pyright"}
GIT_READ = ("status", "diff", "log", "show", "rev-parse", "branch", "ls-files", "blame")
SCRIPT_TEST = re.compile(r"(^|[/\\_-])(test|check|validate)[a-z_]*\.py$|^test_.*\.py$")


def _classify(seg):
    exe = _exe(_clean(seg[0]))
    args = [a.lower() for a in seg[1:]]
    if exe == "git":
        sub, _ = _git_parts(seg)
        return "git-read" if sub in GIT_READ else "git-write"
    if exe in RUNNERS:
        return "test"
    if exe in PYTHONS:
        if "-m" in args:
            mod = args[args.index("-m") + 1] if args.index("-m") + 1 < len(args) else ""
            if mod.split(".")[0] in ("pytest", "unittest", "tox", "nox"):
                return "test"
            if mod in ("ruff", "flake8", "pylint", "mypy", "black"):
                return "lint"
        if "--self-test" in args or any(SCRIPT_TEST.search(a) for a in args if a.endswith(".py")):
            return "test"
        return "other"
    if exe in PKG:
        if "test" in args:
            return "test"
        if "build" in args or (exe == "make" and not args):
            return "build"
        return "other"
    if exe in LINTERS:
        return "lint"
    return "other"


def command_class(command):
    """Coarse, non-secret class of a shell command: test, build, lint, git-write, git-read or other."""
    classes = set()
    try:
        segs = split_segments(command) if isinstance(command, str) else []
    except TooComplex:
        return "other"
    for seg in segs:
        if _script_of(seg) is not None:
            continue  # the unwrapped inner segments carry the class
        classes.add(_classify(seg))
    for c in ("test", "build", "lint", "git-write", "git-read"):
        if c in classes:
            return c
    return "other"
