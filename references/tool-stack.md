# Tool & Research Stack Reference

Canonical tool selection guide for the Super Gem Creator skill. Claude reads this to choose the right tool for each action during gem creation and memory relay sessions.

---

## File Operation Fallback Chain

Always try tools in this order. Stop at the first available tool and use it consistently for the session.

| Priority | Tool | Use Case | Capability |
|----------|------|----------|-----------|
| 1 (Primary) | **Desktop Commander** | All file operations when Drive is locally mounted | Surgical edits (`edit_block`), new files (`write_file`), discovery (`list_directory`), existence check (`get_file_info`) |
| 2 (Fallback) | **Windows MCP `FileSystem`** | If Desktop Commander is unavailable | Full read → modify → rewrite (no surgical edit); slightly higher token cost — inform user |
| 3 (Manual fallback) | **`cowork present_files`** | If both file tools unavailable | Present files to user for manual Drive upload |

**Detection logic:** At session start, run `get_file_info` on `D:\My Drive\` (or user's confirmed Drive root). If it succeeds → Desktop Commander is active. If it fails → try Windows MCP. If both fail → use `present_files`.

**Session consistency:** Once a tool is confirmed, use it throughout. Do not switch mid-session.

---

## Research Fallback Chain

Assume NotebookLM is in scope by default. Do NOT ask "do you want research grounding?" — plan for 2 notebooks (Standard) or up to 5 (Research) from Step 1. Only fall back if the user explicitly declines or NB is unavailable.

| Level | Tool | When to use | Notes |
|-------|------|------------|-------|
| 1 (Default) | **NotebookLM** | All gem creation workflows | ~60 sources/notebook, 2 per Standard gem / up to 5 per Research gem (Knowledge slot constraint) |
| 2 | **Gemini Deep Research** | NB unavailable or user declines | Free, same ecosystem, generates citable Drive reports |
| 3 | **Gemini file uploads** | For smaller, contained reference sets | Upload PDFs/docs directly into Gemini conversation |
| 4 | **Claude web search relay** | For targeted live research | Claude searches → summarizes → user pastes into NB or Drive |
| 5 | **Manual** | User preference or no tools available | Claude provides search query suggestions; user collects sources |

**Hard limit:** 2 NotebookLM notebooks maximum per Standard gem, up to 5 per Research gem — Knowledge slot constraint. Fast Track gems skip notebooks entirely.

---

## Memory Relay Tool Chain

During post-deployment memory relay sessions (applying MEMORY_UPDATE blocks):

| Step | Tool | Action |
|------|------|--------|
| 1 | Desktop Commander `read_file` | Read current memory hub sections |
| 2 | Desktop Commander `edit_block` | Apply surgical section edits |
| 3 | Desktop Commander `get_file_info` | Verify file size (check archive trigger at 12K chars) |
| 4 | Desktop Commander `write_file` | Create Archive file if archive trigger reached |
| Fallback | Windows MCP `FileSystem` | Full read → modify → rewrite if DC unavailable |
| Cloud fallback | Google Drive MCP `google_drive_fetch` | If no local Drive mount available |

---

## Advanced Tool Chain Patterns (Tier 3 — API/ADK Only)

### Thought Signatures (Gemini 3 API with function calling)

**What:** Gemini 3 (API) generates encrypted "Thought Signatures" — a compressed save-state of the model's internal reasoning — before every tool call. Returning the signature in the next request preserves the model's reasoning thread across multi-step tool chains.

**When required:** Only for Tier 3 (API/ADK) gem builders using function calling. **Not applicable to:**
- Consumer Gem (Tier 1) — conversation history handles context retention
- Opal workflows (Tier 2) — DAG handles context at the workflow level
- Local Gems (Tier 4) — uses full conversation history instead

**Critical constraint:** Thought Signatures are **mandatory** in Gemini 3 API calls with function calling. Omitting the previous turn's thought signature returns a `400` error — this is enforced, not optional.

**Pattern:**
```python
# Step 1: Initial query — capture thought signature
response = client.models.generate_content(
    model="gemini-3-pro",
    contents=[{"role": "user", "parts": [{"text": user_query}]}],
    tools=[search_tool, memory_read_tool]
)
thought_sig = response.candidates[0].content.parts[0].thought_signature

# Step 2: Execute tool, return result WITH the signature from step 1
response2 = client.models.generate_content(
    model="gemini-3-pro",
    contents=[
        {"role": "user",  "parts": [{"text": user_query}]},
        {"role": "model", "parts": [{"thought_signature": thought_sig}, tool_call_part]},
        {"role": "user",  "parts": [tool_result_part]}   # tool result
    ]
)
# Always pass thought_sig from response2 into the next call — chain all the way through
```

**Common mistake:** Forgetting to chain the signature through all steps of a multi-turn tool chain. Each step must pass the previous turn's `thought_signature`.

---

## Tool Selection Quick Reference

| Task | Use This Tool |
|------|--------------|
| Write gem files to local Drive | Desktop Commander `write_file` |
| Patch an existing gem file | Desktop Commander `edit_block` |
| Check if a Drive path exists | Desktop Commander `get_file_info` |
| List files in a Drive folder | Desktop Commander `list_directory` |
| Read a file when DC is unavailable | Windows MCP `FileSystem` mode: read |
| Apply a MEMORY_UPDATE block | Read → `edit_block` → confirm size |
| Research for NB1/NB2 topics | NotebookLM (default), then fallback chain |
| Multi-step API tool calling | Gemini 3 API + Thought Signatures pattern above |
| Local offline gem runtime | Ollama + Gemma family + `local-gem-script-template.py` |
| Automated web-search gem | Opal workflow (Tier 2, no code) |
