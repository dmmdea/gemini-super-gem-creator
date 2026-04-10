# Memory Hub Template

Use this skeleton when generating the memory-hub.md file in Step 4. Replace all `[bracketed]` content with specifics from the user's domain. Keep the section numbering (§0-§10) exactly as shown — the gem's MEMORY_UPDATE protocol references these section numbers.

---

## Template

```markdown
# [Gem Name] — Memory Hub

> **Version:** 1.0.0
> **Last updated:** [Date]
> **Owner:** [User name]

---

## §0 — How to Use This File

### Memory Hygiene Protocol
- **Update format**: Canonical delimited block (see §0 Update Protocol below), max 500 chars per MEMORY_UPDATE
- **Staleness check**: Every 10 conversations, review §3–§7 for resolved or outdated items
- **Archive trigger**: When total file exceeds **12,000 chars** (Standard/Local/Fast Track) or **8,000 chars** (Research Gem), move completed/resolved items to `_Memory_[Name]_GemMemoryHub_Archive.md`
- **Version bump**: Patch for updates, minor for structural changes, major for phase transitions
- **Changelog cap**: Keep only last 10 entries in §9. Move older entries to Archive.

### For the Gem (Gemini)
- **Read this file at the START of every conversation.** Do not ask the user questions already answered here.
- **At the END of every conversation where state changed**, output a MEMORY_UPDATE block so the user can relay updates.
- **At session start**, output a [SESSION_SUMMARY — OPENING] per the Session Opening Ritual in your system prompt.

### For the User
- When the gem outputs a MEMORY_UPDATE block, open this file on Google Drive and paste the updated sections. Or relay to Claude with: "Apply this MEMORY_UPDATE to my gem files at [Drive path]."
- Google Drive's version history provides automatic backups — every save creates a recoverable snapshot.
- You can also edit this file directly to correct facts, add constraints, or update the roadmap.

### Cross-Tool Workflow
| Tool | Role | When to Use |
|------|------|------------|
| **Gemini Gem** | Advisor | Strategic questions, planning, advice |
| **NotebookLM** | Researcher | Deep dives, benchmarks, source-grounded answers |
| **Google Drive** | Memory | This file, documents, version history |
| **Claude** | Builder | Implementation, file generation, memory relay |

**The workflow:** Gem advises → You validate → Claude implements → You update memory → Gem learns

---

## §1 — Identity

**Project/Business:** [Name and brief description]
**Domain:** [What the gem advises on]
**Owner:** [User name]
**Started:** [Date]
**Current phase:** [Where things are — e.g., "Initial setup", "Operational", "Scaling"]

---

## §2 — Hard Constraints (🔒 LOCKED)

> _Last validated: [Date]_

These are non-negotiable. The gem must never suggest anything that violates these.

1. 🔒 **[Constraint 1]** — [Why this is non-negotiable] | _Added: [Date]_
2. 🔒 **[Constraint 2]** — [Why] | _Added: [Date]_
3. 🔒 **[Constraint 3]** — [Why] | _Added: [Date]_
[Add more as needed]

> To add a new constraint: Add it here AND in the gem's system prompt (§2 Behavioral Rules). Constraint changes require [HARNESS_PAUSE] confirmation.

---

## §3 — Current State Snapshot

> _Last validated: [Date]_

[Describe the current state of the project/business/system. Use tables for structured data.]

### [Category 1 — e.g., Infrastructure / Team / Products]
| Item | Status | Notes |
|------|--------|-------|
| [Item] | [Status] | [Notes] |

### [Category 2]
| Item | Status | Notes |
|------|--------|-------|
| [Item] | [Status] | [Notes] |

---

## §4 — Decision Log

| Date | Decision | Rationale | Source |
|------|----------|-----------|--------|
| [Date] | [Gem created — initial configuration] | [Domain and setup rationale] | User |
| [Date] | [First key design decision from Step 1] | [Why] | User |

> The gem proposes entries via MEMORY_UPDATE. User pastes them here after review.

---

## §5 — Research Tracker

### Completed Research
| Notebook | Theme | Key Finding | Date |
|----------|-------|-------------|------|
| NB1 | [Core Domain theme] | [Most important finding] | [Date] |
| NB2 | [Expansion theme] | [Most important finding] | [Date] |

### Pending Research Topics
- [ ] [Topic that needs deeper investigation]
- [ ] [Another topic]

---

## §6 — Roadmap / Goals

### Current Priorities
1. **[Priority 1]** — [Brief description] — Status: [Not started / In progress / Done]
2. **[Priority 2]** — [Brief description] — Status: [Status]
3. **[Priority 3]** — [Brief description] — Status: [Status]

### Future Goals
- [Goal for later]
- [Another future goal]

---

## §7 — Known Issues

| Issue | Severity | Status | Notes |
|-------|----------|--------|-------|
| [Issue description] | [High/Medium/Low] | [Open/Investigating/Resolved] | [Any context] |

---

## §8 — Self-Optimization Log

### Never-Recommend List
Items the gem must never suggest. Updated more frequently than the system prompt version.

1. **[Item]** — [Why it was rejected] — Added [Date]
[Add more as they accumulate]

### What Worked Well
[Empty at creation — filled over time as the user notes effective advice patterns]

### What to Improve
[Empty at creation — filled over time as the user notes areas where the gem's advice fell short]

---

## §9 — Version Control

**Current version:** 1.0.0

### Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | [Date] | Initial creation |

### Update Protocol
- Minor updates (new decision, issue logged): increment patch (1.0.0 → 1.0.1)
- Structural changes (new constraint, roadmap shift): increment minor (1.0.0 → 1.1.0)
- Major overhauls (pivot, new phase): increment major (1.0.0 → 2.0.0)

---

## §10 — Hypothesis Tracker

Beliefs the gem is operating under that haven't been confirmed yet.

| Hypothesis | Added | Status | Evidence |
|------------|-------|--------|----------|
| _(empty at creation — add when gem makes unverified assumptions)_ | — | — | — |

**Rules:**
- Before giving advice based on an unconfirmed assumption, the gem states it as a hypothesis and logs it here.
- Confirmed hypotheses graduate to §2 (if a constraint) or §3 (if a fact) — via [HARNESS_PAUSE].
- Rejected hypotheses stay here as "Rejected" to prevent the same assumption from recurring.
```

