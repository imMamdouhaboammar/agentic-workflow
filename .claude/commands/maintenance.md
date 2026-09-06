---
description: "Periodic health check and cleanup for Hook infrastructure"
---

## Setup Maintenance Inspection Analysis

Analyze `.claude/hooks/setup.maintenance.log` and execute necessary maintenance tasks.

### Analysis Protocol:

**Step 1 — Read Log:**
Read `.claude/hooks/setup.maintenance.log` using the Read tool.
If the file does not exist, notify user: "You must run the Maintenance Hook first via `claude --maintenance`."

**Step 2 — Categorize & Audit:**

| Item | Action on WARN/FAIL |
|---|---|
| **Session archives** | List archives older than 30 days → ask user before deleting |
| **Knowledge index** | Inspect invalid JSON line numbers → propose removing corrupt lines |
| **Work log** | If > 1MB, propose pruning old logs (backup before deleting) |
| **Script syntax** | Read script with errors → apply fixes |
| **Doc-code sync** | Discrepancy between code constants and documentation values — check reported files and align docs or code |
| **verification-logs/** | Propose pruning verification logs older than 30 days |
| **pacs-logs/** | Propose pruning pACS logs older than 30 days |
| **autopilot-logs/** | Propose pruning Decision Logs older than 30 days |

**Step 3 — Cleanup Operations (User Approval Mandatory):**

⚠️ **NEVER DELETE:**
- `knowledge-index.jsonl` — RLM Knowledge Archive (cross-session intelligence)
- `latest.md` — Latest snapshot (core session recovery basis)

Eligible for deletion (after user confirmation):
- `sessions/*.md` — Session archives older than 30 days
- `work_log.jsonl` — Excessively large work logs (after backup)

**Step 4 — Final Report:**
```
## Maintenance Results

### Health Summary
- Total: N items
- Healthy: N
- Issues: N

### Maintenance Actions Performed
- [Action Details] → [Result]

### System Status
- Context Preservation System: [Healthy / Attention Needed]
- Knowledge Archive: [N entries, NKB]
- Session Archives: [N files, NKB]
```

### Recommended Execution Cadence:
- **Weekly**: Standard usage cadence
- **On Demand**: After modifying Hook scripts or upon session recovery anomalies
