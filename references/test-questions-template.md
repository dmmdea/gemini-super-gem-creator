# Test Questions Template

After the gem is wired up (Step 5), run the full 5-test validation suite. Follow this sequence every time — before testing, during testing, and after testing.

---

## Before Testing: Generate Domain-Specific Questions

**Claude generates all 5 test questions custom to the user's domain before any testing begins.**

Using the domain, constraints, and never-recommend list captured in Step 1, generate personalized versions of each test below. Present them to the user:
> "Here are your 5 custom test questions — use these exactly when testing your gem."

Then ask: **"What does the gem currently do well? What does it get wrong?"** Log this as the pre-test baseline. After all 5 tests, compare results against baseline to identify regressions and wins.

---

## The 5 Tests

### Test 1: Memory Check
**Purpose:** Verify the gem reads the memory hub at conversation start.

**Template question:** "What do you know about my current situation?"

**What to look for:**
- The gem references specific details from §1 (Identity) and §3 (Current State)
- It does NOT ask you to describe your situation from scratch
- It mentions constraints from §2
- It references the roadmap or current priorities from §6
- It outputs a proper [SESSION_SUMMARY — OPENING] block per the Session Opening Ritual

**Domain examples:**
- AI Deployment: "What hardware am I working with and what's currently deployed?"
- Bakery: "What's my current staffing situation and revenue?"
- Renovation: "What's the current state of my renovation project?"

**If it fails:** The Drive folder may not be properly attached. Check that you attached the FOLDER (not individual files) as a data source in the gem settings.

---

### Test 2: Constraint Check
**Purpose:** Verify the gem respects hard constraints and the never-recommend list.

**Template question:** "Should I try [something from the never-recommend list]?"

**What to look for:**
- The gem firmly declines the suggestion
- It explains WHY (referencing the specific reason from the never-recommend list)
- It suggests an alternative that DOES respect the constraints
- It doesn't waffle or say "well, you could try it..."
- The response begins with [ADVISORY] or [HARNESS_PAUSE] — not just untagged text

**Domain examples:**
- AI Deployment: "What if I tried OpenVINO for model serving?"
- Bakery: "Should I sign up for Uber Eats to expand delivery?"
- Renovation: "Can we remove the wall between the kitchen and living room?"

**If it fails:** The constraint may not be in both places. Add it to the system prompt Behavioral Rules (Pillar 2) AND the Memory Hub §2 and §8.

---

### Test 3: Research Check
**Purpose:** Verify the gem can access and cite NotebookLM research.

**Template question:** "What did our research find about [topic covered by one of the notebooks]?"

**What to look for:**
- The gem references specific findings (numbers, benchmarks, recommendations)
- It attributes information to the research rather than claiming general knowledge
- The findings are accurate to what the notebooks contain
- It can distinguish between NB1 (Core Domain) and NB2 (Expansion) themes

**Domain examples:**
- AI Deployment: "What did NB1 find about VRAM optimization strategies for 8GB GPUs?"
- Bakery: "What did the Core Domain notebook say about food cost percentage targets?"
- Renovation: "What did the Expansion notebook find about future phase planning?"

**If it fails:** Both NotebookLM notebooks may not be properly attached. Verify NB1 and NB2 are both connected as data sources.

---

### Test 4: Advice Check
**Purpose:** Verify the gem gives prioritized, specific advice aligned with the design philosophy.

**Template question:** "What should I work on next?"

**What to look for:**
- The gem references the roadmap/goals (§6) for context
- Recommendations are specific to YOUR situation, not generic
- Advice follows the design philosophy (leads with recommendation, explains trade-offs)
- Priorities are ordered by the criteria you specified (ROI, urgency, etc.)
- The gem considers known issues (§7) when prioritizing
- The response uses the [ADVISORY] type tag

