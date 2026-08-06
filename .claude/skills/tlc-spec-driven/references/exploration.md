# Exploration (Grilling)

**Goal**: Reach shared understanding of WHAT the user actually wants — before a single line of spec is written.

**When**: ALWAYS, as the first step of any feature-level work (Medium, Large, Complex). The only exception is [quick mode](quick-mode.md) — ≤3 files, one-sentence scope, where the overhead is not justified.

**Hard gate**: You may NOT create `spec/`, `tasks.md`, or write any code until the frontier is empty AND the user explicitly confirms shared understanding.

---

## The Method

Interview the user relentlessly until you reach shared understanding. Map the demand as a **question tree**: every answer branches into the questions that hang off it.

Work the tree in **rounds**. The **frontier** is every question whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each round the user answers reshapes the tree — settled points push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in _this_ round belongs to a _later_ round, not this one.

The session is done when the frontier is empty: every branch of the tree visited, nothing left silently assumed.

---

## Question Format

Each question is formatted exactly like this:

```
❓ **Q1** - **<question title>**: <question body, may be multiple paragraphs, may include concrete options>

➡️ <your recommended answer>
```

**Rules for questions:**

- Always give a recommended answer. "I don't know, what do you think?" is not a question — it is abdication.
- Options must be concrete ("hard delete with 30-day audit log" not "Option A").
- One decision per question. If a question has two independent answers, it is two questions.
- Number continuously across rounds (Round 1: Q1-Q4, Round 2: Q5-Q7). The user references them by number.

---

## Facts Are Your Job, Never the User's

When a frontier question needs a fact from the environment — what the codebase already does, which library version is pinned, whether an endpoint exists, how a similar feature was built — **dispatch a sub-agent to find it**. Never ask the user for anything you could look up yourself.

Follow the [Knowledge Verification Chain](../SKILL.md#knowledge-verification-chain) when researching: codebase → project docs → Context7 MCP → web search → flag as uncertain.

**Don't block on research.** A running exploration is an unsettled prerequisite, so only the questions _downstream_ of it wait for the sub-agent to report — ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

| Kind of unknown | Who resolves it |
| --------------- | --------------- |
| "Does this project already have a job queue?" | Sub-agent (codebase) |
| "Which auth library is in use and at what version?" | Sub-agent (codebase + Context7) |
| "What is the current error-response shape of the API?" | Sub-agent (codebase) |
| "Should failed jobs retry or dead-letter?" | User |
| "Is offline support in scope for v1?" | User |
| "Who is allowed to see this screen?" | User |

---

## What to Explore

The tree is not a checklist, but a demand is under-explored if any of these branches is still dark:

| Branch | What you need settled |
| ------ | --------------------- |
| **Problem** | The actual pain, who feels it, why now. Not the solution the user arrived with. |
| **Users & permissions** | Who does this, who must NOT, what changes per role. |
| **Happy path** | The concrete walk-through, step by step, in the user's words. |
| **Boundaries** | What is explicitly out of scope for this round. |
| **Data** | What is created/read/changed, where it lives, what is the source of truth. |
| **Integrations** | What external systems are touched, what happens when they are down. |
| **Failure & edges** | Empty, huge, concurrent, duplicated, unauthorized, partially failed. |
| **Done** | How the user will personally verify it works. |

**Challenge vagueness.** Never accept fuzzy answers. "Good" means what? "Users" means who? "Fast" means how many milliseconds? Make the abstract concrete: "Walk me through using this." "What does that actually look like on screen?"

---

## Rounds in Practice

**Round 1** — the trunk. Problem, users, happy path, scope boundary. Dispatch sub-agents for every environment fact you will need later.

**Round 2..N** — the branches opened by the previous answers, plus anything the sub-agents surfaced. A sub-agent finding ("this project already has a `NotificationService` that does 80% of this") usually _creates_ frontier questions — ask them.

**Final round** — the frontier is empty. Present the **Understanding Summary** and ask for confirmation:

```
Frontier is empty. Here is what I understood — confirm or correct before I write the specs.

**Problem**: ...
**Users**: ...
**In scope**: ...
**Out of scope**: ...
**Key decisions**: Q1 ... / Q4 ... / Q7 ...
**Facts found**: [what the sub-agents established, with file paths]
**Still uncertain**: [anything flagged at Step 5 of the verification chain — or "none"]

**Proposed spec split**: [the cohesive capabilities you will turn into separate spec files]
```

Only after the user confirms do you move to [Specify](specify.md).

---

## Scope Guardrail

Exploration widens _understanding_, not _scope_. When the user drifts into a new capability mid-round, capture it and steer back:

> "That is a separate feature. Noting it in Deferred Ideas. Back to Q3."

Deferred ideas go to `STATE.md` (see [state-management.md](state-management.md)) — never silently dropped, never silently built.

---

## Output

Exploration produces no standalone document. Its output flows into:

- **`spec/*.md`** — the requirements, split by cohesive capability
- **`spec/INDEX.md` → Exploration Summary** — the confirmed understanding, verbatim from the final round
- **`context.md`** — only if [discuss](discuss.md) is later triggered for gray areas
- **`STATE.md`** — decisions and deferred ideas that outlive this feature

---

## Tips

- **Recommend, always** — a question without `➡️` puts the burden back on the user.
- **Whole frontier per round** — drip-feeding one question at a time wastes the user's turn.
- **Never guess ahead** — asking a question whose prerequisite is still open produces answers you have to throw away.
- **Sub-agents in parallel** — dispatch all environment research at the start of a round, not one at a time.
- **Empty frontier ≠ done** — the user confirms; you do not self-approve.
