# Agentic Tier Guide

Reference for selecting the right deployment tier when creating or upgrading a gem. Includes the tier map, harness proxy comparison, and error categories for local script deployments.

---

## Tier Selection Map

v7 uses a 6-tier design-complexity model. Tiers are detected from intent signals in Step 1 — never asked directly.

| Tier | Skill Name | Platform | Key capability added | Code? | When to use |
|------|-----------|----------|---------------------|-------|-------------|
| **1** | Fast Track | gemini.google.com | Prompt-only, no files, zero setup | No | Self-contained advisor, immediate start, ≤1,800 char prompt |
| **2** | Standard | gemini.google.com | Knowledge files (≤6), Relay folder | No | Domain advisor needing reference docs or templates |
| **3** | Memory Gem | gemini.google.com | Memory Hub + cross-session state | No | Long-running advisor needing memory that persists across sessions |
| **4** | Industry Brain | gemini.google.com + NotebookLM | NotebookLM grounding (≤5 NB) | No | Research-heavy domain needing citation-backed grounding |
| **5** | Harness-Proxy | gemini.google.com + Opal dispatch | Real tool calls via Sheets Memory Bus (Apps Script / Python / Manual) | No | Gem needs live APIs, Sheets I/O, email, or external compute |
| **6** | Gem from Labs | labs.google/opal (native) | Native Opal DAG pipeline, published as a Gem from Labs | No | Full agentic pipeline; Fast sub-mode for prototyping, Full for team deployment |

> **Local Gem (Ollama):** Orthogonal to the 6 tiers above — it's an inference-layer choice (local vs. cloud), not a design tier. Any tier 1–4 gem can be re-targeted to Local. See Gemma hardware ladder below.

> **ADK/API (Tier 3 in legacy guide):** Enterprise/API path. Still valid for multi-gem orchestration and Vertex AI deployments. Not part of the 6 consumer tiers. See `references/gemini-gems-specs-and-limits.md` §16.

**Decision flowchart:**
```
Need real tools (APIs, Sheets, email, code execution)?
  → Yes →
    Full native Opal pipeline?  → Yes → Tier 6 (Gem from Labs)
    Dispatch via backend sufficient?  → Yes → Tier 5 (Harness-Proxy)
  ↓ No
Need deep research grounding (NotebookLM)?  → Yes → Tier 4 (Industry Brain)
  ↓ No
Need cross-session memory?  → Yes → Tier 3 (Memory Gem)
  ↓ No
Need reference Knowledge files?  → Yes → Tier 2 (Standard)
  ↓ No
→ Tier 1 (Fast Track) — start here always
```

---

## Gemma Family Hardware → Model Ladder (Tier 4)

The skill walks DOWN this table. First hardware match = recommended model. No choices, no "or" — one answer per profile. The skill picks the STRONGEST model the user's hardware can run comfortably (~5+ tok/sec).

| Hardware Profile | Model | `ollama pull` | Download | Speed (approx) | Quality |
|---|---|---|---|---|---|
| **CPU-only, ≤4GB RAM** (old laptop, Chromebook, thin client) | Gemma 3 270M | `ollama pull gemma3:270m` | ~150 MB | ~15–20 tok/s | ⭐ Basic |
| **CPU-only, 8GB+ RAM** (modern laptop, no dedicated GPU) | Gemma 3 1B-it | `ollama pull gemma3:1b` | ~600 MB | ~8–12 tok/s | ⭐⭐ Solid |
| **Integrated GPU / NPU / 2–4GB VRAM** (Intel Arc, Apple M-series 8GB) | Gemma 4 E2B | `ollama pull gemma4:e2b` | ~900 MB | ~15–25 tok/s | ⭐⭐+ Good |
| **6–8GB VRAM** (RTX 3060 Ti, RTX 3070, RTX 4060, Apple M-series 16GB) | Gemma 4 E4B | `ollama pull gemma4:e4b` | ~1.5 GB | ~15–25 tok/s | ⭐⭐⭐ Strong |
| **8–12GB VRAM, 16GB+ RAM** (RTX 3060 12GB, RTX 4070, Apple M-series 18–24GB) | Gemma 3 12B-it | `ollama pull gemma3:12b` | ~7 GB | ~10–15 tok/s | ⭐⭐⭐⭐ High |
| **8GB+ VRAM, 32GB+ RAM** (RTX 3070+, any 8GB+ GPU with ample system RAM) | Gemma 4 26B MoE | `ollama pull gemma4:27b` | ~10 GB | ~5–10 tok/s | ⭐⭐⭐⭐+ Very High |
| **16GB+ VRAM** (RTX 4080/4090, A6000, Apple M-series 32GB+) | Gemma 4 31B Dense | `ollama pull gemma4:31b` | ~19 GB | ~6–10 tok/s | ⭐⭐⭐⭐⭐ Frontier |

