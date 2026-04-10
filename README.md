# Super Gem Creator — v7.0

A Claude Cowork skill for building expert-level **Gemini Gems** and **Opal (Gem from Labs)** workflows with persistent Drive/Sheets memory, NotebookLM research grounding, and optional Harness-Proxy automation.

---

## What It Does

Guides the creation of production-ready AI advisors in Gemini and Opal in 5 structured steps:

1. **Understand** — Elicit requirements and detect the right tier automatically
2. **Generate** — Produce all gem/workflow artifacts (prompt, memory hub, node instructions, Sheets schema)
3. **Validate** — Walk through a cross-tier validation gate before writing any files
4. **Deploy** — Write files to Google Drive, configure Gemini or Opal, set up memory infrastructure
5. **Test** — Run a calibrated test suite and apply reflexion loops

---

## The 6-Tier Model

| Tier | Name | Best For |
|---|---|---|
| 1 | **Fast Track** | One-time use, no memory, pure system prompt |
| 2 | **Standard** | Most use cases — conversational advisor with memory hub |
| 3 | **Memory Gem** | Multi-domain research synthesis, 4–5 sub-areas, deep knowledge |
| 4 | **Industry Brain** | Offline/private, local models (Ollama/Gemma), data-sensitive |
| 5 | **Harness-Proxy** | Gem as conversational frontend + Opal as autonomous backend |
| 6 | **Gem from Labs** | Native Opal pipeline — Fast (stateless) or Full (memory-bearing) sub-mode |

Tier is inferred automatically from context. The skill never leads with a tier menu.

---

## Repository Structure

```
super-gem-creator-v7.0/
├── SKILL.md                          # Thin router (166 lines) — loaded first
└── references/                       # 29 reference files — loaded on demand
    ├── step1-understand.md           # Tier detection, elicitation, 6-tier signals
    ├── step2-generate.md             # Shared generation base (all tiers)
    ├── step2-fasttrack-delta.md      # Tier 1 generation delta
    ├── step2-research-delta.md       # Tier 3 generation delta
    ├── step2-local-delta.md          # Tier 4 generation delta
    ├── step2-opal-delta.md           # Tier 5/6 generation delta + Node Catalog (16 nodes)
    ├── step3-validate.md             # Cross-tier validation gate (6 tier skeletons)
    ├── step4-deploy.md               # Tier 1/2/3 deploy guide
    ├── step4-local-deploy.md         # Tier 4 deploy guide
    ├── step4-opal-deploy.md          # Tier 5/6 deploy guide + Apps Script harness template
    ├── step5-test.md                 # Test suite (all tiers, incl. Tier 5/6 calibration)
    ├── post-deploy.md                # Memory loop, registry, relay, health schedule
    ├── upgrade-workflow.md           # Upgrade path Tier 1→6, harness-entry-check
    ├── agentic-tier-guide.md         # 6-tier selection map and comparison table
    ├── terminology-glossary.md       # ~35 canonical v7 terms
    ├── gemini-gems-specs-and-limits.md  # Hard limits, Opal Hard Limits (§18)
    ├── budget-reference.md           # Prompt/hub/context budget breakdown
    ├── tool-stack.md                 # File ops, research stack, agentic tiers
    ├── persona-and-routing-defaults.md  # PersonaMatrix, DecisionEngine, Tier 5/6 signals
    ├── memory-hub-template.md        # §1–§8 memory hub scaffold
    ├── memory-relay-protocol.md      # MEMORY_UPDATE format and relay rules
    ├── shared-principles-template.md # Cross-gem behavioral principles
    ├── heuristics-pool-template.md   # Heuristic categories (all tiers)
    ├── test-questions-template.md    # Test question bank by tier
    ├── notebook-themes-examples.md   # NotebookLM grounding themes and examples
    ├── meta-prompt-a-research.md     # Research meta-prompt (Tier 3/4)
    ├── meta-prompt-b-config.md       # Config meta-prompt
    ├── local-research-infrastructure.md  # Tier 4 RAG + source directory setup
    └── local-gem-script-template.py  # Tier 4 local runner + HarnessPollMode class
```

