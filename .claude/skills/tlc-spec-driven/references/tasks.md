# Tasks

**Goal**: Break into GRANULAR, ATOMIC tasks. Clear dependencies. Right tools. Parallel execution plan.

**`tasks.md` is the control file.** It is the single artifact that knows which spec files exist, which are done, and which can run in parallel. It has two layers:

1. **Spec Map** — one row per file in `spec/`: dependencies, parallel flag, status. This is the execution controller.
2. **Task Breakdown** — atomic tasks grouped by spec, each carrying the `Spec:` it came from.

Nothing else tracks spec-file status. `spec/INDEX.md` declares the intended order; `tasks.md` records what actually happened.

**Skip this phase when:** the feature produced a single spec file AND there are ≤3 obvious steps. In that case, tasks are implicit — go straight to Execute and list them inline in your implementation plan.

**Never skip when `spec/` holds more than one file** — with multiple specs there is nothing else tracking status and wave order.

## Why Granular Tasks?

| Vague Task (BAD) | Granular Tasks (GOOD)             |
| ---------------- | --------------------------------- |
| "Create form"    | T1: Create email input component  |
|                  | T2: Add email validation function |
|                  | T3: Create submit button          |
|                  | T4: Add form state management     |
|                  | T5: Connect form to API           |
| "Implement auth" | T1: Create login form             |
|                  | T2: Create register form          |
|                  | T3: Add token storage utility     |
|                  | T4: Create auth API service       |
|                  | T5: Add route protection          |

**Benefits of granular:**

- **Agents don't err** - Single focus, no ambiguity
- **Easy to test** - Each task = one verifiable outcome
- **Parallelizable** - Independent tasks run simultaneously
- **Errors isolated** - One failure doesn't block everything

**Rule**: One task = ONE of these:

- One component
- One function
- One API endpoint
- One file change

---

## Process

### 1. Build the Spec Map

Read `.specs/features/[feature]/spec/INDEX.md` first — it carries the spec list, dependencies, and execution waves. Copy that into the Spec Map table, then read each `spec/NN-*.md` **one at a time** to break it into tasks. Never load all spec files simultaneously.

Then read `design.md` (if it exists) before creating tasks.

**Spec-level parallelism:** two specs run in parallel only when ALL hold:

- Neither declares the other in `Depends on`
- They do not write the same files (check `Where` across their tasks)
- Their required test types are parallel-safe per TESTING.md

If the last two fail, strip the `[P]` from the Spec Map even when `INDEX.md` proposed it — `tasks.md` has task-level file knowledge that `INDEX.md` does not.

### 1.5. Load Test Coverage Matrix

Read `.specs/codebase/TESTING.md` (if it exists) before creating tasks. The Test Coverage Matrix
and Parallelism Assessment drive two critical decisions:

**Co-located tests:** Every task that creates or modifies a code layer with a required test type
MUST include writing/updating those tests in the same task. Tests are NOT separate tasks.

| Task creates...                           | Done When must include...                   |
| ----------------------------------------- | ------------------------------------------- |
| Code layer with "unit" requirement        | Unit test written + quick gate passes       |
| Code layer with "e2e" requirement         | E2E test written + full gate passes         |
| Code layer with "integration" requirement | Integration test written + full gate passes |
| Code layer with "none" requirement        | Gate check at appropriate level             |

**Parallelism flags:** Cross-reference the Parallelism Assessment when marking tasks `[P]`:

- If a task's required test type is marked "Parallel-Safe: No" → strip `[P]` flag
- If a task's required test type is marked "Parallel-Safe: Yes" → `[P]` is allowed
- If a task has no tests → `[P]` depends only on code dependencies

If TESTING.md does not exist (greenfield project), ask the user what test types and commands
the project will use before creating tasks.

### 2. Break Into Atomic Tasks

**Task = ONE deliverable**. Examples:

- ✅ "Create UserService interface" (one file, one concept)
- ❌ "Implement user management" (too vague, multiple files)

### 3. Define Dependencies

What MUST be done before this task can start?

### 4. Create Execution Plan

Group tasks into phases. Identify what can run in parallel.

### 5. Validate Before Presenting (MANDATORY)

Before showing tasks to the user, run ALL four pre-approval checks. These are NOT optional — they are gates. If any check fails, restructure the tasks and re-run until all pass.

**Check 1: Task Granularity** — verify each task is atomic (see Granularity Check section).

**Check 2: Diagram-Definition Cross-Check** — verify the execution diagram matches every task's `Depends on` field (see Diagram-Definition Cross-Check section). Build the cross-check table and include it in the output.

