# Heuristics Pool Template

Use this skeleton when generating `_Heuristics_[Name]_Pool.md` in Step 4 DEPLOY. Replace all `[bracketed]` content with domain-specific specifics. This file lives in the gem's Drive folder but is **never attached as a gem Knowledge source** — it's referenced by Claude during memory relay sessions.

**Research basis:** Experiential Reflective Learning (ERL, arxiv 2603.24639) — heuristics pools produced +23.8% performance improvement at 40 scenarios. The key insight: heuristics must be earned through validation, not invented at creation.

---

## Template

```markdown
# [Gem Name] — Heuristics Pool

> **Version:** 1.0.0
> **Last updated:** [Date]
> **Owner:** [User name]
> **Linked gem:** [Gem name] at [Drive folder path]

---

## Active Heuristics

Rules of thumb that have been validated across 3+ sessions. The gem treats these as soft defaults — they inform advice without overriding hard constraints (§2).

| Heuristic | Domain | Added | Validation Count | Source |
|-----------|--------|-------|-----------------|--------|
| _(empty at creation — heuristics are earned, not invented)_ | — | — | — | — |

---

## Candidate Heuristics (unvalidated)

Observed patterns that have emerged but aren't yet reliable enough to be active. Promoted to Active after 3 sessions of consistent validation.

- _(empty at creation — add when the gem or user spots a recurring pattern)_

---

## Retired Heuristics

Rules that stopped working. Kept here to prevent the same assumption from re-emerging.

| Heuristic | Retired | Reason |
|-----------|---------|--------|
| _(empty at creation)_ | — | — |

---

## Graduation & Retirement Rules

**Candidate → Active:** Observed pattern holds in 3 separate sessions without being overridden. Claude proposes promotion via MEMORY_UPDATE (Bud-level RBT — medium risk, requires user approval).

**Active → Retired:** Heuristic overridden or contradicted 2+ times. Claude proposes retirement via MEMORY_UPDATE. Retired heuristics stay in the table — do not delete them.

**Active → §2 Constraint:** If a heuristic becomes a hard rule (e.g., "always check VRAM before suggesting models" becomes a non-negotiable), it can be promoted to §2 in the Memory Hub. This is a Thorn-level RBT change — requires explicit user confirmation.

---

## How Claude Uses This File

During memory relay sessions (when applying a MEMORY_UPDATE), Claude:

1. Reads this file alongside the Memory Hub
2. Checks if any MEMORY_UPDATE content suggests a new heuristic candidate
3. If a decision was made for the 3rd+ time in the same way, proposes it as a Candidate
4. If a Candidate has been validated 3 times, proposes promotion to Active
5. If an Active heuristic was overridden, notes it toward retirement

Claude does NOT attach this file to the gem — it's too much context overhead. The gem learns heuristics indirectly through the Memory Hub (§4 Decision Log patterns) and the system prompt's behavioral rules.
```

---

## Notes for Generation

When generating this file for a new gem:

- **Always start empty** — do not invent heuristics at creation time. The pool is built from real sessions.
- **Seed the "How Claude Uses This File" section as-is** — this is procedural guidance for Claude's relay behavior, not domain-specific content.
- **File naming:** `_Heuristics_[GemName]_Pool.md` — the leading underscore keeps it sorted with other system files in Drive.
- **Drive location:** Same folder as the Memory Hub (the gem's dedicated Drive folder, not the root).
- **Do not attach to gem:** This file is explicitly excluded from gem Knowledge sources. It's referenced by Claude only.
- **Cross-reference:** After creating this file, add its path to the File Reference Table in `references/memory-relay-protocol.md` with "Attach to Gem? → No (Claude relay only)."

---

## Tier 5 & Tier 6 Heuristic Categories

Gems at Tier 5 (Harness-Proxy) and Tier 6 (Gem from Labs) accumulate heuristics in
additional categories beyond standard domain heuristics. Pre-seed the Candidate
Heuristics section with these **category labels only** (not invented heuristics —
labels guide pattern recognition during real sessions):

### Tier 5 — Harness-Proxy categories to watch

- **Dispatch reliability:** patterns in which tool calls succeed vs. fail consistently
  (e.g., "UrlFetch to endpoint X times out after N seconds under load")
- **Round-trip latency:** observed timing for `harness_request` → `harness_result` cycles;
  flag if consistently >30 seconds (Apps Script trigger poll interval)
- **Output parse failures:** cases where the harness result format is misread or
  partially consumed by the gem — usually a Tool Protocol block mismatch
- **Quota proximity triggers:** patterns where daily Apps Script limits (90 min/day
  execution, 20K UrlFetch calls/day) are approached and at what usage level

### Tier 6 — Gem from Labs categories to watch

- **Node throughput:** which nodes are reliably fast vs. consistently slow — note
  node name and observed latency range
- **Calibration drift:** if the 14-day recalibration reveals behavioral change,
  log the trigger and the delta between calibration artifacts
- **Preview model volatility:** log any behavioral differences observed across
  Gemini Flash model updates, with date and session count before/after
- **Compaction frequency:** how often the between-session insulation pass is
  actually needed vs. scheduled — informs whether the 80% trigger is calibrated correctly
- **Fast→Full upgrade signals:** recurring patterns that consistently indicate a
  Fast Opal prototype is ready for Full upgrade (e.g., User asks about cross-session
  memory more than once, or team sharing is mentioned)

### Promotion note for agentic tiers

The standard promotion threshold of "3 sessions" still applies. However, for Tier 5/6
gems: a single Opal run that produces the same pattern across 3+ workflow executions
within one session counts as equivalent to 3 separate sessions for promotion purposes.
Log both the session count and the within-session execution count in the Candidate
Heuristics table to preserve the distinction.
