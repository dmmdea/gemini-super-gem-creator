# Step 2: GENERATE — Research Gem Delta

> **Load AFTER `step2-generate.md`.** This file contains ONLY Research Gem additions.

## 5-Notebook Research Plan

Generate the 5-notebook research plan using `references/meta-prompt-a-research.md` (Research Gem path). Partitioned by distinct sub-domain:

- **NB1:** Core Fundamentals & Current State
- **NB2:** Technical Depth & Implementation
- **NB3:** Alternatives & Comparative Research
- **NB4:** Advanced / Emerging Approaches
- **NB5:** Benchmarks, Evaluations & Edge Cases

See `references/notebook-themes-examples.md` (Research Gem section) for domain-specific 5-NB examples. Source budget per notebook: seed docs first, 50–100 total.

## Research Gem Prompt Target

System prompt target: **~1,200–1,500 chars** (vs. Standard's ≤ 2,000). Leaner to leave per-turn budget for 5-NB grounding.

## Research Gem Memory Hub Target

Fill §0–§10 but target **5–6K chars** with a **10K ceiling**. Lean sections to leave per-turn budget for 5-notebook grounding. Archive trigger: **8K chars** (vs. Standard's 12K).

## Research Gem Tri-File Override

More conservative threshold — tri-file only if **3+ Strong signals**, because 5 notebooks already consume significant context.
