# Step 4: DEPLOY (Opal tier)

Read state from `_state/step3-validate.json`. All Opal artifacts have been validated by the user.

> **Prerequisite:** User can reach `labs.google/opal` signed into the same Google account that holds Drive files. No API keys required.

## Deploy Order

1. **Create the Sheets memory workbook** (if stateful)
2. **Write all spec files to the Relay folder**
3. **Create the Opal workflow in the Opal editor**
4. **Wire up tool nodes and Sheets connectors**
5. **Debug-console dry run**
6. **Save and share (optional)**

## Step 4.1 — Create Sheets Memory Workbook

If the workflow needs state:

1. In Drive, create a new Google Sheet: `[Opal Name] Memory.gsheet` at `D:\My Drive\AI Ecosystem\Opal\[Opal Name]\`
2. For each tab defined in `_Sheets_[Name]_MemorySchema.md`:
   - Create the tab with the exact name
   - Freeze the header row
   - Add column headers in row 1
   - Add one sample row in row 2 (gives Opal a data type hint; delete before going live if you prefer)
3. Set share: private to the user's Google account (never open link sharing for memory sheets)
4. Copy the Sheet URL — you'll need it in Step 4.4

> **Schema note:** Use the Canonical Sheets Memory Bus Schema from `step2-opal-delta.md § Canonical Sheets Memory Bus Schema` as the authoritative column names and tab names. Never invent alternate column names — the harness backend and Opal tool nodes both reference exact column headers.

## Step 4.2 — Write Spec Files to Relay Folder

Run the **Pre-Write Validation Protocol** first. Then write all Opal artifacts to `[Opal Name] Relay/` at `D:\My Drive\AI Ecosystem\Opal\[Opal Name]\[Opal Name] Relay\`:

| File | Purpose |
|---|---|
| `_Opal_[Name]_GraphSpec.md` | Human-readable graph description |
| `_Opal_[Name]_NodeInstructions.md` | Exact PTCF text for each node |
| `_Sheets_[Name]_MemorySchema.md` | Tab schema + read/write patterns |
| `_Opal_[Name]_TestPlan.md` | 5–6 test scenarios from step5-test.md |
| `_Opal_[Name]_ShareConfig.md` | Only if sharing/publishing |
| `_Progress_[Name]_ActiveTask.md` | Same template as gem tiers |
| `_Heuristics_[Name]_Pool.md` | Same template as gem tiers (start empty) |

Confirm by listing the directory after writing.

## Step 4.3 — Create the Opal Workflow

Guide the user through the Opal UI step-by-step. Profile dictates depth: Technical gets raw @-references; Non-technical gets screenshots-in-text instructions.

1. Open `labs.google/opal` in the browser
2. Click **+ Create** → choose **Start from scratch** (not a template) unless the user's workflow closely matches an existing gallery template
3. Name the Opal `[Opal Name]` — use the same name as the Drive folder for traceability
4. Click the **Describe** tab and paste the workflow goal statement from `_Opal_[Name]_GraphSpec.md`. This seeds the initial auto-generated graph — you'll replace most of it.
5. Switch to the **Advanced editor** view (for Technical/Semi-technical profiles). Non-technical users can stay in the visual builder — the steps below map to both.

## Step 4.4 — Build the Graph Node by Node

For each node in `_Opal_[Name]_GraphSpec.md`:

### User Input node
- Drag a **User Input** node onto the canvas
- Rename it to match the spec (the @ reference uses this name — set it BEFORE writing any downstream prompt)
- Set input type: text / audio / image / file / video (see Node Catalog in `step2-opal-delta.md`)

### Generate node
- Drag a **Generate** node
- Rename to match spec
- Paste the PTCF prompt from `_Opal_[Name]_NodeInstructions.md`
- Set the model if user specified (default = Gemini 3 Flash)
- Add @-references to upstream nodes inside the prompt text

### Agent Step node
- Drag an **Agent Step** node (appears as "Agent" in the visual builder)
- Rename to match spec
- Paste the full Agent Step instruction block from `_Opal_[Name]_NodeInstructions.md`
- Enable the tools listed in the spec — each tool becomes a checkbox or connected tool node
- Set the max tool-call limit (default 10)
- Confirm termination condition is written as the last line of the instruction

### Tool nodes (Sheets Read/Append, Drive Read, Search, Docs Create, etc.)
- Drag the tool node from the tool palette
- For Sheets nodes: paste the Sheet URL from Step 4.1; select the tab; configure the range or key column
- For Drive Read: paste the file URL or folder URL
- For Search: no config needed; just connect the edge
- For Docs/Sheets/Slides Create: configure the output destination folder

### Output node
- Drag an **Output** node
- Choose destination: Docs / Sheets / Slides / Drive file / Manual Layout / Web Page
- Connect the upstream node via the edge
- For web page outputs: accept the auto layout unless user has specific design preferences

### Edge wiring
- Draw edges in the order specified in `_Opal_[Name]_GraphSpec.md`
- Verify each Generate/Agent node's @-references resolve (they should show previews if the upstream node has produced a sample output)

## Step 4.5 — Debug Console Dry Run

1. Click the **Debug console** button (Oct 2025 feature)
2. Enter a sample input that matches Test 1 from `_Opal_[Name]_TestPlan.md`
3. Step through the graph one node at a time, inspecting each output
4. Verify:
   - @-references resolve to the expected upstream data
   - Sheets reads return the expected sample row
   - Agent Step terminates on the termination condition (not the max-tool-call safety cap)
   - Output node produces the expected artifact
5. Fix any issues BEFORE the first real run — debug console catches 90% of prompt/reference bugs for free

## Step 4.5b — Disappearing-Documents Check (Patch F)

> **Bug:** Opal's Output nodes (especially Docs Create and Drive Write) can silently lose their destination setting when the workflow is saved and reopened. The document appears created but is written to an unexpected location or lost entirely.

**Run this check immediately after the debug console dry run:**

1. Click **Save** in the Opal editor
2. Close the workflow completely (navigate away from the URL)
3. Reopen the workflow URL
4. Inspect every Output, Docs Create, Drive Write, and Sheets Create node:
   - Confirm the destination folder URL is still populated (not blank)
   - Confirm the output file name template is still set
5. If any destination field is blank → re-enter it, save again, close/reopen, repeat until it persists

> **Workaround for persistent bug:** Set a sticky note or comment on the affected node with the correct folder URL. If the field clears on every reopen, use a Generate node upstream to produce the folder path as a variable, and reference it via @stepName rather than hardcoding in the node config.

**This check is mandatory** — skip it and the first real run may produce output with no recoverable URL.

## Step 4.6 — Save and (Optionally) Share

1. Click **Save** in the Opal editor
2. If the user wants to share:
   - Click **Share** → choose **Anyone with link can view and run** OR **Specific people**
   - Copy the share URL to `_Opal_[Name]_ShareConfig.md`
3. If the user wants to publish to the gallery:
   - Click **Publish to gallery**
   - Fill in: title, description, category, example input, expected output screenshot
   - Confirm the `_Opal_[Name]_ShareConfig.md` matches the live gallery listing

> **Privacy note:** Publishing to the gallery makes the prompt text and graph structure visible to other users. Never publish an Opal that references private Sheets or Drive files unless you've removed those references or replaced them with placeholder demos.

## Step 4.7 — Scheduled Runs (if applicable)

Opal supports scheduled execution via the **Run on schedule** option (cron-like UI).

- Only enable after the debug console run AND a full Step 5 test suite pass
- Default frequency: daily at a time outside peak hours
- Set the run to log into the `runs` tab of the memory Sheet so the user can audit drift
- Verify Opal's daily run quota can support the schedule (current free-tier soft cap: ~50 runs/day — verify at deploy time as this may change)

## Step 4.8 — Runtime Behavior and Compaction (Patch D)

Opal workflows share Flash's context window across the full graph on each run. For stateful Full-mode workflows, context grows with each run as the `runs` tab accumulates rows.

**Within-session compaction (automatic at 80% fill):**
- When the Agent Step's context reaches 80% of Flash's 1M input limit, it will begin dropping older `runs` rows from its read.
- Design Sheets Read nodes to read only the last N rows (10 is default) rather than the full tab history.
- Add this instruction to every Sheets Read node that reads the `runs` tab: "Read the last 10 rows only. Do not read all rows."

**Between-session insulation:**
- Each Opal run starts fresh — there is no automatic context carry-over between runs.
- The `state` tab provides the only between-session memory. Keep its rows lean (≤ 500 chars per cell).
- If a run needs context from a prior run, the Agent Step must explicitly read the `state` tab at start.

**Compaction monitoring:**
- If a run produces truncated or incoherent output, check the `runs` tab row count.
- If > 50 rows: archive old rows to a `runs_archive` tab and trim the `runs` tab to the last 20 rows.
- Log compaction events to the `runs` tab with event_type `system` and content `"compaction performed"`.

---

## Step 4.9 — Harness Backend Setup (Tier 5 Only)

Skip this step for Tier 6 (Opal handles tool calls natively).

For Tier 5 (Harness-Proxy), set up the backend selected in Step 2:

### Path 1 — Apps Script (default)

1. Open the Memory Sheet from Step 4.1
2. In the Sheet: **Extensions → Apps Script**
3. Delete the default `myFunction()` code
4. Paste the template below
5. Run `createTimeTrigger()` once — this sets up a 1-minute poll
6. Authorize the required scopes when prompted (SpreadsheetApp, UrlFetchApp, GmailApp, DriveApp)
7. Verify: manually run `onTimerTick()` → confirm no errors in the Execution Log

```javascript
// ============================================================
// Harness Backend — Apps Script (Tier 5 Harness-Proxy)
// Paste into a container-bound script on the Memory Sheet.
// Run createTimeTrigger() ONCE to activate the polling loop.
// ============================================================

