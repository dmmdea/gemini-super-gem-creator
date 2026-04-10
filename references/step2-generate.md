# Step 2: GENERATE (Shared Base)

Using Step 1 answers (read from `_state/step1-understand.json`), generate all gem configuration files. Run the **Pre-Write Validation Protocol** (in router SKILL.md) before writing any file to Drive.

## NotebookLM Research Setup (Standard Gem — 2 notebooks)

Generate the 2-notebook research plan using `references/meta-prompt-a-research.md` (Standard path). Create both notebooks at the start. For each:
- **NB1 (Core Domain):** Upload seed documents first (10–30 docs), then run Deep Research (2–3 prompts, ~60 sources each). Target 50–100 curated sources total.
- **NB2 (Expansion):** Same process. Keep themes cleanly separated from NB1.

Source budget per notebook: upload user docs FIRST, then run Deep Research. Stay under 100 total sources per notebook.

## System Prompt (Lean Architecture)

Read `references/meta-prompt-b-config.md` for the template. The prompt contains ONLY:
- Identity and role (2-3 sentences)
- 5-8 behavioral rules (domain-tailored)
- Memory system protocol (file read order)
- Memory update protocol (MEMORY_UPDATE format)
- Cross-tool routing (Claude for implementation, NotebookLM for research)

**What stays OUT of the prompt:** domain specs, hardware, research findings, constraints, roadmap, never-recommend list. All of that lives in the Drive memory files.

**Prompt size targets:** Output ≤ 2,000 chars by default (500 chars headroom below 2,500 hard limit). For complex domains, use compact variant. Include character count check: "[N] / 2,500 chars (target ≤ 2,000)".

## Memory Hub

Read `references/memory-hub-template.md` for the §0–§10 skeleton. Fill ALL sections with specifics from the user's domain. Seed §8 never-recommend from rejected items. Start at version 1.0.0.

**§0 instruction update:** The gem's §0 instructions should tell it to **compress verbose entries** (single-line decisions, compact tables), not just append indefinitely. Include: "When §4 exceeds 7 entries, archive the oldest. When §9 exceeds 10 versions, archive the oldest. Prefer single-line entries over multi-line blocks."

## Memory Hub Compression Playbook

When a memory hub exceeds the archive trigger (12K chars Standard/Local, 8K chars Research) or during an upgrade, apply in order. Each technique is independent — stop when hub is within target.

**Size targets:** Active content ≤ 12K chars (archive trigger). File size ≤ 15KB. Single-line entries preferred.

| Priority | Section | Technique |
|----------|---------|-----------|
| 1 | §4 Decision Log | Archive resolved; keep 5–7 most recent |
| 2 | §7 Open Issues | Remove resolved entirely |
| 3 | §9 Changelog | Compress to 1-line-per-version; keep last 10 |
| 4 | §5 Research | Archive completed; keep only pending |
| 5 | §3 Current State | Compress inventories to single-line-per-tier |
| 6 | §6 Roadmap | Compress sub-tables to inline text |
| 7 | §8 Self-Optimization | Keep "Worked Well" + "To Improve" — archive logs |
| 8 | §10, §11+ | Remove entirely if archived elsewhere |

## Tri-File Cognitive Architecture (Skill-Inferred)

After Step 1 profiling, evaluate these signals to decide whether to propose tri-file:

| Signal | Points toward tri-file |
|--------|----------------------|
| Domain naturally implies 3+ distinct advisor roles (e.g., coach + analyst + critic) | Strong |
| Multiple clearly distinct use modes (strategic planning AND execution review AND technical advisory) | Strong |
| High decision routing complexity — many different question types requiring different response styles | Strong |
| Long-term gem, user expects months of use, wants session continuity across contexts | Medium |
| Single-focus domain, one advisory style, low routing complexity | → memory hub only |

**Decision threshold:** 2+ Strong OR 1 Strong + 2 Medium → propose tri-file:
> "Your gem covers [X] distinct advisory modes — I'll generate a tri-file routing architecture to handle this cleanly. Say 'skip tri-file' to keep it simpler."

No signals met → tri-file is never mentioned. Memory hub + notebooks is the silent default.

**Research Gem override:** More conservative — tri-file only if 3+ Strong signals (5 notebooks already consume significant context).

**Fast Track:** Tri-file is never generated.

Read `references/persona-and-routing-defaults.md` for defaults. Generate three JSON files, presenting each for validation before finalizing:
1. **PersonaMatrix** — Personas, weights, blending rules, interaction modes, accessibility formatting
2. **DecisionEngine** — Input categories, routing rules, quality gates, cross-tool routing
3. **SessionMemory** — User profile, core memories, checkpoint config, performance tracking

**Validation workflow:** Present one component at a time. Show proposed content. Ask for approval or changes. Only advance after confirmation.

## Session Budget Checkpoint

After Step 2 generation is complete and before validation begins, surface a budget estimate:

```
─── Session Budget Check ───────────────────────────────
Estimated tokens consumed so far: ~[N]K
Gem tier: [Fast Track / Standard / Research / Local]
Tri-file: [Active / Not active]
Remaining budget estimate: [comfortable / moderate / tight]

[If "tight"]: "We're at roughly [N]K tokens. I recommend skipping tri-file validation this session — it can be added in a follow-up. Continuing to Step 3."
[If "moderate" or "comfortable"]: Continue normally.
────────────────────────────────────────────────────────
```

**Rough token estimates by tier:**
- Fast Track (no ref reads for notebooks/personas): ~15–20K total
- Standard without tri-file: ~28–32K total
- Standard with tri-file: ~40–48K total
- Research Gem without tri-file: ~35–42K total
- Research Gem with tri-file: ~50–60K total
- Local Gem without tri-file: ~45–55K total
- Local Gem with tri-file: ~60–75K total

## State Output

After Step 2 completes, write `_state/step2-generate.json`:
```json
{
  "status": "success",
  "timestamp": "[ISO 8601]",
  "files_generated": ["prompt.md", "memory-hub.md", "persona.md", "routing.md", "shared-principles.md"],
  "notebooks_generated": ["NB1-theme.md", "NB2-theme.md"],
  "prompt_char_count": 1847,
  "hub_size_kb": 12.4,
  "approved_by_user": true,
  "failed_substeps": []
}
```
