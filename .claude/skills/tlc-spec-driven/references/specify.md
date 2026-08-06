# Specify

**Goal**: Capture WHAT to build with testable, traceable requirements — split across **multiple spec files**, one per cohesive capability.

**Prerequisite**: [Exploration](exploration.md) is complete and the user confirmed the Understanding Summary. Do NOT write specs from an unexplored demand.

If the feature still has ambiguous gray areas after exploration (multiple valid approaches for user-facing behavior), trigger the [discuss gray areas](discuss.md) process within this phase.

---

## Output Shape

One feature = one folder = **many spec files** + one index.

```
.specs/features/[feature]/
├── spec/
│   ├── INDEX.md            # Exploration summary, spec map, global traceability
│   ├── 01-[capability].md  # Self-contained: problem slice, stories, criteria, edges
│   ├── 02-[capability].md
│   └── 03-[capability].md
├── context.md              # Only when discuss is triggered
├── design.md               # Only for Large/Complex
└── tasks.md                # Spec map + atomic tasks (see tasks.md reference)
```

**Why split:** each spec file is a self-contained context unit. A sub-agent implementing spec `02` loads `02-*.md` and nothing else — the other specs never enter its window. Splitting is also what makes spec-level parallelism visible to `tasks.md`.

---

## Process

### 1. Slice the Demand into Cohesive Capabilities

From the confirmed exploration, group requirements into **vertical slices** — each one a coherent capability that can be understood, and ideally demonstrated, on its own.

**Slicing rules:**

| Rule | Meaning |
| ---- | ------- |
| **Cohesive** | Everything in one file serves one capability. If you need "and" to name it, split it. |
| **Self-contained** | The file makes sense read alone. No "see spec 03 for the rules". |
| **Vertical** | A slice crosses layers (API + data + UI) rather than being "the database layer". |
| **Independently valuable** | Each slice delivers something, even if slices later compose. |
| **3-8 files** | Fewer than 3 → the split adds no value, keep it as one. More than 8 → the feature is a milestone; split it in the ROADMAP instead. |

**Good split** (`notifications`): `01-notification-core`, `02-email-channel`, `03-push-channel`, `04-user-preferences`, `05-delivery-retry`
**Bad split** (layers, not capabilities): `01-database`, `02-services`, `03-controllers`, `04-frontend`

### 2. Number by Dependency Order

Prefix files `01-`, `02-`, … in a valid execution order: a spec never depends on one numbered after it. Specs with no dependency between them are parallel candidates — record that in each file's `Depends on` field; `tasks.md` turns it into the execution waves.

### 3. Write Each Spec File

Per file: problem slice, user stories with priorities, WHEN/THEN/SHALL criteria, edge cases, traceability IDs.

**P1 = MVP** (must ship), **P2** (should have), **P3** (nice to have). Each story MUST be **independently testable** — you can implement and demo just that story.

Acceptance criteria use **WHEN/THEN/SHALL** — precise and testable:

- WHEN [event/action] THEN [system] SHALL [response/behavior]

### 4. Write INDEX.md

The index carries the confirmed exploration summary, the spec map, and the global traceability roll-up. It is the only file that sees all specs at once.

### 5. Confirm

Present the spec map and ask for approval before Design/Tasks.

---

## Template: `.specs/features/[feature]/spec/INDEX.md`

````markdown
# [Feature Name] — Spec Index

**Created:** [date]
**Status:** Draft | Approved | In Progress | Done

---

## Exploration Summary

**Problem**: [confirmed during exploration]
**Users**: [who, and per-role differences]
**In scope**: [the boundary]
**Out of scope**: [explicitly excluded, with reason]
**Key decisions**: [the settled answers that shaped this split]
**Facts established**: [what sub-agent research found, with file paths]
**Still uncertain**: [flagged items — or "none"]

---

## Spec Map

| Spec | File                     | Capability   | Depends on | Parallel with | Priority |
| ---- | ------------------------ | ------------ | ---------- | ------------- | -------- |
| S1   | `01-[capability].md`     | [one line]   | -          | -             | P1       |
| S2   | `02-[capability].md`     | [one line]   | S1         | S3            | P1       |
| S3   | `03-[capability].md`     | [one line]   | S1         | S2            | P2       |