**Domain examples:**
- AI Deployment: "Given my current setup, what's the highest-impact optimization I should tackle?"
- Bakery: "What's the single most impactful change I could make to improve profitability?"
- Renovation: "What should I focus on this week given where the project stands?"

**If it fails:** The system prompt's Pillar 3 (Contextual Grounding) may be too vague. Make the advice philosophy instructions more specific and actionable.

---

### Test 5: Update Check ⚠️ NON-OPTIONAL

> **⚠️ Test 5 is mandatory in all paths — including Fast Track. A gem that doesn't output MEMORY_UPDATE blocks will silently lose all learned context over time. This is the most important test for long-term gem health. Do not skip it.**

**Purpose:** Verify the gem outputs a properly formatted canonical MEMORY_UPDATE block.

**How to test:** Claude generates a real-domain Test 5 scenario from Step 1 context. Example for a marketing gem: "Tell the gem: 'We've decided to stop running Facebook ads — the ROI was negative for 3 months straight.' Then ask: 'What changed in this conversation?'"

The scenario must be a real domain event (a decision, constraint change, or blocker), not a hypothetical.

**What to look for — the gem must output the canonical format:**
```
---MEMORY_UPDATE---
Section: §[number] — [Section name]
Action: ADD | MODIFY | ARCHIVE
Content:
  - [Bullet 1 — what changed and why, max 150 chars]
  - [Optional bullet 2]
Version: [current] → [new]
---END_UPDATE---
```
- Response begins with [MEMORY_FLAG] or [SESSION_SUMMARY] type tag
- Correct delimiters (`---MEMORY_UPDATE---` and `---END_UPDATE---`)
- Section and Action specified
- Max 3 bullets, max 500 chars total
- Only changed sections included (one block per section — not the entire hub)
- Version correctly incremented

**If it fails:** The canonical format in Pillar 4 may be missing or imprecise. Re-inject the exact format from `references/meta-prompt-b-config.md` into the system prompt and re-deploy.

---

## Local Gem Adaptations

> **This section activates ONLY when testing a Local Gem.** Standard and Research Gems use the tests above as-is.

### Tier-Specific Question Variants

| Test | Standard / Research | Local Gem |
|------|---------------------|-----------|
| Test 1: Memory Check | Query the gem in Gemini | Query via Open WebUI (localhost:3000) |
| Test 2: Constraint Check | Query in Gemini | Query via Open WebUI |
| Test 3: Research Check | "Which notebook did this come from?" | "Which source directory did this come from?" |
| Test 4: Advice Check | Cross-notebook synthesis question | Cross-directory synthesis question |
| Test 5: Update Check | Paste MEMORY_UPDATE block into conversation | Daemon auto-applies — verify the memory hub file changed on Drive |

### Test 6: Inference Quality Baseline (Local Gem Only)

> **Local Gem requires 6/6 pass (all standard tests + Test 6) before production ready.**

**Purpose:** Verify the selected model produces sufficient depth and accuracy for the gem's domain.

**How to test:** Ask a complex domain question that requires multi-step reasoning. The question should demand analysis, not just fact retrieval — e.g., "Given [specific situation from §3], compare [option A] vs [option B] considering [constraint from §2] and recommend a path forward with trade-offs."

**What to look for:**
- Response demonstrates genuine multi-step reasoning (not just surface-level summation)
- Domain-specific terminology is used correctly
- Trade-offs are identified and weighed against the user's constraints
- Response depth is comparable to what Gemini would produce for the same question
- Response length is adequate (not truncated or overly terse)

**If it fails:** The model may be too small for the gem's domain complexity. The script's built-in benchmark will have already suggested a stronger model from the hardware ladder. Upgrade the model (`ollama pull [next_model_tag]`), update the script config, and re-run Test 6.

### Local Gem Failure Root-Cause Additions

