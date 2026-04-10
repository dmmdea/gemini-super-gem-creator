# Super Gem Creator (v7.0)

A Cowork skill for building expert-level Gemini Gems and Opal (Gem from Labs) workflows with persistent Drive/Sheets memory, NotebookLM research grounding, and optional Harness-Proxy automation.

> **Built for AI power users** who want production-quality Gemini advisors and Opal agents — not just a system prompt, but a full memory architecture, test suite, and deployment pipeline.

---

## The Problem

Building a good Gemini Gem is easy. Building one that actually holds up over time is not:

- **Memory degrades** — gems accumulate contradictory instructions, stale facts, and outdated personas with no structured refresh cycle
- **No tier discipline** — a simple FAQ bot and a deep research advisor get built the same way, producing over-engineered simple gems and under-engineered complex ones
- **Opal is a black box** — Opal (Gem from Labs) has no official workflow guide: node types, Sheets memory schema, Agent Step formatting, and quota limits are all tribal knowledge
- **Deploy is the hard part** — Google Drive folder limits, disappearing-node bugs, Sheets column naming, and Knowledge attachment rules are all footguns that only appear after hours of work

## The Solution

Super Gem Creator runs a structured 5-step pipeline that handles all of the above:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Super Gem Creator v7.0                       │
│                                                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐                  │
│  │ UNDERSTAND│→ │ GENERATE  │→ │ VALIDATE  │→ ...             │
│  │  Step 1   │  │  Step 2   │  │  Step 3   │                  │
│  └───────────┘  └───────────┘  └───────────┘                  │
│       │               │               │                        │
│   Tier detect     All artifacts    Cross-tier                  │
│   6-tier model    per tier         gate + matrix               │
│   Auto-infer      Progressive      6 tier skeletons            │
│   from context    loading                                       │
│                                                                 │
│  ┌───────────┐  ┌───────────┐                                  │
│  │  DEPLOY   │→ │   TEST    │                                  │
│  │  Step 4   │  │  Step 5   │                                  │
│  └───────────┘  └───────────┘                                  │
│       │               │                                        │
│   Write to Drive  Calibrated           Post-deploy:            │
│   Configure gem   test suite        Memory relay loop          │
│   Setup Sheets    Reflexion          Registry update           │
│   Harness setup   loops             30-day health check        │
└─────────────────────────────────────────────────────────────────┘
```

Each step is **independently resumable** — state files track progress across sessions so no work is ever repeated.

---

## The 6-Tier Model

Every build is automatically classified into one of six tiers from context. No tier menus.

| Tier | Name | Best For |
|---|---|---|
| 1 | **Fast Track** | One-time use, no memory, pure system prompt |
| 2 | **Standard** | Most use cases — conversational advisor with memory hub |
| 3 | **Memory Gem** | Multi-domain research synthesis, 4–5 sub-areas, deep knowledge |
| 4 | **Industry Brain** | Offline/private, local models (Ollama/Gemma), data-sensitive |
| 5 | **Harness-Proxy** | Gem as conversational frontend + Opal as autonomous backend |
| 6 | **Gem from Labs** | Native Opal pipeline — Fast (stateless) or Full (memory-bearing) |

**Tier 6 sub-modes:**

| | Fast | Full |
|---|---|---|
| Memory | None — stateless | Sheets Memory Bus (3 tabs) |
| Nodes | ≤ 5 | ≤ 8 |
| Deliverables | 4 | 8 |
| Calibration cycle | Skip | 14-day |
| Test threshold | 3/3 smoke tests | 7/7 full suite |

---

## Architecture

```
super-gem-creator-v7.0/
├── SKILL.md                              # Thin router (166 lines) — loaded first
│                                         # Mode detection, tier routing, step dispatch
└── references/                           # 29 reference files — loaded on demand
    ├── step1-understand.md               # Tier detection, elicitation, 6-tier signal tables
    ├── step2-generate.md                 # Shared generation base (all tiers)
    ├── step2-fasttrack-delta.md          # Tier 1 generation delta
    ├── step2-research-delta.md           # Tier 3 generation delta
    ├── step2-local-delta.md              # Tier 4 generation delta
    ├── step2-opal-delta.md               # Tier 5/6 — Node Catalog (16 nodes), Sheets schema,
    │                                     #   5-block Agent Step, Fast/Full sub-mode, Harness dispatch
    ├── step3-validate.md                 # Cross-tier validation gate, 6 tier skeletons
    ├── step4-deploy.md                   # Tier 1/2/3 deploy guide
    ├── step4-local-deploy.md             # Tier 4 deploy guide
    ├── step4-opal-deploy.md              # Tier 5/6 — disappearing-docs check, compaction,
    │                                     #   Apps Script harness template, 3-path backend
    ├── step5-test.md                     # Test suite, all tiers incl. Tier 5/6 calibration
    ├── post-deploy.md                    # Memory relay loop, registry, 14-day recalibration
    ├── upgrade-workflow.md               # Upgrade path Tier 1→6, harness-entry-check
    ├── agentic-tier-guide.md             # Tier selection map, comparison table
    ├── terminology-glossary.md           # ~35 canonical v7 terms
    ├── gemini-gems-specs-and-limits.md   # Hard limits, Opal quota table (§18)
    ├── budget-reference.md               # Prompt / hub / context budget breakdown
    ├── tool-stack.md                     # File ops, research stack, agentic tiers
    ├── persona-and-routing-defaults.md   # PersonaMatrix, DecisionEngine, Tier 5/6 signals
    ├── memory-hub-template.md            # §1–§8 memory hub scaffold
    ├── memory-relay-protocol.md          # MEMORY_UPDATE format and relay rules
    ├── shared-principles-template.md     # Cross-gem behavioral principles
    ├── heuristics-pool-template.md       # Heuristic categories, all tiers
    ├── test-questions-template.md        # Test question bank by tier
    ├── notebook-themes-examples.md       # NotebookLM grounding themes
    ├── meta-prompt-a-research.md         # Research meta-prompt (Tier 3/4)
    ├── meta-prompt-b-config.md           # Config meta-prompt
    ├── local-research-infrastructure.md  # Tier 4 RAG + source directory setup
    └── local-gem-script-template.py      # Tier 4 local runner + HarnessPollMode class
