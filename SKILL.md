---
name: super-gem-creator
description: >
  Build expert-level Gemini Gems and Opal (Gem from Labs) workflows with persistent
  Drive/Sheets memory, NotebookLM research grounding, and optional Harness-Proxy
  automation. Triggers on: creating a Gemini gem, building a Super Gem, AI advisor
  in Gemini, Opal workflow or agent, vibe-coding an app in Opal, gem for any domain,
  "super gem", "build me a gem", "opal workflow", "opal agent", "mini app in Opal",
  "gem for [topic]", "AI advisor for [domain]", "Gemini assistant for [purpose]",
  or any persistent research-backed AI advisor request.
---

# Super Gem Creator — Thin Router (v7.0)

Build expert-level Gemini Gems and Opal (Gem from Labs) workflows in 5 steps.
Core principle: **infer everything possible, validate only what matters.**
References load on-demand — only the current step's content is in context.

> **v7.0.** 6-tier model: Fast Track / Standard / Memory Gem / Industry Brain /
> Harness-Proxy / Gem from Labs. Tier 5 (Harness-Proxy) and Tier 6 (Gem from Labs)
> are now first-class tiers. Tier 6 has Fast (stateless) and Full (memory-bearing)
> sub-modes. v6.0 archived at `_archive/super-gem-creator-v6.0/`.

## Tool Availability Check

**File operations (try in order):**
1. **Desktop Commander** — `edit_block` for patches, `write_file` for new files, `list_directory`, `get_file_info`
2. **Windows MCP `FileSystem`** — full read → rewrite (no surgical edit); inform User of higher token usage
3. **`cowork present_files`** — manual delivery fallback

**Drive mount:** `get_file_info` on `D:\My Drive\`. Failure → ask User to ensure Google Drive for Desktop is syncing.  
**Opal access (Tier 5/6 only):** Confirm User can reach `labs.google/opal` signed in to the same Google account as Drive.  
**Lessons check:** Read auto-memory Gem Creation Lessons entries for the detected tier. Use to calibrate node counts, schema choices, and known test failure patterns.

## Mode Detection

| Intent Signal | Mode | Dispatch |
|---|---|---|
| New gem / domain description | **New Gem** | → step1-understand.md |
| "Opal", "vibe code", "mini app", "workflow", "agent in Opal" | **Gem from Labs** | → step1-understand.md (Tier 6 confirmed there) |
| "Harness", "closed loop", "gem + Opal", "gem that executes" | **Harness-Proxy** | → step1-understand.md (Tier 5 confirmed there) |
| Existing gem name + "upgrade" / "update" / "bring to v7" | **Upgrade** | → upgrade-workflow.md |
| `MEMORY_UPDATE` block or "update the gem's memory" | **Memory Relay** | → post-deploy.md §relay |
| "Test my gem" / "test my Opal" | **Test Only** | → step5-test.md |
| Ambiguous | Ask ONE question: "New gem, new Opal workflow, or updating an existing one?" | — |

## Tier Detection Summary

Every build is one of six tiers, detected in Step 1. **Do NOT ask the User which tier — infer from signals.**

| Tier | Name | Key Signals | Threshold |
|---|---|---|---|
| 1 | **Fast Track** | "no memory/notebooks", "one-time use", "just a system prompt" | Explicit only |
| 2 | **Standard** | No strong signals for other tiers | Silent default |
| 3 | **Memory Gem** | 4–5 sub-domains, "comprehensive/deep/everything about", research synthesis | 2+ Strong or 3+ Medium |
| 4 | **Industry Brain** | "local", "offline", "private", Ollama/VRAM mentioned, data sensitivity | 2+ Strong (never auto) |
| 5 | **Harness-Proxy** | "DO the work", "closed loop", "agent backend", gem + Opal together | 2+ Strong |
| 6 | **Gem from Labs** | "Opal", "vibe code", "mini app", tool-calling, scheduled runs, shareable agent | 2+ Strong |

Full signal tables and detection logic: `references/step1-understand.md`.

## Step Routing

Check `_state/` on session start:
1. `step5-test.json` with `status: "success"` → post-deploy.md
2. `stepN.json` with `status: "success"` → dispatch to step N+1
3. `stepN.json` with `status: "partial"/"failed"` → re-dispatch to stepN
4. No state files → fresh session → step1-understand.md

| Step | Reference | Notes |
|---|---|---|
| 1: UNDERSTAND | `step1-understand.md` | Tier detection, elicitation, state output |
| 2: GENERATE | `step2-generate.md` + tier delta (see below) | Always read base file first |
| 3: VALIDATE | `step3-validate.md` | Universal + per-tier validation gate |
| 4: DEPLOY | `step4-deploy.md` / `step4-local-deploy.md` / `step4-opal-deploy.md` | By tier |
| 5: TEST | `step5-test.md` | All tiers |
| Post-Deploy | `post-deploy.md` | Memory loop, registry, relay, health schedule |

**Step 2 tier loading:**
1. `step2-generate.md` — ALWAYS (shared base)
2. Tier 3 (Memory Gem): + `step2-research-delta.md`
3. Tier 4 (Industry Brain): + `step2-local-delta.md`
4. Tier 1 (Fast Track): + `step2-fasttrack-delta.md`
5. Tier 5 (Harness-Proxy): + `step2-opal-delta.md`
6. Tier 6 (Gem from Labs): + `step2-opal-delta.md`
7. Tier 2 (Standard): base only

> **Node Catalog (Decision 7):** `step2-opal-delta.md` contains the full Node Catalog inline.
> Load the Quick Reference grid on first read. Load individual `####` node blocks only when
> configuring that specific node type — do not load all 16 blocks at once.

