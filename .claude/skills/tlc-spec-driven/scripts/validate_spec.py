#!/usr/bin/env python3
"""
validate_spec.py - deterministic closure-gate checks for a feature's spec set.

Turns the Requirement Closure Gate (Specify phase) into a checkable pass/fail
run BEFORE specs are presented for confirmation, instead of trusting the model
to remember the checks. Pure standard library, zero dependencies. Operates only
on the markdown artifacts under .specs/ - never on the target codebase - so it
stays stack-agnostic and tool-agnostic.

Layouts (both supported):

  multi  - .specs/features/<feature>/overview.md + specs/NN-<slug>.md   (current)
  single - .specs/features/<feature>/spec.md                            (legacy)

What it checks (heuristic markdown inspection, not a full parser):

  Per spec file:
    ERROR  - a required section is missing
    ERROR  - an acceptance criterion has no SHALL (not testable / not EARS-shaped)
    ERROR  - an Assumptions row has an empty "Chosen default" or "Rationale" cell
    ERROR  - a Requirement Traceability row has a malformed ID
    WARN   - an AC has SHALL but no recognizable EARS lead keyword
    WARN   - template placeholder rows are still present (spec not filled in)
    WARN   - open questions are not explicitly resolved
    WARN   - the spec has no Shared Context digest (self-containment contract)

  Across the feature (multi layout only):
    ERROR  - overview.md missing, or missing a required section
    ERROR  - a Spec Index row points to a spec file that does not exist
    ERROR  - a spec file on disk is absent from the Spec Index
    ERROR  - a `Depends on` names a spec that does not exist
    ERROR  - the Spec Index `Depends on` column disagrees with the spec's own
             `Depends on` field
    ERROR  - the spec dependency graph contains a cycle
    ERROR  - the same requirement ID is minted by two different specs
    WARN   - a spec mints requirement IDs under more than one prefix

Usage:
  python3 <skill-dir>/scripts/validate_spec.py [target] [--root DIR] [--strict]

  Invoke from the skill directory that ships this script (not the project root).
  target    A feature name, a feature directory, a single spec file, or a
            project root. Omitted -> auto-detect the single feature under
            <root>/.specs/features/.
  --root    Project root that contains .specs/ (default: current dir).
  --strict  Treat warnings as errors.

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

REQUIRED_SECTIONS_LEGACY = [
    "Problem Statement",
    "Out of Scope",
    "Assumptions & Open Questions",
    "User Stories",
    "Requirement Traceability",
]

REQUIRED_SECTIONS_SPEC = [
    "Scope",
    "Assumptions & Open Questions",
    "User Stories",
    "Requirement Traceability",
]

REQUIRED_SECTIONS_OVERVIEW = [
    "Problem Statement",
    "Out of Scope",
    "Spec Index",
]

ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")
PLACEHOLDER_RE = re.compile(r"^\s*\[.+\]\s*$")
SPEC_FILE_RE = re.compile(r"^\d{2}-[a-z0-9][a-z0-9-]*$")
STATUS_VALUES = {"pending", "in design", "in tasks", "implementing", "verified"}


# --------------------------------------------------------------------------
# Target resolution
# --------------------------------------------------------------------------

def resolve_target(target, root):
    """Return (mode, feature_dir, paths).

    mode 'multi'  -> feature_dir holds overview.md + specs/
    mode 'single' -> paths is a one-element list with a spec.md (legacy) or an
                     explicitly passed spec file.
    """
    if target:
        if os.path.isfile(target):
            return ("single", os.path.dirname(target) or ".", [target])
        if os.path.isdir(target):
            resolved = _classify_dir(target)
            if resolved:
                return resolved
            return _autodetect(target)
        cand = os.path.join(root, ".specs", "features", target)
        resolved = _classify_dir(cand)
        if resolved:
            return resolved
        return None
    return _autodetect(root)


def _classify_dir(d):
    """Classify a candidate FEATURE directory. Returns None if it is not one."""
    specs_dir = os.path.join(d, "specs")
    if os.path.isdir(specs_dir):
        return ("multi", d, sorted(
            os.path.join(specs_dir, f)
            for f in os.listdir(specs_dir)
            if f.endswith(".md")
        ))
    legacy = os.path.join(d, "spec.md")
    if os.path.isfile(legacy):
        return ("single", d, [legacy])
    return None


def _autodetect(root):
    base = os.path.join(root, ".specs", "features")
    if not os.path.isdir(base):
        return None
    features = []
    for d in sorted(os.listdir(base)):
        if _classify_dir(os.path.join(base, d)):
            features.append(d)
    if len(features) == 1:
        return _classify_dir(os.path.join(base, features[0]))
    if not features:
        return None
    raise SystemExit(
        "validate_spec: multiple features found; pass one explicitly:\n  "
        + "\n  ".join(features)
    )


# --------------------------------------------------------------------------
# Markdown helpers
# --------------------------------------------------------------------------

def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def is_separator(line):
    return bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)) and "-" in line


def unbacktick(s):
    return s.strip().strip("`").strip()


def section_bounds(lines, name):
    """Return (start, end) line indices for a `## name` section body."""
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^#{1,3}\s+" + re.escape(name) + r"\s*$", ln.strip()):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"^#{1,3}\s+\S", lines[j]):
            end = j
            break
    return (start, end)


def table_rows(lines, bounds):
    """Data rows (header and separator dropped) of the first table in a section."""
    if not bounds:
        return []
    rows = [lines[i] for i in range(*bounds) if lines[i].strip().startswith("|")]
    data = [r for r in rows if not is_separator(r)]
    return data[1:] if data else []


def classify_ears(text):
    """Return (ok, note). ok requires a SHALL; note records the EARS pattern."""
    t = text.strip()
    low = t.lower()
    has_shall = bool(re.search(r"\bshall\b", low))
    if not has_shall:
        return (False, "no SHALL")
    kws = []
    if re.search(r"\bwhile\b", low):
        kws.append("WHILE")
    if re.search(r"\bwhen\b", low):
        kws.append("WHEN")
    if re.match(r"^\s*if\b", low) or re.search(r"\bif\b.*\bthen\b", low):
        kws.append("IF/THEN")
    if re.search(r"\bwhere\b", low):
        kws.append("WHERE")
    if len(kws) >= 2:
        return (True, "complex (" + "+".join(kws) + ")")
    if kws:
        pattern = {
            "WHILE": "state-driven",
            "WHEN": "event-driven",
            "IF/THEN": "unwanted-behavior",
            "WHERE": "optional-feature",
        }[kws[0]]
        return (True, pattern)
    if re.match(r"^\s*the\b", low):
        return (True, "ubiquitous")
    return (True, "warn: SHALL present but no EARS lead keyword")


# --------------------------------------------------------------------------
# Per-file checks
# --------------------------------------------------------------------------

def check_spec_file(path, required_sections, label):
    """Check one spec file. Returns (errors, warnings, requirement_ids, depends_on)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    errors, warnings = [], []

    for name in required_sections:
        if section_bounds(lines, name) is None:
            errors.append(f"{label}: missing required section: ## {name}")

    # Acceptance criteria are EARS-shaped (have a SHALL).
    in_ac = False
    for i, ln in enumerate(lines, start=1):
        stripped = ln.strip()
        if re.match(r"^\*{0,2}Acceptance Criteria\*{0,2}.*:?\s*$", stripped) and "Acceptance Criteria" in stripped:
            in_ac = True
            continue
        if in_ac:
            m = re.match(r"^\s*\d+\.\s+(.*)$", ln)
            if m:
                item = m.group(1).strip()
                if PLACEHOLDER_RE.match(item):
                    continue  # untouched template row
                ok, note = classify_ears(item)
                if not ok:
                    errors.append(f"{label}:L{i}: acceptance criterion has no SHALL (not testable): {item[:70]}")
                elif note.startswith("warn"):
                    warnings.append(f"{label}:L{i}: AC has SHALL but no EARS keyword (WHEN/WHILE/WHERE/IF or ubiquitous 'The … shall'): {item[:60]}")
            elif re.match(r"^#{1,3}\s", ln) or stripped.startswith("**") or stripped.startswith("---") or stripped.startswith("|"):
                # A blank line does NOT close the list - the template puts one
                # between the "Acceptance Criteria" heading and the first item.
                in_ac = False

    # Assumptions table cells filled.
    b = section_bounds(lines, "Assumptions & Open Questions")
    if b:
        template_seen = False
        for r in table_rows(lines, b):
            cells = split_row(r)
            if len(cells) < 3:
                continue
            assumption, chosen, rationale = cells[0], cells[1], cells[2]
            if PLACEHOLDER_RE.match(assumption) and PLACEHOLDER_RE.match(chosen):
                template_seen = True
                continue
            if not chosen or PLACEHOLDER_RE.match(chosen):
                errors.append(f"{label}: assumption '{assumption[:40]}' has empty 'Chosen default'")
            if not rationale or PLACEHOLDER_RE.match(rationale):
                errors.append(f"{label}: assumption '{assumption[:40]}' has empty 'Rationale'")
        if template_seen:
            warnings.append(f"{label}: Assumptions table still contains template placeholder rows")
        oq = [lines[i] for i in range(*b) if "open questions" in lines[i].lower()]
        oq_clean = re.sub(r"[*_]", "", " ".join(oq)).lower()
        if not oq:
            warnings.append(f"{label}: no 'Open questions:' line in Assumptions section")
        elif not re.search(r"open questions.*:\s*none", oq_clean):
            warnings.append(f"{label}: open questions do not read as resolved ('Open questions: none')")

    # Requirement traceability IDs.
    ids = []
    b = section_bounds(lines, "Requirement Traceability")
    if b:
        template_seen = False
        for r in table_rows(lines, b):
            cells = split_row(r)
            if not cells:
                continue
            rid = unbacktick(cells[0])
            if PLACEHOLDER_RE.match(rid) or "[" in rid:
                template_seen = True
                continue
            if not rid:
                continue
            if not ID_RE.match(rid):
                errors.append(f"{label}: malformed requirement ID: '{rid}' (expected e.g. AUTH-01)")
            else:
                ids.append(rid)
        if template_seen and not ids:
            warnings.append(f"{label}: Requirement Traceability has only template rows (no real IDs yet)")

    # Self-containment: the spec must carry its own shared-context digest.
    depends = parse_depends_on(lines)
    if required_sections is REQUIRED_SECTIONS_SPEC:
        if section_bounds(lines, "Shared Context") is None:
            warnings.append(f"{label}: no '## Shared Context' digest - a worker reading only this file has no feature context")
        prefixes = {rid.rsplit("-", 1)[0] for rid in ids}
        if len(prefixes) > 1:
            warnings.append(f"{label}: requirement IDs use more than one prefix {sorted(prefixes)} - one prefix per spec keeps IDs traceable")

    return errors, warnings, ids, depends


