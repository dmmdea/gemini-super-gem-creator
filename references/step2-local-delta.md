# Step 2: GENERATE — Local Gem Delta

> **Load AFTER `step2-generate.md`.** This file contains ONLY Local Gem additions — do not duplicate shared generation logic.

## Hardware Profiling (Infer first, ask only what's missing)

The skill infers hardware from Step 1 context. Only ask what you can't infer:

**Single question (if needed):** "What's your computer like? (e.g., 'laptop, no GPU' / 'desktop, RTX 3060' / 'Mac M2 16GB')"

**Auto-inference rules:**
- "old laptop" / "Chromebook" / "no GPU" → CPU-only, assume ≤8GB RAM
- "laptop" with no GPU mention → CPU-only or integrated GPU, 8–16GB RAM
- "Mac M1/M2/M3/M4" → Unified memory, stated RAM = shared VRAM+RAM
- "RTX 3060" → 12GB VRAM. "RTX 3070" → 8GB. "RTX 4090" → 24GB. (Skill knows common GPUs.)
- RAM but no GPU → CPU-only profile
- "gaming PC" / "desktop" with no specifics → ask the single question

## Inference Engine: Ollama Only

**Ollama is the only supported engine.** No llama-server, no llama.cpp, no GGUF downloads, no speculative decoding.

```bash
curl -fsSL https://ollama.com/install.sh | sh   # Install
ollama pull [MODEL_TAG]                           # Pull model
```

**Escape hatch (advanced users only):** If user already runs a local server (llama-server, LM Studio, vLLM), the script accepts `"inference_url": "http://localhost:8080/v1"`. Mention ONCE as footnote.

## Hardware → Model Ladder (Deterministic Selection)

Walk DOWN this table. First hardware match = recommended model. No choices — one answer per profile.

**Design rule:** Pick the STRONGEST model the hardware can run comfortably (~5+ tok/sec).

| Hardware Profile | Model | `ollama pull` | Download | Speed | Quality |
|---|---|---|---|---|---|
| **CPU-only, ≤4GB RAM** | Gemma 3 270M | `gemma3:270m` | ~150 MB | ~15–20 tok/s | ⭐ Basic |
| **CPU-only, 8GB+ RAM** | Gemma 3 1B-it | `gemma3:1b` | ~600 MB | ~8–12 tok/s | ⭐⭐ Solid |
| **Integrated/NPU/2–4GB VRAM** | Gemma 4 E2B | `gemma4:e2b` | ~900 MB | ~15–25 tok/s | ⭐⭐+ Good |
| **6–8GB VRAM** | Gemma 4 E4B | `gemma4:e4b` | ~1.5 GB | ~15–25 tok/s | ⭐⭐⭐ Strong |
| **8–12GB VRAM, 16GB+ RAM** | Gemma 3 12B-it | `gemma3:12b` | ~7 GB | ~10–15 tok/s | ⭐⭐⭐⭐ High |
| **8GB+ VRAM, 32GB+ RAM** | Gemma 4 26B MoE | `gemma4:27b` | ~10 GB | ~5–10 tok/s | ⭐⭐⭐⭐+ Very High |
| **16GB+ VRAM** | Gemma 4 31B Dense | `gemma4:31b` | ~19 GB | ~6–10 tok/s | ⭐⭐⭐⭐⭐ Frontier |

**MoE note:** MoE models (E2B, E4B, 26B) activate a fraction of params per token. The 26B MoE activates ~4B per pass — Ollama routes inactive experts through system RAM. A 27B model runs on 8GB VRAM with 32GB+ system RAM.

**Apple Silicon:** Unified memory = all RAM available for weights + context. M2 16GB → E4B. M3 Pro 36GB → 31B Dense.

## Full Feature Parity Across All Models

**Critical:** The gem script provides identical memory management, source directory support, health monitoring, and session continuity regardless of Gemma model. Model size affects answer quality — never feature availability.

## Built-In Benchmark (Script-Side, Automatic)

After first launch, the script runs a self-test confirming inference works and suggesting upgrades if hardware supports a stronger model. Never nags — mentions once.

## Local Gem System Prompt Overrides

- No character limit (context-injected, not Gemini UI). Recommend ≤ 4,000 chars for quality.
- Can include richer behavioral rules and routing logic.
- Cross-tool routing references Claude for implementation and local source directories for research (not NotebookLM).

## Local Gem Memory Hub Overrides

- Fill §0–§10 full (same as Standard — 8K target / 15K ceiling). No slot pressure.
- Script injects full hub as context every turn.

## Local Gem Research Setup

Replace NotebookLM with local source directories + optional progressive research stack.

Read `references/local-research-infrastructure.md` for full reference.

### Source Directory Architecture

```
[Gem Memory Folder]/
├── _Prompt_[Name]_GemSystemPrompt_v1.0.md
├── _Memory_[Name]_GemMemoryHub_Active.md
├── sources/
│   ├── core/           # Equivalent to NB1
│   ├── expansion/      # Equivalent to NB2
│   └── [domain-N]/     # No limit unlike cloud tiers
└── research-cache/     # Cached SearXNG/Perplexica results
```

### Progressive Research Stack (Each Layer Independently Optional)

| Layer | What it adds | Setup | Dependency |
|-------|-------------|-------|------------|
| **Layer 0 (DEFAULT)** | Drop files in `sources/` — script reads as raw context | None | None |
| **Layer 1 (OPT-IN)** | SearXNG meta-search | `docker run -d --name searxng -p 8888:8888 searxng/searxng` | Docker |
| **Layer 2 (OPT-IN)** | RAG indexing via Ollama embeddings | `python gem-script.py --index` | Ollama |
| **Layer 3 (OPT-IN)** | Perplexica — AI-synthesized deep research | `docker compose -f perplexica-compose.yml up -d` | Layer 1 + Ollama |

**Frictionless principle:** Never block gem creation on research infra. Layer 0 is default. Layers 1–3 suggested AFTER gem works.

**Research routing:** When gem outputs `[RESEARCH_NEEDED: topic]`, daemon routes through best available: Perplexica → SearXNG → manual fallback.

### Source Directory Construction Plan

Generate research plan targeting local source directories. See `references/meta-prompt-a-research.md` (Local Gem template) and `references/notebook-themes-examples.md` (Local Gem examples).

```
Local Gem Research Plan — [Gem Name]

Source Directory 1: core/
  Theme: [domain-specific]
  Seed Documents: [specific files]
  Research Queries: [SearXNG queries, if Layer 1]
  Expected Sources: [N] documents

Source Directory 2: expansion/
  [same structure]

[Additional directories as needed — no limit]

RAG Configuration (if Layer 2):
  Embedding model: nomic-embed-text (Ollama, auto-pulled)
  Chunk size: 512 tokens / Top-K: 5 chunks per query
```

## Quick-Start Summary

```
Step 1:  curl -fsSL https://ollama.com/install.sh | sh    → Install Ollama
Step 2:  ollama pull [MODEL_TAG]                           → Download model
Step 3:  docker run ... open-webui                         → Chat UI at localhost:3000
Step 4:  python gem-script.py --setup && --daemon          → Memory manager running
```
