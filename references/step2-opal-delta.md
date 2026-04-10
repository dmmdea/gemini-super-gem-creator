# Step 2: GENERATE — Opal Delta

Load this AFTER `step2-generate.md` when tier == "Opal". Replaces gem-specific generation (system prompt, memory hub, tri-file) with Opal-specific artifacts.

> **Read on demand:** Node Catalog and Canonical Sheets Memory Bus Schema are embedded in this file (§ Node Catalog, § Canonical Sheets Memory Bus Schema below). No additional reference files required.

## Opal Build Principles

1. **Smallest graph that works.** v1 ≤ 8 nodes. Don't prematurely branch — use Agent Step for anything resembling "maybe do X, maybe do Y".
2. **Memory lives in Sheets, not prompts.** Never duplicate state in node instructions. Prompts reference the Sheet as ground truth.
3. **One Agent Step per purpose.** If you have two distinct jobs (e.g., research + draft), use two Agent Steps chained, not one monster instruction block.
4. **Every Output node is reviewable.** Debug console first, then scheduled/shared.
5. **PTCF per Generate/Agent node** — Persona, Task, Context, Format. Same discipline as a gem system prompt.
6. **@ references are load-bearing.** Use `@stepName` and `@toolName` to keep prompts dry and self-updating when graph changes.
7. **Opal is a synthesis engine, not a generation engine.** Flash context window: 1M tokens input / 64K tokens output. Design every graph to AGGREGATE upstream data and COMPRESS it into a focused output — never ask a node to generate content from scratch when upstream nodes can supply grounding.

## Opal Tier Decision Tree

Before generating anything, walk the decision tree with the user's answers:

1. **Does the workflow need to remember state across runs?**
   - Yes → Sheets memory tab is mandatory (see § Canonical Sheets Memory Bus Schema below)
   - No → Stateless pipeline; skip memory section
2. **Does the workflow need to decide between paths at runtime?**
   - Yes, complex → Use **Agent Step** (dynamic routing)
   - Yes, simple (2–3 fixed branches) → Use graph edges + conditional text
   - No → Linear chain of Generate nodes
3. **Does the workflow call external services (Search, Drive, Sheets, Docs)?**
   - Yes → Add Tool nodes; enable them on the Agent Step if routing is dynamic
   - No → Pure Generate nodes
4. **Is the output a single artifact or a batch?**
   - Single → One Output node, one destination
   - Batch → Loop via Agent Step with termination condition OR use a For-Each pattern over a Sheets range
5. **Who will run this?**
   - Just the user → Keep in labs.google/opal workspace; no publish
   - Team/public → Generate share config + gallery metadata

## Artifacts Generated (Opal Tier)

| Artifact | Location | Purpose |
|---|---|---|
| `_Opal_[Name]_GraphSpec.md` | Relay folder | Human-readable graph spec: node list, edges, data flow |
| `_Opal_[Name]_NodeInstructions.md` | Relay folder | Exact text for each Generate/Agent Step — copy-paste ready |
| `_Sheets_[Name]_MemorySchema.md` | Relay folder | Google Sheets tab definitions, columns, sample rows, read/write patterns |
| `_Opal_[Name]_TestPlan.md` | Relay folder | 5–6 test scenarios matching `step5-test.md` |
| `_Opal_[Name]_ShareConfig.md` | Relay folder | Share/publish config (only if shared/published) |

No Knowledge folder is created unless a companion gem exists (Harness-Proxy layer).

## Generation Order

1. **Workflow goal statement** (1 sentence)
2. **Node graph** — text diagram; use ASCII or a numbered list
3. **Sheets memory schema** — only if state is needed
4. **Node instructions** — one PTCF block per Generate/Agent node
5. **Output layout** — which destination, which fields
6. **Test plan** — 5 test scenarios (see `step5-test.md`)
7. **Share config** — only if user wants to publish

## Node Graph Template

Use this structure for `_Opal_[Name]_GraphSpec.md`:

```markdown
# [Opal Name] — Graph Specification

## Goal
[One sentence: what this workflow does end-to-end]

## Nodes
1. **input_query** (User Input, type: text) — entry point
2. **fetch_memory** (Tool: Sheets Read) — loads state from `[Sheet].[Tab]`
3. **planner** (Agent Step, Gemini 3 Flash) — decides which branch to take; tools enabled: Search, Drive Read
4. **generator** (Generate) — drafts the output using `@planner` and `@fetch_memory`
5. **reviewer** (Generate) — QA pass on `@generator`
6. **save_state** (Tool: Sheets Append) — logs run to `[Sheet].[Tab]`
7. **output_doc** (Output: Google Doc) — final deliverable

## Edges
input_query → fetch_memory → planner → generator → reviewer → save_state → output_doc

## Data Flow
- Sheet `[Name] Memory`, tab `runs`: append-only log
- Sheet `[Name] Memory`, tab `state`: upsert (one row keyed by session_id)
- Generate nodes reference upstream via @stepName
```

## Node Instructions Template

Use this structure for `_Opal_[Name]_NodeInstructions.md`:

```markdown
# [Opal Name] — Node Instructions (v1.0)

## Global conventions
- All prompts follow PTCF (Persona, Task, Context, Format)
- Never invent data; if Sheets read returns empty, say so and halt
- Output language: [English/Spanish/user's default]

---

## Node 3: planner (Agent Step, Gemini 3 Flash)
**Persona:** You are a planning agent for [domain]. You route work to the right tool.
**Task:** Decide whether this query needs [path A], [path B], or [path C]. Execute the chosen path using available tools.
**Context:** User query = @input_query. Prior state = @fetch_memory.
**Format:** Return a JSON block: {"path": "A|B|C", "reason": "...", "payload": {...}}
**Tools enabled:** Google Search, Drive Read, Sheets Read
**Termination:** Stop after producing the JSON. Do not chain further tool calls.
**Never:** [list items from §8 never-recommend]

---

## Node 4: generator (Generate)
**Persona:** ...
**Task:** ...
**Context:** Use @planner.payload and @fetch_memory.
**Format:** ...

[Repeat for each Generate/Agent node]
```

## Sheets Memory Schema Template

Minimum schema for a stateful Opal. Full canonical schema in § Canonical Sheets Memory Bus Schema below.

```markdown
# [Opal Name] — Sheets Memory Schema (v1.0)

## Sheet: "[Name] Memory"
Drive path: D:\My Drive\AI Ecosystem\Opal\[Name]\[Name] Memory.gsheet
Share: private to [user account]

### Tab: `state` (upsert keyed by session_id)
| session_id | last_run_at | last_query | last_result_url | status | notes |
|---|---|---|---|---|---|
| text | ISO 8601 | text | url | enum(idle,running,error) | text |

### Tab: `runs` (append-only log)
| run_id | timestamp | input | output_url | tokens_used | success |
|---|---|---|---|---|---|
| uuid | ISO 8601 | text | url | int | bool |

### Tab: `never_recommend` (read-only constraints)
| item | reason | added_at |
|---|---|---|
| text | text | ISO 8601 |

### Read patterns
- `state`: read latest row where session_id = [current]
- `runs`: read last 10 rows for context
- `never_recommend`: read all rows at start of each run; inject as constraints into the planner node

### Write patterns
- `state`: upsert on every run completion
- `runs`: append at end of every run (success or failure)
- `never_recommend`: manual edits only; do NOT write from the graph
```

## Opal System Prompt Equivalent

Opal doesn't have a single system prompt. The equivalent is the **Agent Step instruction block** (if Agent Step is used) OR the **first Generate node's prompt**. Character budget: ≤ 2,500 chars, target ≤ 1,800. Same PTCF discipline as a gem system prompt.

**What stays IN the node instructions:**
- Persona and role
- Hard constraints and never-recommend items
- Format requirements
- @-references to upstream nodes

**What stays OUT of node instructions:**
- Mutable state (goes in Sheets)
- Long domain knowledge (goes in uploaded files via User Input file node, or Drive Read)
- Research findings (goes in Sheets or linked Docs)

## Agent Step — When and How

Agent Step was introduced with Gemini 3 Flash (Feb 2026). Use it when:

- The next step depends on the content of the previous step in ways you can't pre-wire with edges
- The workflow needs to call tools in a sequence determined at runtime
- You want the agent to loop until a condition is met (e.g., "keep searching until you find 3 sources that meet criteria X")

**Agent Step instruction format (5-block):**

<!-- Gemini 3 Flash is highly directive: short imperative instructions outperform verbose explanations. Keep each block ≤ 3 sentences. -->

