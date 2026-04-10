# Step 3 — Validate

<!-- Load at Step 3 ONLY. Cross-tier — applies to ALL tiers, not Opal-only.
     Phase 1 = universal gates (always run). Phase 2 = tier-specific skeleton
     (run for detected tier only). Phase 3 = matrix cross-check (tier-scaled).
     Decision 4 + Decision 5 locked 2026-04-09. -->

## Overview

Step 3 runs AFTER gem artifact generation (Step 2) and BEFORE deployment (Step 4).
It is a gate, not a suggestion. Any FAIL in Phase 1 or Phase 2 must be resolved
before proceeding. Phase 3 is mandatory for Tier 6 Full; offered for all others.

---

## Phase 1 — Universal Safety Gate

**Run all 5 checks for every tier. Any FAIL = stop, fix, re-check.**

### Check 1 — Hard Limits
- [ ] Prompt ≤2,500 chars (character count, not token count)
- [ ] Prompt ≤2,000 chars target (500-char headroom preserved)
- [ ] Knowledge folder ≤10 files total (subfolders inside Knowledge count toward limit)
- [ ] Recommended: ≤6 Knowledge files to preserve headroom
- [ ] No `.bak` files in Knowledge folder (Drive version history is the backup)
- [ ] Relay folder is a SIBLING of Knowledge folder — not a subfolder inside it
- [ ] Memory Hub ≤15,000 chars (warn User at 12,000 chars to start compaction)
- [ ] Notebooks: ≤2 for Standard gems, ≤5 for Research gems
- [ ] *Skip Knowledge/Relay/Hub sub-checks for Tier 1 — Fast Track (no files)*

### Check 2 — Disappearing-Documents
- [ ] Open Knowledge panel — confirm every attached file is still listed
- [ ] Run the "Update" command on the Knowledge folder before finalizing
- [ ] If any file has silently detached: re-attach, re-run Update, re-validate
- [ ] *Skip for Tier 1 (no Knowledge files attached)*

### Check 3 — Terminology Canonicalization
Auto-fix non-canonical terms in the gem prompt, then notify User of changes:
- [ ] "four pillars" / "4 sections" → **4 Pillars**
- [ ] "persona cluster" / "persona components" / "persona building blocks" → **Persona Primitive Cluster**
- [ ] "analytical brain" / "logic brain" / "reasoning engine" → **Operational Algorithmic Brain**
- [ ] "personality calculator" / "personality blend" / "tone blend" → **Personality Blend Calculator**
- [ ] "info hierarchy" / "information hierarchy" → **Information Hierarchy Principle**
- [ ] "harness pattern" / "proxy pattern" / "tool proxy" → **Harness-Proxy**
- [ ] "fast opal" (in formal design artifacts) → **Tier 6 Fast**
- [ ] "full opal" (in formal design artifacts) → **Tier 6 Full**
- [ ] Confirm no first names appear in any design artifact — use "User" throughout

### Check 4 — Context-Asymmetry Sanity
*(1M-token input window vs. 64K output cap → gems are synthesis engines, not generation engines)*
- [ ] Output format instructions emphasize synthesis and decision-relevance
- [ ] Prompt does NOT instruct the gem to output long raw lists or full documents unprompted
- [ ] Output format leads with the highest-variance, most-discriminating signal first
      (variance-first prompting — Information Hierarchy Principle applied)
- [ ] *Tier 1 is inherently lean — this check passes by default for Fast Track*

### Check 5 — Compaction Readiness
*(Memory-bearing tiers only — Tiers 3, 4, 5, 6 Full)*
- [ ] Memory Hub §0 contains compression instruction: "compress oldest entries, do not just append"
- [ ] Within-session trigger documented: 80% fill → compress in-place
- [ ] Between-session insulation pass documented in Relay or Hub §0
- [ ] Relay folder exists and is accessible to User
- [ ] *Skip for Tiers 1 and 2 (no Memory Hub)*

---

## Phase 2 — Per-Tier Deep-Dive

Run ONLY the skeleton that matches the detected tier. Do not run other tier skeletons.

---

### Tier 1 — Fast Track (3 checks)

- [ ] **T1-1 Router intent lock:** gem Persona pillar declares a single, specific role.
      No hedging, no "I can also help with..." — one clear identity.
- [ ] **T1-2 Prompt-only sufficiency:** prompt is entirely self-contained, ≤1,800 chars.
      No Knowledge files attached. If context requires files → escalate to Tier 2.
- [ ] **T1-3 Frictionless deploy:** zero Knowledge files, zero Relay folder, zero memory setup.
      If any of these exist → re-classify the gem to the appropriate tier.

---

### Tier 2 — Standard (5 checks)

- [ ] **T2-1 Knowledge file count:** ≤6 files in Knowledge folder (hard limit is 10,
      but ≤6 is the operating target)
