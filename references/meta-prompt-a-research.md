# Meta-Prompt A: Research Plan Generator

Generate the research plan between Steps 1 and 2. Notebook architecture depends on gem tier: Standard Gems use 2 themed notebooks; Research Gems use 5 domain-partitioned notebooks.

---

## Notebook Architecture by Gem Tier

### Standard Gem: 2-Notebook Architecture

Every Standard gem gets exactly 2 NotebookLM notebooks. The split is always:

| Notebook | Theme | Content Focus |
|----------|-------|---------------|
| **NB1: Core Domain** | Fundamentals + current state | Domain basics, current operations, known constraints, user's seed documents, primary research |
| **NB2: Expansion** | Growth + future | Optimization, alternatives, future planning, edge cases, strategic questions, emerging approaches |

**Hard limit:** 2 notebooks maximum per Standard gem (Knowledge slot constraint). Do not plan more.

### Research Gem: 5-Notebook Architecture

Research Gems use 5 domain-partitioned NotebookLM notebooks. The split is:

| Notebook | Theme | Content Focus |
|----------|-------|---------------|
| **NB1: Fundamentals** | Core principles + foundations | Foundational theory, domain basics, established best practices, first principles, historical context |
| **NB2: Technical Depth** | Implementation + mechanics | Technical systems, tools, methodologies, hands-on techniques, debugging, optimization |
| **NB3: Alternatives** | Competing approaches + trade-offs | Alternative methods, vendor comparison, trade-off analysis, decision frameworks, known limitations |
| **NB4: Advanced** | Cutting edge + research | Emerging practices, research frontiers, novel approaches, academic findings, future directions |
| **NB5: Benchmarks** | Comparative data + real-world performance | Case studies, performance metrics, cost analysis, ROI comparisons, real-world applications |

**Hard limit:** 5 notebooks maximum per Research gem. Keep each notebook independent; avoid topic overlap.

**Source budget per notebook:** Upload seed documents FIRST (10–30), then run Deep Research (2–3 prompts, ~60 sources each). Target 50–100 curated sources total. Stay under 100 to keep grounding noise low.

See `references/notebook-themes-examples.md` for domain-specific theme examples (2-NB Standard and 5-NB Research).

---

## NotebookLM Tier Limits

### Account-Level Limits (Tier System)

| Tier | Notebooks | Sources/NB | Words/Source | Total Context/NB |
|------|-----------|-----------|-------------|-----------------|
| Free | 100 | 50 | 500K | 25M words |
| Plus | 200–500 | 100–300 | 500K | 50–150M words |
| Ultra | 500 | 600 | 500K | 300M words |

### Gem-Level Source Budgets (Per Notebook)

**Standard Gem (2 notebooks):**
- **Per notebook:** 50–100 curated sources total
- **Allocation:** Upload seed docs FIRST (10–30), then Deep Research (2–3 prompts, ~60 sources each)
- **Total per gem:** ~100–200 sources across both notebooks

**Research Gem (5 notebooks):**
- **Per notebook:** 50–100 curated sources total
- **Allocation:** Upload seed docs FIRST (10–30), then Deep Research (2–3 prompts, ~60 sources each)
- **Total per gem:** ~250–500 sources across all 5 notebooks

**Deep Research source consumption:** Each Deep Research query pulls ~40–60 web sources into the notebook. ~10–15% may be inaccessible. Net: ~40–50 usable sources per query.

**Planning rule:** Upload seed documents FIRST (they consume 1 source each). Then run Deep Research. A notebook with 5 seed docs + 2 Deep Research runs = ~85–105 sources. Monitor total carefully. Keep grounding noise low by staying under 100 sources per notebook.

---

## Knowledge Source Budget Calculator

### Standard Gem

```
Total Knowledge slots available: ~10

Allocated:
  Drive memory folder:     1 slot
  NB1 (Core Domain):       1 slot
  NB2 (Expansion):         1 slot
  ─────────────────────────────────
  Used:                    3 slots
  Remaining:               7 slots

Remaining slots can be used for:
  - Additional reference folders (templates, domain docs)
  - Specialized reference notebooks (future expansion)
  - External data sources (if supported)
```

### Research Gem

