# Sub-Agent Delegation

Full mechanics for phase-batch workers and the Verifier sub-agent used during Execute.

## Phase-Batch Workers

**Three layers - keep them distinct:**

- **Spec** = the deliverable unit - one context/activity, one file under `specs/`, one Verifier report. A batch never spans two specs.
- **Phase** = the semantic / dependency unit (Foundation → Core → Integration), authored during Tasks, belonging to exactly one spec. Indivisible.
- **Batch** = the execution / logistics unit - one or more *consecutive whole phases of the same spec* assigned to a single worker.

Conflating phase and batch (one worker per phase) is what fragments execution: a feature's dependency-layer count has nothing to do with the ideal per-worker workload. Batching by task budget separates the two concerns without breaking phases. Keeping batches inside a spec is what keeps a worker's payload down to a single spec file.

**Trigger:** Count total tasks across all phases. If the feature packs into **more than one batch** (> ~8 tasks), offer the user phase-batch sub-agents before starting Execute. If it fits a single batch (≤ ~8 tasks), execute inline in the main window - no sub-agents spawned.

**Batching algorithm (task budget ≈ 7 tasks/worker, phase-aligned):**

The benchmarked sweet spot is ~7 tasks of context per worker (~20 tasks → 3 workers). Pack whole phases into that budget:

1. Count total tasks `T`.
2. If `T ≤ ~8` → **inline, no sub-agents.** Inline execution still walks spec by spec and still runs each spec's Verifier as that spec closes - the batching decision is about *who executes*, never about whether a spec gets verified. A 6-task feature split across 3 specs runs inline and produces 3 validation reports.
3. Otherwise walk phases **in order**, accumulating whole phases into the current batch. When the batch's running task count reaches ~7 **and** phases remain, close the batch and start the next.
4. **Close the batch at every spec boundary**, regardless of budget - a batch never mixes specs, so the worker receives exactly one spec file and the spec can be verified as soon as its last batch reports. This applies only once step 3 is in play; it never turns a `T ≤ ~8` feature into a multi-worker dispatch.
5. **Never split a phase** across workers - the cut only ever lands on a phase boundary. This preserves dependency ordering and keeps a phase's tasks + shared context in one worker.
6. If the final batch **of a spec** is a lone tail (1-2 tasks), fold it into the previous batch of that same spec - never into a batch of another spec.

Result ≈ `ceil(T / 7)` workers within each spec, scaling linearly. Unevenness is absorbed by greedy packing - phases never need to divide evenly. Worked examples (20 tasks, single spec):

- Phases `[3,3,3,3,4,4]` → `{P1+P2=6, P3+P4=6, P5+P6=8}` = **3 workers**
- Phases `[8,2,2,8]` → `{P1=8, P2+P3=4, P4=8}` = **3 workers** (no even split needed)
- Phases `[5,5,5,5]` → `{P1+P2=10, P3+P4=10}` = **2 workers** (phases too coarse to hit 3 - see below)

**Coarse-phase caveat:** Because the cut lands only on phase boundaries, very coarse phases limit how finely you can pack. If a single phase alone exceeds ~1.5× the budget (~10+ tasks), that is a Tasks-authoring smell - split it into real sub-phases during Tasks (at a genuine dependency/cohesion boundary), never at dispatch time.

**Offer-then-confirm (never auto-spawn):**

> "This feature has [T] tasks across [N] phases in [S] specs. I can pack them into [K] sub-agents (~7 tasks each, whole phases, one spec per worker) - every worker runs its phases in order, reports a compact summary, and each spec closes with its own Verifier before the next spec starts. This keeps the main window lean without over-fragmenting. Want to proceed that way?"

The user must explicitly accept. If they decline (or if the feature fits one batch), execute inline.

**Execution model - one worker per task-budgeted batch, sequential:**

```
spec 01: Phases 1+2 (7 tasks)  --→ Batch Worker 1 --→ compact summary --→ orchestrator updates tasks.md
spec 01: Phases 3+4 (6 tasks)  --→ Batch Worker 2 --→ compact summary --→ orchestrator updates tasks.md
         ↓
         Verifier(01) --→ validation/01-[slug].md must be PASS before spec 02 starts
         ↓
spec 02: Phase 5    (7 tasks)  --→ Batch Worker 3 --→ compact summary --→ orchestrator updates tasks.md
         ↓
         Verifier(02) --→ validation/02-[slug].md
...
```