- [ ] **T2-2 Relay sibling confirmed:** Relay folder exists as sibling, NOT inside Knowledge
- [ ] **T2-3 Memory escalation guard:** if the gem needs to remember User context across
      sessions → escalate to Tier 3 (Memory Gem), do not improvise memory in a Standard build
- [ ] **T2-4 Prompt budget:** ≤2,000 chars target; ≤2,500 chars hard cap; no `.bak` files present
- [ ] **T2-5 No stale references:** prompt does not cite files that are absent from the
      Knowledge folder or that have detached (cross-check against Check 2)

---

### Tier 3 — Memory Gem (6 checks)

- [ ] All Tier 2 checks pass ✓
- [ ] **T3-1 Hub structure:** Memory Hub has §0 with compression instruction; §1+ for content;
      no flat-append-only structure that will bloat without bound
- [ ] **T3-2 Sheets schema (if harness-adjacent or Opal-adjacent):** uuid, parent_uuid,
      timestamp, event_type, role, content, metadata columns present or formally planned
- [ ] **T3-3 Relay populated:** Relay contains at minimum the system prompt backup;
      ideally also heuristics file and archive doc
- [ ] **T3-4 Archive trigger documented:** User knows the 12,000-char (Standard/Local) or
      8,000-char (Research) trigger and the compaction procedure

---

### Tier 4 — Industry Brain / Research Gem (7 checks)

- [ ] All Tier 3 checks pass ✓
- [ ] **T4-1 NB count justified:** each notebook has a stated domain rationale;
      count is ≤2 (Standard) or ≤5 (Research); no redundant notebooks covering the same source
- [ ] **T4-2 Source verification:** spot-check that notebook sources are reachable, current,
      and not returning 404 or access-denied
- [ ] **T4-3 Cross-NB routing:** prompt instructs gem which notebook to query for which
      topic class — explicit routing, not "search all notebooks for everything"

---

### Tier 5 — Harness-Proxy (7 checks; check #7 has 8 sub-items)

- [ ] All Tier 3 checks pass ✓
- [ ] **T5-1 Harness entry:** prompt contains dispatch block instructing gem to write
      `harness_request` rows to Sheets Memory Bus when a tool call is needed
- [ ] **T5-2 Harness return:** prompt contains result-integration rule instructing gem to
      poll for `harness_result` rows and incorporate them before generating its response
- [ ] **T5-3 Tool Protocol block:** all Agent Step instructions contain a Tool Protocol
      block (block 3 of 5-block structure) specifying: tool name, input parameters, parse rule
- [ ] **T5-4 event_type enum extended:** `harness_request` and `harness_result` values
      are declared in the Sheet header or documented in the Relay folder
- [ ] **T5-5 Preview warning logged:** User was shown the preview-model volatility warning
      (Opal is on Flash preview — behavior may change without notice); acknowledgment recorded
- [ ] **T5-6 Backend path declared:** exactly one of the three paths is selected and set up:
      - **Path 1 — Apps Script (default):** container-bound script on Memory Bus Sheet;
        time-driven trigger active; quotas reviewed (90 min/day, 20K calls/day);
        API keys stored in Script Properties (encrypted at rest)
      - **Path 2 — Local Python:** polling script deployed on a persistent machine
        (see `local-gem-script-template.py` → "Harness polling mode" section)
      - **Path 3 — Manual copy-paste:** format documented; User knows the read→execute→paste cycle
- [ ] **T5-7 Full backend setup verified (8 sub-items):**
  - [ ] a. Backend path declared and selected (from T5-6)
  - [ ] b. `event_type` enum extended with `harness_request` + `harness_result` values
  - [ ] c. Dispatch block present in gem prompt (write `harness_request` row)
  - [ ] d. Result-integration rule present in gem prompt (read `harness_result` row)
  - [ ] e. Path-specific setup verified (trigger active / script deployed / format documented)
  - [ ] f. Tool Protocol block present in every Agent Step that calls an external tool
  - [ ] g. Sheets Memory Bus accessible to both the gem (via Knowledge) and the backend (via Drive)
  - [ ] h. harness-entry-check added to the gem's 30-day health check schedule

---

### Tier 6 — Gem from Labs

> **Identify sub-mode first.** Infer from context:
> - Fast triggers: "try", "test", "prototype", "quick", "experiment", "just see if",
>   "minimal", "simple workflow", "no memory needed", "personal use only"
> - Full triggers: "deploy", "publish", "share with team", "production", "save memory",
>   "track over time", "calibrated", "complete"
> - Ambiguous → ask exactly one question:
>   *"Is this a prototype/personal experiment, or a production/team deployment?"*

#### Tier 6 Fast — Stateless prototype (4 checks)

