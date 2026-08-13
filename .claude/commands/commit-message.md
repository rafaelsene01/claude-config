---
description: Generates a semantic commit message (Conventional Commits) from the staged changes. If nothing is staged, stops and asks the user to stage the files first. NEVER commits or pushes — it only produces the message for the user to copy.
allowed-tools: Bash(git diff:*), Read
---

# Semantic Commit Message Generator

Analyze the **staged** changes of the repository and produce **one commit message** in the
[Conventional Commits](https://www.conventionalcommits.org) format. The output is text
only — committing is the user's decision.

## Hard rule

**NEVER run `git commit`, `git push`, `git add`, `git reset`, or any command that mutates
repository state.** This command is read-only. If the user asks to commit here, reply that
the command only generates the message and that they must run the commit themselves. The
only allowed command is `git diff` (reading the staged changes).

## Steps

1. **Check whether anything is staged:**
   ```
   git diff --cached --stat
   ```
   - If the output is **empty** → **stop immediately** and tell the user nothing is staged,
     asking them to stage the intended files (`git add <file>`) and run the command again.
     Do not analyze the working tree, do not suggest a message, do not use `git commit -a`.
   - If there is output → go to step 2. The staged changes are the only source of analysis.

2. **Read the full staged diff** (`git diff --cached`) to understand what actually changed —
   do not rely on file names alone. Untracked files and working-tree-only changes are
   **ignored**: they are not part of the commit.

3. **Build the message** in this format:
   ```
   <type>(<optional scope>): <imperative description, lowercase, no trailing period>

   <optional body: what and why, one blank line after the subject>

   <optional footer: BREAKING CHANGE:, issue refs, etc.>
   ```

## Types (Conventional Commits)

| Type       | When to use                                                        |
|------------|--------------------------------------------------------------------|
| `feat`     | New functionality                                                   |
| `fix`      | Bug fix                                                             |
| `refactor` | Code change without altering external behavior                      |
| `perf`     | Performance improvement                                             |
| `test`     | Adding or adjusting tests                                           |
| `docs`     | Documentation only                                                  |
| `style`    | Formatting, no logic change                                         |
| `build`    | Build system, dependencies                                          |
| `ci`       | CI configuration                                                    |
| `chore`    | Maintenance tasks that fit none of the above                        |

## Guidelines

- **Subject ≤ 72 characters**, imperative mood ("add", not "added"/"adding"), lowercase
  first letter, no trailing period.
- **Hard cap: every `-m "..."` string must be ≤ 100 characters** (see Length check).
- Write the message in the **project's dominant language** (CLAUDE.md, docs, comments and
  strings in the diff). If there is no clear signal, use the language configured for
  Claude's responses in the session.
- Use a **scope** when it makes sense and the repository already does (e.g. affected
  module/folder).
- If the staged changes span distinct purposes, **flag it to the user** — they may deserve
  separate commits — and suggest one message per group.
- Include a **body** only when it adds real context (reason for the change, impact).
- Add `BREAKING CHANGE:` in the footer when compatibility is broken.

## Length check (mandatory before output)

Every `-m "..."` string is hard-capped at **100 characters**, counted on the text inside
the quotes.

Before printing the command, check each `-m` string one by one:

1. Count its characters (do not estimate — count).
2. If a string exceeds 100:
   - **subject**: rewrite it shorter (drop the scope, shorten the description); never
     wrap the subject across paragraphs.
   - **body/footer**: split it into additional `-m` paragraphs, each ≤ 100, instead of
     truncating information.
3. Re-check after every rewrite. Only print the command when all `-m` strings pass.

State the character count of the subject next to the command so the limit is verifiable.

## Output

Deliver to the user:

1. How many staged files were analyzed.
2. The **complete `git commit` command**, inside a code block, ready to copy and paste.
   This is the main item of the output.
   - Subject only (no body):
     ```
     git commit -m "feat(scope): imperative description"
     ```
   - With body and/or footer, use multiple `-m` flags (each `-m` becomes a paragraph):
     ```
     git commit -m "feat(scope): imperative description" \
       -m "Body explaining what changed and why." \
       -m "BREAKING CHANGE: describe the compatibility break."
     ```
   - Escape double quotes inside the message properly, or prefer single quotes when the
     text contains `"`.
   - Never offer `git commit -a`: the commit must cover only what is staged.

**Reminder: only display the command. NEVER run `git commit`.** Execution is the user's
responsibility.