Batches run strictly sequentially: a batch never starts until the previous batch's summary shows all its tasks complete, and a spec's first batch never starts until every spec it depends on has a PASS report.

**What a batch worker receives:**

- The task definitions for **every** phase in its batch (from `tasks.md`)
- The Test Coverage Matrix and Gate Check Commands (from `tasks.md`)
- `references/coding-principles.md`
- **Exactly one spec file** - `.specs/features/[feature]/specs/NN-[slug].md`, the spec its batch belongs to. Never `overview.md`, never a sibling spec. If the worker feels it needs another spec to proceed, that is a seam or phase-partition bug: stop and report it, do not go read it.
- The `design.md` sections relevant to that spec's components

**What a batch worker does:**

Executes ALL tasks in its assigned batch **in order** - finishing every task in one phase before starting the next phase in the batch - following the `implement.md` cycle for each task (implement → gate → atomic commit). It does NOT spawn further sub-agents. After completing all tasks in the batch, the worker reports a **compact summary** to the orchestrator:

```
Batch (spec [NN-slug], phases [N]-[M]) complete:
- Tasks done: [list with commit hashes]
- Tests: [N passed, 0 failed]
- Spec finished? [yes -> dispatch Verifier | no -> N tasks remain in this spec]
- Deviations/blockers: [none | description]
```

No raw logs, no full test output - only the above fields keep the main context clean.

**No nesting:** Batch workers execute their tasks themselves. They never spawn sub-sub-agents. Execution is strictly sequential within and across batches - there is no intra-phase or intra-batch parallelism.

**The orchestrating agent's role during Execute:**

1. Count total tasks and pack phases into task-budgeted batches (~7 tasks each, never crossing a spec) - if that yields more than one batch, offer batch sub-agents and wait for the user to accept
2. Dispatch the next batch to a worker (or execute inline if not using sub-agents), handing it only its own spec file
3. Receive the compact summary
4. Update `tasks.md` with results
5. If all tasks in the summary show complete: when the spec is finished, dispatch its Verifier and wait for PASS; then dispatch the next batch
6. If a task failed: the worker has already stopped; decide fix/escalate before dispatching the next batch

**Failure handling:** If a task in a batch fails (gate does not pass, blocker hit), the worker stops and includes the failure in its summary. The next batch does not start until the current batch's summary shows all tasks complete. The orchestrator decides: fix and re-run, or escalate to the user.

**Context sizing signal:** If a batch's task list would likely push the worker's context beyond ~40k tokens, close the batch at an earlier phase boundary (fewer phases per worker). If a *single* phase alone would blow the budget, that phase is too coarse - split it during Tasks per the granularity guidance in `references/tasks.md`.

---

## Verifier Sub-Agent

**Always-on, never prompted - one per spec.** The Verifier is a separate role from the batch worker. It runs once per spec - after the last task of that spec is committed - as an independent quality gate, dispatched automatically by the orchestrator. It is **not** gated behind the batching offer; it always runs. Do NOT ask the user whether to run validation; it is mandatory. A feature with four specs gets four Verifier runs and four reports.

**Author ≠ verifier:** The agent (or batch worker) that wrote the code and tests is the author. The Verifier is a fresh sub-agent dispatched by the orchestrator after the spec's final commit. It does not inherit the author's context, mental model, or assumptions. This separation is what makes the gate trustworthy.

**What the Verifier receives:**
- **One** spec file: `.specs/features/[feature]/specs/NN-[slug].md` (its ACs = source of truth). Not the overview, not the siblings - a Verifier that reads the whole feature stops being a check on *this* spec.
- The git diff surface for **this spec's** tasks (the commit range covering them)
- The test files in scope
- `references/validate.md` as its operating checklist