<!-- Decision 8 deferred gaps: Tier 5↔6 hybrid (single gem driving multi-workflow Opal chains),
     multi-tenant Opal (gallery + private variants), cross-Opal orchestration.
     ADK/API path is a legacy alternative — not covered in v7 skill. -->

## Pre-Write Validation Protocol

> Reference before every file write in Steps 2 and 4.

1. **Path check:** `get_file_info` or `list_directory` on parent path. Surface errors before writing.
2. **Knowledge folder count:** Count ALL files (subfolders count toward the limit). ≥ 10 → STOP, move non-essential files to Relay. 7–9 → warn. Target ≤ 6.
3. **Exists check:** Before writing Memory / Core / Controller / State / Opal / Sheets files — check existence first. Present overwrite/cancel choice. **Never overwrite silently. No `.bak` files — Drive version history is the backup.**
4. **Confirm write:** `list_directory` on parent folder after every write.
5. **Opal-specific:** All graph specs and Sheets schema files go in Relay folder only — never Knowledge folder.

## Relay Folder Architecture

Knowledge-attached folder: **10-file hard limit** (flat count including subfolders). Target ≤ 6 files.

```
Gemini/
  [Gem Name] Memory/          ← Knowledge-attached (≤ 6 files recommended)
    _Memory_[Name]_GemMemoryHub_Active.md
    _Core_[Name]_PersonaMatrix.json        (Tier 3/4/5 tri-file)
    _Controller_[Name]_DecisionEngine.json (Tier 3/4/5 tri-file)
    _State_[Name]_SessionMemory.json       (Tier 3/4/5 tri-file)
  [Gem Name] Relay/           ← SIBLING folder (no file limit, never indexed)
    _Memory_[Name]_GemMemoryHub_Archive.md
    _Progress_[Name]_ActiveTask.md
    _Heuristics_[Name]_Pool.md
    _Prompt_[Name]_GemSystemPrompt_v[X].md
    _Opal_[Name]_GraphSpec.md             (Tier 5/6 only)
    _Sheets_[Name]_MemorySchema.md        (Tier 5/6 only)
    _Opal_[Name]_NodeInstructions.md      (Tier 5/6 only)
```

**Critical:** No subfolders inside Knowledge folder. No `.bak` files. Relay = `[Gem Name] Relay/` at same Drive level as `[Gem Name] Memory/`. Tier 6 (Gem from Labs) only: Relay folder only — no Knowledge folder needed.

## Hard Limits

| Constraint | T1 | T2 | T3 | T4 | T5/T6 Agent Step |
|---|---|---|---|---|---|
| Prompt / Agent Step | ≤ 2,500 (target ≤ 2,000) | ≤ 2,500 (target ≤ 2,000) | ≤ 2,500 (target 1,200–1,500) | ≤ 4,000 (no hard cap) | ≤ 2,500 per node (target ≤ 1,500) |
| Memory hub | 8K / 15K ceiling | 8K / 15K ceiling | 5–6K / 10K ceiling | 8K / 15K ceiling | N/A — Sheets tabs instead |
| Knowledge files | 1 | ≤ 6 / max 10 | ≤ 6 / max 10 | N/A | N/A |
| Notebooks | 0 | 2 | ≤ 5 | Local files only | Google Search + Sheets reads |
| Opal nodes | — | — | — | — | ≤ 20 (target ≤ 8 v1); Fast mode: ≤ 5 |

> **Opal Hard Limits (Apps Script quotas, Flash I/O caps, run budgets):** `gemini-gems-specs-and-limits.md § 18`.  
> **Full budget breakdown:** `budget-reference.md`.

## File Naming Convention

All Drive files: `_Category_Name_Description.extension`

| Type | Example |
|---|---|
| System prompt | `_Prompt_[Name]_GemSystemPrompt_v1.0.md` |
| Memory hub | `_Memory_[Name]_GemMemoryHub_Active.md` |
| Tri-file JSON | `_Core_[Name]_PersonaMatrix.json` / `_Controller_[Name]_DecisionEngine.json` / `_State_[Name]_SessionMemory.json` |
| Opal graph spec | `_Opal_[Name]_GraphSpec.md` |
| Opal node instructions | `_Opal_[Name]_NodeInstructions.md` |
| Sheets schema | `_Sheets_[Name]_MemorySchema.md` |

Full tool and research stack: `references/tool-stack.md`. Agentic tier guide: `references/agentic-tier-guide.md`.

## Key Principles

1. **Infer, don't interrogate** — Context answers tier, domain, and depth. Ask only when genuinely ambiguous.
2. **Lean prompts / lean nodes** — Behavioral rules only. Facts live in Drive files or Sheets tabs. No duplication.
3. **One component per exchange** — Present, get approval, advance. Never batch validations.
4. **Folder as Knowledge source** — Connect the Drive folder, not individual files.
5. **RAG-optimized naming** — Descriptive `_Category_` prefixes improve Gemini retrieval.
6. **Synthesis over generation (Tier 6)** — Flash = 1M input / 64K output. Graph design = aggregate → compress → deliver.
7. **Tier-appropriate depth** — Fast Track for simple; Standard for most; Memory Gem for multi-domain; Industry Brain for offline/private; Harness-Proxy for dual frontend+backend; Gem from Labs for native execution.
8. **Health monitoring** — Gems and Opals degrade silently. Scheduled checks and relay triggers catch drift early.