**Execution waves** (derived from Depends on):

```
Wave 1: S1
Wave 2: S2 [P] + S3 [P]
```

---

## Global Traceability

| Requirement ID | Spec | Story       | Phase  | Status  |
| -------------- | ---- | ----------- | ------ | ------- |
| [FEAT]-01      | S1   | P1: [Story] | Design | Pending |
| [FEAT]-02      | S1   | P1: [Story] | Design | Pending |
| [FEAT]-03      | S2   | P2: [Story] | -      | Pending |

**ID format:** `[CATEGORY]-[NUMBER]` (e.g., `AUTH-01`, `CART-03`)
**Status values:** Pending → In Design → In Tasks → Implementing → Verified
**Coverage:** X total, Y mapped to tasks, Z unmapped ⚠️

---

## Out of Scope (feature-wide)

| Item        | Reason         |
| ----------- | -------------- |
| [Feature X] | [Why excluded] |

---

## Success Criteria (feature-wide)

- [ ] [Measurable outcome — e.g., "User completes X in < 2 minutes"]
- [ ] [Measurable outcome — e.g., "Zero errors in Y scenario"]
````

---

## Template: `.specs/features/[feature]/spec/NN-[capability].md`

```markdown
# S[N]: [Capability Name]

**Feature:** [feature name]
**Index:** `./INDEX.md`
**Depends on:** [S1, S2 | None]
**Parallel with:** [S3 | None]
**Status:** Draft | Approved | In Tasks | Implementing | Verified

---

## Capability

[2-3 sentences. What this slice delivers and why it is a slice of its own. Written so a
sub-agent that reads ONLY this file understands what to build.]

## Context Needed

Everything an implementer must know to build this slice without reading the other specs:

- [Existing code to reuse — with file path]
- [Contract this slice must honor — inline it, do not cross-reference]
- [Decision from exploration that constrains this slice]

## Out of Scope (this slice)

| Item        | Where it lives instead |
| ----------- | ---------------------- |
| [Item X]    | S3 / deferred / never  |

---

## User Stories

### P1: [Story Title] ⭐ MVP

**User Story**: As a [role], I want [capability] so that [benefit].

**Why P1**: [Why this is critical for MVP]

**Acceptance Criteria**:

1. WHEN [user action/event] THEN system SHALL [expected behavior]
2. WHEN [user action/event] THEN system SHALL [expected behavior]
3. WHEN [edge case] THEN system SHALL [graceful handling]

**Independent Test**: [How to verify this story alone — "Do X, see Y"]

---

### P2: [Story Title]

**User Story**: As a [role], I want [capability] so that [benefit].

**Why P2**: [Why this isn't MVP but important]

**Acceptance Criteria**:

1. WHEN [event] THEN system SHALL [behavior]

**Independent Test**: [How to verify]

---

## Edge Cases

- WHEN [boundary condition] THEN system SHALL [behavior]
- WHEN [error scenario] THEN system SHALL [graceful handling]
- WHEN [unexpected input] THEN system SHALL [validation response]

---

## Requirements

| Requirement ID | Story       | Status  |
| -------------- | ----------- | ------- |
| [FEAT]-01      | P1: [Story] | Pending |
| [FEAT]-02      | P1: [Story] | Pending |

---

## Done When

- [ ] [Slice-level verifiable outcome]
- [ ] All P1 acceptance criteria pass
```

---

## Tips

- **Explore first** — a spec written before the frontier is empty is a guess in markdown.
- **Self-contained beats DRY** — duplicating a contract into two spec files is cheaper than a sub-agent loading both.
- **P1 = Vertical Slice** — a complete, demo-able capability, not just backend or frontend.
- **WHEN/THEN is code** — if you can't write it as a test, rewrite it.
- **Requirement IDs are mandatory** — unique across the whole feature, never restarted per file.
- **Numbering encodes order** — `NN-` prefix must be a valid topological order.
- **Out of Scope prevents creep** — per slice AND feature-wide.
- **Confirm before moving on** — user approves the spec map before Design/Tasks.
