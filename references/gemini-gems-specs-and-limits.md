# Gemini Gems — Specifications, Limits & Optimization Reference

**Research date**: 2026-04-03
**Sources**: Google support forums, developer documentation, community testing, empirical testing (Zora Deployment Advisor gem)

---

## 1. Hard Limits (Documented by Google)

### Knowledge Base Files
- **Max files per Gem**: 10
- **Max file size**: 100 MB each
- **Supported types**: PDFs, documents, spreadsheets, Google Drive files
- **Drive files auto-sync**: When referencing Drive files, the Gem always uses the most recent version

### NotebookLM Integration
- **Sources per notebook**: 300 (Pro plan), 600 (Ultra plan) — up from previous 10-file limit
- **Max notebooks per Gem**: Not officially documented. No hard cap stated by Google, but empirically limited by context budget (see Section 3)
- **Auto-sync**: If you add a new document to a NotebookLM notebook, the Gem automatically has access next session without re-uploading
- **Notebooks are read-only**: Gemini references your sources but doesn't modify the notebook

### System Instructions (Gem Prompt)
- **Character/token limit**: Not officially documented by Google
- **Practical observation**: Community reports that when instructions get too long, the Gem may start ignoring connected knowledge files
- **Magic Wand**: Gemini can auto-expand your instructions — but this can bloat them past practical limits

### Per-Turn File Attachments
- **Max files per prompt**: 10
- **Max file size per attachment**: 100 MB

---

## 2. Context Window Architecture

### The 1M Token Reality

Google advertises a 1 million token context window for Gemini 3 Pro (200K for Flash). However, the consumer web app (where Gems run) allocates this budget very differently than the API:

| Component | Tokens | Notes |
|-----------|--------|-------|
| **Actual conversation budget** | **~32,000** | What you get for chat in the web app |
| File uploads & system overhead | ~968,000 | Reserved by the web app infrastructure |
| **Total model capacity** | 1,000,000 | The model CAN process this much via API |

**This is the critical insight**: Your Gem's system prompt, knowledge retrieval, notebook grounding, conversation history, AND the model's response all compete for roughly **32K tokens** in the consumer web app. The 1M window is the model's theoretical capacity, not what the web interface actually gives you.

### Deep Think Context
- Deep Think mode has a **192,000 token** window — significantly more than the standard ~32K
- This explains why Deep Research prompts work when standard prompts fail

### Deep Research Mode — UI Behavior Quirks (IMPORTANT for gem design)

When the user enables **Deep Research** in the Gemini UI, a platform-level research agent runs the prompt. This has two consequences that affect how custom Gem prompts behave:

1. **Plan preview bypass:** Deep Research always returns a numbered, canonical **research plan** (1-N bullet steps, each phrased as a research sub-task) **before executing**. The user must approve or edit the plan before the actual research runs. This preview step is Gemini UI behavior, not Gem behavior — it happens regardless of what the Gem's system prompt says.
2. **Session-open ritual override:** Custom rituals in the Gem's system prompt (e.g., `[SESSION_SUMMARY — OPENING]`, thinking blocks, output tags) are **skipped or compressed** when Deep Research runs, because the Deep Research agent owns the response flow on that turn. The ritual may re-emerge on follow-up turns that don't use Deep Research.

**Implications for gem authors:**
- Do NOT treat "missing SESSION_SUMMARY at Deep Research turn" as a Rule 4 violation — it's platform behavior.
- Gem-side routing rules like `[RESEARCH_NEEDED]` still work for non-Deep-Research turns, and the Deep Research plan inherits the Gem's behavioral rules (sourcing discipline, framework naming, flagging) in the final output even if the opening ritual is skipped.
- When validating a research gem in Step 5, grade the Deep Research plan preview against the system prompt's methodology rules (layered search, triangulation, framework commitment). If the plan defers framework choice or skips source pre-commitment, ask the user to reply in-chat with a refinement before hitting execute — the Gem will honor refinements before the actual research runs.

### What DR Preserves vs Suppresses (Rule Substance vs Rule Form)

Deep Research treats the Gem's system prompt as **research methodology input**, not as a behavioral harness. This produces a predictable split between what survives in the DR essay and what gets absorbed by the DR agent's own response flow. Grade these two layers separately.