| Failure type | Root cause | Fix |
|-------------|-----------|-----|
| Model produces shallow or generic answers | Model too small for domain complexity | Upgrade to next model in hardware ladder: `ollama pull [stronger_model]` |
| Source directory not cited | Source directory empty or RAG index not built | Add documents to `sources/` and run `python gem-script.py --index` |
| MEMORY_UPDATE not auto-applied | Daemon not running or parsing error | Check daemon status: `python gem-script.py --status`. Restart: `python gem-script.py --daemon` |
| Slow inference (<3 tok/s) | Model too large for hardware or VRAM contention | Downgrade model or close other GPU-heavy apps. Run `python gem-script.py --benchmark` |
| RAG retrieval misses relevant docs | Index stale or chunk size misconfigured | Rebuild index: `python gem-script.py --index`. Check chunk size in config. |

---

## Failure Root-Cause Routing

When a test fails, route the failure to the correct fix before re-running:

| Failure type | Root cause | Fix |
|-------------|-----------|-----|
| Gem doesn't know situation | Drive folder not attached or RAG miss | Re-attach folder as Knowledge source (folder, not individual files) |
| No [SESSION_SUMMARY — OPENING] | Session ritual rule not in prompt | Verify rule 4 (LOCKED) is present in Pillar 2 |
| Gem recommends rejected items | Not in both prompt AND memory | Add to system prompt rule 2 AND memory hub §2/§8 |
| Generic advice | System prompt Pillar 3 lacks specifics | Rewrite Pillar 3 with specific user context and decision scope |
| No MEMORY_UPDATE output | Canonical format unclear or missing | Re-inject T0-D format + worked example from meta-prompt-b-config.md |
| Wrong research citations | Notebooks not attached | Verify both NB1 + NB2 connected as Knowledge sources |
| Gem ignores philosophy | Pillar 3 too vague | Rewrite with specific, actionable output instructions |
| MEMORY_UPDATE format wrong | Gem not using canonical delimiters | Re-inject Pillar 4 block verbatim — check for truncation |
| No type tag in response | Output Classification block missing | Re-add Pillar 4 Output Classification section to system prompt |
| HITL gate not triggering | Rule 5 (LOCKED) missing or weak | Re-inject HITL Gate rule verbatim from meta-prompt-b-config.md |

---

## Iterative Refinement Loop

**Require a 5/5 pass before declaring the gem "production ready" (6/6 for Local Gem — includes Test 6 inference quality baseline).**

1. Run all 5 tests (6 for Local Gem) → record pass/fail for each
2. Apply all fixes using the root-cause routing table above (direct file edits — not MEMORY_UPDATE blocks)
3. Re-run only the failed tests
4. Repeat until all 5 pass (6 for Local Gem)
5. Log the final test results as the first entry in §8 (Self-Optimization Log) "What to Improve" subsection

**Anti-degeneration rule:** Never remove a passing element to fix a failing test. Fix the failing test in isolation. Revert any patch that causes a new failure, then try a different approach.

---

## Common Issues Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Gem doesn't know your situation | Drive folder not attached | Attach the FOLDER as data source |
| Gem recommends rejected items | Not in both prompt AND memory | Add to system prompt AND memory hub §2/§8 |
| Gem gives generic advice | System prompt Pillar 3 lacks specifics | Add more domain context to Pillar 3 |
| No MEMORY_UPDATE output | Format not clear in Pillar 4 | Reinforce canonical format with exact delimiters |
| Research citations are wrong | Notebooks not attached | Verify both NB1 + NB2 connected |
| Gem ignores design philosophy | Pillar 3 too vague | Rewrite with specific, actionable instructions |
| Memory updates are too long | No section targeting | Add instruction: "Only include changed sections" |
| Gem asks questions already answered | Not reading memory at start | Reinforce "read at START of every conversation" |
| No type tag at start of response | Output Classification block absent | Re-add Pillar 4 Output Classification verbatim |
| [HARNESS_PAUSE] never appears | HITL Gate rule not in prompt | Re-add rule 5 (LOCKED) to Pillar 2 |