- [ ] **T6F-1 Node instruction compliance:** every Opal node has a 5-block Agent Step
      instruction (Role / Goal / Tool Protocol / Output Format / Edge Cases);
      each instruction is ≤2,500 chars
- [ ] **T6F-2 Stateless guard:** NO Sheets memory referenced anywhere — not in node
      instructions, not in the gem prompt. Fast Opal is deliberately stateless.
      If memory is needed → escalate to Tier 6 Full.
- [ ] **T6F-3 Preview warning displayed:** preview-model volatility warning was shown
      to User before the build began and acknowledged
- [ ] **T6F-4 Smoke test plan:** ≥3 distinct test inputs documented, covering:
      normal/expected input, edge case, and error/fallback case

#### Tier 6 Full — Memory-bearing production (8 checks)

- [ ] **T6L-1 Graph spec doc:** Opal workflow graph is fully documented — all node names,
      connections, conditional branches, and loop boundaries captured in a reference doc
- [ ] **T6L-2 Node instructions complete:** every node has a 5-block Agent Step instruction,
      each ≤2,500 chars; no placeholder or stub nodes present
- [ ] **T6L-3 Sheets memory schema confirmed:** Memory Bus Sheet has all 7 canonical columns:
      `uuid` (STRING), `parent_uuid` (STRING), `timestamp` (DATETIME),
      `event_type` (ENUM), `role` (ENUM: user | agent | harness),
      `content` (TEXT), `metadata` (JSON)
- [ ] **T6L-4 Full test plan:** ≥5 test inputs covering normal flow, harness round-trip,
      compaction trigger, error/fallback path, and multi-turn memory persistence
- [ ] **T6L-5 Share config confirmed:** gem published via "Gem from Labs" mechanism;
      share settings explicit (team access vs. personal-only; link-sharing on/off documented)
- [ ] **T6L-6 Calibration run completed:** smoke run executed against live pipeline;
      artifact `[gem-name]-opal-calibration-[YYYY-MM-DD].md` saved to Relay folder
- [ ] **T6L-7 Preview warning logged:** preview-model volatility warning shown and
      acknowledgment recorded inside the calibration artifact
- [ ] **T6L-8 Disappearing-docs Update command:** "Update" command run on Knowledge panel
      post-publish; outcome documented in the calibration artifact

---

## Phase 3 — Matrix Cross-Check

Fill this table for the gem being validated. A blank cell = a gap to close.

| Deliverable | Present | Correct format | Accessible to User |
|---|:---:|:---:|:---:|
| Gem system prompt | ☐ | ☐ | ☐ |
| Knowledge folder (Tiers 2–6) | ☐ | ☐ | ☐ |
| Relay folder (Tiers 2–6) | ☐ | ☐ | ☐ |
| Memory Hub doc (Tiers 3–6 Full) | ☐ | ☐ | ☐ |
| Sheets Memory Bus (Tiers 5–6 Full) | ☐ | ☐ | ☐ |
| Notebook sources (Tier 4) | ☐ | ☐ | ☐ |
| Graph spec doc (Tier 6 Full) | ☐ | ☐ | ☐ |
| Node instructions (Tier 6) | ☐ | ☐ | ☐ |
| Calibration artifact (Tier 6 Full) | ☐ | ☐ | ☐ |
| Test plan / smoke test | ☐ | ☐ | ☐ |
| harness-entry-check scheduled (Tier 5) | ☐ | N/A | ☐ |

**When to run Phase 3:**

| Tier | Phase 3 |
|---|---|
| Tier 1 Fast Track | Optional — offer if User wants a confidence check |
| Tier 2 Standard | Optional |
| Tier 3 Memory Gem | Optional |
| Tier 4 Industry Brain | Strongly recommended |
| Tier 5 Harness-Proxy | Strongly recommended |
| Tier 6 Fast | Offered, default off (prototyping intent) |
| Tier 6 Full | **Mandatory before sign-off** |

If any cell is unchecked after Phase 3 → identify the relevant Phase 2 check,
fix the gap, then re-run Phase 3 for the affected rows only. Do not restart all
of Phase 3 from scratch.

---

## Validation Sign-Off Block

When all phases pass, paste this block into the build session log:

```
STEP 3 VALIDATION COMPLETE
Date: [YYYY-MM-DD]
Gem name: [gem name]
Tier: [Tier N — name | Tier 6 Fast | Tier 6 Full]
Phase 1 Universal Safety Gate: PASS
Phase 2 Per-Tier Deep-Dive: PASS
Phase 3 Matrix Cross-Check: [PASS | OFFERED-DECLINED | N/A]
Auto-fixes applied: [list any terminology corrections made, or NONE]
Items waived: [list any checks skipped with reason, or NONE]
```

Proceed to Step 4 — Deploy once this block is filled and logged.