**Check 3: Test Co-location Validation** — verify every task's `Tests` field matches the TESTING.md coverage matrix (see Test Co-location Validation section). Build the validation table and include it in the output.

**Check 4: Spec Coverage** — verify every spec file has at least one task and every requirement ID in `spec/INDEX.md` maps to a task (see Spec Coverage Validation section). Build the coverage table and include it in the output.

**Output all tables with the tasks** so the user can see the validation results. Any ❌ means you MUST restructure before presenting — do not show failing tasks to the user and ask them to approve.

### 6. ASK About MCPs and Skills

**CRITICAL**: Before execution, ask the user:

> "For each task, which tools should I use?"
>
> **Available MCPs**: [list from project or user]
> **Available Skills**: [list from project or user]

---

## Template: `.specs/features/[feature]/tasks.md`

````markdown
# [Feature] Tasks

**Specs**: `.specs/features/[feature]/spec/`
**Design**: `.specs/features/[feature]/design.md` (if it exists)
**Status**: Draft | Approved | In Progress | Done

---

## Spec Map (execution control)

The controller. One row per file in `spec/`. Update Status here as specs complete —
this table, not the spec files, is the source of truth for what has been executed.

| Spec | File                    | Capability | Depends on | [P] with | Tasks       | Status  |
| ---- | ----------------------- | ---------- | ---------- | -------- | ----------- | ------- |
| S1   | `spec/01-core.md`       | [one line] | -          | -        | T1.1 - T1.3 | Pending |
| S2   | `spec/02-channel.md`    | [one line] | S1         | S3       | T2.1 - T2.2 | Pending |
| S3   | `spec/03-prefs.md`      | [one line] | S1         | S2       | T3.1        | Pending |

**Status values:** Pending → In Progress → Done | Blocked

**Execution waves:**

```
Wave 1 (sequential):  S1
Wave 2 (parallel):    S2 [P] + S3 [P]
```

**Wave rule:** a wave starts only when every spec in the previous wave is `Done`.
Within a wave, `[P]` specs are dispatched as one sub-agent per spec, concurrently.

---

## Task Breakdown

Tasks are grouped by spec. Task ID format: `T[spec].[n]` — `T2.1` is the first task of S2.
A sub-agent running `T2.1` receives `spec/02-channel.md` and nothing from S1 or S3.

### S1 — `spec/01-core.md`

#### T1.1: [Create X Interface]

**Spec**: S1
**What**: [One sentence: exact deliverable]
**Where**: `src/path/to/file.ts`
**Depends on**: None
**Reuses**: `src/existing/BaseInterface.ts`
**Requirement**: [FEAT]-01

**Tools**:

- MCP: `filesystem` (or NONE)
- Skill: NONE

**Done when**:

- [ ] Interface defined with all methods from design
- [ ] Types exported correctly
- [ ] No TypeScript errors

**Tests**: [unit/e2e/integration/none — from coverage matrix]
**Gate**: [quick/full/build — from gate check commands]

---

#### T1.2: [Implement Y Service] [P]

**Spec**: S1
**What**: [Exact deliverable]
**Where**: `src/services/YService.ts`
**Depends on**: T1.1
**Reuses**: `src/services/BaseService.ts` patterns
**Requirement**: [FEAT]-02

**Tools**:

- MCP: `filesystem`, `context7`
- Skill: NONE

**Done when**:

- [ ] Implements interface from T1.1
- [ ] Handles error cases from design
- [ ] Gate check passes: `[quick gate command from TESTING.md]`
- [ ] Test count: [N] tests pass (no silent deletions)

**Tests**: unit
**Gate**: quick

---

### S2 — `spec/02-channel.md`

#### T2.1: [Create Z Component] [P]

**Spec**: S2
**What**: [Exact deliverable]
**Where**: `src/components/ZComponent.tsx`
**Depends on**: T1.1
**Reuses**: `src/components/BaseComponent.tsx`
**Requirement**: [FEAT]-05

**Tools**:

- MCP: `filesystem`
- Skill: NONE

**Done when**:

- [ ] Component renders correctly
- [ ] Handles props from interface
- [ ] Follows existing component patterns
- [ ] Gate check passes: `[quick gate command from TESTING.md]`
- [ ] Test count: [N] tests pass (no silent deletions)

**Tests**: unit
**Gate**: quick

---

#### T2.2: [Add A Feature to Y]