```

### Design Principles

| Pattern | How It's Applied |
|---|---|
| **Thin router** | SKILL.md is 166 lines — step logic lives in reference files, loaded only when needed |
| **State-based resumption** | JSON state files per step — never redo completed work across sessions |
| **Intent inference** | Tier is detected from the first message, never from a menu |
| **Progressive loading** | Only the active step's reference is in context. Node Catalog `####` blocks load per-node |
| **Zero dangling refs** | All 30 files cross-verified — no forward references to non-existent files |

---

## What Each Step Does

### Step 1: UNDERSTAND
Elicits the gem's domain, audience, and behavioral requirements. Auto-detects tier from signals in the first message — no questions asked unless the signal is genuinely ambiguous. Produces a `step1-state.json` with tier, sub-mode (Fast/Full for Tier 6), harness backend preference, and detected user profile.

### Step 2: GENERATE
Reads the shared base (`step2-generate.md`) then the tier-specific delta. Produces all artifacts in one pass: system prompt, memory hub, tri-file JSONs (if applicable), node instructions, Sheets schema, test plan. For Tier 6 Full: 8 deliverables. For Tier 6 Fast: 4 deliverables.

### Step 3: VALIDATE
Walks through a cross-tier validation gate before any files are written. Phase 1: 5 universal safety checks (hard limits, disappearing-docs, terminology, context-asymmetry, compaction readiness). Phase 2: tier-specific deep-dive skeleton. Phase 3: matrix cross-check (mandatory for Tier 6 Full).

### Step 4: DEPLOY
Writes files to Google Drive following the relay folder architecture. Runs pre-write validation on every file (path check, Knowledge folder count, existence check). For Tier 5/6: sets up the Sheets Memory Bus, runs the disappearing-docs check, configures the harness backend.

