# Step 4: DEPLOY — Local Gem (Tier 4 — Offline / Private)

> This file activates ONLY when Local Gem tier is detected in Step 1. The inference configuration (hardware profiling, model selection) was completed in Step 2.

Read state from `_state/step3-validate.json`.

## Deployment Overview

The user chats in Open WebUI (browser at `localhost:3000`). The gem script runs as a background daemon managing memory lifecycle automatically. The user never interacts with the script after setup.

## Quick Start (4 commands)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull the model selected in Step 2 (from Hardware → Model Ladder)
ollama pull [MODEL_TAG]

# 3. Start Open WebUI (chat interface)
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main

# 4. Setup and start the gem memory daemon
python gem-script.py --setup && python gem-script.py --daemon
```

Four commands. User opens `localhost:3000`, selects their Gemma model, starts chatting. The gem script manages memory lifecycle, source indexing, and health checks silently.

**Terminal fallback:** If user explicitly requests terminal-only (no Docker, no browser), use `python gem-script.py` without `--daemon`. Only if user says "terminal," "no Docker," or "CLI only."

## What the Script Handles

Automated memory hub injection (full context every turn), MEMORY_UPDATE block parsing and application, auto-archive at 80% ceiling, version incrementing, session summaries to progress file, health monitoring, built-in RAG over source directories (if `--index` used), tiered research routing (SearXNG → Perplexica if available).

**Hardware → Model:** Determined in Step 2 using Hardware → Model Ladder. See `references/agentic-tier-guide.md` for full Gemma family table.

**Memory relay:** Unlike cloud tiers, Local Gem script applies MEMORY_UPDATE blocks automatically — no manual relay. Same Drive memory hub format; all hard limits still apply.

**Script template:** See `references/local-gem-script-template.py` for the full daemon/terminal dual-mode script.

## Local Gem Health Schedule (Additional Checks)

```
Name: Gem Health Check — [Gem Name] (Local)
Due: [date 30 days from deployment]
Description: Standard checks PLUS: model file integrity, source directory freshness, RAG index staleness, inference performance baseline, script version tracking.
Drive path: [gem memory folder path]
Engine: Ollama + [model tag]
```

The gem script runs a subset automatically on session start. The 30-day check adds deeper checks requiring Claude.

## State Output

After Step 4 completes, write `_state/step4-deploy.json`:
```json
{
  "status": "success",
  "timestamp": "[ISO 8601]",
  "files_written": ["prompt → script config", "hub → Memory/", "script → gem folder"],
  "relay_folder_created": true,
  "gemini_knowledge_attached": false,
  "local_deployment": {
    "model_tag": "[MODEL_TAG]",
    "open_webui": true,
    "daemon_started": true
  },
  "failed_substeps": []
}
```