```
Total Knowledge slots available: ~10

Allocated:
  Drive memory folder:     1 slot
  NB1 (Fundamentals):      1 slot
  NB2 (Technical Depth):   1 slot
  NB3 (Alternatives):      1 slot
  NB4 (Advanced):          1 slot
  NB5 (Benchmarks):        1 slot
  ─────────────────────────────────
  Used:                    6 slots
  Remaining:               4 slots

Remaining slots can be used for:
  - Additional reference folders (templates, domain docs)
  - Specialized reference notebooks (future expansion)
  - External data sources (if supported)

NOTE: Research Gems consume 6 of ~10 Knowledge slots.
Keep memory hub lean (5–6K target / 10K ceiling) to
preserve per-turn context budget for grounding.
```

---

## Research Plan Templates

### Standard Gem Research Plan

```
I'm creating a Gemini Gem that will serve as an expert advisor for:

**Domain:** [What the gem advises on]
**My situation:** [Specific context — hardware, budget, team, location, etc.]
**What I want the gem to do:** [Kind of advice needed]
**My constraints:** [Hard limits the gem must respect]
**Things I've rejected:** [Optional — becomes never-recommend list]

Based on this, generate a 2-notebook research plan:

**Knowledge Brief** — 1 paragraph: what the gem needs to know across both notebooks

**NB1: Core Domain** — Theme: [specific theme]
  - Source Gathering Checklist: specific documents to upload BEFORE research
  - Deep Research Prompts (2–3): phrased as questions, referencing user's specific constraints
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources

**NB2: Expansion** — Theme: [specific theme]
  - Source Gathering Checklist: specific documents to upload BEFORE research
  - Deep Research Prompts (2–3): future-looking, alternatives, optimization questions
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources
```

### Research Gem Research Plan

```
I'm creating a Research Gem that will serve as a deep-research advisor for:

**Domain:** [What the gem advises on]
**My situation:** [Specific context — hardware, budget, team, location, etc.]
**What I want the gem to do:** [Kind of research-backed advice needed]
**My constraints:** [Hard limits the gem must respect]
**Things I've rejected:** [Optional — becomes never-recommend list]
**Why Research Gem tier:** [Which detection signals fired — e.g., domain spans 4+ sub-areas, primary use is research synthesis]

Based on this, generate a 5-notebook research plan:

**Knowledge Brief** — 1 paragraph: what the gem needs across all 5 notebooks

**NB1: Fundamentals** — Theme: [domain-specific]
  - Source Gathering Checklist: foundational documents to upload BEFORE research
  - Deep Research Prompts (2–3): core principles, established best practices
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources

**NB2: Technical Depth** — Theme: [domain-specific]
  - Source Gathering Checklist: technical references to upload BEFORE research
  - Deep Research Prompts (2–3): implementation details, tools, methodologies
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources

**NB3: Alternatives** — Theme: [domain-specific]
  - Source Gathering Checklist: comparison docs to upload BEFORE research
  - Deep Research Prompts (2–3): competing approaches, trade-off analysis
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources

**NB4: Advanced** — Theme: [domain-specific]
  - Source Gathering Checklist: research papers or emerging docs to upload BEFORE research
  - Deep Research Prompts (2–3): cutting edge, novel approaches, future directions
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources

**NB5: Benchmarks** — Theme: [domain-specific]
  - Source Gathering Checklist: case studies, evaluations to upload BEFORE research
  - Deep Research Prompts (2–3): performance data, ROI, real-world outcomes
  - Source Allocation: [N] seed docs + [2–3] research runs = ~[estimated total] sources
```

---

### Local Gem Research Plan