const HARNESS_CONFIG = {
  SHEET_NAME: 'bus',
  POLL_LIMIT: 20,         // max request rows to process per tick
  POLL_INTERVAL_MIN: 1,  // trigger interval in minutes
};

// ---- Entry point (time-driven trigger) ----
function onTimerTick() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(HARNESS_CONFIG.SHEET_NAME);
  if (!sheet) { Logger.log('bus tab not found'); return; }

  const data = sheet.getDataRange().getValues();
  if (data.length < 2) return;
  const headers = data[0];
  const col = (name) => headers.indexOf(name);

  let processed = 0;
  for (let i = 1; i < data.length && processed < HARNESS_CONFIG.POLL_LIMIT; i++) {
    const row = data[i];
    if (row[col('event_type')] !== 'harness_request') continue;
    if (row[col('role')] !== 'gem') continue;

    const uuid = row[col('uuid')];
    const alreadyHandled = data.slice(1).some(
      r => r[col('event_type')] === 'harness_result' && r[col('parent_uuid')] === uuid
    );
    if (alreadyHandled) continue;

    let result;
    try {
      const payload = JSON.parse(row[col('content')]);
      result = dispatchTool(payload.tool, payload.params);
    } catch (e) {
      result = { error: e.message };
    }

    const resultRow = new Array(headers.length).fill('');
    resultRow[col('uuid')] = Utilities.getUuid();
    resultRow[col('parent_uuid')] = uuid;
    resultRow[col('timestamp')] = new Date().toISOString();
    resultRow[col('event_type')] = 'harness_result';
    resultRow[col('role')] = 'harness';
    resultRow[col('content')] = JSON.stringify(result);
    sheet.appendRow(resultRow);
    processed++;
  }
}