### Step 5: TEST
Runs a calibrated test suite. Tier 1/2/3: 5 scenario tests with reflexion loop. Tier 5: harness round-trip variants. Tier 6 Fast: 3/3 smoke test threshold. Tier 6 Full: 7/7 calibration suite including multi-turn memory and compaction trigger tests. Reflexion applies failing lessons back to the prompt before closing.

---

## Key v7 Features

### Node Catalog (Tier 5/6)
16-node quick-reference grid embedded in `step2-opal-delta.md`. Quick Reference card grid always loaded; individual `####` detail blocks loaded only when configuring that specific node type.

| Category | Nodes |
|---|---|
| Core | User Input, Generate, Agent Step, Output |
| Sheets | Sheets Read, Sheets Append |
| Drive | Drive Read, Drive Write |
| Google | Google Search, Docs Create, Sheets Create, Slides Create, Gmail Send, Calendar Read |
| Control | For-Each, Conditional Branch |

### Canonical Sheets Memory Bus Schema
3-tab schema (`bus` / `state` / `runs`) with a 8-value `event_type` enum. Used identically by Tier 5 (harness dispatch) and Tier 6 Full (Opal memory). Column names are locked — harness backends and Opal tool nodes both reference exact headers.

```
bus tab:   uuid | parent_uuid | timestamp | event_type | role | content | metadata
state tab: session_id | last_run_at | last_query | last_result_url | status | notes
runs tab:  run_id | timestamp | input | output_url | tokens_used | success
```

### 5-Block Agent Step Format
```
## Role           — 1–2 sentence role statement
## Goal           — single concrete objective with explicit termination condition
## Tool Protocol  — one line per enabled tool: when to call + what to pass
## Output Format  — JSON schema (status / path / payload / termination_reason)
## Edge Cases     — halt conditions, loop detection (3× same tool+args), never-list
```
Budget: 1,500 chars target / 2,500 chars hard cap.

### Harness Backend (Tier 5) — 3 Paths
- **Apps Script** (default) — container-bound script on the Memory Sheet, 1-min poll trigger. ~70-line template in `step4-opal-deploy.md §4.9`. Handles Gmail, Drive, Calendar, UrlFetch, Gemini API. Limit: 90 min/day execution.
- **Local Python** — `HarnessPollMode` class in `local-gem-script-template.py`, run with `--harness` flag. Best for local files, Ollama, code execution.
- **Manual** — zero infrastructure, copy-paste fallback for low-frequency workflows.

---

## Relay Folder Architecture

Gemini has a hard **10-file limit** on Knowledge-attached folders (flat count, subfolders included). The relay folder pattern keeps infrastructure files out of the Knowledge index.

```
Gemini/
  [Gem Name] Memory/          ← Knowledge-attached (≤ 6 files recommended, max 10)
    _Memory_[Name]_GemMemoryHub_Active.md
    _Core_[Name]_PersonaMatrix.json
    _Controller_[Name]_DecisionEngine.json
    _State_[Name]_SessionMemory.json

  [Gem Name] Relay/           ← Sibling folder (no limit, never indexed)
    _Memory_[Name]_GemMemoryHub_Archive.md
    _Progress_[Name]_ActiveTask.md
    _Heuristics_[Name]_Pool.md
    _Prompt_[Name]_GemSystemPrompt_v[X].md
    _Opal_[Name]_GraphSpec.md             (Tier 5/6)
    _Sheets_[Name]_MemorySchema.md        (Tier 5/6)
    _Opal_[Name]_NodeInstructions.md      (Tier 5/6)
```

Tier 6 (Gem from Labs) only: Relay folder only — Opal doesn't consume Gemini Knowledge slots.

---

## Hard Limits

| Constraint | Tiers 1–4 | Tier 5/6 Agent Step |
|---|---|---|
| System prompt / Agent Step | ≤ 2,500 chars (target ≤ 2,000) | ≤ 2,500 chars per node (target ≤ 1,500) |
| Memory hub | 8K target / 15K ceiling | N/A — Sheets tabs instead |
| Knowledge folder files | ≤ 10 (recommend ≤ 6) | N/A |
| Notebooks (NotebookLM) | 0 (T1) / 2 (T2) / ≤5 (T3) / local (T4) | Google Search + Sheets reads |
| Opal nodes per workflow | — | ≤ 20 (target ≤ 8 for v1); Fast mode: ≤ 5 |
| Opal runs per day | — | ~50 soft cap (free tier) |
| Apps Script execution | — | 90 min/day / 6 min per run |