def parse_depends_on(lines):
    """Read the `**Depends on:** ...` line. Returns a list of spec IDs."""
    for ln in lines[:40]:
        m = re.match(r"^\*{0,2}Depends on\*{0,2}\s*:\s*(.*)$", ln.strip(), re.IGNORECASE)
        if m:
            body = m.group(1)
            if not body.strip() or re.match(r"^\s*(none|-|n/?a)\s*$", body.strip(), re.IGNORECASE):
                return []
            found = re.findall(r"\d{2}-[a-z0-9][a-z0-9-]*", body)
            return found
    return []


def check_overview(path, spec_ids, deps):
    """Check overview.md: required sections, Spec Index parity with the files on
    disk, and agreement between the Index's `Depends on` column and each spec's
    own `Depends on` field."""
    errors, warnings = [], []
    if not os.path.isfile(path):
        errors.append("overview.md: missing - the feature has a specs/ directory but no overview")
        return errors, warnings
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    for name in REQUIRED_SECTIONS_OVERVIEW:
        if section_bounds(lines, name) is None:
            errors.append(f"overview.md: missing required section: ## {name}")

    b = section_bounds(lines, "Spec Index")
    rows = [lines[i] for i in range(*b) if lines[i].strip().startswith("|")] if b else []
    data = [r for r in rows if not is_separator(r)]
    header = split_row(data[0]) if data else []
    dep_col = next((i for i, h in enumerate(header) if h.lower().startswith("depends")), None)

    indexed = []
    for r in data[1:]:
        cells = split_row(r)
        if not cells:
            continue
        sid = unbacktick(cells[0])
        if not sid or "[" in sid:
            continue
        indexed.append(sid)
        if dep_col is not None and dep_col < len(cells) and sid in spec_ids:
            listed = set(re.findall(r"\d{2}-[a-z0-9][a-z0-9-]*", cells[dep_col]))
            actual = set(deps.get(sid, []))
            if listed != actual:
                errors.append(
                    f"overview.md: Spec Index says '{sid}' depends on "
                    f"{sorted(listed) or ['none']} but specs/{sid}.md declares "
                    f"{sorted(actual) or ['none']} - the index and the spec must agree"
                )

    for sid in indexed:
        if sid not in spec_ids:
            errors.append(f"overview.md: Spec Index lists '{sid}' but specs/{sid}.md does not exist")
    for sid in spec_ids:
        if sid not in indexed:
            errors.append(f"overview.md: specs/{sid}.md is not listed in the Spec Index")
    return errors, warnings


