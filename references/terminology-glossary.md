# Terminology Glossary — Super Gem Creator v7.0

<!-- Cross-cutting lookup. Load when User asks "what is X?" or when any step
     needs canonical term clarification. Do NOT load by default — load on demand.
     Patch H source. Last updated: 2026-04-09. -->

## How to use this glossary

Entries are listed alphabetically. The **bold term** is the canonical name to use
in all design artifacts. *Italicized* alternatives are acceptable aliases only in
conversation — never in prompts, templates, or reference files. Cross-references
use → notation.

---

## A

**4 Pillars** — The four mandatory sections of every gem system prompt:
Persona, Task Boundaries, Contextual Grounding, Output Format. Aliases:
*4P structure*, *four-pillar structure*. The prompt must not grow beyond 4 Pillars.
Hard ceiling: ≤2,500 chars total. Target: ≤2,000 chars.

**Agent Step** — A single node instruction in an Opal workflow. Structured as
5 mandatory blocks: Role / Goal / Tool Protocol / Output Format / Edge Cases.
Budget: 1,500 chars target, 2,500 chars hard cap per step. Stored as `content`
payload in the Sheets Memory Bus. See also → Node Catalog.

**Apps Script (Harness backend Path 1)** — Container-bound Google Apps Script
running as a time-driven trigger on the memory hub Sheet. Default harness backend
for API-bound and Google-native tool calls. Free-tier limits: 90 min/day execution,
20K UrlFetchApp calls/day, 6 min max per execution. ~60-line template in
`step4-opal-deploy.md`. API keys stored in Script Properties (encrypted at rest).

---

## C

**Calibration Run** — A mandatory smoke test for Tier 6 Full (Gem from Labs)
builds. Verifies node throughput, Sheets write latency, and harness round-trip
under realistic inputs. Artifact: `[gem-name]-opal-calibration-[YYYY-MM-DD].md`
saved to the Relay folder.

**Compaction Playbook** — Memory hub maintenance protocol. Two triggers:
(1) within-session at 80% fill → compress oldest entries in-place;
(2) between-session insulation pass → archive stale context to Relay.
Full playbook in `step4-opal-deploy.md` → "Runtime Behavior" subsection.

**Context Asymmetry** — Gemini's structural constraint: 1M-token input window
vs. 64K output cap. Consequence: gems are synthesis engines, not generation
engines — design outputs to be dense and decision-ready, not exhaustive.
Enforced via Phase 1 Universal Safety Gate check #4.

---

## D–E

**Disappearing-Documents Bug** — Known Opal platform issue where Knowledge
files silently detach from a gem between sessions without error. Mitigation:
always check the Knowledge menu and run the mandatory "Update" command before
each session. Phase 1 Universal Safety Gate check #2.

**event_type enum** — The Sheets Memory Bus column that classifies each row.
Canonical values: `user_input`, `agent_output`, `tool_call`, `tool_result`,
`harness_request`, `harness_result`. Extensible by User via Apps Script editor.

---

## F

**Fast Opal** → see **Tier 6 Fast**.

**Fast Track** → see **Tier 1 — Fast Track**.

**4 Pillars** → see entry under **A** (listed there for canonical sort order).

---

## G

**Gem from Labs** → see **Tier 6 — Gem from Labs**.

---

## H

**harness-entry-check** — A v7 addition to 30-day gem health reviews for any
harness-bearing gem. Validates that the dispatch block in the gem prompt is intact,
the backend trigger is active, and the Sheets Memory Bus is reachable.

**harness_request / harness_result** — The two `event_type` enum values that
signal a Harness-Proxy round-trip in the Sheets Memory Bus. `harness_request`
is written by the gem when it needs a tool executed; `harness_result` is written
by the backend after execution.

**Harness-Proxy** — Architecture pattern where the gem delegates tool execution
to an external backend via the Sheets Memory Bus. Optional; offered proactively
when intent warrants. Three backend paths: Apps Script (default), Local Python,
Manual copy-paste. Available on: Standard (Tier 2), Research/Industry Brain
(Tier 4), Opal Pipeline (Tier 5). NOT available on: Fast Track (Tier 1),
Local (Tier 3). See `step4-opal-deploy.md` for setup.

**Hub** → see **Memory Hub**.

---

## I