```
## Role
[1–2 sentence role statement. State what kind of agent this is and what domain it operates in.]

## Goal
[The single objective the agent must accomplish before terminating. Be concrete. "Do X until condition Y" is better than "help with X."]

## Tool Protocol
[List only the tools enabled on this node. One line each: when to call it and what to pass.]
- Google Search: call when [condition]; pass the exact query string
- Sheets Read: call at start of each run; pass tab name + key column value
- [Add or remove tools to match the node's enabled tools exactly]

## Output Format
[Exact output structure. Prefer JSON with a defined schema.]
{"status": "done|error", "path": "A|B|C", "payload": {...}, "termination_reason": "..."}

## Edge Cases
- If Sheets read returns empty: halt; output {"status":"error","reason":"empty_state"}
- If the same tool + args appears 3× consecutively: halt; output {"status":"error","reason":"tool_loop"}
- Never: [items from gem's §8 never-recommend list]
```

**Budget:** 1,500 chars target / 2,500 chars hard cap. Count characters before committing.  
**Loop safety:** Always set explicit termination condition AND max-tool-call limit (default 10). An Agent Step without a termination condition can exhaust the daily run quota in minutes.

## @ Reference Discipline

- Use `@nodeName` to reference upstream node outputs; use `@toolName.field` for structured tool outputs.
- Rename nodes BEFORE writing instructions — renaming later updates the @ references automatically, but only within the same graph session.
- If a Generate node needs data from two upstream nodes, reference both explicitly rather than asking the model to "use previous context".

## Fast Opal Sub-Mode (Tier 6 Fast)

Tier 6 Fast is a stateless prototype pipeline. Apply this sub-mode when User signals are: "try", "test", "prototype", "quick", "experiment", "minimal", "personal use only", "no memory needed".

**Differences from Tier 6 Full:**

| Aspect | Tier 6 Fast | Tier 6 Full |
|---|---|---|
| Memory | None — no Sheets connector | Sheets Memory Bus (all 3 tabs) |
| Node count | ≤ 5 nodes | ≤ 8 nodes |
| Artifacts generated | 4 (node instructions, preview warning, docs-check, smoke test) | 8 (graph spec, node instructions, Sheets schema, test plan, share config, calibration, preview warning, docs-check) |
| Sheets schema | Skip | Generate in full |
| Calibration | Skip | 14-day cycle (see post-deploy.md) |
| Test plan | 3 smoke tests | 5–6 test scenarios (see step5-test.md) |
| Share / publish | User's own workspace only | Gallery-ready (optional) |

**Fast-mode generation checklist:**
- [ ] ≤ 5 nodes; no Sheets tool nodes
- [ ] One Agent Step max (if routing is needed); else pure Generate chain
- [ ] Node instructions only — skip graph spec, Sheets schema, share config
- [ ] Smoke test table: 3 inputs × expected output (pass/fail)
- [ ] Preview-model warning block (show once at start of deploy)
- [ ] Docs-check: confirm step4-opal-deploy.md Fast shortcut section applies

---

## Canonical Sheets Memory Bus Schema

This is the authoritative schema for all Tier 5 and Tier 6 Full memory Sheets. Do NOT invent column names or tab names — use this exactly.

### Tab: `bus` (Harness dispatch channel — Tier 5 only)

| Column | Type | Notes |
|---|---|---|
| `uuid` | text (UUID v4) | Unique row identifier |
| `parent_uuid` | text or blank | Links result row back to its request row |
| `timestamp` | ISO 8601 | UTC; set by writer |
| `event_type` | enum | See event_type enum below |
| `role` | enum: `gem`, `harness`, `system` | Who wrote this row |
| `content` | text (JSON string) | Payload — tool name + args (request) or result (result) |
| `metadata` | JSON or blank | Optional: session_id, model, node_name |

**event_type enum (exhaustive):**
`harness_request` | `harness_result` | `memory_update` | `session_start` | `session_end` | `calibration` | `health_check` | `error`

### Tab: `state` (Upsert keyed by session_id — Tier 5 and Tier 6 Full)

| Column | Type | Notes |
|---|---|---|
| `session_id` | text | Unique per run |
| `last_run_at` | ISO 8601 | UTC |
| `last_query` | text | Truncate to 500 chars |
| `last_result_url` | url or blank | Output artifact URL |
| `status` | enum: `idle`, `running`, `error` | |
| `notes` | text | Free-form agent notes |

### Tab: `runs` (Append-only log — Tier 5 and Tier 6 Full)

