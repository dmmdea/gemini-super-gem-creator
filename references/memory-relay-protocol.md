# Memory Relay Protocol

How to apply MEMORY_UPDATE blocks from a live gem to its Drive files. Run this protocol every time the gem outputs a `[MEMORY_FLAG]` or `[SESSION_SUMMARY]` block.

---

## When to Run This Protocol

Run when ANY of these occur:
- Gem outputs a `[MEMORY_FLAG]` block containing one or more `---MEMORY_UPDATE---` blocks
- Gem outputs a `[SESSION_SUMMARY]` block (contains MEMORY_UPDATE + optional progress log)
- User says "apply this update to my gem files at [Drive path]"
- User says "I talked to [gem name] about X" and describes a state change

---

## Step-by-Step Relay Protocol (T8-A)

**Step 1 — Parse the update block(s)**
Extract each `---MEMORY_UPDATE--- ... ---END_UPDATE---` block from the gem's output. Validate:
- Contains `Section: §N — Name`
- Contains `Action: ADD | MODIFY | ARCHIVE`
- Contains `Content:` with ≤3 bullets, each ≤150 chars
- Contains `Version: X.X.X → Y.Y.Y`
- Total block is ≤500 chars
If validation fails, surface the specific issue to the user before proceeding.

**Step 2 — Conflict detection (T8-C) — run before writing**

For each update block, check:
| Conflict type | Check | Resolution |
|--------------|-------|-----------|
| Duplicate constraint | Is the new §2 content already in the file? | Flag as duplicate — ask user: merge or skip? |
| LOCKED rule modification | Does the update target a `[LOCKED]` behavioral rule? | Safety gate: require explicit user confirmation before applying |
| Version collision | Does the proposed new version already exist in §9? | Auto-resolve: increment one patch level beyond the current file version |
| Archive trigger | Will this update push the active file over 12,000 chars (Standard/Local/Fast Track) or 8,000 chars (Research Gem)? | Trigger archive protocol before writing (see Archive Relay below) |

**Step 3 — RBT pre-classification**

Classify each update before applying:
- 🌹 **Rose** (low risk — apply directly): New §4 decision log entry, new §5/§7 entry, new §10 hypothesis, §9 version bump
- 🌱 **Bud** (medium risk — apply with user note): New heuristic candidate, persona weight proposal, §10 hypothesis graduation to §3, new §6 roadmap item
- 🌵 **Thorn** (high risk — require explicit confirmation): Any change to §2 LOCKED constraints, change to never-recommend list (§8), §10 hypothesis graduation to §2, memory anchor creation

Tell the user the classification before writing Thorns. Example:
> "This update adds a new LOCKED constraint to §2 — that's a 🌵 Thorn (high risk). Confirm to apply, or cancel."

**Step 4 — Apply the update (T8-A surgical edit)**

Using Desktop Commander `edit_block` (or Windows MCP as fallback):
1. Read the relevant section(s) of `_Memory_[Name]_GemMemoryHub_Active.md`
2. Apply only the changed section(s) — never rewrite the full file
3. Increment the version as specified in the MEMORY_UPDATE block
4. Add a changelog entry to §9 (format: `| X.X.X | [Date] | [One-line description] |`)
5. Keep §9 changelog capped at 10 entries — move older entries to the Archive file

**Step 5 — Handle [SESSION_SUMMARY] progress log**

If the triggering block was `[SESSION_SUMMARY]` and contains a progress log entry:
1. Read `_Progress_[Name]_ActiveTask.md`
2. Update: Current Task Goal, Status, Progress Log table, and "Next Session: Start Here" section
3. If the session goal is marked Complete, move the progress log to `_Memory_[Name]_GemMemoryHub_Archive.md` and reset the ActiveTask file to the blank template

**Step 6 — Archive relay (trigger: active file > 12,000 chars Standard/Local/Fast Track, or > 8,000 chars Research Gem)**

If `_Memory_[Name]_GemMemoryHub_Active.md` exceeds its tier's archive threshold after the update:
1. Read `_Memory_[Name]_GemMemoryHub_Archive.md`
2. Move to Archive: completed/resolved §7 items, all §4 decision log entries older than the last 10, §9 changelog entries beyond the last 10
3. Add a datestamp header to each moved block in Archive (e.g., `> Archived: 2026-04-07`)
4. Report to user: "Moved [N] items to Archive. Active hub is now [X] chars."

**Step 7 — Confirm**

Output:
```
✅ Memory relay complete
  Sections updated: [list]
  New version: [X.X.X]
  Active hub size: ~[N] chars ([within/approaching] 8,000 target, [within/approaching] 12,000 archive trigger)
  Conflicts detected: [none / description]
  Archive action: [none / description]
```

---

## Loop Trigger Detection (T8-B)

The gem should output a MEMORY_UPDATE when ANY of the following occurred in the session:

| Trigger | Action |
|---------|--------|
| A decision was made not previously in §4 | ADD to §4 Decision Log |
| A constraint was discovered, modified, or confirmed | ADD/MODIFY §2 (🌵 Thorn — confirm first) |
| A new issue or blocker surfaced | ADD to §7 Known Issues |
| Research findings were discussed | ADD to §5 Research Tracker |
| User explicitly said "remember this" | ADD to most relevant section |
| Roadmap shifted | MODIFY §6 (🌱 Bud — note to user) |
| A §10 hypothesis was confirmed or rejected | MODIFY §10, possibly graduate to §2 or §3 |
| Persona weight pattern emerged (after 10 sessions) | 🌱 Bud — propose weight change |

If the gem didn't output a MEMORY_UPDATE after a session that had decision triggers, ask the user: "Did anything change in this session that should be recorded? I can generate a MEMORY_UPDATE if you describe what happened."

---

## Standalone Relay (User-Initiated)

When the user says: "Apply this MEMORY_UPDATE to my gem files at [Drive path]"

1. Confirm the Drive path is accessible (run `get_file_info` or `list_directory`)
2. Confirm the gem name matches the file naming convention (`_Memory_[Name]_GemMemoryHub_Active.md`)
3. Run the full protocol above (Steps 1–7)
4. If the path is unknown, check Claude's auto-memory for a saved reference entry for this gem's Drive location

---

## File Reference

| File | Purpose | Attach to Gem? |
|------|---------|----------------|
| `_Prompt_[Name]_GemSystemPrompt_v1.0.md` | System prompt | ❌ No (paste into Gemini Instructions field) |
| `_Memory_[Name]_GemMemoryHub_Active.md` | Live memory — all active state | ✅ Yes (via Drive folder) |
| `_Memory_[Name]_GemMemoryHub_Archive.md` | Historical — resolved decisions, old changelog | ❌ No |
| `_Progress_[Name]_ActiveTask.md` | Mid-task continuity — current goal, progress log | ❌ No |
| `_Heuristics_[Name]_Pool.md` | Domain heuristics pool (Claude relay only) | ❌ No |
| `_Core_[Name]_PersonaMatrix.json` | Persona weights, blending rules, evolution tracking | ✅ Yes (via Drive folder) |
| `_Controller_[Name]_DecisionEngine.json` | Routing categories, quality gates | ✅ Yes (via Drive folder) |
| `_State_[Name]_SessionMemory.json` | User profile, checkpoints, anchors | ✅ Yes (via Drive folder) |
| `_Registry_SharedPrinciples.md` | Cross-gem principles (optional, multi-gem only) | ✅ Optional (add if user has 2+ gems) |
| `_Registry_GemInventory.md` | Gem registry at Drive root | ❌ No (Claude reference only) |