**Information Hierarchy Principle** — Abstract principle (TurboQuant-sourced):
structure information by decision-relevance — most-actionable signal first,
supporting detail after. Applied to Agent Step output format design. Paired with
→ variance-first prompting.

---

## K

**Knowledge folder** — The Google Drive folder attached to a Gemini gem via the
Knowledge panel in Gemini's gem builder. Hard platform limit: 10 files TOTAL,
including any files inside subfolders. Recommended: ≤6 files to leave headroom.
Subfolders inside the Knowledge folder count toward the 10-file limit — they are
NOT safe containers.

---

## L

**Local Python polling (Harness backend Path 2)** — A persistent Python polling
script for local compute needs (Zora, Ollama, code execution, local filesystem).
Template in `local-gem-script-template.py` → "Harness polling mode" section.
Use when the tool call requires local compute that Apps Script cannot reach.

---

## M

**Manual copy-paste (Harness backend Path 3)** — Zero-infrastructure harness
fallback. User manually reads `harness_request` rows from the Sheet, executes
the tool, and pastes `harness_result` back. Slowest path; works anywhere with
no setup.

**Memory Bus** → see **Sheets Memory Bus**.

**Memory Hub** — The primary Google Doc storing gem conversation memory.
Structured in numbered sections (§0 = instructions, §1–§N = content). Target:
5,000–8,000 chars (Standard/Local), 5,000–6,000 chars (Research). Max: 15,000
chars. Archive trigger: 12,000 chars (Standard/Local), 8,000 chars (Research).
§0 must instruct the gem to compress, not just append.

---

## N

**Node Catalog** — Quick-reference index of ~15 common Opal workflow nodes
embedded inside `step2-opal-delta.md`. Two layers: (1) Quick Reference card grid
(~30-40 lines, always loaded with the file); (2) Full Node Reference with one
`####` block per node (~15 lines each, treated as load-on-demand boundaries).
Claude reads the card grid first and expands specific node blocks only when the
User selects nodes or asks about them.

---

## O

**Operational Algorithmic Brain** — Canonical component name within the
→ Persona Primitive Cluster. Represents the gem's analytical processing function:
pattern recognition, structured reasoning, decision frameworks. Do not abbreviate
as "OAB" in design artifacts.

**Opal** — Google AI Studio's visual agent-workflow builder. Used for Tier 5
(Harness-Proxy pipeline) and Tier 6 (Gem from Labs) builds. Current model:
Gemini 2.0/3.0 Flash preview (subject to volatility — see → Preview-Model
Volatility Warning).

**Opal Hard Limits table** — A 9-row reference table covering: daily workflow
runs by tier, nodes per workflow, tool calls per run, Sheets append caps, Flash
preview status. Lives in SKILL.md router. Patch A source. Confidence flags
indicate verified vs. estimated limits.

---

## P

**Persona Primitive Cluster** — The canonical name for the set of atomic persona
components assembled into a gem's Persona pillar: → Operational Algorithmic Brain,
→ Personality Blend Calculator, role label, domain lens, communication style
vector. Each component is independently tunable without rewriting the full persona.

**Personality Blend Calculator** — Canonical component name within the
→ Persona Primitive Cluster. Sets the gem's communication style as a weighted
blend (e.g., 70% analytical / 30% warm-supportive). Always expressed as
percentages summing to 100%.

**Phase 1 — Universal Safety Gate** — The 5 always-on validation checks applied
to every gem tier before deployment sign-off: (1) Hard Limits check vs. Opal
limits table, (2) Disappearing-Documents check, (3) Terminology Canonicalization,
(4) Context-Asymmetry Sanity, (5) Compaction Readiness. See `step3-validate.md`.