| Column | Type | Notes |
|---|---|---|
| `run_id` | UUID v4 | |
| `timestamp` | ISO 8601 | UTC |
| `input` | text | Truncate to 500 chars |
| `output_url` | url or blank | |
| `tokens_used` | int | Gemini Flash token count |
| `success` | bool | |

**Read/write discipline:**
- `state`: upsert on every run completion (key = session_id)
- `runs`: append on every run (success or failure)
- `bus`: Tier 5 only — append request, then append result when harness completes
- `never_recommend`: read-only; manual edits only; inject as constraints into planner node at run start

---

## Harness Dispatch Block (Tier 5)

When Tier 5 (Harness-Proxy) is selected, include the following dispatch block in the **first Generate or Agent Step node** that needs to invoke a tool externally.

### Dispatch Block (embed in node instruction, after ## Goal)

```
## Harness Dispatch
When you need to call an external tool, write a row to the `bus` tab of the Memory Sheet:
- event_type: harness_request
- role: gem
- content: {"tool": "<tool_name>", "params": {<params>}}
- uuid: generate a UUID v4 string
Then WAIT. Do not continue until a row with event_type=harness_result and parent_uuid=<your uuid> appears.
Read that row's content field for the tool result.
Available tools (harness-backed): [list exactly the tools the harness backend supports for this gem]
```

### Harness Backend Selection (surface to User at end of Step 2)

Ask User which backend path they want:

> "Your Harness-Proxy gem needs a backend to process tool calls. Three options — all zero-code:
> 1. **Apps Script** (default) — runs inside Google Sheets, automatic. Best for Gmail, Drive, Calendar, Gemini API. Limit: 90 min/day.
> 2. **Local Python** — runs on your machine. Best for local files, Zora/Ollama, code execution. Machine must stay on.
> 3. **Manual** — you check the Sheet yourself, run the tool, paste the result. Zero setup. Best for low-frequency calls.
> Which path fits your workflow?"

Record the answer in `step2-generate.json` as `harness_backend`. The Apps Script template is in `step4-opal-deploy.md §4.8`.

---

## Node Catalog

### Quick Reference (always loaded)

| Node | Icon | Input | Output | Key config |
|---|---|---|---|---|
| User Input | 📥 | User types/speaks/uploads | Raw text / file / audio | type: text\|audio\|image\|file\|video |
| Generate | ✨ | @upstream | Text / JSON | Model, PTCF prompt, @refs |
| Agent Step | 🤖 | @upstream | JSON + tool calls | 5-block instruction, tools enabled, max calls |
| Output | 📤 | @upstream | Artifact | Destination: Doc/Sheet/Slide/Drive/Web |
| Sheets Read | 📊 | Sheet URL + tab | Row(s) as JSON | Key column, range |
| Sheets Append | 📊➕ | JSON row | Confirmation | Sheet URL, tab, column order |
| Drive Read | 📂 | File/folder URL | File content | Supports Docs, PDFs, text |
| Drive Write | 💾 | Text + destination | File URL | Destination folder |
| Google Search | 🔍 | Query string | Search results JSON | No config; just enable on Agent Step |
| Docs Create | 📝 | Text content | Doc URL | Destination folder |
| Sheets Create | 📊✨ | Schema + data | Sheet URL | Destination folder, tab names |
| Slides Create | 📊🎞️ | Slide content | Slides URL | Destination folder |
| Gmail Send | ✉️ | To, subject, body | Send confirmation | Requires Gmail scope |
| Calendar Read | 📅 | Date range | Events JSON | Requires Calendar scope |
| For-Each | 🔄 | List / Sheet range | Iterated outputs | Loop variable name |
| Conditional | 🔀 | Boolean / enum | Route A or B | Edge labels match condition values |

> Load the #### blocks below only when you need exact configuration for a specific node.

---

#### User Input
**Purpose:** Entry point. Accepts typed text, voice, uploaded files, or images.  
**Types:** `text` (default) | `audio` (transcribed by Gemini) | `image` | `file` (PDF/Docs/Sheets) | `video`  
**Naming:** Name before wiring any downstream @references. Rename = all @refs update automatically in the same session.  
**Tip:** For multi-field forms, use one User Input node per field, or use a single text node and parse structured input in the first Generate node.

#### Generate
**Purpose:** Stateless text generation using a PTCF prompt.  
**Model:** Default = Gemini 3 Flash. Override only if User specifies (e.g., Gemini 3 Pro for final-draft quality).  
**PTCF discipline:** Persona / Task / Context / Format — all four required. Context should be @refs, not pasted text.  
**Output:** Text or JSON string. If downstream nodes need structured data, set Format to JSON and validate the schema in an Edge Case note.  
**Character budget:** Same as Agent Step — 1,500 chars target, 2,500 hard cap.

