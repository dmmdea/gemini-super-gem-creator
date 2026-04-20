# Upgrade Workflow — Major Version Upgrades

Use this workflow when upgrading an existing gem to a new skill version or making structural changes (adding tri-file, restructuring folders, major memory hub overhaul). Runs BEFORE the Quick Update Checklist.

## Phase 1: Pre-Flight Audit

Run BEFORE creating or modifying any files:

```
─── UPGRADE PRE-FLIGHT AUDIT ──────────────────────────
Gem: [Name]
Current version: [X.X.X]
Target version: [X.X.X]

1. Knowledge folder file count:  [N] / 10 max
   └─ Action needed: [none / move N files to Relay]
2. .bak files present:           [N] files, [N] KB
   └─ Action needed: [none / delete — Drive has version history]
3. Subfolders in Knowledge:      [list or "none"]
   └─ Action needed: [none / move to sibling Relay folder]
4. Memory hub size:              [N] KB / [N] chars / [N] lines
   └─ Action needed: [none / compress — see Compression Playbook]
5. System prompt char count:     [N] / 2,500 max
   └─ Action needed: [none / trim to ≤2,000 target]
6. Relay folder exists:          [yes — path / no — will create]
────────────────────────────────────────────────────────
```

Present audit to user before proceeding. Get confirmation.

## Phase 2: Archive Pass

Move resolved/historical content BEFORE adding new files:

1. **Memory hub trimming:** Apply the Compression Playbook (see `references/step2-generate.md` §Compression) to bring active hub within target
2. **Archive resolved items:** Move completed §4 decisions, resolved §7 issues, old §9 changelog to `_Memory_[Name]_GemMemoryHub_Archive.md` in Relay folder
3. **Remove .bak files:** Delete from Knowledge folder. Drive version history is the backup.
4. **Relocate misplaced files:** Move Archive, Progress, Heuristics, prompt backup, and non-essential files from Knowledge to Relay (create Relay if needed)

## Phase 3: File Routing

Ensure correct placement per Relay Folder Architecture (router SKILL.md):

1. **Knowledge folder** (≤ 6 recommended): Memory Hub Active, PersonaMatrix JSON, DecisionEngine JSON, SessionMemory JSON
2. **Relay folder** (no limit): Archive, Progress, Heuristics, prompt backup, infrastructure refs, roadmap
3. **Verify:** `list_directory` on both folders. Output file counts.

## Phase 4: Content Upgrade

Apply the actual version changes:

1. **System prompt upgrade:**
   - Read old prompt from Relay backup (or Gemini UI)
   - Generate new prompt using current skill template
   - Show **diff summary**: "Changed: [list]. Added: [list]. Removed: [list]."
   - Verify ≤ 2,000 chars (≤ 2,500 absolute max)
   - Save backup to Relay, paste into Gemini UI

2. **Memory hub upgrade:**
   - Read current (compressed) hub
   - Apply structural changes (new sections, renamed sections, format changes)
   - Preserve all user-specific content (§2 constraints, §8 never-recommends, §3 state)
   - Increment version in §9

3. **New files** (if upgrade introduces them):
   - Check Knowledge folder count BEFORE writing
   - Route to Knowledge or Relay per file routing rules
   - Never exceed 6 files in Knowledge without explicit user approval

## Phase 5: Budget Verification

```
─── POST-UPGRADE BUDGET CHECK ─────────────────────────
Knowledge folder: [N] / 10 files ([N] headroom)
Knowledge folder total size: [N] KB
Memory hub (active): [N] chars / [ceiling] ceiling
System prompt: [N] / 2,500 chars
Relay folder: [N] files (no limit)
Status: [PASS / FAIL — see issues below]
────────────────────────────────────────────────────────
```

## Phase 6: Deploy & Verify

1. In Gemini: re-attach Memory folder as Knowledge source (forces cache refresh)
2. Paste new system prompt into Instructions field
3. Verify "Processing complete" (no "Couldn't process file" errors)
4. If processing fails: check file count, check for subfolders, reduce and retry
5. Run full 5-test suite (see `references/step5-test.md`)
6. Update Gem Registry entry with new version

## Tier 6 Upgrade Considerations

Before running Phases 1–6 on a Tier 6 (Gem from Labs) gem:

**Check for Opal model version drift first:**
- Compare current Gemini Flash preview version to the version noted in the last
  calibration artifact (`[gem-name]-opal-calibration-[YYYY-MM-DD].md` in Relay)
- If the model version has changed, run a calibration smoke test before editing
  node instructions — avoid patching against drifted baseline behavior

**Re-run calibration after upgrade:**
- After any Phase 4 content changes to node instructions, save a new calibration
  artifact with the upgrade date in the filename
- Reset the 14-day recalibration timer from the upgrade date

**Sheets Memory Bus schema compatibility:**
- New columns must be additive — never rename or remove existing columns
- If schema changes are needed, add new columns and migrate data via a relay session;
  do not break existing row format in the hub Sheet

**Fast→Full upgrade path:**
- If upgrading from Tier 6 Fast to Tier 6 Full, treat it as a full Phase 1–6 upgrade
- Additional deliverables needed: Sheets memory schema, share config, full test plan
  (7/7), calibration run, harness round-trip verification

## Quick Update Checklist (Minor Updates)

Use for adding a constraint, fixing a behavioral rule, updating never-recommend. For major upgrades, use Phases 1–6 above.

1. **Save Before Changing** — Verify Drive version history is active. Add named snapshot comment. **Never create `.bak` files.**
2. **Update System Prompt** — Paste into Gemini UI (Standard/Research/FT) or update script config (Local). Verify char count.
3. **Re-attach Drive Folder** — If memory files changed, remove and re-add in Gem Knowledge panel (forces refresh). Local: no action needed.
4. **Re-attach Grounding Sources** — If notebooks changed, remove and re-add. Local: run `--index` to rebuild RAG.
5. **Run All 5 Tests** — Full suite. Failed test = regression.
6. **Log Re-deployment Decision** — Ask gem for MEMORY_UPDATE block noting what changed and why. Paste into §4.
7. **Check for Constraint Drift** — Compare new never-recommend list against old. Missing items must be re-added.
8. **harness-entry-check (Tier 5/6 only)** — Verify dispatch block is intact in the gem prompt, backend trigger is active (Apps Script trigger enabled / Python script running), and Sheets Memory Bus is reachable (open Sheet, check last row). If any sub-check fails → treat as a Phase 1–6 major upgrade, not a Quick Update.