**What the Verifier does (full process in `validate.md`):**
1. **Spec-anchored coverage check** - re-derives coverage evidence-or-zero: every AC traced to `file:line` + assertion expression. For each covered criterion, confirms the test's asserted value matches the **spec-defined expected outcome** (not just that an assertion exists). Where the spec does not define a precise outcome, flags a **spec-precision gap** rather than passing silently.
2. **Discrimination sensor** - injects a small behavior-level fault (flip a condition, change a return value, off-by-one, remove a required side effect) in an **isolated scratch** (temporary `git worktree` or temp file copies - never `git stash`), runs the relevant tests there, confirms they FAIL (kill the mutant), discards the scratch, and verifies the real worktree's `git status --porcelain` matches the pre-sensor baseline. Tiered by risk: lightweight (1-3 mutations) for standard features; expanded (≥5 mutations or full mutation tooling) for P0/critical paths. Surviving mutants become fix tasks.
3. Applies the **payload/conjunction rule**: checks payload fields are asserted on value/state, not just that the call occurred.
4. **Writes the persisted report** to `.specs/features/[feature]/validation/NN-[slug].md` - PASS/FAIL, per-AC evidence (`file:line` + assertion + spec outcome), sensor result (killed/survived per mutation), gate exit results, diff/commit range.
5. **Returns a compact verdict in chat** to the orchestrator.
6. Does **NOT** write, modify, or fix any code or tests - the real working tree is never mutated (sensor mutations run in scratch state only).

**What the Verifier reports back (compact chat format):**
```
## Validation: [feature] / spec `NN-[slug]` - [PASS ✅ | FAIL ❌]

**Spec-anchored check**: [N/N ACs matched spec outcome | M spec-precision gaps flagged]
**Gate**: [X passed, 0 failed]
**Sensor**: [N mutations injected, N killed, N survived]
**Report**: `.specs/features/[feature]/validation/NN-[slug].md`

**Ranked gaps** (if FAIL):
1. [Gap description] - [AC or criterion] - [file:line or "no evidence"]
2. ...
```

**Failure handling:** The orchestrator routes the ranked gaps to an implementer as fix tasks **scoped to that spec**, then re-dispatches the Verifier. This fix→re-verify loop is bounded to a maximum of **3 iterations**. If gaps remain after 3 iterations, escalate to the user. Specs that depend on a FAILing spec stay blocked.

**Standalone fallback:** When running without sub-agents (a single agent executing the full feature), run `validate.md` as an independent fresh-eyes pass **at the end of every spec** - re-read that spec file and the diff from scratch, apply evidence-or-zero, run the spec-anchored check and discrimination sensor, write `validation/NN-[slug].md`, then run `python3 <skill-dir>/scripts/validate_state.py <feature>` to confirm every report so far is a real PASS, and report PASS/FAIL before moving to the next spec.

---

## Model Tier per Role

**Applies only if the harness can assign a model per sub-agent.** If it cannot, ignore this section and run everything on the default model - the workflow is correct either way. The point is to spend high-reasoning capacity where ambiguity and consequence are high, and a faster tier where the work is mechanical, instead of paying top-tier cost uniformly.

Judge the tier by the work in front of the role, not by the role's title:

| Role / work | Characteristic | Suggested tier |
| ----------- | -------------- | -------------- |
| Design phase | High ambiguity, hard-to-reverse structural decisions | High-reasoning |
| Batch worker - core-domain or high-ambiguity phase | Non-obvious logic, tricky edge cases, novel integration | High-reasoning |
| Batch worker - mechanical phase | Entities, DTOs, config, wiring, straightforward CRUD against a settled pattern | Faster / cheaper |
| Verifier | Adversarial reasoning: designs mutations, re-derives coverage, judges outcome precision | Mid-to-high |
| Specify / Tasks authoring | Structured but judgment-heavy | Mid-to-high |

**Rules of thumb:**

- When unsure, size up, not down. An under-powered worker on ambiguous logic produces gaps the Verifier then has to catch - more expensive than paying for reasoning once.
- The Verifier is never the cheapest tier; a weak Verifier defeats the author ≠ verifier gate.
- Set the tier per batch, from that batch's phases and the ambiguity of its spec. A feature can mix tiers across specs and batches.
- This is advisory metadata only. No gate, commit, or verification step depends on it.