**Why MoE models work on modest hardware:** Mixture-of-Experts models (E2B, E4B, 26B) only activate a fraction of their parameters per token. The 26B MoE activates ~4B parameters per forward pass — Ollama routes inactive experts through system RAM while keeping active layers on GPU.

**Apple Silicon note:** Macs with unified memory treat all RAM as available for both model weights and context. M2 16GB → Gemma 4 E4B. M3 Pro 36GB → Gemma 4 31B Dense.

**Practical context limit:** Despite 128–256K model windows, consumer hardware inference quality degrades past ~32K tokens. The same hard limits from the gem architecture apply at all tiers.

**Quick start (4 commands):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull [MODEL_TAG]
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
python gem-script.py --setup && python gem-script.py --daemon
```

---

## Harness-Proxy — Tier 5 vs. Tier 6 Comparison

Both Tier 5 and Tier 6 add real tool execution to a gem. The key distinction is where the dispatch happens and how much of the pipeline is native to Opal.

| Harness Component | Tier 5 — Harness-Proxy | Tier 6 — Gem from Labs |
|------------------|------------------------|------------------------|
| Dispatch mechanism | Gem writes `harness_request` row → backend polls Sheets → writes `harness_result` | Opal node calls tool natively (no Sheets round-trip) |
| Backend | Apps Script / Local Python / Manual (User choice) | Opal DAG built-in tool nodes |
| Memory | Sheets Memory Bus + Memory Hub (same as Tier 3) | Sheets Memory Bus (Full) / None (Fast) |
| Latency | ~10–60s round-trip (Apps Script poll interval) | Near-realtime (native node execution) |
| Setup complexity | Low — Apps Script + one Sheet | Low — visual Opal builder |
| Tool extensibility | High — any UrlFetch target, any Apps Script tool | Constrained to Opal's available nodes |
| Offline capable | Partial (Local Python path) | No (Opal is cloud-only) |
| Preview model risk | Low (gem is Gemini consumer, stable) | High (Opal runs Flash preview — volatile) |
| Code required? | No | No |
| When to use | Gem needs external APIs but User wants to stay in Gemini UI | User wants a fully native Opal pipeline published as a gem |

**Key insight:** Tier 5 keeps the gem in the familiar Gemini consumer UI and adds tool power via a dispatch layer. Tier 6 moves the entire workflow into Opal — more seamless, but dependent on preview model stability. Offer Tier 5 first; escalate to Tier 6 when User explicitly wants a native Opal gem.

### Tier 5 Harness Backends (3 paths)

| Path | Infrastructure | Best For | Limits |
|------|---------------|---------- |--------|
| **Path 1 — Apps Script** (default) | Container-bound script on Memory Bus Sheet, time-driven trigger | API calls, Gmail, Drive, Calendar, Sheets, Gemini API | 90 min/day execution, 20K UrlFetch/day, 6 min/run |
| **Path 2 — Local Python** | Persistent polling script on User's machine | Local compute, Zora/Ollama, local filesystem, code execution | Machine must stay on while gem is active |
| **Path 3 — Manual** | User reads `harness_request` rows, executes manually, pastes result | Zero infrastructure, any environment | Slowest; only for low-frequency tool calls |

---

## Error Categories (Tier 4 — Local Script)

Four-category error handling schema for `local-gem-script-template.py`. These mirror the harness anatomy from the research literature.

| Category | Examples | Recovery Action | Script Behavior |
|----------|---------|----------------|----------------|
| **Transient** | Tool timeout, network failure, file locked | Retry with exponential backoff | Max 3 retries, 2/4/8s wait; escalates to Fatal if all retries fail |
| **LLM-recoverable** | Hallucinated tool arg name, wrong JSON format | Return error as context: "That call failed: [reason]. Try again." | Injects error as tool result, retries in same turn |
| **User-fixable** | Missing file, wrong path, permission denied | Output `[HARNESS_PAUSE]` with specific problem + what to fix | Prints to terminal, waits for CONFIRM or CANCEL |
| **Fatal** | Loop detected (3+ same calls), context overflow, unrecognized output | Save state to progress file, exit with resume instructions | Writes progress file, prints resume instructions, raises SystemExit(1) |

**Loop detection:** If the same tool name + arguments appears 3+ consecutive times in `tool_call_history`, the script raises `FatalError` with: "I've tried [action] 3 times without progress. Here's what I know: [state]. What should I do differently?"

**Context overflow recovery (T11-7):** At 24K tokens (75% of 32K limit), the script automatically:
1. Requests a `[SESSION_SUMMARY]` from the model
2. Saves the summary to `_Progress_[Name]_ActiveTask.md`
3. Resets `messages` to `[system_prompt + memory_hub + session_summary]`
4. Continues the loop — user never sees the reset

---

## Cross-Tier Architecture Notes

### Shared Architecture (all tiers)
- System prompt structure: 4-pillar, ≤2,500 chars (cloud tiers) or unconstrained (Local Gem, recommend ≤4,000)
- Memory hub: `_Memory_[Name]_GemMemoryHub_Active.md` — same format, same §0-§9 structure at all tiers
- Hard limits: 2 notebooks max (Standard), up to 5 (Research), unlimited source directories (Local) — see Hard Limits table in SKILL.md
- MEMORY_UPDATE format: canonical delimited block — relayed via Claude (Tier 1/2) or auto-applied by script (Tier 4)

### Key Differences by Tier

| Aspect | Tier 1 Fast Track | Tier 2 Standard | Tier 3 Memory Gem | Tier 4 Industry Brain | Tier 5 Harness-Proxy | Tier 6 Gem from Labs |
|--------|------------------|-----------------|-------------------|-----------------------|----------------------|----------------------|
| Memory loading | None | RAG from Drive Knowledge | RAG + Memory Hub | RAG + Memory Hub + NB grounding | Sheets Memory Bus + Hub | Sheets Memory Bus (Full) / None (Fast) |
| Memory relay | None | Manual → Claude | Manual → Claude | Manual → Claude | Auto via harness backend | Auto via Opal DAG |
| Tool calling | None | None | None | None (research only) | Via harness dispatch | Native Opal nodes |
| Research | None | NotebookLM (2 NB) | NotebookLM (2 NB) | NotebookLM (≤5 NB) | NotebookLM (≤5 NB) | Opal tool nodes |
| Offline | No | No | No | No | Partial (Local Python) | No |
| Privacy | Google servers | Google servers | Google servers | Google servers | Google + backend | Google (Opal) |
| Setup time | Zero | ~20 min | ~30 min | ~45 min | ~45–60 min | ~30 min (Fast) / ~90 min (Full) |
| Preview risk | None | None | None | None | None (gem) + Low (Opal dispatch) | High (Flash preview) |

### Upgrade Path

```
Tier 1 (Fast Track) → Tier 2 (Standard) → Tier 3 (Memory Gem)
  → Tier 4 (Industry Brain) → Tier 5 (Harness-Proxy) → Tier 6 (Gem from Labs)
```

Each upgrade adds capability without breaking the gem's Memory Hub or system prompt — the 4 Pillars architecture and memory format transfer at every step. Local Gem (Ollama) can be applied at any tier 1–4 as an inference-layer choice.

Each upgrade adds capability without breaking the gem's memory hub or system prompt — the architecture transfers.