---

## Key v7 Features

### Node Catalog (Tier 5/6)
16-node quick-reference grid embedded in `step2-opal-delta.md` with full `####` detail blocks loaded on demand. Covers: User Input, Generate, Agent Step, Output, Sheets Read/Append, Drive Read/Write, Google Search, Docs Create, Sheets Create, Slides Create, Gmail Send, Calendar Read, For-Each, Conditional Branch.

### Canonical Sheets Memory Bus Schema
3-tab schema (`bus` / `state` / `runs`) with a 8-value `event_type` enum (`harness_request`, `harness_result`, `memory_update`, `session_start`, `session_end`, `calibration`, `health_check`, `error`). Used by both Tier 5 and Tier 6 Full workflows.

### Harness Backend (Tier 5) — 3 Paths
- **Apps Script** (default) — container-bound script on the Memory Sheet, 1-min poll trigger, ~70-line template in `step4-opal-deploy.md §4.9`
- **Local Python** — `HarnessPollMode` class in `local-gem-script-template.py`, run with `--harness` flag
- **Manual** — zero infrastructure, copy-paste fallback

### 5-Block Agent Step Format
```
## Role      — 1–2 sentence role statement
## Goal      — single concrete objective with termination condition
## Tool Protocol — one line per enabled tool: when + what to pass
## Output Format — JSON schema for structured output
## Edge Cases — halt conditions, loop detection, never-list
```
Budget: 1,500 chars target / 2,500 chars hard cap.

### Gem from Labs — Fast vs Full Sub-Modes
| | Fast | Full |
|---|---|---|
| Memory | None (stateless) | Sheets Memory Bus (3 tabs) |
| Nodes | ≤ 5 | ≤ 8 |
| Deliverables | 4 | 8 |
| Calibration | Skip | 14-day cycle |
| Test threshold | 3/3 smoke tests | 7/7 full suite |

---

## Hard Limits (Quick Reference)

| Constraint | Tiers 1–4 | Tier 5/6 Agent Step |
|---|---|---|
| System prompt / Agent Step | ≤ 2,500 chars (target ≤ 2,000) | ≤ 2,500 chars per node (target ≤ 1,500) |
| Knowledge folder files | ≤ 10 (recommend ≤ 6) | N/A — Sheets instead |
| Memory hub | 8K target / 15K ceiling | N/A |
| Opal nodes per workflow | — | ≤ 20 (target ≤ 8 for v1) |

Full Opal quota table (Apps Script limits, Flash I/O caps, run budgets): `gemini-gems-specs-and-limits.md §18`.

---

## Installation

Drop the `super-gem-creator-v7.0/` folder into your Claude Cowork skills directory and reload. The skill auto-triggers on gem/Opal creation requests.

---

## Changelog

### v7.0 (2026-04-09)
- Added Tier 5 (Harness-Proxy) and Tier 6 (Gem from Labs) as first-class tiers
- 16-node Node Catalog embedded inline in `step2-opal-delta.md`
- Canonical Sheets Memory Bus schema with full `event_type` enum
- Apps Script harness backend template (syntax-verified)
- `HarnessPollMode` Python class + `--harness` argparse flag
- 5-block Agent Step format replacing old 7-field format
- Compaction playbook, disappearing-docs check, context-asymmetry principle
- Tri-File JSON Architecture section for stateful Opal workflows
- Cross-tier validation gate (`step3-validate.md`)
- Canonical terminology glossary (`terminology-glossary.md`)
- Zero dangling forward references across all 30 files
- SKILL.md trimmed to 166 lines (thin router pattern)

### v6.0 (2026-04-08)
- Opal introduced as Tier 5 (vibe-code agent builder)
- Harness-Proxy layer added as optional cross-tier extension
- Progressive reference loading (context savings ~65%)
- v5.x archived

---

*Built with Claude Cowork · [dmmdea](https://github.com/dmmdea)*
