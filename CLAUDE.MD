# Instruções Globais

## Execução de Comandos Bash

- Sempre usar `run_in_background: true` em chamadas do Bash tool para comandos que possam demorar.
- Prefixar comandos longos com `timeout 3600` para limitar a 60 minutos no nível do shell.

@AGENTS.md

## Task Observer (meta-skill)

At the start of any task-oriented session — any interaction where you will
use tools and produce deliverables — invoke the task-observer skill before
beginning work. This ensures skill improvement opportunities are captured
throughout the session.

When loading any skill, check the observation log for OPEN observations
tagged to that skill. Apply their insights to the current work, even if
the skill file hasn't been updated yet. This enables immediate application
of observations before they're permanently integrated during the weekly
review.

Skill instalada em `~/.claude/skills/task-observer/`. Log de observações:
`~/.claude/projects/<project-id>/skill-observations/log.md`.