def check_graph(deps):
    """deps: {spec_id: [dep_id, ...]}. Returns error strings."""
    errors = []
    known = set(deps)
    for sid, ds in deps.items():
        for d in ds:
            if d not in known:
                errors.append(f"{sid}: 'Depends on' names '{d}', which is not a spec of this feature")

    WHITE, GREY, BLACK = 0, 1, 2
    color = {s: WHITE for s in deps}
    stack = []

    def visit(node):
        color[node] = GREY
        stack.append(node)
        for nxt in deps.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GREY:
                cycle = stack[stack.index(nxt):] + [nxt]
                errors.append("spec dependency cycle: " + " -> ".join(cycle))
            elif color[nxt] == WHITE:
                visit(nxt)
        stack.pop()
        color[node] = BLACK

    for s in sorted(deps):
        if color[s] == WHITE:
            visit(s)
    return errors


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def check(mode, feature_dir, paths):
    errors, warnings = [], []

    if mode == "single":
        for p in paths:
            e, w, _ids, _d = check_spec_file(p, REQUIRED_SECTIONS_LEGACY, os.path.basename(p))
            errors += e
            warnings += w
        return errors, warnings

    if not paths:
        errors.append("specs/ exists but contains no spec files - Specify produced nothing")
        return errors, warnings

    ids_by_spec = {}
    deps = {}
    for p in paths:
        sid = os.path.splitext(os.path.basename(p))[0]
        if not SPEC_FILE_RE.match(sid):
            warnings.append(f"specs/{sid}.md: filename is not NN-slug (two digits, kebab-case) - spec IDs come from filenames")
        label = f"specs/{sid}.md"
        e, w, ids, d = check_spec_file(p, REQUIRED_SECTIONS_SPEC, label)
        errors += e
        warnings += w
        ids_by_spec[sid] = ids
        deps[sid] = d

    e, w = check_overview(os.path.join(feature_dir, "overview.md"), set(ids_by_spec), deps)
    errors += e
    warnings += w

    errors += check_graph(deps)

    seen = {}
    for sid, ids in sorted(ids_by_spec.items()):
        for rid in ids:
            if rid in seen:
                errors.append(f"requirement ID '{rid}' is minted by both '{seen[rid]}' and '{sid}' - prefixes must be unique per spec")
            else:
                seen[rid] = sid

    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_spec.py", description="Closure-gate checks for a feature's spec set.")
    p.add_argument("target", nargs="?", default=None)
    p.add_argument("--root", default=".")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)

    resolved = resolve_target(args.target, args.root)
    if not resolved:
        print(
            "validate_spec: could not locate a feature. Pass a feature name or path, "
            "or run from the project root that contains .specs/.",
            file=sys.stderr,
        )
        return 2
    mode, feature_dir, paths = resolved

    errors, warnings = check(mode, feature_dir, paths)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    fail = errors or (warnings and args.strict)
    scope = f"{len(paths)} spec file(s) in {feature_dir}" if mode == "multi" else paths[0]
    print(f"\nvalidate_spec: {len(errors)} error(s), {len(warnings)} warning(s) in {scope}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