---

## Notes for Generation

When filling this template for a specific gem:

- **§0 Memory Hygiene Protocol:** Include as-is — do not edit the protocol rules. These govern how the archive trigger and staleness checks work.
- **§1 Identity:** Pull from the user's situation description. Be factual. If user didn't provide a project name, use: "[Domain] Advisor — rename after first session."
- **§2 Constraints:** Copy directly from the user's hard constraints. Add lock emoji. Add `_last_validated: [date]` and `_Added: [date]` per entry. If no constraints given, seed with: "🔒 No hallucinated constraints — gem must cite evidence for all claims."
- **§3 Current State:** Ask the user for current status of key items. Use tables. Add `> _Last validated: [date]_` to the section header. If no status given, seed with: "Status: Not yet established — update after first session."
- **§4 Decision Log:** Always seed with exactly 2 entries: (1) gem creation date, (2) first design decision made in Step 1.
- **§5 Research Tracker:** Standard Gem — exactly 2 rows (NB1 Core Domain, NB2 Expansion). Research Gem — up to 5 rows (NB1–NB5 domain-partitioned). Local Gem — rows match source directories (no limit).
- **§6 Roadmap:** If no roadmap given, prompt: "What's the first thing you want this gem to help you accomplish?"
- **§7 Known Issues:** Can start empty or with any known gaps.
- **§8 Never-Recommend:** Seed from rejected items + 1–2 domain starters labeled [Suggested — confirm or remove]. Leave "What Worked Well" and "What to Improve" empty.
- **§9 Version Control:** Always start at 1.0.0. Keep only last 10 entries in §9 changelog; older entries move to Archive.
- **§10 Hypothesis Tracker:** Always start empty — table structure only with the placeholder row.

**Active Memory target:** **8,000** chars / ceiling **15,000** chars (Standard/Local), **5–6,000** chars / ceiling **10,000** chars (Research). Archive trigger: **12,000** chars (Standard/Local/Fast Track), **8,000** chars (Research).