**Phase 2 — Per-Tier Deep-Dive** — Tier-specific validation checklist run after
Phase 1 passes. Check counts: Tier 1 = 3, Tier 2 = 5, Tier 3 = 6, Tier 4 = 7,
Tier 5 = 7 (with 8 sub-items on check #7), Tier 6 Fast = 4, Tier 6 Full = 8.
See `step3-validate.md`.

**Phase 3 — Matrix Cross-Check** — Final cross-reference validation of the
complete gem artifact set against the tier's deliverable checklist. Mandatory
for Tier 6 Full; strongly recommended at Tier 4/5; offered (default off) for
Tier 6 Fast; optional for Tiers 1–3.

**Preview-Model Volatility Warning** — A one-time notice surfaced at the start
of any Opal (Tier 5) or Gem from Labs (Tier 6) build. Acknowledges that Gemini
Flash preview model behavior, rate limits, or availability may change without
notice. Logged in the Calibration Run artifact.

---

## R

**Relay folder** — A Drive folder that is a SIBLING of the Knowledge folder
(never inside it). Naming convention: `[Gem Name] Relay/`. Stores files that
Claude or User needs but that Gemini should not index: archive docs, heuristics,
system prompt backup, infrastructure refs, roadmap, calibration artifacts.

---

## S

**Sheets Memory Bus** — The Google Sheet acting as the shared state layer between
a Gemini gem and its Opal backend or harness. Column schema (Patch C canonical):
`uuid` (STRING), `parent_uuid` (STRING), `timestamp` (DATETIME),
`event_type` (ENUM), `role` (ENUM: user | agent | harness), `content` (TEXT),
`metadata` (JSON).

**Shared Principles** — Cross-tier gem design rules that apply regardless of tier.
Stored in `shared-principles-template.md`. Not re-stated in tier-specific step
files — reference by name only.

---

## T

**Tier 1 — Fast Track** — Prompt-only gem. No Knowledge files, no memory hub,
no relay. Prompt ≤1,800 chars. Deploy in under 20 minutes. Frictionless by design.

**Tier 2 — Standard** — Classic gem with ≤6 Knowledge files + optional Relay
folder. No agentic backend. Prompt ≤2,000 chars target, ≤2,500 chars hard cap.

**Tier 3 — Memory Gem** — Standard gem augmented with a Memory Hub (Google Doc)
+ Relay folder. Sub-type of Standard; not a separate platform tier. Inherits
all Tier 2 checks plus hub schema compliance.

**Tier 4 — Industry Brain / Research Gem** — Memory Gem + NotebookLM grounding
layer. ≤2 notebooks for Standard, ≤5 for Research. Deep domain knowledge through
curated source notebooks.

**Tier 5 — Harness-Proxy** — Memory Gem + Opal workflow acting as a tool
dispatcher. Connects gem to external APIs or local compute via the Sheets Memory
Bus and → Harness-Proxy pattern. Harness is OPTIONAL and offered proactively.

**Tier 6 — Gem from Labs** — A gem backed by a native Google AI Studio Opal
agent pipeline published via the "Gem from Labs" mechanism. Two sub-modes:
Fast (stateless, 4 deliverables) and Full (memory-bearing, 8 deliverables).

**Tier 6 Fast** — Prototyping sub-mode of Tier 6. Stateless (no Sheets memory).
4 deliverables: node instructions, preview-model volatility warning,
disappearing-docs Update command, smoke test plan (≥3 inputs). Router triggers:
"try", "test", "prototype", "quick", "experiment", "just see if", "minimal",
"simple workflow", "no memory needed", "personal use only".

**Tier 6 Full** — Production sub-mode of Tier 6. Memory-bearing (Sheets Memory
Bus). 8 deliverables: graph spec doc, node instructions, Sheets memory schema,
test plan, share config, calibration run, preview warning, disappearing-docs
Update command. Router triggers: "deploy", "publish", "share with team",
"production", "save memory", "track over time", "calibrated", "complete".

**Tool Protocol block** — Block 3 of the 5-block → Agent Step structure.
Declares the tool to invoke (`url_fetch`, `gmail_send`, `drive_write`,
`calendar_create_event`, `anthropic_call`, `gemini_call`, `docs_edit`,
`sheets_append`, `custom`), its input parameters, and output parse instructions.

**Tri-File JSON Architecture** — Advanced sub-variant for Opal builds that
splits memory across 3 Sheets instead of one: (1) Working Memory (current session),
(2) Episodic Buffer (recent sessions, compressed), (3) Long-Term Store (distilled
facts, rarely written). Covered in `step2-opal-delta.md` → "Advanced: Tri-File
JSON Architecture" section. Use when single-hub write contention is observed.

---

## U–V

**Universal Safety Gate** → see **Phase 1 — Universal Safety Gate**.

**variance-first prompting** — Abstract principle (TurboQuant-sourced): lead
every output with the highest-variance, most-discriminating signal — not preamble,
not methodology. Applied to gem output format instructions so the gem's first
sentence answers the User's actual question. Paired with → Information Hierarchy
Principle.
