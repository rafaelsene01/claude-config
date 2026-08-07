# Context Limits

## File Size Limits

| File                  | Max Tokens | ~Words | Warning At |
| --------------------- | ---------- | ------ | ---------- |
| overview.md           | 2,000      | 1,200  | 1,600      |
| specs/NN-[slug].md    | 3,500      | 2,100  | 2,800      |
| design.md             | 8,000      | 4,800  | 6,400      |
| tasks.md              | 10,000     | 6,000  | 8,000      |

A spec over its limit is usually two contexts wearing one filename - split it at the activity seam rather than trimming prose. Only ONE spec file is ever loaded at a time, so the budget is per file, not for the whole `specs/` directory.

## Context Zones

🟢 **Healthy** (<40k total): Silent
🟡 **Moderate** (40-60k): Discrete footer note
🔴 **Critical** (>60k): Active warning, suggest optimization

## Monitoring

Display context status in footer when >40k:

```
📊 Context: 52k tokens (moderate)
  - tasks.md: 11k (ok)
  - design.md: 6k (ok)
  - Total: 52k / 200k (26%)
```

## Principles

**Target:** <40k tokens loaded (20% of window)
**Reserve:** 160k+ tokens for work, reasoning, outputs