// ---- Tool dispatcher — add cases as needed ----
function dispatchTool(toolName, params) {
  switch (toolName) {
    case 'url_fetch': {
      const resp = UrlFetchApp.fetch(params.url, params.options || {});
      return { status: resp.getResponseCode(), body: resp.getContentText().slice(0, 8000) };
    }
    case 'gmail_send': {
      GmailApp.sendEmail(params.to, params.subject, params.body);
      return { sent: true };
    }
    case 'drive_write': {
      const folder = DriveApp.getFolderById(params.folderId);
      const file = folder.createFile(params.name, params.content, MimeType.PLAIN_TEXT);
      return { fileId: file.getId(), url: file.getUrl() };
    }
    case 'sheets_append': {
      const sh = SpreadsheetApp.openById(params.spreadsheetId).getSheetByName(params.tab);
      sh.appendRow(params.row);
      return { appended: true };
    }
    case 'gemini_call': {
      const resp = UrlFetchApp.fetch(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + params.apiKey,
        { method: 'post', contentType: 'application/json',
          payload: JSON.stringify({ contents: [{ parts: [{ text: params.prompt }] }] }) }
      );
      const body = JSON.parse(resp.getContentText());
      return { text: body.candidates?.[0]?.content?.parts?.[0]?.text || '' };
    }
    default:
      return { error: 'Unknown tool: ' + toolName };
  }
}