```
I'm creating a Local Gem that will serve as a fully offline, locally-hosted advisor for:

**Domain:** [What the gem advises on]
**My situation:** [Specific context — hardware, existing infrastructure, team, etc.]
**What I want the gem to do:** [Kind of advice needed]
**My constraints:** [Hard limits the gem must respect]
**Things I've rejected:** [Optional — becomes never-recommend list]
**Hardware profile:** [From Step 2 hardware profiling — e.g., "RTX 3060, 32GB RAM"]
**Selected model:** [From hardware ladder — e.g., "gemma4:27b"]
**Research layers:** [Which optional layers the user wants — e.g., "Layer 0 only" / "Layer 1 + 2" / "All layers"]

Based on this, generate a source directory research plan:

**Knowledge Brief** — 1 paragraph: what the gem needs across all source directories

**Source Directory 1: core/**
  Theme: [domain-specific — fundamentals, current state]
  Seed Documents: [specific files the user should add — be concrete]
  Research Queries: [SearXNG/Perplexica queries to run, if Layer 1+ enabled]
  Expected Sources: [N] documents

**Source Directory 2: expansion/**
  Theme: [domain-specific — growth, alternatives, future]
  Seed Documents: [specific files]
  Research Queries: [queries]
  Expected Sources: [N] documents

**[Additional Source Directories as needed — no limit]**
  Theme: [domain-specific partition]
  Seed Documents: [specific files]
  Research Queries: [queries]
  Expected Sources: [N] documents

RAG Configuration (if Layer 2 enabled):
  Embedding model: nomic-embed-text (via Ollama, auto-pulled)
  Chunk size: 512 tokens (default — adjust for domain)
  Top-K retrieval: 5 chunks per query (default — increase for broad domains)
  Estimated index size: ~[N] chunks across all directories

Research Infrastructure Summary:
  Layer 0: ✅ Manual curation (always active)
  Layer 1: [✅/❌] SearXNG — [status/setup command if needed]
  Layer 2: [✅/❌] RAG indexing — [status/setup command if needed]
  Layer 3: [✅/❌] Perplexica — [status/setup command if needed]
```

---

## Local Gem Knowledge Source Budget

Unlike cloud tiers, Local Gem has no Knowledge slot budget and no notebook limit. The practical constraint is the model's context window and RAG retrieval quality.

```
Source Directories: No hard limit

Practical guidelines:
  - Start with core/ + expansion/ (mirrors Standard's NB1/NB2)
  - Add domain-specific directories as the gem matures
  - Without RAG (Layer 0): keep total sources under ~20 documents
  - With RAG (Layer 2): no practical document limit — index handles retrieval
  - RAG top-K of 5 uses ~2,500 tokens per query — fits easily in context
  - Memory hub + source context + conversation should stay under 32K tokens
    for quality (regardless of model's raw context window)
```

---

## Generation Guidelines

- **Ground every prompt in specifics.** Reference the user's constraints, not generic questions.
- **Tier determines source architecture.** Standard = 2 notebooks (Core + Expansion). Research = 5 notebooks (domain-partitioned). Local = source directories (core/ + expansion/ + unlimited additional). Never mix architectures.
- **Standard: NB1 = current reality, NB2 = future possibility.** Core fundamentals and current constraints first, expansion and alternatives second.
- **Research: each notebook = independent sub-domain.** Minimize overlap. Each notebook should make sense on its own.
- **Local: `core/` + `expansion/` always, then add as needed.** Start with the Standard split, then add domain-specific directories without limit. Name directories descriptively (lowercase, hyphenated).
- **Source gathering = specific documents.** "Monthly P&L for 6 months" not "financial documents."
- **Leave 20–30% headroom** per notebook for future sources (cloud tiers). Local Gem has no headroom concern — directories grow freely.
- **Research prompts = questions.** NotebookLM Deep Research works best with clear questions, not instructions. SearXNG/Perplexica queries also work best as questions.
- **Standard: never plan more than 2 notebooks.** If the domain seems to need 3+, consolidate into cleaner NB1/NB2 themes. The knowledge slot budget requires discipline.
- **Research: never plan more than 5 notebooks.** If the domain seems to need 6+, consolidate. 5 notebooks already consume 5 of ~10 Knowledge slots.
- **Local: plan as many directories as the domain needs.** No consolidation pressure. But keep directories independent and avoid topic overlap.
- **Research Gem memory trade-off.** 5 notebooks consume more Knowledge slots → memory hub must be leaner (5–6K target / 10K ceiling vs Standard's 8K / 15K). Remind the user of this trade-off in the research plan.
- **Local Gem: no memory trade-off.** Full memory hub (8K / 15K) — same as Standard. No slot pressure means memory and source directories coexist freely.
