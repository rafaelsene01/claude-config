#!/usr/bin/env python3
"""
validate_state.py - deterministic completion gate for a feature.

The skill's strongest invariant is "the Verifier is always-on, never prompted;
Execute is not done until validation.md reports PASS." That is prose the model
must remember. This turns it into a checkable pass/fail the closing step runs
automatically, so declaring a feature done without a real Verifier report fails
loudly instead of slipping through.

It does NOT merely check that a report exists - a report that exists but is
empty, still holds the template placeholder, or has no evidence would pass a
shallow existence check while proving nothing. This gate requires a real,
filled verdict plus at least one file:line evidence citation.

Two layouts are supported:

  multi  - one spec per context under specs/, one report per spec under
           validation/<spec-id>.md. A spec whose tasks are all complete MUST
           have a real PASS report; a spec still in flight is not gated.
  single - a legacy flat spec.md + validation.md.

Operates only on the .specs/ markdown artifacts (stack- and tool-agnostic). No
dependencies. Run from the project root (the dir that contains .specs), or pass
--root. Meant to be invoked by the skill as the closing gate of Execute, the
same way lessons.py is invoked at distillation - not a manual step.

Usage:
  python3 <skill-dir>/scripts/validate_state.py [feature]
  python3 <skill-dir>/scripts/validate_state.py

  Invoke from the skill directory that ships this script (not the project root).
  Pass --root when cwd is not the project that contains .specs/.

Exit codes: 0 ok, 1 a completed feature is missing a real PASS report,
            2 usage error.
"""

import argparse
import os
import re
import sys

# A file:line citation: a path with an extension, then :<line>. e.g. src/a.ts:42
EVIDENCE_RE = re.compile(r"[\w./-]+\.[A-Za-z0-9]+:\d+")


def _feature_dirs(root):
    base = os.path.join(root, ".specs", "features")
    if not os.path.isdir(base):
        return base, []
    dirs = [
        d for d in sorted(os.listdir(base))
        if os.path.isdir(os.path.join(base, d))
    ]
    return base, dirs


def _verdict(text):
    """Return 'pass', 'fail', 'unfilled', or None from a validation report."""
    # Look at the '## Validation' heading first, then a '**Result**' line.
    lines = text.splitlines()
    candidates = [
        ln for ln in lines
        if re.search(r"^#{1,4}\s*validation\b", ln.strip(), re.IGNORECASE)
        or re.search(r"\*{0,2}result\*{0,2}\s*:", ln.strip(), re.IGNORECASE)
    ]
    hay = " ".join(candidates) if candidates else text
    has_pass = re.search(r"\bPASS\b", hay) is not None
    has_fail = re.search(r"\bFAIL\b", hay) is not None
    if has_pass and has_fail:
        # Both present on the verdict line = unfilled template "[PASS | FAIL]".
        return "unfilled"
    if has_pass:
        return "pass"
    if has_fail:
        return "fail"
    return None


def _spec_ids(fdir):
    """Spec IDs for the multi-spec layout, or None for the legacy layout."""
    specs_dir = os.path.join(fdir, "specs")
    if not os.path.isdir(specs_dir):
        return None
    return sorted(
        os.path.splitext(f)[0] for f in os.listdir(specs_dir) if f.endswith(".md")
    )


def _spec_task_state(fdir):
    """Map spec_id -> {'tasks': n, 'open': m} by walking tasks.md task blocks.

    Returns {} when there is no tasks.md (Tasks phase skipped or not authored).
    """
    tasks = os.path.join(fdir, "tasks.md")
    if not os.path.exists(tasks):
        return {}
    body = open(tasks, encoding="utf-8", errors="replace").read()
    blocks = re.split(r"^#{2,4}\s+T\d+\s*:", body, flags=re.MULTILINE)[1:]
    state = {}
    for block in blocks:
        # A task block ends at the next top-level section (## / #). Without this
        # cut the LAST block runs to EOF and absorbs trailing checklists, whose
        # unchecked boxes would mark the spec permanently "in flight".
        cut = re.search(r"^#{1,2}\s+\S", block, re.MULTILINE)
        if cut:
            block = block[: cut.start()]
        m = re.search(r"^\*{0,2}Spec\*{0,2}\s*:\s*(.*)$", block, re.MULTILINE | re.IGNORECASE)
        if not m:
            continue
        sid = re.search(r"\d{2}-[a-z0-9][a-z0-9-]*", m.group(1))
        if not sid:
            continue
        sid = sid.group(0)
        entry = state.setdefault(sid, {"tasks": 0, "open": 0})
        entry["tasks"] += 1
        if re.search(r"^\s*-\s*\[\s\]", block, re.MULTILINE):
            entry["open"] += 1
    return state


