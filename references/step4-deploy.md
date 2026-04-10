# Step 4: DEPLOY (Standard / Research / Fast Track)

Read state from `_state/step3-validate.json`. All components have been validated by the user.

## Option A: Direct Write (preferred — when Google Drive is mounted locally)

1. Run the **Pre-Write Validation Protocol** (router SKILL.md) — confirm Drive path exists AND run Knowledge folder file count check
2. Write **Knowledge files only** to `[Gem Name] Memory/` folder via Desktop Commander:
   - Memory Hub (`_Memory_[Name]_GemMemoryHub_Active.md`)
   - If tri-file active: PersonaMatrix JSON, DecisionEngine JSON, SessionMemory JSON
3. Create the **Relay folder** as a SIBLING: `[Gem Name] Relay/` at the same directory level as Memory folder. NEVER as a subfolder.
4. Write **Relay files** to the Relay folder:
   - `_Memory_[Name]_GemMemoryHub_Archive.md` — archive storage
   - `_Progress_[Name]_ActiveTask.md` — task tracking (see template below)
   - `_Heuristics_[Name]_Pool.md` — use template from `references/heuristics-pool-template.md`; start empty
   - `_Prompt_[Name]_GemSystemPrompt_v1.0.md` — backup copy of system prompt
5. Confirm files landed: list BOTH Memory and Relay directories after writing
6. **Post-write file count:** Output "Knowledge folder: [N]/10 files ([N] headroom remaining). Relay folder: [N] files (no limit)."
7. **Pre-paste character count check:** Count chars in system prompt. Output: "Your system prompt is [N] characters (limit: 2,500; target ≤ 2,000)." If over 2,500: trim NOW. Trim order: cross-tool routing examples → behavioral rule descriptions → never trim [LOCKED] rules.
8. In Gemini: Create new Gem → paste system prompt into Instructions field
9. **Knowledge source count check:** Standard: 1 folder + 2 NBs = 3 slots. Research: 1 folder + up to 5 NBs = 6 slots. Connect Drive folder first (verify ≤ 6 files inside), then notebooks.
10. Connect the **Memory folder** (NOT Relay) as Knowledge source
11. Connect NotebookLM notebooks — 2 for Standard, up to 5 for Research

> ⚠️ **Knowledge vs Relay:** Memory folder = Memory Hub + tri-file JSONs only. Relay folder = everything else. NEVER attach Relay as Knowledge source.

## File Routing Table (Complete)

| File | Location | Why |
|------|----------|-----|
| Memory Hub (Active) | Knowledge folder | Gemini needs RAG access for session context |
| PersonaMatrix JSON | Knowledge folder | Gemini needs RAG access for persona routing |
| DecisionEngine JSON | Knowledge folder | Gemini needs RAG access for decision routing |
| SessionMemory JSON | Knowledge folder | Gemini needs RAG access for user profile |
| Memory Hub (Archive) | **Relay folder** | Historical only — Claude manages, Gemini never reads |
| Progress file | **Relay folder** | Claude-managed task tracking, not gem context |
| Heuristics Pool | **Relay folder** | Claude-managed optimization data |
| System prompt backup | **Relay folder** | Reference copy — actual prompt is in Gemini UI |
| Infrastructure/Roadmap refs | **Relay folder** | Planning docs, not runtime context |

## Option B: Manual Upload

1. Create Google Drive folder at the path agreed in Step 1
2. Upload all generated files to that folder
3. Same steps 3–11 as Option A

Remind: connecting the folder (not individual files) means any file added later is automatically available.

## Opal Deployment Path (Tier 2 — No Code)

Use Opal when the gem needs real tool calling, automation, or multi-model pipelines.

**When to offer Opal instead of consumer Gem UI:**
- Gem needs live web search on every query, Google Sheets read/write, code execution
- Automated workflow needed (daily briefing, scheduled task)
- Multi-model pipeline required

**Opal quick-start (3-node pipeline):**
1. **Input node** → receives user query + optional context
2. **AI Generation node** → paste gem's 2,500-char system prompt as node instruction
3. **Tool node** → add tools (Search, Drive Read, Sheets, code runner)
4. **AI Generation node (synthesis)** → merges tool output + gem reasoning → final response

**Memory loading in Opal:** Add a Tool node of type "Google Drive — Read File," set to `_Memory_[Name]_GemMemoryHub_Active.md` URL, pipe output as variable into AI Generation node.

> See `references/tool-stack.md` and `references/gemini-gems-specs-and-limits.md` §14 for full Opal specs.

## Progress File Starter Template

```markdown
# [Gem Name] — Active Task Progress

## Current Task
**Goal:** [Set at session start via Sprint Contract]
**Started:** —
**Status:** No active task

## Progress Log
| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| — | — | — | — |

## Blockers
_(none)_

## Next Session: Start Here
_(Updated by Claude relay agent after each [SESSION_SUMMARY] block)_
```

## Gem Health Schedule

At end of deployment, Claude writes a health schedule entry to auto-memory:
```
Name: Gem Health Check — [Gem Name]
Due: [date 30 days from deployment]
Description: Run gem-audit. Check: memory hub size, constraint staleness, system prompt char count, never-recommend drift.
Drive path: [gem memory folder path]
```

## State Output

After Step 4 completes, write `_state/step4-deploy.json`:
```json
{
  "status": "success",
  "timestamp": "[ISO 8601]",
  "files_written": ["prompt → Gemini", "hub → Memory/", "persona → Memory/"],
  "relay_folder_created": true,
  "gemini_knowledge_attached": true,
  "failed_substeps": []
}
```
