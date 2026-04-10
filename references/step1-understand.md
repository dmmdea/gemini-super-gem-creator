# Step 1: UNDERSTAND

Capture the user's intent through conversation. Infer as much as possible from context.

## Must-Have Answers (ask only what's missing)

1. What domain should the gem advise on? Be specific.
2. What's the user's specific situation? (hardware, constraints, scale, team, etc.)
3. What kind of advice? (strategic, operational, technical, creative)
4. Hard constraints — things the gem must NEVER violate
5. Already tried and rejected — becomes the never-recommend list
6. Communication preferences — how they like to receive advice
7. **Drive setup** — Where is Google Drive mounted locally? (e.g., `D:\My Drive\` on Windows, `~/Google Drive/` on Mac.) What folder path should hold gem files?
8. **Deployment target** — Do NOT ask directly. Local Gem is detected via signals (see below). Only surface if signals are strong enough.

**Infer from context:** proficiency level, role, tools they use, working style.

## User Profile Detection

Infer technical level from Step 1 language — do NOT ask directly. Signals:
- Uses tool names (Desktop Commander, NotebookLM API, JSON schemas, ollama, ADK) → **Technical**
- Uses general descriptions ("AI memory," "smart file," "helper that remembers things") → **Non-technical**
- Mix of both → **Semi-technical**

| Profile | Behavior |
|---------|----------|
| **Technical** | Full hand-holding (always) + context/rationale for decisions, PowerShell/CLI alternatives, raw JSON option offered |
| **Non-technical** | Full hand-holding, plain language, no code; visual cues for Drive/Gemini UI steps (e.g., "Click the ⚙️ icon in Gemini") |
| **Semi-technical** | Full hand-holding + optional technical depth ("Want to see the JSON?") |

> **Rule:** Hand-holding is never removed for any profile. Technical detection ADDS options — it never removes care or steps.

**Persist the profile:** Note the detected profile internally. Use it in all subsequent steps — especially Step 4 DEPLOY and memory relay instructions.

## 6-Tier Gem Architecture

Every gem is one of six tiers, detected below. The Drive folder and memory system are mandatory on Tiers 1–5; Tier 6 uses Opal-native storage.

| Component | Fast Track | Standard Gem | Research Gem | Local Gem |
|-----------|-----------|--------------|--------------|-----------|
| Drive folder (Knowledge slot) | ✅ Always | ✅ Always | ✅ Always | ✅ Always (local mount) |
| Memory hub | §0–§4 starter only | §0–§10 full (8K target / 15K ceiling) | §0–§10 lean (5–6K target / 10K ceiling) | §0–§10 full (8K / 15K) |
| Grounding sources | 0 | 2 NB (NotebookLM) | Up to 5 NB (NotebookLM) | Local source directories (unlimited) |
| Tri-file architecture | ❌ Never | Skill-inferred | Conservative inference only | Skill-inferred (no slot pressure) |
| System prompt budget | ~2,000 chars (inline context) | ≤ 2,000 chars (target; 2,500 max) | ~1,200–1,500 chars | Unconstrained (context-injected) |
| Knowledge slots used | 1 | 3 | 6 | N/A — no Gemini UI |
| Memory relay | Manual → Claude | Manual → Claude | Manual → Claude | Automated (script) |
| Inference engine | Gemini | Gemini | Gemini | Ollama (Gemma family: 270M → 31B) |
| Research capability | None | NotebookLM Deep Research | NotebookLM Deep Research | Local Research (SearXNG, optional) |
| Cost per query | Free | Free | Free | Free (local compute) |
| Privacy | Google servers | Google servers | Google servers | Fully local |
| Offline capable | No | No | No | Yes |

### Tier 5 & Tier 6 — Agentic Extensions

| Component | Tier 5 — Harness-Proxy | Tier 6 Fast — Gem from Labs | Tier 6 Full — Gem from Labs |
|-----------|------------------------|----------------------------|----------------------------|
| Platform | gemini.google.com + Opal dispatch backend | labs.google/opal (native pipeline) | labs.google/opal (native pipeline) |
| Memory | Sheets Memory Bus + Memory Hub | None (stateless) | Sheets Memory Bus |
| Tool calling | Via harness backend (Apps Script / Python / Manual) | Native Opal tool nodes | Native Opal tool nodes + harness |
| Relay | Auto via backend + MEMORY_UPDATE | None | Auto via Opal DAG |
| Knowledge slots | ≤6 (same as Standard) | ≤6 if attached | ≤6 if attached |
| System prompt budget | ≤2,000 chars target / ≤2,500 hard cap | ≤2,000 chars per Agent Step | ≤2,000 chars per Agent Step |
| Inference engine | Gemini (consumer) | Gemini Flash preview (Opal) | Gemini Flash preview (Opal) |
| Code required? | No | No — visual builder | No — visual builder |
| Deliverables | Standard build + dispatch block + harness backend | 4 (node instructions, preview warning, docs-check, smoke test) | 8 (graph spec, node instructions, Sheets schema, test plan, share config, calibration, preview warning, docs-check) |

### Why Local Gem is a full tier, not a deployment variant

1. **Own research infrastructure.** Source directories from local files + optional SearXNG instead of NotebookLM.
2. **Own memory management.** Script reads/writes memory hub directly — no manual relay.
3. **Hardware-adaptive inference.** Runs on anything from CPU-only laptop to workstation GPU.
4. **No Gemini UI constraints.** System prompt injected as full context — no char/slot limits.
5. **Full feature parity at every model size.** Model size affects inference quality, never feature availability.

## Gem Tier Detection

After capturing domain and constraint information, infer the gem tier. Do NOT ask which tier — detect from signals.

### Research Gem Signals

| Signal | Weight |
|--------|--------|
| Domain naturally spans 4–5 distinct research sub-areas | Strong |
| User mentions needing "comprehensive," "deep," or "everything about" | Strong |
| Primary use is research synthesis, not operational advice | Strong |
| User describes needing citations or source-backed answers | Medium |
| Domain is academic, legal, medical, or technical (multi-faceted) | Medium |

**Detection threshold:** 2+ Strong OR 3+ Medium → propose Research Gem:
> "Your domain spans [N] distinct research areas — I'll set this up as a Research Gem with up to 5 notebooks for deep grounding. This keeps the memory system lean to leave budget for the research. Say 'standard' if you'd prefer 2 notebooks with a fuller memory hub."

No Research signals → Standard Gem proceeds silently.

### Local Gem Signals

Local Gem is **completely optional** — never auto-propose unless signals are very strong.

| Signal | Weight |
|--------|--------|
| User explicitly requests local/offline/private deployment | Strong |
| User mentions Ollama, VRAM, local models, or local inference by name | Strong |
| User mentions data sensitivity requiring no cloud | Strong |
| User mentions wanting zero API cost for ongoing use | Medium |
| User already has local inference infrastructure running | Medium |
| User mentions hardware specs (GPU model, VRAM size, RAM) | Medium |

**Detection threshold:** 2+ Strong → propose Local Gem with mandatory warnings. 1 Strong + 2 Medium → mention as option. Medium-only → do NOT propose.

**Proposal wording (when threshold met):**
> "Based on your [privacy requirements / existing infrastructure / hardware], a Local Gem might be the strongest option — fully offline, automated memory, and potentially faster than cloud. This is an advanced path that runs on your own hardware with Ollama. Want to proceed with Local Gem, or would you prefer Standard/Research on Gemini?"

**Mandatory warnings (surface before proceeding with Local Gem):**
```
🖥️ LOCAL GEM — Runs on any computer. We'll set it up for you.

1. SETUP: Install Ollama, pull one Gemma model, start Open WebUI, run gem script. Four commands total.
2. TIME: ~10 minutes. Model download is the longest part (150MB–19GB).
3. HARDWARE: Works on everything. No GPU? Gemma 3 270M/1B runs on pure CPU. Got a GPU? We match the strongest model your hardware supports.
4. FEATURES: Every model size gets the same automated memory, source directories, health monitoring, session continuity.
5. INTERFACE: Chat in Open WebUI at localhost:3000 — looks like ChatGPT.
6. TOKEN USAGE: This session uses more tokens (hardware profiling + script). Worth it for zero-cost, private, unlimited inference.

Continue with Local Gem? (Say 'standard' or 'research' to switch tiers.)
```

### Fast Track Detection

Fast Track ONLY activates when the user explicitly states the gem does not need persistent advanced memory. Qualifying phrases: "this gem doesn't need memory/notebooks," "one-time use," "temporary gem," "no Drive files needed," "no notebooks needed," "just a system prompt, nothing else."

Casual phrasing like "quick," "simple," or "basic" is treated as a style preference — Standard Gem proceeds.

Note at end of Step 1 when Fast Track activates:
> "Fast Track mode confirmed. I'll generate a complete system prompt with constraints and context inline, plus a starter memory hub (§0–§4). No notebooks or tri-file. Your gem will work as a self-contained advisor. Add notebooks or memory expansion anytime in a follow-up session. Test 5 is still required."

### Tier 5 — Harness-Proxy Detection

Harness-Proxy is **optional and offered proactively** — never assumed. Detect from signals, then offer as an add-on to a Standard/Memory Gem build.

| Signal | Weight |
|--------|--------|
| User needs gem to "call an API," "fetch live data," "send an email," "write to a sheet," "run a script" | Strong |
| User describes bidirectional data flow (gem reads AND writes external systems) | Strong |
| User mentions existing Google Sheets or Apps Script infrastructure | Medium |
| Use case requires real-time data the gem cannot hold in Knowledge files | Medium |
| User says "keep it simple," "no backend," or is clearly in early exploration | Negative |

**Detection threshold:** 2+ Strong OR 1 Strong + 2 Medium → offer Harness-Proxy after proposing the base tier.

**Proposal wording (frictionless — state the benefit, not the complexity):**
> "Your gem can also dispatch real tool calls — fetching live data, writing to Sheets, sending emails — through a lightweight Apps Script backend. This is zero-code and uses your existing Google account. Want to include that, or keep it to the gem-only path?"

If User declines → proceed with Standard/Memory Gem, no further mention.
If User accepts → tier becomes Tier 5; load `references/step2-opal-delta.md` at Step 2.

### Tier 6 — Gem from Labs Detection

Gem from Labs is a native Opal pipeline published directly as a gem. Detect from intent signals — **infer sub-mode before asking**.

**Tier 6 Fast signals** (stateless prototype):
"try," "test," "prototype," "quick," "experiment," "just see if," "minimal," "simple workflow," "no memory needed," "personal use only"

**Tier 6 Full signals** (memory-bearing production):
"deploy," "publish," "share with team," "production," "save memory," "track over time," "calibrated," "complete"

**Ambiguous:** ask exactly one question — *"Is this a prototype/personal experiment, or a production/team deployment?"*

**Preview-model volatility warning** — show once before starting any Tier 6 build:
> "Tier 6 runs on Gemini Flash preview inside Opal — behavior and rate limits may change without notice. I'll note this in the calibration artifact. Ready to proceed?"

If User proceeds → load `references/step2-opal-delta.md` at Step 2 (covers both Fast and Full).

### Standard Gem Notebooks

Plan 2 themed notebooks from Step 1 as default. Do NOT ask whether to use NotebookLM — assume yes. The 2-notebook split is always:
- **NB1: Core Domain** — Fundamentals, current operations, known constraints, seed documents
- **NB2: Expansion** — Optimization, alternatives, future planning, edge cases, strategic questions

See `references/notebook-themes-examples.md` for domain examples.

## Elicitation Protocol

If Step 1 answers are thin, apply before moving to Step 2:

**Elicitation triggers:**
- Domain described in < 20 words, or uses generic terms ("AI assistant," "helper," "advisor") → Offer a concrete framing: "It sounds like you want an advisor for [inferred domain] — is that right?" Then ask ONE targeted follow-up.
- No constraints mentioned → Ask: "Is there anything this gem should never suggest — tools you've tried and rejected, or approaches that don't fit your situation?"
- No advice style mentioned → Default to: "Direct and specific. Lead with recommendation, explain trade-offs."

**Rules:** Max 2 clarifying rounds total. Infer the rest from context. Do not ask questions the context already answers.

**Limits reminder (output before transitioning to Step 2 — tier-aware):**
> "Before generating your gem files, here are the constraints for your [tier]: system prompt ≤ [tier-specific] characters (target [tier-specific range] for headroom), memory hub ≤ [tier-specific] characters (target [tier-specific]), [tier-specific grounding], and 32K per-turn context budget. Everything will be built to these limits."

## State Output

After Step 1 completes, write `_state/step1-understand.json`:
```json
{
  "status": "success",
  "timestamp": "[ISO 8601]",
  "tier": "[Fast Track | Standard | Memory Gem | Research | Harness-Proxy | Gem from Labs Fast | Gem from Labs Full]",
  "gem_name": "[inferred or confirmed name]",
  "domain": "[domain description]",
  "profile": "[Technical | Non-technical | Semi-technical]",
  "constraints": ["[constraint 1]", "[constraint 2]"],
  "drive_path": "[full local path to gem memory folder]",
  "notebook_count": 2,
  "harness_backend": "[apps_script | local_python | manual | null]",
  "opal_sub_mode": "[fast | full | null]",
  "failed_substeps": []
}
```