def _appears_complete(fdir):
    """Conservative completeness heuristic for the cross-check mode.

    A feature 'appears complete' if it already has a validation.md, or if it has
    a tasks.md with at least one task and no unchecked '- [ ]' boxes left. When
    the signal is ambiguous (no tasks.md, Tasks phase skipped), returns False so
    an in-flight feature is never falsely flagged.
    """
    vdir = os.path.join(fdir, "validation")
    if os.path.isdir(vdir) and any(f.endswith(".md") for f in os.listdir(vdir)):
        return True
    if _spec_ids(fdir) is not None:
        state = _spec_task_state(fdir)
        return bool(state) and any(v["open"] == 0 for v in state.values())
    if os.path.exists(os.path.join(fdir, "validation.md")):
        return True
    tasks = os.path.join(fdir, "tasks.md")
    if not os.path.exists(tasks):
        return False
    body = open(tasks, encoding="utf-8", errors="replace").read()
    if not re.search(r"^#{2,4}\s+T\d+\s*:", body, re.MULTILINE):
        return False
    if re.search(r"^\s*-\s*\[\s\]", body, re.MULTILINE):
        return False  # unchecked box remains -> still in progress
    return True


def _check_report(vpath, label):
    """Verdict + evidence checks for one validation report."""
    errors = []
    text = open(vpath, encoding="utf-8", errors="replace").read()
    verdict = _verdict(text)
    if verdict is None:
        errors.append(f"{label}: no PASS/FAIL verdict (a prose-only report does not count)")
    elif verdict == "unfilled":
        errors.append(f"{label}: verdict is still the template placeholder '[PASS | FAIL]' - not filled")
    elif verdict == "fail":
        errors.append(f"{label}: verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (not done)")
    if verdict == "pass" and not EVIDENCE_RE.search(text):
        errors.append(f"{label}: PASS but cites no file:line evidence - evidence-or-zero not satisfied")
    return errors


def _check_feature(fdir, name):
    """Return list of error strings for one feature (empty = pass)."""
    specs = _spec_ids(fdir)
    if specs is None:
        return _check_legacy_feature(fdir, name)

    errors = []
    if not specs:
        errors.append(f"{name}: specs/ exists but holds no spec files - nothing was specified")
        return errors

    state = _spec_task_state(fdir)
    has_tasks_file = os.path.exists(os.path.join(fdir, "tasks.md"))
    vdir = os.path.join(fdir, "validation")
    unreported = []
    for sid in specs:
        vpath = os.path.join(vdir, sid + ".md")
        if not os.path.exists(vpath):
            st = state.get(sid)
            if not has_tasks_file:
                # Tasks phase was legitimately skipped: there is no completion
                # signal to read, so report the gap instead of failing on it.
                unreported.append(sid)
            elif st is None:
                errors.append(
                    f"{name}/{sid}: no validation report and no task in tasks.md declares `Spec: {sid}` - "
                    f"the spec is unimplemented, so the feature is not done"
                )
            elif st["open"] == 0:
                errors.append(
                    f"{name}/{sid}: all tasks complete but no validation/{sid}.md - a spec closes with its "
                    f"own Verifier (author != verifier). Dispatch validation before moving on."
                )
            # open tasks remain -> spec is legitimately in flight, not gated
            continue
        errors += _check_report(vpath, f"{name}/{sid}: validation/{sid}.md")
    if unreported:
        print(
            f"  NOTE  {name}: no tasks.md, so spec completion cannot be determined. "
            f"No validation report yet for: {', '.join(unreported)}. "
            f"Each must be verified before the feature is done."
        )
    return errors


def _check_legacy_feature(fdir, name):
    """Flat spec.md + validation.md layout."""
    vpath = os.path.join(fdir, "validation.md")
    if not os.path.exists(vpath):
        return [
            f"{name}: no validation.md - Execute is not done until the Verifier "
            f"writes it (author != verifier). Dispatch validation before marking done."
        ]
    return _check_report(vpath, f"{name}: validation.md")


def _resolve(root, feature):
    base, dirs = _feature_dirs(root)
    if not os.path.isdir(base):
        print(f"validate_state: no {base} directory - nothing to check.")
        return []
    if feature:
        fdir = feature if os.path.isdir(feature) else os.path.join(base, feature)
        if not os.path.isdir(fdir):
            print(f"validate_state: feature not found: {feature}", file=sys.stderr)
            raise SystemExit(2)
        return [(fdir, os.path.basename(fdir.rstrip("/")))]
    if len(dirs) == 1:
        return [(os.path.join(base, dirs[0]), dirs[0])]
    if not dirs:
        print("validate_state: no features under .specs/features/ - nothing to check.")
        return []
    # Cross-check mode: only features that appear complete.
    picked = [(os.path.join(base, d), d) for d in dirs if _appears_complete(os.path.join(base, d))]
    if not picked:
        print("validate_state: no completed feature detected (all in progress) - nothing to gate.")
    return picked


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_state.py", description="Deterministic completion gate: every finished spec must have a real PASS validation report.")
    p.add_argument("feature", nargs="?", default=None, help="Feature dir or name (default: sole feature, else cross-check all completed)")
    p.add_argument("--root", default=".", help="Project root containing .specs/ (default: current dir)")
    args = p.parse_args(argv)
    root = os.path.abspath(args.root)

    targets = _resolve(root, args.feature)
    all_errors = []
    for fdir, name in targets:
        all_errors += _check_feature(fdir, name)

    for e in all_errors:
        print(f"  ERROR {e}")
    n = len(all_errors)
    checked = ", ".join(name for _, name in targets) or "(none)"
    print(f"\nvalidate_state: {n} error(s) across [{checked}]")
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