Full quota table: `gemini-gems-specs-and-limits.md §18`.

---

## Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/dmmdea/gemini-super-gem-creator.git
   ```
2. Copy the skill folder to your Cowork skills directory:
   ```bash
   cp -r gemini-super-gem-creator/ ~/.claude/skills/super-gem-creator/
   ```
3. Reload Claude Cowork.

---

## Usage

The skill triggers automatically on natural conversation:

```
"Build me a gem for [domain]"              → Full 5-step build, tier auto-detected
"Create an Opal workflow that does X"      → Tier 6 Gem from Labs pipeline
"I want the gem to actually run the work"  → Tier 5 Harness-Proxy
"Upgrade my existing [gem name] to v7"     → Upgrade workflow
"Test my gem"                              → Step 5 test suite only
"Update the gem's memory"                  → Memory relay loop
```

### Resuming Across Sessions

The skill writes state files after each step. If a session ends mid-build, the next invocation detects the partial state and resumes from the right step — no repeated work.

---

## Requirements

- Claude Cowork (desktop app Cowork mode)
- Google account with Drive and Gemini access
- For Tier 5/6: access to `labs.google/opal` (same Google account as Drive)
- For Tier 5 Apps Script path: Google Workspace or personal Gmail with Apps Script enabled
- For Tier 5 Local Python path: `pip install gspread google-auth`, service account JSON

---

## FAQ

**Q: How is tier detected?**
From the first message. Strong signals (explicit keywords like "Opal", "local", "harness") resolve immediately. Ambiguous cases get one clarifying question. The skill never presents a tier menu.

**Q: Does Tier 6 require an Opal account?**
Just a Google account — Opal (Gem from Labs) is a free consumer Labs product at `labs.google/opal`. No API key needed.

**Q: Can I run just one step?**
Yes. Say "validate my gem" for Step 3 only, "deploy the files" for Step 4 only, etc. Each step is independently valuable.

**Q: What's the difference between Harness-Proxy (Tier 5) and Gem from Labs (Tier 6)?**
Tier 5: a standard Gemini Gem fronts the conversation while an Opal workflow does autonomous backend work (file writes, API calls, email sends). Tier 6: Opal is the primary interface — no Gem UI, native Opal pipeline with visual node graph.

**Q: Will this work with Claude Code?**
The skill is designed for Cowork. The references and architecture assume the Cowork environment, Drive access, and the Cowork file operation tools.

---

## Changelog

### v7.0 (2026-04-09)
- Added Tier 5 (Harness-Proxy) and Tier 6 (Gem from Labs) as first-class tiers
- 16-node Node Catalog embedded inline — Quick Reference grid always loaded, `####` detail blocks on demand
- Canonical Sheets Memory Bus schema with full `event_type` enum
- Apps Script harness backend template (~70 lines, syntax-verified)
- `HarnessPollMode` Python class + `--harness` argparse flag for local backend
- 5-block Agent Step format replacing old 7-field format
- Compaction playbook, disappearing-docs check, context-asymmetry principle
- Tri-File JSON Architecture section for stateful Opal workflows
- Cross-tier validation gate (`step3-validate.md`) with 6 tier skeletons
- Canonical terminology glossary (`terminology-glossary.md`, ~35 terms)
- SKILL.md trimmed to 166 lines (thin router pattern)
- Zero dangling forward references across all 30 files

### v6.0 (2026-04-08)
- Opal introduced as Tier 5 with Agent Step, Sheets memory, tool calling
- Harness-Proxy layer added as optional cross-tier extension
- Progressive reference loading (~65% context savings vs v5)
- v5.x archived

---

## License

[MIT](LICENSE)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Credits

Built by Daniel using patterns from the Cowork skill ecosystem. Architecture informed by quick-agent-deployer, Claude-Cowork-Optimizer, and skill-creator.