// ---- One-time setup ----
function createTimeTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'onTimerTick') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('onTimerTick')
    .timeBased().everyMinutes(HARNESS_CONFIG.POLL_INTERVAL_MIN).create();
  Logger.log('Trigger created. Run onTimerTick() to test manually.');
}
```

**Quota limits (Apps Script):** 90 min/day execution, 6 min per single run, 20K UrlFetch calls/day. See `gemini-gems-specs-and-limits.md § 18` for full table.

### Path 2 — Local Python

Install dependencies: `pip install gspread google-auth`. The harness polling class is in `local-gem-script-template.py` — run with `--harness` flag. Machine must remain on while the gem is active.

### Path 3 — Manual

1. Open the Memory Sheet `bus` tab
2. Watch for new rows with event_type = `harness_request`
3. Execute the requested tool manually
4. Paste the result into a new row: event_type = `harness_result`, parent_uuid = the request row's uuid, role = `harness`, content = JSON result string

---

## Step 4.10 — Fast Opal Deploy Shortcut (Tier 6 Fast)

If the workflow is Tier 6 Fast (stateless prototype), skip:
- Step 4.1 (no Sheets memory needed)
- Step 4.7 (no scheduled runs for prototypes)
- Step 4.9 (no harness backend)
- Step 4.5b (run it anyway — disappearing-docs bug affects all sub-modes)

Fast deploy order: **4.2 → 4.3 → 4.4 → 4.5 → 4.5b → 4.6**

Fast relay folder contains only:
- `_Opal_[Name]_NodeInstructions.md`
- `_Opal_[Name]_TestPlan.md` (3 smoke tests, not 5–6)
- `_Progress_[Name]_ActiveTask.md`

After passing the 3/3 smoke test threshold, the Fast workflow is ready. Upgrade to Full by adding the Sheets memory layer and re-running Steps 4.1, 4.9, and the calibration suite from `step5-test.md`.

---

## File Routing Table (Opal Tier)

| File | Location | Why |
|---|---|---|
| Graph spec | Relay folder | Source of truth for the workflow |
| Node instructions | Relay folder | Copy-paste ready text |
| Sheets schema | Relay folder | Reference for schema changes |
| Test plan | Relay folder | Matches step5-test.md |
| Share config | Relay folder | Records published state |
| Progress file | Relay folder | Task tracking (same as gem tiers) |
| Heuristics Pool | Relay folder | Optimization notes |
| Opal workflow itself | Opal editor (labs.google/opal) | Lives in Google's cloud, not Drive |
| Sheets memory | Drive root (shared with Opal) | Indexed by Opal's Sheets tool, NOT attached as Knowledge |

> ⚠️ **The Opal workflow is NOT a file in Drive.** It lives in the Opal editor. The Relay folder holds the *specification* of the workflow so you can rebuild it if Opal ever loses it.

## Opal Health Schedule

At end of deployment, Claude writes a health schedule entry to auto-memory:
```
Name: Opal Health Check — [Opal Name]
Due: [date 30 days from deployment]
Description: Run opal-audit. Check: node count drift, Sheets schema staleness, run success rate in `runs` tab, daily quota headroom, termination condition still firing.
Drive path: [opal relay folder path]
Opal URL: [labs.google/opal workflow URL]
```

## State Output

After Step 4 Opal completes, write `_state/step4-deploy.json`:
```json
{
  "status": "success",
  "tier": "Opal",
  "timestamp": "[ISO 8601]",
  "files_written": ["graph.md", "nodes.md", "sheets-schema.md", "test-plan.md"],
  "opal_workflow_created": true,
  "opal_workflow_url": "[labs.google/opal/...]",
  "sheets_memory_url": "[docs.google.com/spreadsheets/...]",
  "debug_console_passed": true,
  "scheduled": false,
  "shared": false,
  "failed_substeps": []
}
```