**Spec**: S2
**What**: [Exact deliverable]
**Where**: `src/services/YService.ts` (modify)
**Depends on**: T2.1
**Reuses**: Existing service patterns
**Requirement**: [FEAT]-06

**Tools**:

- MCP: `filesystem`, `github`
- Skill: `api-design`

**Done when**:

- [ ] Feature works per acceptance criteria
- [ ] Gate check passes: `[full gate command from TESTING.md]`
- [ ] Test count: [N] tests pass (no silent deletions)

**Tests**: integration
**Gate**: full

**Commit**: `feat([scope]): [description]`
````

---

## Cross-Spec Dependencies

A task may depend on a task in an earlier spec (`T2.1` depends on `T1.1`) — that is normal
and is exactly what the Spec Map's `Depends on` column encodes.

A task must NEVER depend on a task in a spec marked `[P]` with its own. If that happens,
the two specs are not parallel: fix the Spec Map, or move the task.

## Parallel Execution Map

Parallelism exists at two levels: **specs** (waves) and **tasks** (inside a wave).

```

Wave 1 (Sequential):
  S1: T1.1 ──→ T1.2 ──→ T1.3

Wave 2 (S2 [P] + S3 [P] — one sub-agent per spec):
  S1 done, then:
    ├── S2: T2.1 ──→ T2.2
    └── S3: T3.1 [P] + T3.2 [P]

Wave 3 (Sequential):
  S2, S3 done, then:
    S4: T4.1 ──→ T4.2

```

**Spec-level parallelism constraint:** two specs run in the same wave only when ALL hold:

- Neither declares the other in `Depends on` (Spec Map)
- No task in one writes a file written by a task in the other
- Their required test types are parallel-safe (per TESTING.md Parallelism Assessment)

**Task-level parallelism constraint:** A task marked `[P]` must have ALL of these:

- No unfinished dependencies
- Required test type is parallel-safe (per TESTING.md Parallelism Assessment)
- No shared mutable state with other `[P]` tasks in the same phase

If a task's tests are NOT parallel-safe, it MUST run sequentially even if its
implementation code has no dependencies. The test execution is the bottleneck.

**How parallel execution works:**

Specs in the same wave are dispatched as one sub-agent per spec, concurrently. Each sub-agent
receives its spec file (`spec/NN-*.md`) plus its tasks from `tasks.md` — never the other specs
(see Sub-Agent Delegation in SKILL.md). This is why specs are self-contained: cross-references
between spec files would force a sub-agent to load context that does not belong to it.

Within a spec, tasks marked `[P]` may be split across further sub-agents. Sequential tasks
(no `[P]`) are also delegated, one at a time — this keeps implementation artifacts (file reads,
test output, gate check logs) out of the main context.

The orchestrating agent waits for every spec in a wave to complete before starting the next wave.

**The orchestrating agent's role during Execute:**
1. Read the Spec Map, pick the next wave (all specs whose dependencies are `Done`)
2. Dispatch one sub-agent per spec in the wave, with its spec file + task definitions
3. Monitor sub-agent completion
4. Update the Spec Map status and task checkboxes in tasks.md
5. Decide whether to proceed to the next wave, fix, or escalate

**Failure inside a wave:** a spec that comes back `Blocked` does not block its wave siblings —
let them finish, mark the failed spec `Blocked` in the Spec Map, and stop before the next wave
if anything depends on it.

---

## Task Granularity Check

Before approving tasks, verify they are granular enough:

| Task                            | Scope         | Status       |
| ------------------------------- | ------------- | ------------ |
| T1: Create email input          | 1 component   | ✅ Granular  |
| T2: Add validation function     | 1 function    | ✅ Granular  |
| T3: Create form with all fields | 5+ components | ❌ Split it! |
| T4: Connect to API              | 1 function    | ✅ Granular  |

**Granularity check**:

- ✅ 1 component / 1 function / 1 endpoint = Good
- ⚠️ 2-3 related things in same file = OK if cohesive
- ❌ Multiple components or files = MUST split

---

## Diagram-Definition Cross-Check

Before approving tasks, verify the execution diagram is consistent with the task definitions. These are independent artifacts that can drift — the diagram is drawn for visual clarity while task bodies are written for precision. Both must agree.

For each task, check:

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T[N] | [deps from body] | [deps from diagram arrows] | ✅ Match or ❌ Mismatch |

**Rules:**

- Every `Depends on` in a task body must have a corresponding arrow in the diagram.
- Every arrow in the diagram must correspond to a `Depends on` in the target task's body.
- Tasks shown as parallel (`[P]`) in the diagram must not depend on each other.
- If a task depends on another task in the same parallel phase, they are NOT parallel — fix the diagram or remove the `[P]` flag.