#### Agent Step
**Purpose:** Dynamic routing and tool orchestration. Use when next action depends on content of previous output.  
**Instruction format:** 5-block (## Role / ## Goal / ## Tool Protocol / ## Output Format / ## Edge Cases).  
**Tools enabled:** Check each tool as a checkbox in the node config panel. Only enable what the block references.  
**Max tool calls:** Default 10. Set lower (3–5) for simple routing; set higher (15–20) only for deep research loops.  
**Termination:** Must be the last line of ## Goal or an explicit condition in ## Edge Cases. No termination = quota risk.  
**Loop detection:** If same tool + args appears 3× consecutively → halt with error JSON (built into 5-block Edge Cases template).

#### Output
**Purpose:** Delivers the final artifact to the User.  
**Destinations:** Google Doc | Google Sheet | Google Slides | Drive file (any format) | Web Page (rendered in Opal UI)  
**Web Page:** Accepts Markdown or HTML. Auto-layout unless User has design preferences.  
**One Output node per graph** as a v1 rule. Multi-output graphs add complexity and are a v2+ consideration.  
**Trigger:** Opal runs the Output node after all upstream edges complete and no errors were raised.

#### Sheets Read
**Purpose:** Loads structured state or reference data from a Google Sheet at runtime.  
**Config:** Sheet URL (from Step 4.1) + tab name + key column (for keyed reads) or range (for bulk reads).  
**When to use:** Start of run (load state), after harness_result row appears (read tool result), lookup in never_recommend tab.  
**Output format:** JSON array of row objects, keyed by column headers.  
**Empty result:** Always handle in Edge Cases — halt or branch on empty rather than proceeding with null state.

#### Sheets Append
**Purpose:** Writes a new row to an append-only tab (typically `runs` or `bus`).  
**Config:** Sheet URL + tab name + column order. Column order must match the Canonical Sheets Memory Bus Schema exactly.  
**When to use:** End of every run (append to `runs`); after harness dispatch (append to `bus` as harness_request).  
**Idempotency:** Append is not idempotent — ensure it fires exactly once per run. Gate it with a success condition in the upstream Agent Step.

#### Drive Read
**Purpose:** Reads the content of a Google Doc, PDF, or text file from Drive.  
**Config:** File URL or folder URL. Folder URL = read all files in the folder (use sparingly — can be slow).  
**Output:** Raw text content. For Docs, includes headings and paragraphs. For PDFs, OCR-extracted text.  
**Use case:** Loading domain knowledge docs, reading the relay folder spec files, reading a User-provided brief.  
**Alternative:** For very large documents (>100K chars), consider chunking with a For-Each node over page ranges.

#### Drive Write
**Purpose:** Writes a file to a Drive folder.  
**Config:** Destination folder URL + file name + MIME type.  
**Output:** URL of the written file.  
**Use case:** Saving intermediate outputs, archiving run results, writing the relay folder artifacts programmatically.

#### Google Search
**Purpose:** Returns web search results as a JSON array (title, URL, snippet).  
**Config:** None — enable on Agent Step node; the agent passes the query string when calling the tool.  
**Result count:** Default 10 results. The agent can call multiple times with refined queries.  
**Grounding note:** Search results are NOT automatically cited in Generate nodes — the Agent Step must extract and pass relevant snippets explicitly.

#### Docs Create
**Purpose:** Creates a new Google Doc and writes content to it.  
**Config:** Destination folder URL. File name and content come from the upstream node output.  
**Output:** URL of the created Doc.  
**Formatting:** Supports Markdown headings and lists. Bold/italic via Markdown syntax.  
**Tip:** Use as the final Output node when the deliverable is a polished document.

#### Sheets Create
**Purpose:** Creates a new Google Sheet with specified tabs and data.  
**Config:** Destination folder + tab schema (tab name, column headers, initial data rows).  
**Output:** URL of the created Sheet.  
**Use case:** One-time setup of the Memory Sheet (do this manually in Step 4.1 rather than with a node — nodes are for runtime writes).

#### Slides Create
**Purpose:** Creates a new Google Slides deck.  
**Config:** Destination folder + slide content (title, body per slide).  
**Output:** URL of the created Slides deck.  
**Content format:** Upstream node must output structured JSON: `[{"title": "...", "body": "..."}, ...]`.

#### Gmail Send
**Purpose:** Sends an email from the User's Gmail account.  
**Config:** Requires Gmail scope (User must authorize in Opal settings).  
**Inputs:** To, subject, body (plain text or HTML).  
**Output:** Send confirmation.  
**Privacy:** Never send emails without explicit User confirmation in the workflow. Add a Generate node before Gmail Send that shows a preview and asks "Confirm? (yes/no)".

#### Calendar Read
**Purpose:** Reads upcoming calendar events from the User's Google Calendar.  
**Config:** Requires Calendar scope. Date range passed by upstream node.  
**Output:** JSON array of events (title, start, end, attendees, description).  
**Use case:** Meeting prep workflows, schedule-aware planning agents.

#### For-Each
**Purpose:** Loops over a list or Sheet range, running downstream nodes once per item.  
**Config:** Input = array or Sheet range. Loop variable = `@forEach.item`.  
**Output:** Array of results, one per iteration.  
**Termination:** Automatic when list is exhausted. Set a max-iteration guard in the upstream Agent Step if the list length is dynamic.  
**v1 caution:** For-Each multiplies token cost by N. Profile token use before enabling on large datasets.

#### Conditional Branch
**Purpose:** Routes graph execution to one of two edges based on a boolean or enum value.  
**Config:** Edge labels must match the upstream node's output values exactly (case-sensitive).  
**Output:** Passes upstream data unchanged to the selected branch.  
**Tip:** For simple 2-way branches, use Conditional. For 3+ branches or dynamic routing, use Agent Step.

---

## Tri-File JSON Architecture (Patch B — stateful workflows)

For Tier 6 Full workflows that need rich cross-session state beyond the flat Sheets schema, implement the Tri-File JSON Architecture. This is optional — only recommend when the workflow needs to track layered context that a flat Sheet cannot represent.

**Three files in the relay folder:**

| File | Role | Size target | Write frequency |
|---|---|---|---|
| `_WorkingMemory_[Name].json` | Current run state — inputs, intermediate outputs, current step | ≤ 8K chars | Every node completion |
| `_EpisodicBuffer_[Name].json` | Last 10 run summaries — compressed; enables cross-run pattern detection | ≤ 15K chars | End of each run |
| `_LongTermStore_[Name].json` | Stable facts: User preferences, never-recommend items, calibration baselines | ≤ 20K chars | Manual + calibration updates only |

**Schema conventions:**
- All three files use JSON (not Markdown)
- `last_updated`: ISO 8601 UTC timestamp on every write
- `version`: increment on each write (for conflict detection)
- The Agent Step reads all three at run start; writes WorkingMemory at each step; writes EpisodicBuffer at run end

**When to recommend:**
- Workflow needs to detect drift across runs (calibration use cases)
- Workflow needs to remember User preferences that change over time
- Flat Sheets schema would require >6 custom columns not in the canonical schema

**When NOT to recommend:**
- v1 builds (adds setup complexity)
- Stateless (Tier 6 Fast) or low-frequency workflows
- Workflows where the canonical 3-tab Sheets schema is sufficient

---

## Session Budget Checkpoint

After Step 2 Opal generation is complete, surface a budget estimate:

```
─── Session Budget Check ───────────────────────────────
Estimated Claude tokens consumed so far: ~[N]K
Opal workflow: [nodes count] nodes, [tool nodes count] tool calls per run
Sheets memory: [tabs count] tabs, ~[bytes] per run
Estimated Opal tokens per run: ~[N]K (Gemini 3 Flash pricing)
Estimated runs per day: [expected usage]
Opal free-tier headroom: [comfortable / moderate / tight]

[If tight]: "You're close to Opal's free-tier daily run budget. Consider reducing node count, caching tool results in Sheets, or accepting that scheduled runs may need paid tier."
────────────────────────────────────────────────────────
```

## State Output

After Step 2 Opal completes, write `_state/step2-generate.json`:
```json
{
  "status": "success",
  "tier": "Opal",
  "timestamp": "[ISO 8601]",
  "files_generated": ["graph.md", "nodes.md", "sheets-schema.md", "test-plan.md"],
  "node_count": 7,
  "agent_step_used": true,
  "sheets_tabs": 3,
  "approved_by_user": true,
  "failed_substeps": []
}
```