**DR PRESERVES (rule substance — non-negotiable, grade strictly):**
- Sourcing discipline (authoritative source hierarchy, pre-commitment to named sources)
- Framework naming and commitment (e.g., TAM/SAM/SOM, Porter's Five Forces, named by the gem)
- Triangulation (≥2 independent sources per quantitative claim)
- Proxy methodologies (where direct data is unavailable, gem must name the proxy)
- Ranges-not-points discipline (empirical estimates expressed as ranges with bounds)
- Bias disclosure (gem names the directional bias of its own sources)
- Reliability ratings (gem grades confidence in each claim)
- Source hierarchy adherence (tier-1 official > tier-2 trade > tier-3 general)

**DR SUPPRESSES (rule form — format-accommodated, do not grade in DR mode):**
- `[UNVERIFIED]` / `[ESTIMATED]` bracket tags (DR replaces with prose hedging: "empirical estimates", "directionally indicative", "subject to verification")
- `[SESSION_SUMMARY]` / `[ADVISORY]` / `[MEMORY_FLAG]` output type tags (DR agent owns the response envelope)
- Session-open ritual (`[SESSION_SUMMARY — OPENING]` block)
- `---MEMORY_UPDATE---` emission (DR never writes memory — it's a one-shot research agent)

**Grading rule:** If the essay passes every substance item above, the gem is DR-compliant **even if** no tag, ritual, or memory block appears. Conversely, if a tag is present but a triangulation is missing, the gem fails — form without substance is a worse signal than substance without form.

### How Each Context Source Consumes Tokens

| Source | Loading Behavior | Token Impact |
|--------|-----------------|--------------|
| **System instructions** | Loaded **in full** every single turn | Direct, permanent cost — every token counts |
| **Knowledge base files** | **RAG retrieval** — only relevant segments pulled per turn | Variable — depends on query relevance matching |
| **NotebookLM notebooks** | **Source grounding** — relevant portions retrieved, not full notebooks | Variable — but more notebooks = more retrieval overhead |
| **Drive memory files** | Treated as knowledge files — RAG retrieval | Variable — same as knowledge base |
| **Conversation history** | Accumulates across the session | Grows with each turn — eventually pushes out other context |
| **User prompt** | Loaded in full for the current turn | Direct cost |
| **Model response** | Generated from remaining budget | Capped by whatever tokens remain |

### The Key Distinction

**System instructions = fully loaded every turn** (expensive, permanent). **Knowledge files and notebooks = retrieval-based** (cheaper per turn, only relevant chunks). This means a 3,500-token system prompt costs MORE than 10 knowledge files, because the prompt is always present while files are only partially retrieved.

---

## 3. Empirical Limits (From Zora Deployment Advisor Testing)

### What Crashed (Error 13, complete hang on "hi")
- v1.3 system prompt: ~12,400 chars / ~3,500 tokens
- 5 NotebookLM notebooks attached
- 7 files in Drive memory folder
- **Result**: Gem completely unresponsive, "something went wrong (13)"

### What Works
- v1.4 system prompt: ~2,200 chars / ~620 tokens
- 2 NotebookLM notebooks attached
- 1 file in Drive memory folder (Memory Hub only)
- **Result**: Responsive, accurate, reads Memory Hub correctly

### Incremental Testing Results
| Config | Result |
|--------|--------|
| Slim prompt + 1 notebook + 1 Drive file | ✅ Works |
| Slim prompt + 2 notebooks + 1 Drive file | ✅ Works |
| Bloated prompt + 5 notebooks + 7 Drive files | ❌ Error 13, hang |

### Error 13 Specifics
- Error 13 in Gemini is typically described as an "account-level sync issue" where text input fails
- However, in the Gems context, it appears to also trigger when the Gem's total pre-turn context exceeds what the web app can process
- Voice input may still work when text input fails (different pipeline)
- Creating a new Gem with the same overloaded config reproduces the error — confirming it's a context problem, not account corruption

---

## 4. Known Issues (Community Reports, 2025-2026)

### Gems Ignoring Knowledge Files
- **Multiple community reports** of Gems ignoring uploaded knowledge base files
- Root cause appears to be instruction length: when system instructions are too long, the Gem deprioritizes knowledge file retrieval
- **Workaround**: Keep instructions short, put detailed content in knowledge files instead

### Gems Ignoring Instructions Over Long Sessions
- Gems can "lose" their instructions over extended conversations as conversation history grows and pushes instructions out of effective context
- **Workaround**: Start new conversations rather than continuing very long ones

### Knowledge Files Disappearing
- Documents in a Gem's knowledge section can sometimes vanish from the Gem's perspective
- Must click "UPDATE" button to save knowledge changes
- Drive-linked files are more reliable (auto-sync)

### Regression Issues
- Google has introduced regressions where Gems stop accessing knowledge files properly
- Reported in Jan 2026: "Custom Gem Ignoring Knowledge Base Files (Gemini Advanced)"
- These are server-side issues that Google fixes over time

---

## 5. How NotebookLM Source Grounding Works in Gems

### Architecture
1. NotebookLM uses Gemini's large context window for **source grounding** — responses are anchored to your uploaded sources
2. Unlike traditional RAG (chunk → embed → retrieve), NotebookLM can ingest **entire documents** maintaining structural integrity
3. When a notebook is attached to a Gem, Gemini uses it as a **grounding layer** — it reasons on your sources, applies its own intelligence, and can also search the web

### What This Means for Gems
- Each attached notebook adds a grounding layer that the model must process
- More notebooks = more grounding layers = more processing overhead per turn
- The notebook content isn't chunked and embedded like traditional RAG — it maintains document structure
- This is WHY multiple large notebooks can overwhelm the Gem: each one adds significant grounding overhead even if the retrieval is selective

### Notebook vs Knowledge File vs Drive File

| Source Type | In Gem Config | Loaded How | Best For |
|-------------|---------------|------------|----------|
| Knowledge file (uploaded) | Knowledge section (max 10) | RAG retrieval per turn | Static reference docs, templates, schemas |
| Knowledge file (Drive) | Knowledge section via Drive link | RAG retrieval, auto-syncs | Living documents that change frequently |
| NotebookLM notebook | Attached as data source | Full source grounding layer | Deep research bases with many sub-sources |
| Drive memory folder | Referenced in system instructions | Gem reads on demand (if instructed) | Working memory, decision logs, state files |

---

## 6. Optimization Guidelines for Gem Creation

### System Prompt (The #1 Lever)

**Target**: Under 1,500 characters (~420 tokens). Absolute max: 3,000 characters (~840 tokens).

**Rules**:
- The prompt is loaded IN FULL on EVERY turn — it's the most expensive context source
- Never duplicate content that exists in knowledge files or notebooks
- Use the prompt for: role definition, behavioral rules, memory protocol, hard constraints
- Put everything else in knowledge files: hardware specs, model inventories, research findings, commands
- Reference knowledge by section number, don't inline it: "See Memory Hub section A3 for model inventory"

### Knowledge Files (10 max, 100MB each)

**Rules**:
- Only relevant segments are retrieved per turn (RAG) — large files are OK
- Use structured formats (headers, tables) so retrieval can find the right section
- Consolidate related content into fewer, well-organized files rather than many small files
- Each file adds retrieval overhead — aim for 3-5 focused files, not 10

### NotebookLM Notebooks

**Target**: 1-2 notebooks attached at a time. Max safe: 2-3.

**Rules**:
- Each notebook adds a full grounding layer — this is heavier than a knowledge file
- Don't attach notebooks for reference material that could be a knowledge file instead
- Use notebooks for deep research bases where source grounding (citations, cross-referencing) matters
- Swap notebooks based on topic rather than keeping all attached permanently
- 5 notebooks = confirmed crash. 2 notebooks = confirmed stable.

### Drive Memory Files

**Rules**:
- The Gem reads Drive files when instructed to in the system prompt
- Keep the memory folder lean — 1-2 files max
- Use a single Memory Hub file as the source of truth
- Don't put reference docs in the Drive folder — put them in knowledge files or notebooks
- Drive files that the Gem is told to "read at the start of every conversation" add context overhead on every turn

### Conversation Management

**Rules**:
- Start new conversations rather than extending long ones
- The conversation history grows with each turn and competes for the ~32K budget
- For multi-part analysis (like audits), split across 2-3 messages in one conversation, not one mega-prompt
- Attach files at conversation level only when needed for that specific question

---

## 7. Context Budget Planner

Use this to estimate whether your Gem configuration will work:

```
Available budget (consumer web app): ~32,000 tokens

System prompt:        _____ tokens (target: <800)
Memory Hub read:      _____ tokens (only relevant chunks retrieved)
Knowledge retrieval:  _____ tokens (varies by query, ~1-3K typical)
Notebook grounding:   _____ tokens per notebook (~2-5K typical per notebook)
Conversation history: _____ tokens (grows each turn)
User prompt:          _____ tokens (varies)
Model response:       _____ tokens (needs room to generate)
─────────────────────────────────
Total must be:        < 32,000 tokens
```

### Example: Zora Deployment Advisor (Working Config)

```
System prompt (v1.4):        ~620 tokens
Memory Hub retrieval:        ~2,000 tokens (varies)
Knowledge retrieval:         ~1,500 tokens (varies)
Notebook grounding (×2):     ~6,000 tokens (estimate)
Conversation history:        ~0 tokens (first turn)
User prompt ("hi"):          ~1 token
Model response budget:       ~21,879 tokens remaining ✅
```

### Example: Zora Deployment Advisor (Crashed Config)

```
System prompt (v1.3):        ~3,500 tokens
Drive files (7 files):       ~8,000 tokens (retrieval from 7 sources)
Notebook grounding (×5):     ~15,000 tokens (estimate)
Conversation history:        ~0 tokens (first turn)
User prompt ("hi"):          ~1 token
Model response budget:       ~5,499 tokens remaining (IF it even loads) ❌
```

The crashed config was likely exceeding the web app's internal processing threshold for Gems initialization, causing Error 13 before the model even attempted to generate.

---

## 8. Revised Gem Architecture Template

Based on all findings, here's the optimal Gem structure:

```
┌─────────────────────────────────────────┐
│ SYSTEM PROMPT (~600-800 tokens)         │
│ • Role definition                       │
│ • Memory protocol (read hub, update)    │
│ • Core behavioral rules (5-8 max)       │
│ • References to knowledge sections      │
│ • NO duplicated content                 │
├─────────────────────────────────────────┤
│ KNOWLEDGE FILES (3-5 files)             │
│ • Memory Hub (living state file)        │
│ • Domain reference #1                   │
│ • Domain reference #2                   │
│ • Templates/schemas (if needed)         │
│ • (Retrieved via RAG — cheap per turn)  │
├─────────────────────────────────────────┤
│ NOTEBOOKS (1-2, swap as needed)         │
│ • Primary research notebook             │
│ • Secondary notebook (topic-specific)   │
│ • (Source grounding — heavier per turn) │
├─────────────────────────────────────────┤
│ DRIVE MEMORY FOLDER (1 file)            │
│ • Memory Hub only                       │
│ • (Referenced by prompt for read/write) │
└─────────────────────────────────────────┘
```

---

---

## 9. Token Budget Quick Reference (T0-F)

Why the ≤2,500 char / ~700 token system prompt limit matters — it's calculated to protect response quality:

```
GEMINI WEB APP PER-TURN BUDGET: ~32,000 tokens
─────────────────────────────────────────────
System Prompt      ≤700 tokens    (~2%)   ENFORCED  (target 420–560)
Memory Hub RAG     ~2,000 tokens  (~6%)   MONITORED
Knowledge Files    ~1,500 tokens  (~5%)   3–5 files
Notebook Grounding ~6,000 tokens  (~19%)  2 NBs
Conversation Hist  ~8,000 tokens  (~25%)  grows each turn
User Prompt        ~1,000 tokens  (~3%)   variable
Model Response     ~12,800 tokens (~40%)  PROTECTED
─────────────────────────────────────────────
TOTAL:             ~32,000 tokens
Response headroom: 40% reserved ✅
```

**Key insight:** Exceeding the 700-token prompt limit compresses the 40% response headroom — the gem produces shorter, lower-quality answers, not just shorter prompts. The limit is a quality budget, not an arbitrary constraint.

---

## 10. Permanent Memory UI Bug

Gemini's **built-in memory system** (the native "Memories" feature in your Gemini account) has a hard **10-slot FIFO limit**. When an 11th memory instruction is saved, Gemini silently ejects the oldest. There is no warning.

**Critical implication:** Never rely on Gemini's native memory slots for gem persistence. This is the architectural reason why the monolithic memory hub file approach is mandatory — it bypasses the 10-slot limit entirely by storing all state in a Drive file the gem reads on demand.

---

## 11. NotebookLM Tier Limits (as of April 2026)

| Tier | Notebooks | Sources/NB | Words/Source | Total Context/NB |
|------|-----------|-----------|-------------|-----------------|
| Free | 100 | 50 | 500K | 25M words |
| Plus | 200–500 | 100–300 | 500K | 50–150M words |
| Ultra | 500 | 600 | 500K | 300M words |

**Gem implications:** Free tier users are limited to 50 sources per notebook — enough for most gems. Plus users can go to 300. Ultra gives 600 sources/notebook. For gem creation, target 50–100 curated sources per notebook regardless of tier to keep grounding noise low.

---

## 12. File Upload Limits by Interface

| Interface | Max File Size | Max Files | Notes |
|-----------|--------------|-----------|-------|
| Gemini Web | 7MB standard / 75MB advanced | 10 per prompt | Standard gem creation interface |
| Vertex AI | 7MB direct / 50MB cloud import | 3,000 files | Developer/enterprise |
| Files API | 5GB per file | 50GB project quota | Programmatic/API |

**Gem creation:** Web interface (7–75MB, 10 files/prompt) is the operative limit for most users.

---

## 13. Context Caching

Available for repeated static prompts via the Gemini API — reduces token cost for heavy meta-prompts on high-frequency API deployments. Context caching is **not applicable** to standard gem web app use. Relevant only for Tier 3 (ADK/API) gem builders who send the same system prompt at high volume.

---

## 14. Google Opal (Tier 2 — Workflow-Based Gems)

Google Opal (`labs.google/opal`) is a visual DAG workflow builder available to all Google accounts. As of February 24, 2026, it added an **Agent Step** powered by Gemini 3 Flash that autonomously selects tools and models.

**What Opal adds that consumer Gems can't do:**
- Real tool calling: Google Search, Maps, weather, code execution, Google Sheets, URL fetch
- Automated workflows (scheduled or triggered)
- Multi-model pipelines (e.g., Deep Research → Gem synthesis → Veo output)
- Memory hub injection via Drive file read (explicit, not RAG) — more reliable retrieval

**When to use Opal instead of a consumer Gem:** The gem needs web search, spreadsheet I/O, code execution, or automated background tasks. See the Opal Deployment Path section in Step 4: DEPLOY of the skill.

**The 2,500-char system prompt limit still applies** inside Opal's AI Generation nodes — the gem architecture hard limits are unchanged at Tier 2.

---

## 15. JSON Tri-File Architecture (Advanced)

Three-file pattern for enterprise-grade gems needing dynamic persona blending:

- `_Core_[Name]_PersonaMatrix.json` — Persona primitives: weights, traits, interaction modes, blending rules
- `_Controller_[Name]_DecisionEngine.json` — Routing logic: input categories, quality gates, cross-tool routing
- `_State_[Name]_SessionMemory.json` — Temporal memory: user profile, session checkpoints, performance tracking

**When to use:** When a gem needs to select and blend different expert personas dynamically based on query type. Overkill for simple advisor gems — the recommendation engine built from this playbook is the appropriate level for most use cases.

**Hard limits:**
- Max 3 active personas per gem (context overhead)
- Max 8 DecisionEngine categories (prevents over-routing)
- Max 5 session checkpoints (anchors exempt from rotation)

---

## 16. Agentic Capability Stack (April 2026)

Four tiers of agentic capability, each requiring different infrastructure:

| Tier | Platform | Agentic Capabilities | Code Required? |
|------|----------|---------------------|---------------|
| **Tier 1: Reasoning-Enhanced Gem** | gemini.google.com | Extended thinking, multi-step reasoning, DecisionEngine routing | No |
| **Tier 2: Opal Workflow Gem** | labs.google/opal | Real tool calling (Search, Maps, Sheets, code), DAG workflows, Agent Step | No — visual builder |
| **Tier 3: ADK/API Gem** | Gemini API + Google ADK | Full function calling, Thought Signatures (mandatory for Gemini 3 multi-step), Computer Use, multi-agent orchestration | Yes — Python/JS/Go |
| **Tier 3b: Edge Gem** | Gemma 4 on-device | All Tier 3 capabilities, fully offline, Apache 2.0 | Yes — Python script |

### Gemma 4 Key Specs (Tier 3b, April 3 2026)

| Model | Effective Params | Context | Min Hardware | Best For |
|-------|-----------------|---------|-------------|---------|
| E2B | 2.3B active | 128K | 4GB RAM | Mobile / IoT |
| E4B | 4.5B active | 128K | 8GB RAM | Mid-range laptop |
| **26B A4B** (recommended) | 4B active / 26B total (MoE) | 256K | 16GB VRAM | Workstation default |
| 31B Dense | 31B | 256K | 24GB VRAM | Best reasoning |

**Practical context limit on consumer hardware:** ~32K tokens (same effective budget as Tier 1) despite the 128–256K window. The gem architecture hard limits apply at all tiers.

**Quick start:** `ollama pull gemma4:27b && ollama serve` — exposes OpenAI-compatible API at `localhost:11434`. Function calling uses standard OpenAI JSON schema format.

### Thought Signatures (Tier 3 — Gemini 3 API)

Thought Signatures are **mandatory** in Gemini 3 API calls with function calling. Omitting the previous turn's thought signature in a multi-step tool chain returns a 400 error. Pass the `thought_signature` field from each response back in the next request's model content parts. Not applicable to consumer gem (Tier 1) or Gemma 4 (Tier 3b).

---

---

## 17. Enterprise Upgrade Path

**Gemini Enterprise** (formerly Google Agentspace, renamed October 9, 2025) is the organizational upgrade path when a gem project outgrows the Drive-based consumer architecture.

**When to consider the enterprise path:**

| Signal | Recommendation |
|--------|---------------|
| Building for an organization, not personal use | Evaluate Gemini Enterprise |
| Data governance, compliance, or audit trail required | Gemini Enterprise mandatory |
| Multiple users need shared agent access | Gemini Enterprise |
| IT security review of AI tools required | Gemini Enterprise |
| Personal advisor gem for one user | Stay on consumer path (this playbook) |
| Small team sharing a Drive folder | Stay on consumer path — the Gem Registry handles this |

**Features relevant to gem builders:**
- **Agent Gallery** — Centralized view of all agents across the enterprise (equivalent to the Gem Registry in T9-10, but organization-managed)
- **Agent Designer** — No-code agent builder with enterprise security controls (similar to Opal but IT-governed)
- **Built-in Deep Research agent** — Enterprise-grounded research equivalent to NotebookLM
- **Chrome Enterprise integration** — Agents surface in the browser as employees work

**Connection to this playbook:** The gem creation methodology (system prompt, memory hub, NotebookLM grounding) is the consumer-path equivalent of what Gemini Enterprise provides at the organizational level. The architecture transfers — your system prompts, memory hub format, and NotebookLM notebooks all remain valid if you migrate to Gemini Enterprise.

---

## 18. Opal Hard Limits (Tier 5/6 Platform Constraints)

Applies to Tier 5 (Harness-Proxy dispatch via Opal) and Tier 6 (Gem from Labs native pipeline). Confidence flags: **Verified** = official Google/Apps Script documentation; **Estimated** = community reports + empirical testing; **Low confidence** = extrapolated, treat as directional only.

| Constraint | Limit | Confidence | Notes |
|---|---|---|---|
| Daily workflow runs — personal account | ~50 / day | Estimated | No official Opal documentation; community reports vary |
| Daily workflow runs — Google Workspace | ~200 / day | Low confidence | Workspace quota unconfirmed; may scale with plan tier |
| Nodes per workflow | No hard cap observed | Low confidence | >30 nodes shows significant latency degradation |
| Tool calls per workflow run | ~100 combined | Estimated | UrlFetch + Sheets + other tools counted together |
| Apps Script daily execution time | 90 minutes | Verified | Official quota; shared across ALL scripts on the account |
| Apps Script UrlFetch calls / day | 20,000 | Verified | Official Apps Script quota |
| Apps Script max execution per run | 6 minutes | Verified | Hard platform limit; long-running tasks must be chunked |
| Sheets append rows / day (via Apps Script) | 20,000 | Verified | Counts toward Sheets service quota; Sheets Memory Bus rows included |
| Gemini Flash preview model stability | Subject to change without notice | Verified | Preview models are volatile; behavioral drift between sessions is expected |

**Practical implications for Tier 5/6 builds:**

- **Apps Script is the tightest bottleneck.** The 90 min/day quota is shared with any other Apps Script automations on the account. High-frequency Harness-Proxy builds can exhaust it by midday.
- **The 6-minute per-run limit** requires chunking long tool chains. Agent Steps that fan out to many UrlFetch calls should be parallelized or batched, not serialized.
- **Flash preview drift** is the primary risk for Tier 6 Full builds. The mandatory 14-day recalibration cycle exists to detect behavioral drift before it silently breaks node instruction assumptions.
- **Node count has no hard cap** — but treat 30 nodes as a soft performance ceiling. Past that, Opal's visual builder and execution latency both degrade.
- **Confidence gaps:** Daily workflow run limits are the least-documented constraint. If a build hits unexpected quota errors, check the Apps Script execution log first (Quota.dailyQuotaExceeded) before assuming an Opal-level limit.

*This document should be updated as Google changes Gems capabilities. Last verified: 2026-04-09 (v2.0 — added §9-16; v2.1 — added §17 Gemini Enterprise; v2.2 — added §18 Opal Hard Limits, Patch A).*