---

## Test Co-location Validation

Before approving tasks, verify EVERY task's `Tests` field is consistent with the TESTING.md Test Coverage Matrix. This is a hard gate — tasks that fail this check MUST be fixed.

For each task, check: does the task create or modify a code layer that has a required test type in the coverage matrix? If yes, the task's `Tests` field MUST match.

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T[N]: [name] | [layer from coverage matrix] | [test type] | [task's Tests field] | ✅ OK or ❌ VIOLATION |

**Rules:**

- "Tested in another task" is NOT a valid justification for `Tests: none`. That is test deferral — the exact anti-pattern this validation prevents.
- `Tests: none` is only valid when the coverage matrix says "none" for that code layer.
- If a task creates MULTIPLE code layers (e.g., service + controller), use the HIGHEST test type required by any of them.
- Any ❌ VIOLATION → restructure the task to include its required tests before proceeding.

**Resolving compilation dependencies:**

When a task creates code that can't be tested until a later task completes (e.g., a controller that needs module wiring before its e2e tests can run), do NOT defer the tests to a separate task. Instead, restructure:

1. **Merge forward:** Move the untestable task's tests into the earliest task where they become runnable (e.g., the wiring task includes wiring + e2e tests for the controller it enables).
2. **Merge backward:** Absorb the blocking dependency into the current task so it becomes self-testable (e.g., controller task includes its own module registration).

Pick whichever option keeps tasks atomic and cohesive. The goal: no task produces unverified code. If code can't be tested in the task that creates it, the task boundaries are wrong.

---

## Spec Coverage Validation

Before approving tasks, verify the Spec Map and the Task Breakdown are complete and consistent with `spec/INDEX.md`. A spec file with no task is a requirement that will never be built.

| Spec | File | Requirements in spec | Requirements mapped to tasks | Tasks | Status |
| ---- | ---- | -------------------- | ---------------------------- | ----- | ------ |
| S1 | `spec/01-core.md` | FEAT-01, FEAT-02 | FEAT-01, FEAT-02 | T1.1, T1.2 | ✅ OK |
| S2 | `spec/02-channel.md` | FEAT-05 | — | — | ❌ UNCOVERED |

**Rules:**

- Every file in `spec/` has a row in the Spec Map. No orphan spec files.
- Every spec has ≥1 task. A spec with zero tasks means either the split was wrong or a requirement was dropped — resolve with the user, do not silently skip it.
- Every requirement ID in `spec/INDEX.md` maps to at least one task.
- Every task's `Spec:` field names an existing spec.
- The Spec Map's `Depends on` column matches `spec/INDEX.md`, unless deliberately tightened by file-write or test-parallelism conflicts — when tightened, note why in the row.

Any ❌ → fix before presenting. Report the coverage line with the tasks: `Coverage: X requirements, Y mapped, Z unmapped ⚠️`.

---

## Tips

- **Spec Map is the controller** — spec status lives here, nowhere else
- **Task IDs carry the spec** — `T2.1` is self-describing; plain `T7` is not
- **[P] = Parallel OK** — Mark tasks that can run simultaneously
- **Reuses = Token saver** — Always reference existing code
- **Tools per task** — MCPs and Skills prevent wrong approaches
- **Dependencies are gates** — Clear what blocks what
- **Done when = Testable** — If you can't verify it, rewrite it
- **Requirement ID = Traceable** — Every task traces back to a spec requirement
- **One commit per task** — Plan the commit message format in advance

---

## Task Verification Standards

Every task MUST include:

**Done when checklist:**

- Specific, testable outcomes
- Pass/fail criteria
- The specific test command from the Gate Check Commands table
- Expected pass count (prevents silent test deletion)

**Verify section:**

- Commands to prove functionality
- Expected outputs
- Success indicators

**Structure:**

```markdown
### T1: [Task name]

**What:** [Deliverable]
**Where:** [File path]
**Tests**: [unit/e2e/integration/none]
**Gate**: [quick/full/build]

**Done when:**

- [ ] [Specific outcome]
- [ ] [Specific outcome]
- [ ] Gate check passes: `[command from Gate Check Commands]`
- [ ] Test count: [N] tests pass (no silent deletions)

**Verify:**
[Command to prove it works]
[Expected output/behavior]
```

**Quality check:**

- Can task be verified without human judgment?
- Is success criteria binary (pass/fail)?
- Can verification be automated?
