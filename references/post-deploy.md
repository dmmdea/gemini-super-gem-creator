# Post-Deployment: Memory Loop

The gem outputs MEMORY_UPDATE blocks when state changes. The user relays these to Claude. Claude writes updated files to Drive. Drive syncs. Gem reads updated files next session.

## Canonical MEMORY_UPDATE Format

The gem must output updates in this exact format (defined in `references/meta-prompt-b-config.md`):

```
---MEMORY_UPDATE---
Section: §[number] — [Section name]
Action: ADD | MODIFY | ARCHIVE
Content:
  - [Bullet 1 — what changed and why, max 150 chars]
  - [Bullet 2 — optional]
  - [Bullet 3 — optional]
Version: [current] → [new]
---END_UPDATE---
```

**Rules:** Max 3 bullets per section. Max 500 chars per block. One block per changed section. Never output the full memory hub.

## Activating the Memory Loop

After gem is deployed and tested, Claude activates as the gem's memory manager.

**1. Save gem config to Claude's persistent memory:**

```
Type: reference
Name: [Gem Name] — Drive Location
Description: Drive path and local mount for [Gem Name]'s memory hub
Drive root: [user's local Drive mount]
Gem memory folder: [full local path]
Files: [list all deployed files]
Current version: 1.0.0
Gem tier: [Standard / Research / Fast Track / Local]
Engine: [Gemini / Ollama + model tag]
Gem domain: [what it advises on]
```

Tell the user:
- *Standard/Research/Fast Track:* "Your gem is live. Whenever you paste a MEMORY_UPDATE block from the gem, or tell me about a decision you made with it, I'll update the memory hub directly on Drive."
- *Local Gem:* "Your gem is live. The daemon handles memory updates automatically — no need to paste anything. If you want to manually trigger an update, tell me and I'll write it to Drive."

**2. Watch for these triggers in future conversations:**
- User pastes a `MEMORY_UPDATE` block → parse and apply to memory hub on Drive
- User says "I talked to [gem name] about X" → ask if memory should be updated, then apply
- User says "update the gem's memory" → read current hub, ask what changed, write updates
- *Local Gem:* Daemon applies automatically. Claude shifts to periodic review + manual overrides.

**3. How to apply updates:**

> Full relay protocol (RBT pre-classification, conflict detection, archive trigger, loop detection) in `references/memory-relay-protocol.md`.

Via Desktop Commander (local Drive mount) or Google Drive MCP — use whichever is available:
1. Read current `_Memory_[Name]_GemMemoryHub_Active.md`
2. Apply only changed sections — never rewrite the entire file
3. Increment version: patch (decision/issue) → minor (constraint/roadmap) → major (pivot/phase)
4. Add changelog entry to §9
5. **If from `[SESSION_SUMMARY]`:** also update `_Progress_[Name]_ActiveTask.md`
5b. **Degradation check (passive — every relay):**
   - Hub approaching ceiling → flag with exact size and recommendation
   - Stale constraint (§2 entry >90 days unvalidated) → flag
   - System prompt missing version header → flag
   - *Local Gem additional:* source directory empty, RAG index stale, throughput dropped >20%, model integrity, script version
   - **Frictionless health rule:** Every message includes the exact command to fix it.
6. Check hub size. If approaching archive trigger: move completed items to Archive file
7. Confirm by showing user what changed and new version number

## Gem Registry

After creation, add gem to central registry. Use Drive root from Step 1 for registry location. If `[Drive root]/_Registry_GemInventory.md` doesn't exist, create it:

```markdown
# Gem Inventory
| Gem Name | Domain | Drive Path | Version | Tier | Engine | Last Audit | Status |
|----------|--------|------------|---------|------|--------|------------|--------|
| [Name] | [Domain] | [relative path]/[Name] Memory/ | 1.0.0 | [tier] | [engine] | — | Active |
```

Store registry path in Claude's memory so `gem-audit` and `gem-evolve` can find any gem's files.

**If user has 2+ gems:** Also create `_Registry_SharedPrinciples.md` at Drive root using `references/shared-principles-template.md`. Reference its path in each gem's system prompt.

## Tier 6 — Gem from Labs Post-Deploy

After a Tier 6 (Opal) build deploys, run these steps in addition to the standard
memory loop activation above.

### Immediate post-deploy (both Tier 6 Fast and Full)

- [ ] Confirm gem appears in Gemini under the "Gems from Labs" panel
- [ ] Run smoke test: ≥3 inputs as defined in the test plan (Step 5)
- [ ] Verify preview-model volatility warning was acknowledged and is logged
- [ ] Run "Update" command on Knowledge panel (disappearing-docs check)

### Tier 6 Full — additional steps

- [ ] Open Sheets Memory Bus; confirm all 7 column headers match the schema
  (`uuid`, `parent_uuid`, `timestamp`, `event_type`, `role`, `content`, `metadata`)
- [ ] Run one full harness round-trip: write a `harness_request` row → confirm
  backend picks it up → verify `harness_result` row appears → confirm gem integrates it
- [ ] Save calibration artifact: `[gem-name]-opal-calibration-[YYYY-MM-DD].md` to Relay folder
- [ ] Set a 14-day calendar reminder for first recalibration (see below)
- [ ] Update Gem Registry entry with Opal-specific fields (see registry additions below)

### 14-Day Recalibration (Tier 6 Full only)

Opal preview models can drift in behavior between sessions. At the 14-day mark:

1. Re-run the calibration smoke test (≥3 inputs from the original test plan)
2. Compare throughput and latency to the original calibration artifact
3. If drift detected → update calibration artifact + patch affected node instructions
4. Reset the 14-day timer from the recalibration date

Time estimate: ~15 min if no drift detected; ~45 min if node instructions need patching.

### Gem Registry additions for Tier 6

Extend the registry row with Opal-specific columns:

```markdown
| [Gem Name] | [Domain] | [path] | 1.0.0 | Tier 6 Full | Opal/Flash | [YYYY-MM-DD] | Active |
```

Additional notes to track per Tier 6 entry:
- **Opal sub-mode:** Fast | Full
- **Backend path:** Apps Script | Local Python | Manual | N/A
- **Last calibration:** [YYYY-MM-DD]
- **Next calibration due:** [YYYY-MM-DD + 14 days]
- **harness-entry-check:** ✓ scheduled | N/A (Fast)

## What's Next

| When | Action | Skill |
|------|--------|-------|
| Right now | Run 5-test validation suite | `gem-audit` |
| Right now (Tier 6 Full) | Run calibration + smoke test | Step 5 |
| After 3–5 sessions | Add research grounding if not done | `gem-research` |
| After 5+ sessions | Analyze patterns and patch issues | `gem-evolve` |
| Day 14 (Tier 6 Full) | Recalibration check | post-deploy.md |
| Day 30 (all tiers) | 30-day health check incl. harness-entry-check | `gem-evolve` |
| If behavior needs restructuring | Rebuild persona/routing | `gem-architect` |
