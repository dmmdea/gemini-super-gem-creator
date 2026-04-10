# Step 5: TEST

Read state from `_state/step4-deploy.json`. Use `references/test-questions-template.md` for the full validation suite.

## Test Execution

1. **Generate domain-specific test questions** from Step 1 context before testing begins. Present all 5 to the user.
2. **Capture baseline** — ask: "What does the gem currently do well? What does it get wrong?"
3. **Run all 5 tests** — record pass/fail for each
4. **Route failures** using the root-cause table in `test-questions-template.md`. Apply fixes as direct file edits (not MEMORY_UPDATE blocks).
5. **Re-run failed tests only** — repeat until 5/5 pass
6. **Log results** in §8 (Self-Optimization Log) "What to Improve" subsection

> **5/5 pass required** before declaring production ready (6/6 for Local Gem — includes Test 6). Test 5 (MEMORY_UPDATE check) is non-optional in all paths including Fast Track.

## Research Gem Test Calibration

Test 3 (constraint check) should include: "Does the gem correctly cite which notebook a finding came from?" Test 4 becomes cross-notebook synthesis: ask a question requiring info from multiple notebooks and verify integration. Full 5-test suite still applies.

## Local Gem Test Calibration

Tests run via Open WebUI (localhost:3000) instead of Gemini UI.

| Test | Standard/Research | Local Gem |
|------|-------------------|-----------|
| Test 1: Domain knowledge | Query in Gemini | Query via Open WebUI |
| Test 2: Constraint respect | Query in Gemini | Query via Open WebUI |
| Test 3: Source grounding | "Which notebook?" | "Which source directory?" |
| Test 4: Cross-source synthesis | Cross-notebook question | Cross-directory question |
| Test 5: MEMORY_UPDATE | Paste block into conversation | Daemon auto-applies — verify file changed |

**Test 6 (Local Gem only): Inference quality baseline.** Ask a complex domain question requiring multi-step reasoning. Evaluate whether the selected model produces sufficient depth/accuracy. If insufficient, the script's benchmark will have suggested a stronger model. Re-run Test 6 after any model upgrade. Local Gem requires **6/6 pass**.

## Tier 5 — Harness-Proxy Test Calibration

Run after the standard 5-test suite with these additional harness-specific checks:

| Test | Standard check | Harness-Proxy variant |
|------|---------------|----------------------|
| Test 3: Constraint check | Prompt constraint respected | Verify `harness_request` row written with correct `event_type` value |
| Test 4: Cross-source synthesis | Cross-notebook question | Full harness round-trip: `harness_request` written → backend picks up → `harness_result` row confirmed → gem integrates result |
| Test 5: MEMORY_UPDATE | Paste block into conversation | Confirm backend (Apps Script / Python) is processing the queue; verify quota headroom is >15 min remaining |

**Pass threshold:** 5/5 standard tests + harness round-trip pass. If round-trip fails,
treat as Phase 1–6 issue before declaring production ready.

## Tier 6 — Gem from Labs Test Calibration

### Tier 6 Fast — Stateless smoke test (pass threshold: 3/3)

| Test | Check |
|------|-------|
| Smoke 1: Normal input | Node chain executes end-to-end; output matches expected format |
| Smoke 2: Edge case input | Gem handles unusual/boundary input without stub or placeholder node errors |
| Smoke 3: Error/fallback | If a node receives malformed input, graceful fallback fires (no silent failure) |

Tier 6 Fast does not require harness round-trip or memory persistence checks — it is
stateless by design. If User wants cross-session memory → escalate to Tier 6 Full.

### Tier 6 Full — Full calibration suite (pass threshold: 7/7)

| Test | Check |
|------|-------|
| Test 1: Node chain execution | Full workflow runs input → processing → output without stall |
| Test 2: Output format compliance | Every node output matches the format declared in its Agent Step Output Format block |
| Test 3: Constraint enforcement | Gem's persona constraints hold through multi-node pipeline (no constraint bypass) |
| Test 4: Cross-node synthesis | Ask question requiring data from ≥2 nodes; verify integrated output |
| Test 5: Harness round-trip | `harness_request` written → backend picks up → `harness_result` read → gem integrates (if Harness-Proxy is in the pipeline; skip if not) |
| Test 6: Multi-turn memory persistence | Close and reopen the session; verify Sheets Memory Bus state persists and gem correctly reconstructs context from prior rows |
| Test 7: Compaction trigger | Push hub to simulated 80% fill; verify compaction fires and between-session insulation pass executes without data loss |

After all 7 pass: save calibration artifact `[gem-name]-opal-calibration-[YYYY-MM-DD].md`
to Relay folder. This is the baseline for the 14-day recalibration check.

## First-Cycle Reflexion (run after all tests pass)

1. **Evaluate** — Which tests needed fixes? What was the failure pattern?
2. **Reflect** — What does this reveal about the gem's design?
3. **Store** — Log as first entry in §8 "What to Improve"
4. **Condition** — Define the trigger that would cause recurrence
5. **Improve** — If condition identifies a process gap, note for final integration

**Anti-degeneration safeguards:**
- Never remove a Rose (something working) to fix a Thorn — patch additive-first
- Minimum viable patch: change fewest files necessary per failure
- Revert protocol: if a patch causes a new failure, revert and try differently
- Reflexion findings that become permanent → §8 "What Worked Well"; recurring triggers → `_Heuristics_[Name]_Pool.md`

## Skill Self-Optimization (Lessons Log)

After all tests pass (5/5 or 6/6), Claude writes a structured lessons entry to auto-memory:

```
Type: reference
Name: Gem Creation Lessons — [Gem Name] ([Date])
Description: Post-session lessons from creating [Gem Name] in [domain]
---
Gem type: [fast-track / standard / research / local / opal-fast / opal-full]
Domain: [what it advised on]
Tri-file activated: [yes/no] — [reason]
Tier detected: [signals that fired]
Engine: [Gemini / Ollama + model tag]
Harness backend path: [apps_script / local_python / manual / N/A]
Opal sub-mode: [fast / full / N/A]
Calibration run: [pass / not-applicable]
Harness round-trip tested: [yes / no / N/A]
Test failures before pass: [which tests, root cause, fix]
User corrections during validation: [what changed]
Session weight estimate: [light <20K / medium 20–40K / heavy >40K]
Lesson: [one sentence — most non-obvious thing for next time]
```

**Rules:** Only on all-pass. Max 10 lessons in memory; oldest pruned. Read all at session start.

## State Output

After Step 5 completes, write `_state/step5-test.json`:
```json
{
  "status": "success",
  "timestamp": "[ISO 8601]",
  "tests_total": 5,
  "tests_passed": 5,
  "reflexion_needed": false,
  "lessons_logged": true,
  "failed_substeps": []
}
```
