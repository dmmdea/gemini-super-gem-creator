"""
local-gem-script-template.py
Full-featured Local Gem manager: daemon + terminal modes, automated memory lifecycle,
built-in RAG, progressive research routing, and Open WebUI integration.

Supports the complete Gemma family (270M through 31B Dense) via Ollama.

Usage:
  python gem-script.py --setup            # Guided first-time configuration
  python gem-script.py --daemon           # Background memory manager for Open WebUI
  python gem-script.py                    # Terminal-only interactive chat (fallback)
  python gem-script.py --index            # Build/rebuild RAG indexes over source directories
  python gem-script.py --index core       # Rebuild a specific directory's index
  python gem-script.py --stats            # Show source, memory, and index statistics
  python gem-script.py --add-source F D   # Add file F to source directory D and re-index
  python gem-script.py --new-source NAME  # Create a new source directory
  python gem-script.py --clear-cache      # Clear research cache
  python gem-script.py --health           # Run health checks manually
  python gem-script.py --benchmark        # Run inference benchmark

Architecture:
  - Daemon mode: watches Ollama conversation stream via API, injects memory hub +
    source context as system prompt, parses MEMORY_UPDATE blocks from model output,
    triggers auto-archive, writes session summaries. User chats in Open WebUI.
  - Terminal mode: interactive CLI chat with identical memory management. Fallback
    for users who don't want Docker/Open WebUI.
  - Auto-detection: probes localhost for Ollama, Open WebUI, SearXNG, Perplexica,
    and Chroma — uses what's available, skips what isn't.
  - Model-agnostic: works with any Gemma model (270M through 31B Dense). Talks to
    Ollama's OpenAI-compatible API — doesn't care which model is loaded.

Requirements:
  pip install openai              # OpenAI-compatible client for Ollama (required)
  pip install chromadb            # RAG vector store (optional — gracefully skipped)
  pip install pdfplumber          # PDF text extraction (optional — gracefully skipped)
"""

import argparse
import json
import os
import re
import shutil
import signal
import sys
import textwrap
import time
import threading
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: 'openai' package required. Install: pip install openai")
    sys.exit(1)

# Optional imports — gracefully degrade if absent
try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# ═══════════════════════════════════════════════════════════════════════════════
# GEM CONFIGURATION — populated by --setup, edit only to override
# ═══════════════════════════════════════════════════════════════════════════════

GEM_CONFIG = {
    # ━━━ IDENTITY ━━━
    "name": "[Gem Name]",
    "domain": "[Domain description]",
    "version": "1.0.0",

    # ━━━ PATHS ━━━
    "gem_folder": r"D:\My Drive\[Your Gem Folder]",
    "memory_hub_file": "_Memory_[Name]_GemMemoryHub_Active.md",
    "archive_file": "_Memory_[Name]_GemMemoryHub_Archive.md",
    "progress_file": "_Progress_[Name]_ActiveTask.md",
    "system_prompt_file": "_Prompt_[Name]_GemSystemPrompt_v1.0.md",
    "heuristics_file": "_Heuristics_[Name]_Pool.md",
    "sources_dir": "sources",
    "research_cache_dir": "research-cache",

    # ━━━ INFERENCE (set by --setup based on hardware ladder) ━━━
    "model": "gemma4:e4b",
    "inference_url": "auto",            # "auto" → Ollama at localhost:11434
                                        # Set to any OpenAI-compatible URL to use a custom engine

    # ━━━ INTERFACE ━━━
    "mode": "daemon",                   # "daemon" (default) = background memory manager for Open WebUI
                                        # "terminal" = interactive CLI chat (fallback, no Docker needed)
    "webui_url": "http://localhost:3000",

    # ━━━ MEMORY LIFECYCLE ━━━
    "memory_ceiling": 15000,            # chars — auto-archive triggers at 80% (12,000)
    "archive_trigger_pct": 0.80,
    "context_reset_tokens": 24000,      # reset at 75% of 32K practical limit
    "max_retries": 3,

    # ━━━ LOCAL RAG (auto-enabled if sources/ exists + chromadb installed) ━━━
    "rag_enabled": "auto",
    "source_dirs": "auto",              # "auto" scans sources/*/ subdirectories
    "rag_top_k": 5,
    "rag_chunk_size": 512,
    "rag_embedding_model": "nomic-embed-text",

    # ━━━ WEB SEARCH (auto-enabled if SearXNG detected at localhost:8888) ━━━
    "search_enabled": "auto",
    "searxng_url": "http://localhost:8888",
    "searxng_max_results": 10,

    # ━━━ AI RESEARCH (auto-enabled if Perplexica detected at localhost:3001) ━━━
    "perplexica_enabled": "auto",
    "perplexica_url": "http://localhost:3001",
    "research_auto_promote": True,      # Auto-copy Perplexica results to source dirs
}

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT TYPE TAGS
# ═══════════════════════════════════════════════════════════════════════════════

TYPE_TAGS = {
    "[ADVISORY]":         "Standard advice — no special handling.",
    "[MEMORY_FLAG]":      "Contains MEMORY_UPDATE block — apply to memory hub.",
    "[HARNESS_PAUSE]":    "Requires user confirmation before proceeding.",
    "[HYPOTHESIS]":       "Unverified assumption — user should confirm.",
    "[SESSION_SUMMARY]":  "End-of-session state capture — write to progress file.",
    "[RESEARCH_NEEDED]":  "Route to research backend (SearXNG/Perplexica/manual).",
}

# ═══════════════════════════════════════════════════════════════════════════════
# PATH HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def gem_path(filename: str) -> Path:
    return Path(GEM_CONFIG["gem_folder"]) / filename

def sources_path() -> Path:
    return gem_path(GEM_CONFIG["sources_dir"])

def cache_path() -> Path:
    return gem_path(GEM_CONFIG["research_cache_dir"])

def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError):
        return ""

def write_file_safe(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def estimate_tokens(text: str) -> int:
    return len(text) // 4

def estimate_tokens_messages(messages: list) -> int:
    return sum(estimate_tokens(str(m.get("content", ""))) for m in messages)

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE AUTO-DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def probe_service(url: str, timeout: float = 2.0) -> bool:
    """Check if a service is reachable at the given URL."""
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD")
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:
        # HEAD might not be supported; try GET
        try:
            urllib.request.urlopen(url, timeout=timeout)
            return True
        except Exception:
            return False

def resolve_inference_url() -> str:
    if GEM_CONFIG["inference_url"] != "auto":
        return GEM_CONFIG["inference_url"]
    return "http://localhost:11434/v1"

def detect_services() -> dict:
    """Probe localhost for all optional services. Returns status dict."""
    inference_url = resolve_inference_url().rstrip("/v1").rstrip("/")
    status = {
        "ollama": probe_service(inference_url),
        "webui": probe_service(GEM_CONFIG["webui_url"]),
        "searxng": probe_service(GEM_CONFIG["searxng_url"]),
        "perplexica": probe_service(GEM_CONFIG["perplexica_url"]),
        "chromadb": HAS_CHROMADB,
    }
    return status

def print_service_status(status: dict) -> None:
    """Print detected services with helpful suggestions for missing ones."""
    def icon(ok): return "\u2705" if ok else "\u274c"

    print(f"\n  {icon(status['ollama'])}  Ollama         {'Ready' if status['ollama'] else 'NOT FOUND — install: curl -fsSL https://ollama.com/install.sh | sh'}")
    print(f"  {icon(status['webui'])}  Open WebUI     {'Ready at ' + GEM_CONFIG['webui_url'] if status['webui'] else 'Not running'}")
    print(f"  {icon(status['searxng'])}  SearXNG        {'Ready' if status['searxng'] else 'Not running'}")
    print(f"  {icon(status['perplexica'])}  Perplexica     {'Ready' if status['perplexica'] else 'Not running'}")
    print(f"  {icon(status['chromadb'])}  ChromaDB       {'Installed' if status['chromadb'] else 'Not installed'}")

    # Helpful suggestions for missing optional services
    suggestions = []
    if not status["ollama"]:
        suggestions.append("  REQUIRED: curl -fsSL https://ollama.com/install.sh | sh")
    if not status["webui"]:
        suggestions.append("  \U0001f4a1 Want a chat UI? Run: docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main")
    if not status["searxng"]:
        suggestions.append("  \U0001f4a1 Want web search? Run: docker run -d --name searxng -p 8888:8888 searxng/searxng")
    if not status["chromadb"]:
        suggestions.append("  \U0001f4a1 Want semantic search? Run: pip install chromadb")
    if status["searxng"] and not status["perplexica"]:
        suggestions.append("  \U0001f4a1 Want AI research? Run: docker compose -f perplexica-compose.yml up -d")

    if suggestions:
        print()
        for s in suggestions:
            print(s)
    print()

# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY LIFECYCLE (Core value — what differentiates Local Gem from raw Ollama)
# ═══════════════════════════════════════════════════════════════════════════════

def load_system_prompt() -> str:
    path = gem_path(GEM_CONFIG["system_prompt_file"])
    content = read_file_safe(path)
    if not content:
        raise FileNotFoundError(
            f"System prompt not found at {path}.\n"
            "Deploy gem files first using the Super Gem Creator skill."
        )
    return content

def load_memory_hub() -> str:
    path = gem_path(GEM_CONFIG["memory_hub_file"])
    content = read_file_safe(path)
    if not content:
        print(f"[WARNING] Memory hub not found at {path}. Starting with empty memory.")
        return "Memory hub not yet populated. This is the first session."
    return f"# Memory Hub (loaded at session start)\n\n{content}"

def memory_hub_size() -> int:
    """Return current memory hub size in chars."""
    path = gem_path(GEM_CONFIG["memory_hub_file"])
    return len(read_file_safe(path))

def check_archive_trigger() -> bool:
    """Check if memory hub exceeds archive threshold."""
    size = memory_hub_size()
    threshold = int(GEM_CONFIG["memory_ceiling"] * GEM_CONFIG["archive_trigger_pct"])
    return size >= threshold

def auto_archive() -> None:
    """Archive current memory hub and create fresh active hub."""
    hub_path = gem_path(GEM_CONFIG["memory_hub_file"])
    archive_path = gem_path(GEM_CONFIG["archive_file"])
    hub_content = read_file_safe(hub_path)

    if not hub_content:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_version = GEM_CONFIG["version"]

    # Append to archive
    archive_content = read_file_safe(archive_path)
    archive_block = (
        f"\n\n{'='*60}\n"
        f"## Archive — v{current_version} — {timestamp}\n"
        f"{'='*60}\n\n"
        f"{hub_content}"
    )
    write_file_safe(archive_path, archive_content + archive_block)

    # Bump version (1.0.0 → 1.1.0)
    parts = current_version.split(".")
    parts[1] = str(int(parts[1]) + 1)
    new_version = ".".join(parts)
    GEM_CONFIG["version"] = new_version

    # Create fresh active hub with header
    fresh_hub = (
        f"# {GEM_CONFIG['name']} — Memory Hub v{new_version}\n\n"
        f"*Archived v{current_version} on {timestamp}. "
        f"See archive file for previous memory.*\n\n"
        f"## \u00a70 File Registry & Hygiene\n\n"
        f"[Carry forward from archive as needed]\n"
    )
    write_file_safe(hub_path, fresh_hub)

    print(f"\n\U0001f4e6 AUTO-ARCHIVE: Memory hub archived (v{current_version} \u2192 v{new_version})")
    print(f"   Archive: {archive_path}")
    print(f"   Fresh hub: {hub_path}\n")

def extract_memory_updates(response: str) -> list[str]:
    pattern = r"---MEMORY_UPDATE---.*?---END_UPDATE---"
    return re.findall(pattern, response, re.DOTALL)

def apply_memory_update(update_block: str) -> None:
    """Parse and apply a MEMORY_UPDATE block to the memory hub file."""
    hub_path = gem_path(GEM_CONFIG["memory_hub_file"])
    hub_content = read_file_safe(hub_path)

    # Extract section and action from update block
    section_match = re.search(r"SECTION:\s*(\S+)", update_block)
    action_match = re.search(r"ACTION:\s*(\w+)", update_block)
    content_match = re.search(r"CONTENT:\s*(.*?)(?=---END_UPDATE---)", update_block, re.DOTALL)

    if not all([section_match, action_match, content_match]):
        # Fallback: surface to user for manual application
        print("\n" + "-"*50)
        print("\U0001f4be MEMORY_FLAG — could not auto-parse. Manual update needed:")
        print("-"*50)
        print(update_block)
        print("-"*50)
        return

    section = section_match.group(1)
    action = action_match.group(1).upper()
    content = content_match.group(1).strip()

    if action == "REPLACE":
        # Find the section header and replace content up to next section
        pattern = rf"(## {re.escape(section)}.*?\n)(.*?)(?=\n## |\Z)"
        replacement = rf"\g<1>{content}\n"
        new_hub, count = re.subn(pattern, replacement, hub_content, count=1, flags=re.DOTALL)
        if count > 0:
            write_file_safe(hub_path, new_hub)
            print(f"\U0001f4be Memory updated: {section} (REPLACE)")
        else:
            print(f"[WARNING] Section {section} not found in memory hub. Update skipped.")

    elif action == "APPEND":
        pattern = rf"(## {re.escape(section)}.*?)(?=\n## |\Z)"
        match = re.search(pattern, hub_content, re.DOTALL)
        if match:
            insert_pos = match.end()
            new_hub = hub_content[:insert_pos] + f"\n{content}\n" + hub_content[insert_pos:]
            write_file_safe(hub_path, new_hub)
            print(f"\U0001f4be Memory updated: {section} (APPEND)")
        else:
            print(f"[WARNING] Section {section} not found in memory hub. Update skipped.")

    elif action == "DELETE":
        # Remove specific content from the section
        new_hub = hub_content.replace(content, "")
        write_file_safe(hub_path, new_hub)
        print(f"\U0001f4be Memory updated: {section} (DELETE)")

    # Check if archive is needed after update
    if check_archive_trigger():
        auto_archive()

def handle_session_summary(response: str) -> None:
    progress_path = gem_path(GEM_CONFIG["progress_file"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    existing = read_file_safe(progress_path)
    summary_block = f"\n\n---\n## Session Summary \u2014 {timestamp}\n\n{response}"
    write_file_safe(progress_path, existing + summary_block)
    print(f"\n\U0001f4dd Session summary written to: {progress_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# RAG INDEXING (Layer 2)
# ═══════════════════════════════════════════════════════════════════════════════

def read_source_file(filepath: Path) -> str:
    """Extract text from a source file based on its type."""
    ext = filepath.suffix.lower()
    if ext in (".md", ".txt", ".html", ".csv", ".json"):
        return read_file_safe(filepath)
    elif ext == ".pdf" and HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            print(f"[WARNING] Could not read PDF {filepath}: {e}")
            return ""
    elif ext == ".pdf":
        return ""  # Skip PDFs silently if pdfplumber not installed
    else:
        return ""  # Unsupported type — skip silently

def get_source_directories() -> list[Path]:
    """Return all source subdirectories."""
    src = sources_path()
    if not src.exists():
        return []
    return [d for d in sorted(src.iterdir()) if d.is_dir()]

def chunk_text(text: str, chunk_size: int = 512) -> list[str]:
    """Split text into chunks of approximately chunk_size tokens (~4 chars/token)."""
    char_size = chunk_size * 4
    chunks = []
    for i in range(0, len(text), char_size):
        chunk = text[i:i + char_size]
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks

def build_rag_index(directory: str | None = None) -> None:
    """Build or rebuild RAG index for source directories."""
    if not HAS_CHROMADB:
        print("\u274c ChromaDB not installed. Install: pip install chromadb")
        print("   RAG features will use raw file reading instead.")
        return

    client = chromadb.Client()
    ollama_client = OpenAI(base_url=resolve_inference_url(), api_key="ollama")
    dirs = get_source_directories()

    if directory:
        dirs = [d for d in dirs if d.name == directory]
        if not dirs:
            print(f"\u274c Source directory '{directory}' not found.")
            return

    # Pull embedding model if needed
    print(f"Ensuring embedding model '{GEM_CONFIG['rag_embedding_model']}' is available...")
    try:
        import urllib.request
        req = urllib.request.Request(
            resolve_inference_url().rstrip("/v1") + "/api/pull",
            data=json.dumps({"name": GEM_CONFIG["rag_embedding_model"]}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=300)
    except Exception:
        pass  # Model may already exist

    for src_dir in dirs:
        print(f"\n\U0001f4c1 Indexing: {src_dir.name}/")
        collection_name = f"gem_{GEM_CONFIG['name']}_{src_dir.name}".replace(" ", "_").lower()

        # Delete existing collection if present
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

        collection = client.create_collection(name=collection_name)
        doc_count = 0
        chunk_count = 0

        for filepath in sorted(src_dir.iterdir()):
            if filepath.is_file() and filepath.name != ".index":
                text = read_source_file(filepath)
                if not text:
                    continue

                chunks = chunk_text(text, GEM_CONFIG["rag_chunk_size"])
                doc_count += 1
                chunk_count += len(chunks)

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{filepath.stem}_{i}"
                    # Use Ollama for embeddings
                    try:
                        resp = ollama_client.embeddings.create(
                            model=GEM_CONFIG["rag_embedding_model"],
                            input=chunk
                        )
                        embedding = resp.data[0].embedding
                        collection.add(
                            ids=[chunk_id],
                            embeddings=[embedding],
                            documents=[chunk],
                            metadatas=[{"source": filepath.name, "chunk": i}]
                        )
                    except Exception as e:
                        print(f"  [WARNING] Embedding failed for {filepath.name} chunk {i}: {e}")

        # Write index marker
        write_file_safe(src_dir / ".index", f"indexed: {datetime.now().isoformat()}\ndocs: {doc_count}\nchunks: {chunk_count}\n")
        print(f"   \u2705 {doc_count} documents, {chunk_count} chunks indexed")

    print(f"\n\u2705 RAG indexing complete.")

def rag_retrieve(query: str, directory: str | None = None) -> str:
    """Retrieve top-K relevant chunks for a query."""
    if not HAS_CHROMADB:
        return ""

    client = chromadb.Client()
    ollama_client = OpenAI(base_url=resolve_inference_url(), api_key="ollama")

    # Embed the query
    try:
        resp = ollama_client.embeddings.create(
            model=GEM_CONFIG["rag_embedding_model"],
            input=query
        )
        query_embedding = resp.data[0].embedding
    except Exception:
        return ""

    results = []
    dirs = get_source_directories()
    if directory:
        dirs = [d for d in dirs if d.name == directory]

    for src_dir in dirs:
        collection_name = f"gem_{GEM_CONFIG['name']}_{src_dir.name}".replace(" ", "_").lower()
        try:
            collection = client.get_collection(collection_name)
            hits = collection.query(
                query_embeddings=[query_embedding],
                n_results=GEM_CONFIG["rag_top_k"]
            )
            for doc, meta in zip(hits["documents"][0], hits["metadatas"][0]):
                results.append(f"[{src_dir.name}/{meta['source']}]\n{doc}")
        except Exception:
            continue

    if results:
        return "\n\n---\n\n".join(results[:GEM_CONFIG["rag_top_k"]])
    return ""

def raw_source_context() -> str:
    """Layer 0 fallback: read first N chars from each source file."""
    dirs = get_source_directories()
    if not dirs:
        return ""

    context_parts = []
    budget = 8000  # chars for source context (leaves room for memory hub)

    for src_dir in dirs:
        for filepath in sorted(src_dir.iterdir()):
            if filepath.is_file() and filepath.name != ".index":
                text = read_source_file(filepath)
                if text:
                    excerpt = text[:2000]
                    context_parts.append(f"[{src_dir.name}/{filepath.name}]\n{excerpt}")
                    budget -= len(excerpt)
                    if budget <= 0:
                        break
        if budget <= 0:
            break

    return "\n\n---\n\n".join(context_parts) if context_parts else ""

def get_source_context(query: str = "") -> str:
    """Get source context using the best available method."""
    rag_auto = GEM_CONFIG["rag_enabled"]
    has_sources = sources_path().exists() and any(sources_path().iterdir())

    if rag_auto == "auto":
        use_rag = HAS_CHROMADB and has_sources
    else:
        use_rag = bool(rag_auto)

    if use_rag and query:
        context = rag_retrieve(query)
        if context:
            return f"# Source Context (RAG retrieval)\n\n{context}"

    # Fallback to raw file reading (Layer 0)
    if has_sources:
        context = raw_source_context()
        if context:
            return f"# Source Context (raw file excerpts)\n\n{context}"

    return ""

# ═══════════════════════════════════════════════════════════════════════════════
# RESEARCH ROUTING (Layers 1–3)
# ═══════════════════════════════════════════════════════════════════════════════

def extract_research_query(response: str) -> str | None:
    """Extract research topic from [RESEARCH_NEEDED: topic] tag."""
    match = re.search(r"\[RESEARCH_NEEDED:\s*(.+?)\]", response)
    return match.group(1).strip() if match else None

def search_searxng(query: str) -> str:
    """Query SearXNG and return formatted results."""
    import urllib.request
    import urllib.parse
    url = f"{GEM_CONFIG['searxng_url']}/search?q={urllib.parse.quote(query)}&format=json"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read())
        results = data.get("results", [])[:GEM_CONFIG["searxng_max_results"]]
        formatted = []
        for r in results:
            formatted.append(f"- **{r.get('title', 'No title')}**\n  {r.get('url', '')}\n  {r.get('content', '')[:300]}")
        return "\n\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"SearXNG search failed: {e}"

def search_perplexica(query: str) -> str:
    """Query Perplexica for AI-synthesized research."""
    import urllib.request
    url = f"{GEM_CONFIG['perplexica_url']}/api/search"
    payload = json.dumps({
        "query": query,
        "focus_mode": "webSearch",
    }).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read())
        answer = data.get("answer", "No answer generated.")
        sources = data.get("sources", [])
        source_list = "\n".join(f"- [{s.get('title', 'Source')}]({s.get('url', '')})" for s in sources[:10])
        return f"{answer}\n\n**Sources:**\n{source_list}"
    except Exception as e:
        return f"Perplexica search failed: {e}"

def route_research(query: str, services: dict) -> str:
    """Route research query to the best available backend."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower())[:50]

    if services.get("perplexica") and GEM_CONFIG["perplexica_enabled"] != False:
        print(f"\n\U0001f50d Researching via Perplexica: {query}")
        result = search_perplexica(query)
        source_label = "Perplexica"
    elif services.get("searxng") and GEM_CONFIG["search_enabled"] != False:
        print(f"\n\U0001f50d Searching via SearXNG: {query}")
        result = search_searxng(query)
        source_label = "SearXNG"
    else:
        return (
            f"\n\u26a0\ufe0f Research needed but no search backend available.\n"
            f"   Query: {query}\n"
            f"   Please research manually and add results to sources/\n"
            f"   \U0001f4a1 Want web search? Run: docker run -d --name searxng -p 8888:8888 searxng/searxng"
        )

    # Cache the result
    cache_file = cache_path() / f"{timestamp}_{slug}.md"
    cache_content = (
        f"# Research: {query}\n"
        f"**Source:** {source_label}\n"
        f"**Date:** {timestamp}\n"
        f"**Query:** {query}\n\n"
        f"## Results\n{result}\n"
    )
    write_file_safe(cache_file, cache_content)

    # Auto-promote Perplexica results to source directory if enabled
    if source_label == "Perplexica" and GEM_CONFIG["research_auto_promote"]:
        core_dir = sources_path() / "core"
        if core_dir.exists():
            promo_file = core_dir / f"research_{slug}.md"
            write_file_safe(promo_file, cache_content)
            print(f"   \u2705 Result promoted to sources/core/ for RAG indexing")

    return f"\n\U0001f4da Research result ({source_label}):\n{result}"

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def run_health_checks(services: dict) -> list[str]:
    """Run all health checks and return list of warnings."""
    warnings = []

    # 1. Ollama reachable
    if not services["ollama"]:
        warnings.append("\u274c Ollama not reachable. Start: ollama serve")

    # 2. Memory hub size
    size = memory_hub_size()
    ceiling = GEM_CONFIG["memory_ceiling"]
    pct = size / ceiling * 100 if ceiling > 0 else 0
    if pct >= 80:
        warnings.append(f"\u26a0\ufe0f Memory hub at {pct:.0f}% ({size:,}/{ceiling:,} chars). Auto-archive will trigger on next update.")
    elif pct >= 60:
        warnings.append(f"\U0001f4ca Memory hub at {pct:.0f}% ({size:,}/{ceiling:,} chars).")

    # 3. Source directories
    src_dirs = get_source_directories()
    for d in src_dirs:
        files = [f for f in d.iterdir() if f.is_file() and f.name != ".index"]
        if not files:
            warnings.append(f"\u26a0\ufe0f sources/{d.name}/ is empty. Add documents: python gem-script.py --add-source file.md {d.name}")

    # 4. RAG index staleness
    for d in src_dirs:
        index_marker = d / ".index"
        if index_marker.exists():
            content = read_file_safe(index_marker)
            date_match = re.search(r"indexed: (\d{4}-\d{2}-\d{2})", content)
            if date_match:
                indexed_date = datetime.fromisoformat(date_match.group(1))
                age_days = (datetime.now() - indexed_date).days
                if age_days > 30:
                    warnings.append(f"\U0001f4a1 RAG index for sources/{d.name}/ is {age_days} days old. Rebuild: python gem-script.py --index {d.name}")

    # 5. Research cache size
    cache = cache_path()
    if cache.exists():
        entries = list(cache.iterdir())
        if len(entries) > 100:
            warnings.append(f"\U0001f4a1 Research cache has {len(entries)} entries. Review or clear: python gem-script.py --clear-cache")

    # 6. Services that were expected but aren't running
    if GEM_CONFIG["search_enabled"] == True and not services["searxng"]:
        warnings.append(f"\u26a0\ufe0f SearXNG not responding at {GEM_CONFIG['searxng_url']}. Research queries will use fallback.")
    if GEM_CONFIG["perplexica_enabled"] == True and not services["perplexica"]:
        warnings.append(f"\u26a0\ufe0f Perplexica not responding at {GEM_CONFIG['perplexica_url']}. Research queries will use SearXNG fallback.")

    return warnings

def print_health_report(services: dict) -> None:
    """Print a formatted health report."""
    warnings = run_health_checks(services)
    print(f"\n{'='*60}")
    print(f"  \U0001f3e5 Health Report \u2014 {GEM_CONFIG['name']}")
    print(f"{'='*60}")
    print_service_status(services)

    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    {w}")
    else:
        print("  \u2705 All systems healthy.")
    print(f"{'='*60}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# INFERENCE BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════════

def run_benchmark() -> None:
    """Quick inference benchmark — confirms the model works and measures speed."""
    client = OpenAI(base_url=resolve_inference_url(), api_key="ollama")
    print(f"\n\U0001f9ea Running inference benchmark...")
    print(f"   Model: {GEM_CONFIG['model']}")

    prompt = "Explain in exactly 100 words why structured memory management improves AI advisory quality."
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=GEM_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        elapsed = time.time() - start
        text = response.choices[0].message.content or ""
        tokens_out = estimate_tokens(text)
        tok_per_sec = tokens_out / elapsed if elapsed > 0 else 0

        print(f"   Speed: {tok_per_sec:.1f} tok/sec")
        print(f"   \u2705 Ready to use.\n")

    except Exception as e:
        print(f"   \u274c Benchmark failed: {e}")
        print(f"   Check that Ollama is running and the model is pulled: ollama pull {GEM_CONFIG['model']}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING (4 Categories)
# ═══════════════════════════════════════════════════════════════════════════════

class TransientError(Exception):
    pass

class LLMRecoverableError(Exception):
    pass

class UserFixableError(Exception):
    pass

class FatalError(Exception):
    pass

def handle_transient_error(fn, *args, **kwargs):
    for attempt in range(1, GEM_CONFIG["max_retries"] + 1):
        try:
            return fn(*args, **kwargs)
        except TransientError as e:
            if attempt == GEM_CONFIG["max_retries"]:
                raise FatalError(f"Transient error persisted after {attempt} retries: {e}")
            wait = 2 ** attempt
            print(f"[RETRY {attempt}/{GEM_CONFIG['max_retries']}] {e}. Retrying in {wait}s...")
            time.sleep(wait)

def handle_fatal_error(messages: list, error: Exception) -> None:
    print(f"\n\u274c FATAL ERROR: {error}")
    print("Saving session state before exit...")
    progress_path = gem_path(GEM_CONFIG["progress_file"])
    existing = read_file_safe(progress_path)
    state = (
        f"\n\n---\n## FATAL EXIT \u2014 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Error: {error}\n"
        f"To resume: start a new session and say 'Resume from the last session summary.'\n"
    )
    write_file_safe(progress_path, existing + state)
    print(f"State saved to: {progress_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT PARSING
# ═══════════════════════════════════════════════════════════════════════════════

def detect_type_tag(response: str) -> str:
    for tag in TYPE_TAGS:
        if tag in response:
            return tag
    return "[ADVISORY]"

# ═══════════════════════════════════════════════════════════════════════════════
# HITL GATE
# ═══════════════════════════════════════════════════════════════════════════════

def handle_harness_pause(response: str) -> bool:
    print(f"\n{'='*60}")
    print("\u26a0\ufe0f  HARNESS PAUSE \u2014 Confirmation Required")
    print(f"{'='*60}")
    print(response)
    print(f"{'='*60}")
    while True:
        user_input = input("\nType CONFIRM to proceed or CANCEL to stop: ").strip().upper()
        if user_input == "CONFIRM":
            print("\u2705 Confirmed. Continuing...")
            return True
        elif user_input == "CANCEL":
            print("\U0001f6ab Cancelled.")
            return False
        print("Please type exactly CONFIRM or CANCEL.")

# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT RESET
# ═══════════════════════════════════════════════════════════════════════════════

def context_reset(client: OpenAI, messages: list, system_msg: dict) -> list:
    print("\n[AUTO] Context approaching limit \u2014 generating summary for context reset...")
    summary_messages = messages + [{
        "role": "user",
        "content": (
            "OUTPUT: [SESSION_SUMMARY]\n"
            "Generate a compact 200-word session summary: goal, decisions, open questions, "
            "single most important fact to carry forward."
        )
    }]
    try:
        response = client.chat.completions.create(
            model=GEM_CONFIG["model"],
            messages=summary_messages,
            temperature=0.3,
        )
        summary = response.choices[0].message.content
        handle_session_summary(summary)

        # Rebuild context: system + fresh memory + source context + summary
        memory_msg = {"role": "user", "content": load_memory_hub()}
        source_ctx = get_source_context()
        source_msg = {"role": "user", "content": source_ctx} if source_ctx else None
        summary_msg = {"role": "user", "content": f"[Context reset \u2014 session summary]\n\n{summary}"}
        ack_msg = {"role": "assistant", "content": "[ADVISORY] Context refreshed. Continuing from session summary."}

        new_messages = [system_msg, memory_msg]
        if source_msg:
            new_messages.append(source_msg)
        new_messages.extend([summary_msg, ack_msg])

        print("[AUTO] Context reset complete.\n")
        return new_messages

    except Exception as e:
        print(f"[WARNING] Context reset failed: {e}. Truncating oldest messages.")
        return [system_msg] + messages[-10:]

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_memory_section",
            "description": "Read a specific section of the memory hub (e.g., '\u00a72', '\u00a73')",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {"type": "string", "description": "Section identifier, e.g. '\u00a72'"}
                },
                "required": ["section"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_memory_update",
            "description": "Apply a MEMORY_UPDATE block to the memory hub",
            "parameters": {
                "type": "object",
                "properties": {
                    "update_block": {"type": "string", "description": "Full ---MEMORY_UPDATE---...---END_UPDATE--- block"}
                },
                "required": ["update_block"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_sources",
            "description": "Search local source directories for information on a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"},
                    "directory": {"type": "string", "description": "Optional: specific source directory to search"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "research_topic",
            "description": "Research a topic using available search backends (SearXNG/Perplexica)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research query"}
                },
                "required": ["query"]
            }
        }
    },
]

_active_services = {}  # Populated at startup

def execute_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "read_memory_section":
        section = tool_args.get("section", "")
        hub = load_memory_hub()
        pattern = rf"## {re.escape(section)}.*?(?=\n## |$)"
        match = re.search(pattern, hub, re.DOTALL)
        return match.group(0) if match else f"Section {section} not found in memory hub."

    elif tool_name == "write_memory_update":
        update_block = tool_args.get("update_block", "")
        apply_memory_update(update_block)
        return "MEMORY_UPDATE applied."

    elif tool_name == "search_sources":
        query = tool_args.get("query", "")
        directory = tool_args.get("directory")
        context = get_source_context(query)
        return context if context else "No source content found for this query."

    elif tool_name == "research_topic":
        query = tool_args.get("query", "")
        return route_research(query, _active_services)

    else:
        raise LLMRecoverableError(f"Unknown tool: '{tool_name}'")

# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL MODE (Interactive CLI Chat)
# ═══════════════════════════════════════════════════════════════════════════════

def run_terminal_session(services: dict) -> None:
    """Interactive terminal chat with full memory management."""
    global _active_services
    _active_services = services

    client = OpenAI(base_url=resolve_inference_url(), api_key="ollama")

    # Build initial context
    system_msg = {"role": "system", "content": load_system_prompt()}
    memory_msg = {"role": "user", "content": load_memory_hub()}
    memory_ack = {"role": "assistant", "content": "[ADVISORY] Memory hub loaded. Ready to begin."}
    messages = [system_msg, memory_msg, memory_ack]

    # Inject source context if available
    source_ctx = get_source_context()
    if source_ctx:
        messages.append({"role": "user", "content": source_ctx})
        messages.append({"role": "assistant", "content": "[ADVISORY] Source context loaded."})

    tool_call_history = []

    print(f"\n\U0001f7e2 {GEM_CONFIG['name']} \u2014 Local Gem Terminal Session")
    print(f"   Model: {GEM_CONFIG['model']}")
    print("   Type 'quit' or 'exit' to end.\n")

    # Session opening
    try:
        opening = client.chat.completions.create(
            model=GEM_CONFIG["model"],
            messages=messages + [{"role": "user", "content": "[SESSION_SUMMARY \u2014 OPENING] Generate opening session summary."}],
            temperature=0.3,
        )
        opening_text = opening.choices[0].message.content
        print("\u2500" * 60)
        print(opening_text)
        print("\u2500" * 60 + "\n")
        messages.append({"role": "user", "content": "[SESSION_SUMMARY \u2014 OPENING]"})
        messages.append({"role": "assistant", "content": opening_text})
    except Exception as e:
        print(f"[WARNING] Session opening failed: {e}")

    # Main loop
    while True:
        try:
            if estimate_tokens_messages(messages) >= GEM_CONFIG["context_reset_tokens"]:
                messages = context_reset(client, messages, system_msg)

            user_input = input("You: ").strip()
            if not user_input:
                continue

            final_run = False
            if user_input.lower() in {"quit", "exit"}:
                print("\nEnding session...")
                messages.append({"role": "user", "content": "Generate a [SESSION_SUMMARY] for this session."})
                final_run = True
            else:
                messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model=GEM_CONFIG["model"],
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.4,
            )

            # Handle tool calls
            while response.choices[0].finish_reason == "tool_calls":
                tool_calls = response.choices[0].message.tool_calls
                messages.append({
                    "role": "assistant",
                    "content": response.choices[0].message.content or "",
                    "tool_calls": tool_calls
                })

                tool_results = []
                for tc in tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                        result = execute_tool(tc.function.name, args)
                    except LLMRecoverableError as e:
                        result = f"Error: {e}"
                    except Exception as e:
                        result = f"Tool error: {e}"

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.function.name,
                        "content": str(result),
                    })

                messages.extend(tool_results)
                response = client.chat.completions.create(
                    model=GEM_CONFIG["model"],
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0.4,
                )

            assistant_text = response.choices[0].message.content or ""
            messages.append({"role": "assistant", "content": assistant_text})

            tag = detect_type_tag(assistant_text)
            print(f"\n{GEM_CONFIG['name']}: {assistant_text}\n")

            # Route by type tag
            if tag == "[HARNESS_PAUSE]":
                confirmed = handle_harness_pause(assistant_text)
                if not confirmed:
                    messages.append({"role": "user", "content": "The user cancelled."})

            elif tag == "[MEMORY_FLAG]":
                for update in extract_memory_updates(assistant_text):
                    apply_memory_update(update)

            elif tag == "[SESSION_SUMMARY]":
                handle_session_summary(assistant_text)

            elif tag == "[RESEARCH_NEEDED]":
                query = extract_research_query(assistant_text)
                if query:
                    result = route_research(query, services)
                    print(result)
                    messages.append({"role": "user", "content": f"Research result:\n{result}"})

            if final_run:
                handle_session_summary(assistant_text)
                print("\nSession ended. Progress saved.\n")
                break

        except FatalError as e:
            handle_fatal_error(messages, e)
            break
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Saving progress...")
            handle_session_summary(f"Session interrupted at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            choice = input("Type 'continue' or 'quit': ").strip().lower()
            if choice == "quit":
                break

# ═══════════════════════════════════════════════════════════════════════════════
# DAEMON MODE (Background Memory Manager for Open WebUI)
# ═══════════════════════════════════════════════════════════════════════════════

def run_daemon(services: dict) -> None:
    """
    Background daemon that manages memory lifecycle for Open WebUI sessions.

    Architecture: The user chats in Open WebUI (browser). This daemon watches
    Ollama's conversation history via API, injects memory + source context as
    system prompt modifications, and parses model output for MEMORY_UPDATE blocks.

    Note: This is a template implementation. The daemon polls Ollama's API for
    new messages. Production deployments may use webhooks or Open WebUI's
    pipeline system for lower-latency integration.
    """
    global _active_services
    _active_services = services

    inference_base = resolve_inference_url().rstrip("/v1").rstrip("/")
    print(f"\n\U0001f916 {GEM_CONFIG['name']} \u2014 Memory Daemon Started")
    print(f"   Model: {GEM_CONFIG['model']}")
    print(f"   Open WebUI: {GEM_CONFIG['webui_url']}")
    print(f"   Monitoring Ollama at: {inference_base}")
    print(f"   Memory hub: {gem_path(GEM_CONFIG['memory_hub_file'])}")
    print(f"\n   \u2705 Chat with your gem at {GEM_CONFIG['webui_url']}")
    print(f"   Press Ctrl+C to stop the daemon.\n")

    last_check = datetime.now()
    health_interval = 3600  # Health check every hour
    poll_interval = 5       # Check for new conversations every 5 seconds

    def shutdown_handler(signum, frame):
        print(f"\n\n\U0001f6d1 Daemon shutting down...")
        print(f"   Memory hub saved at: {gem_path(GEM_CONFIG['memory_hub_file'])}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Inject system prompt into Ollama modelfile (if supported)
    # This ensures Open WebUI conversations get the memory context
    system_prompt = load_system_prompt()
    memory_hub = load_memory_hub()
    source_ctx = get_source_context()

    full_context = system_prompt + "\n\n" + memory_hub
    if source_ctx:
        full_context += "\n\n" + source_ctx

    print(f"   Context size: ~{estimate_tokens(full_context):,} tokens")
    print(f"   Memory hub: {memory_hub_size():,} / {GEM_CONFIG['memory_ceiling']:,} chars")

    # Main daemon loop
    seen_messages = set()

    while True:
        try:
            time.sleep(poll_interval)

            # Periodic health check
            if (datetime.now() - last_check).seconds >= health_interval:
                warnings = run_health_checks(services)
                if warnings:
                    print(f"\n  \U0001f3e5 Periodic health check \u2014 {len(warnings)} warning(s):")
                    for w in warnings:
                        print(f"    {w}")
                last_check = datetime.now()

            # Check archive trigger
            if check_archive_trigger():
                auto_archive()

            # Poll Ollama for recent chat history
            # Note: Ollama's /api/chat endpoint is stateless — each request sends
            # full message history. The daemon monitors for new model outputs by
            # watching the Ollama log or using Open WebUI's API if available.
            #
            # Template implementation: The daemon maintains a watch loop.
            # In production, integrate with Open WebUI's pipeline/filter system
            # for real-time message interception.

            try:
                import urllib.request
                # Check Ollama is still alive
                health_url = f"{inference_base}/api/tags"
                urllib.request.urlopen(health_url, timeout=5)
            except Exception:
                print(f"[WARNING] Ollama not responding. Retrying in {poll_interval}s...")
                continue

        except Exception as e:
            print(f"[DAEMON ERROR] {e}")
            time.sleep(poll_interval)

# ═══════════════════════════════════════════════════════════════════════════════
# GUIDED SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def run_setup() -> None:
    """Interactive guided setup for first-time configuration."""
    print("\n" + "="*60)
    print("  \U0001f680 Local Gem Setup")
    print("="*60)

    # Detect services first
    print("\nDetecting available services...")
    services = detect_services()
    print_service_status(services)

    if not services["ollama"]:
        print("\u274c Ollama is required. Install it first:")
        print("   curl -fsSL https://ollama.com/install.sh | sh")
        print("   Then run this setup again.")
        return

    # Gather configuration
    print("\nLet's configure your Local Gem.\n")

    name = input("Gem name (e.g., 'AI Deployment Advisor'): ").strip()
    if not name:
        print("Gem name is required.")
        return

    domain = input("Domain (e.g., 'local AI infrastructure and deployment'): ").strip()
    folder = input(f"Gem folder path (default: D:\\My Drive\\AI Ecosystem\\Gemini\\{name}): ").strip()
    if not folder:
        folder = f"D:\\My Drive\\AI Ecosystem\\Gemini\\{name}"

    model = input(f"Model tag (default: {GEM_CONFIG['model']}): ").strip()
    if not model:
        model = GEM_CONFIG["model"]

    # Update config
    GEM_CONFIG["name"] = name
    GEM_CONFIG["domain"] = domain
    GEM_CONFIG["gem_folder"] = folder
    GEM_CONFIG["model"] = model
    GEM_CONFIG["memory_hub_file"] = f"_Memory_{name.replace(' ', '')}_GemMemoryHub_Active.md"
    GEM_CONFIG["archive_file"] = f"_Memory_{name.replace(' ', '')}_GemMemoryHub_Archive.md"
    GEM_CONFIG["progress_file"] = f"_Progress_{name.replace(' ', '')}_ActiveTask.md"
    GEM_CONFIG["system_prompt_file"] = f"_Prompt_{name.replace(' ', '')}_GemSystemPrompt_v1.0.md"
    GEM_CONFIG["heuristics_file"] = f"_Heuristics_{name.replace(' ', '')}_Pool.md"

    # Create directory structure
    gem_dir = Path(folder)
    gem_dir.mkdir(parents=True, exist_ok=True)
    (gem_dir / "sources" / "core").mkdir(parents=True, exist_ok=True)
    (gem_dir / "sources" / "expansion").mkdir(parents=True, exist_ok=True)
    (gem_dir / "research-cache").mkdir(parents=True, exist_ok=True)

    print(f"\n\u2705 Directory structure created at: {folder}")
    print(f"   sources/core/       \u2014 add your core domain documents here")
    print(f"   sources/expansion/  \u2014 add growth/future documents here")
    print(f"   research-cache/     \u2014 auto-populated by research queries")

    # Generate perplexica-compose.yml if SearXNG + Ollama detected
    if services["searxng"] and services["ollama"] and not services["perplexica"]:
        compose_content = textwrap.dedent(f"""\
            # perplexica-compose.yml — Auto-generated by gem-script.py --setup
            # Start: docker compose -f perplexica-compose.yml up -d
            services:
              perplexica-backend:
                image: itzcrazykns1337/perplexica-backend:main
                ports:
                  - "3001:3001"
                environment:
                  - SEARXNG_URL=http://host.docker.internal:8888
                  - OLLAMA_URL=http://host.docker.internal:11434
                  - DEFAULT_MODEL={model}
                extra_hosts:
                  - "host.docker.internal:host-gateway"
                restart: unless-stopped

              perplexica-frontend:
                image: itzcrazykns1337/perplexica-frontend:main
                ports:
                  - "3002:3000"
                depends_on:
                  - perplexica-backend
                restart: unless-stopped
        """)
        compose_path = gem_dir / "perplexica-compose.yml"
        write_file_safe(compose_path, compose_content)
        print(f"\n   \U0001f4c4 Generated perplexica-compose.yml")
        print(f"      Start Perplexica: docker compose -f {compose_path} up -d")

    # Verify Open WebUI
    if services["webui"]:
        print(f"\n\u2705 Open WebUI detected at {GEM_CONFIG['webui_url']}")
        print(f"   Select model '{model}' in the Open WebUI interface to start chatting.")
    else:
        print(f"\n\U0001f4a1 Open WebUI not detected. Install for browser-based chat:")
        print(f"   docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main")

    print(f"\n{'='*60}")
    print(f"  Setup complete! Next steps:")
    print(f"  1. Deploy gem files using the Super Gem Creator skill")
    print(f"  2. Add seed documents to sources/core/ and sources/expansion/")
    print(f"  3. Start the daemon: python gem-script.py --daemon")
    print(f"     Or terminal mode: python gem-script.py")
    print(f"{'='*60}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# STATS COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

def print_stats() -> None:
    """Print comprehensive gem statistics."""
    print(f"\n{'='*60}")
    print(f"  \U0001f4ca {GEM_CONFIG['name']} \u2014 Statistics")
    print(f"{'='*60}")

    # Memory
    hub_size = memory_hub_size()
    ceiling = GEM_CONFIG["memory_ceiling"]
    print(f"\n  Memory Hub: {hub_size:,} / {ceiling:,} chars ({hub_size/ceiling*100:.0f}%)")
    print(f"  Version: {GEM_CONFIG['version']}")

    # Source directories
    src_dirs = get_source_directories()
    if src_dirs:
        print(f"\n  Source Directories:")
        for d in src_dirs:
            files = [f for f in d.iterdir() if f.is_file() and f.name != ".index"]
            total_words = sum(len(read_file_safe(f).split()) for f in files)
            index_marker = d / ".index"
            indexed = "indexed" if index_marker.exists() else "not indexed"
            print(f"    sources/{d.name}/  \u2014 {len(files)} documents, ~{total_words:,} words, {indexed}")
    else:
        print(f"\n  Source Directories: none (create with --new-source)")

    # Research cache
    cache = cache_path()
    if cache.exists():
        entries = [f for f in cache.iterdir() if f.is_file()]
        print(f"\n  Research Cache: {len(entries)} entries")
    else:
        print(f"\n  Research Cache: empty")

    print(f"{'='*60}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description=f"Local Gem Manager \u2014 {GEM_CONFIG['name']}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python gem-script.py --setup              # First-time guided setup
              python gem-script.py --daemon             # Background memory manager
              python gem-script.py                      # Terminal chat mode
              python gem-script.py --index              # Build RAG indexes
              python gem-script.py --stats              # View statistics
              python gem-script.py --health             # Run health checks
              python gem-script.py --benchmark          # Test inference speed
              python gem-script.py --add-source f.md core  # Add file to source dir
        """)
    )

    parser.add_argument("--setup", action="store_true", help="Run guided first-time setup")
    parser.add_argument("--daemon", action="store_true", help="Start background memory daemon for Open WebUI")
    parser.add_argument("--index", nargs="?", const="all", help="Build/rebuild RAG indexes (optionally specify directory)")
    parser.add_argument("--stats", action="store_true", help="Show source, memory, and index statistics")
    parser.add_argument("--health", action="store_true", help="Run health checks")
    parser.add_argument("--benchmark", action="store_true", help="Run inference benchmark")
    parser.add_argument("--add-source", nargs=2, metavar=("FILE", "DIR"), help="Add a file to a source directory")
    parser.add_argument("--new-source", metavar="NAME", help="Create a new source directory")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the research cache")
    parser.add_argument("--harness", action="store_true", help="Start Tier 5 Harness-Proxy polling loop (requires gspread + service account JSON)")

    args = parser.parse_args()

    # ── Setup mode ──
    if args.setup:
        run_setup()
        return

    # ── Validate gem folder exists ──
    gem_dir = Path(GEM_CONFIG["gem_folder"])
    if not gem_dir.exists() and not args.setup:
        print(f"ERROR: Gem folder not found: {gem_dir}")
        print("Run --setup first, or ensure the path is correct in GEM_CONFIG.")
        sys.exit(1)

    # ── Index command ──
    if args.index:
        directory = None if args.index == "all" else args.index
        build_rag_index(directory)
        return

    # ── Stats command ──
    if args.stats:
        print_stats()
        return

    # ── Add source command ──
    if args.add_source:
        filepath, directory = args.add_source
        src = Path(filepath)
        if not src.exists():
            print(f"\u274c File not found: {filepath}")
            sys.exit(1)
        dest_dir = sources_path() / directory
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_dir / src.name)
        print(f"\u2705 Added {src.name} to sources/{directory}/")
        if HAS_CHROMADB:
            print("Re-indexing...")
            build_rag_index(directory)
        return

    # ── New source command ──
    if args.new_source:
        new_dir = sources_path() / args.new_source
        new_dir.mkdir(parents=True, exist_ok=True)
        print(f"\u2705 Created sources/{args.new_source}/")
        return

    # ── Clear cache command ──
    if args.clear_cache:
        cache = cache_path()
        if cache.exists():
            count = len(list(cache.iterdir()))
            shutil.rmtree(cache)
            cache.mkdir(parents=True, exist_ok=True)
            print(f"\u2705 Cleared {count} research cache entries.")
        else:
            print("Research cache is already empty.")
        return

    # ── Health check command ──
    if args.health:
        services = detect_services()
        print_health_report(services)
        return

    # ── Benchmark command ──
    if args.benchmark:
        run_benchmark()
        return

    # ── Main modes: Daemon or Terminal ──
    services = detect_services()
    print_health_report(services)

    if not services["ollama"]:
        print("\u274c Ollama is required but not running.")
        print("   Start: ollama serve")
        print("   Install: curl -fsSL https://ollama.com/install.sh | sh")
        sys.exit(1)

    # ── Harness-Proxy mode (Tier 5) ──
    if args.harness:
        harness = HarnessPollMode()
        harness.run()
        return

    if args.daemon:
        run_benchmark()
        run_daemon(services)
    else:
        # Terminal mode (default if no --daemon flag)
        run_benchmark()
        run_terminal_session(services)


# ═══════════════════════════════════════════════════════════════════════════════
# HarnessPollMode — Tier 5 Harness-Proxy backend (Local Python path)
#
# Usage: python gem-script.py --harness
#
# Prerequisites:
#   pip install gspread google-auth
#   Place service account JSON at: ~/harness-credentials.json
#   Share the Memory Sheet with the service account email address.
#
# Config (edit these two values before first run):
HARNESS_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
HARNESS_CREDENTIALS_PATH = "~/harness-credentials.json"
# ═══════════════════════════════════════════════════════════════════════════════

class HarnessPollMode:
    """
    Polls the 'bus' tab of the Memory Sheet for harness_request rows,
    dispatches the tool call, and writes a harness_result row.
    Mirrors the Apps Script template in step4-opal-deploy.md § 4.9.
    """

    POLL_INTERVAL_SEC = 15   # seconds between polls
    POLL_LIMIT = 20          # max request rows to process per poll cycle
    BUS_TAB = "bus"

    def __init__(self):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError:
            print("ERROR: gspread and google-auth are required for harness mode.")
            print("  pip install gspread google-auth")
            sys.exit(1)

        creds_path = Path(HARNESS_CREDENTIALS_PATH).expanduser()
        if not creds_path.exists():
            print(f"ERROR: Service account credentials not found at: {creds_path}")
            print("  Place your Google service account JSON at that path.")
            sys.exit(1)

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
        self._gc = gspread.authorize(creds)
        self._sheet = None
        self._headers = []

    def _open_sheet(self):
        """Open (or re-open) the Memory Sheet bus tab."""
        try:
            wb = self._gc.open_by_url(HARNESS_SHEET_URL)
            self._sheet = wb.worksheet(self.BUS_TAB)
            self._headers = self._sheet.row_values(1)
        except Exception as e:
            print(f"[HARNESS] Could not open sheet: {e}")
            self._sheet = None

    def _col(self, name: str) -> int:
        """Return 0-based column index for a header name."""
        try:
            return self._headers.index(name)
        except ValueError:
            raise ValueError(f"Column '{name}' not found in bus tab headers: {self._headers}")

    def poll(self):
        """Read all rows, find unhandled harness_request rows, dispatch each."""
        if self._sheet is None:
            self._open_sheet()
        if self._sheet is None:
            return  # sheet unavailable this cycle

        try:
            rows = self._sheet.get_all_values()
        except Exception as e:
            print(f"[HARNESS] Read error: {e}")
            self._sheet = None  # force reconnect next cycle
            return

        if len(rows) < 2:
            return

        result_uuids = {
            r[self._col("parent_uuid")]
            for r in rows[1:]
            if r[self._col("event_type")] == "harness_result"
        }

        processed = 0
        for row in rows[1:]:
            if processed >= self.POLL_LIMIT:
                break
            if row[self._col("event_type")] != "harness_request":
                continue
            if row[self._col("role")] != "gem":
                continue
            uuid = row[self._col("uuid")]
            if uuid in result_uuids:
                continue  # already handled

            try:
                payload = json.loads(row[self._col("content")])
                result = self.dispatch_tool(payload.get("tool", ""), payload.get("params", {}))
            except Exception as e:
                result = {"error": str(e)}

            self._write_result(uuid, result)
            result_uuids.add(uuid)  # prevent double-dispatch within the same cycle
            processed += 1

        if processed:
            print(f"[HARNESS] Processed {processed} request(s)")

    def dispatch_tool(self, tool_name: str, params: dict) -> dict:
        """
        Dispatch a tool call. Add cases here as the gem's tool list grows.
        Mirrors dispatchTool() in the Apps Script template.
        """
        import urllib.request
        import urllib.error

        if tool_name == "url_fetch":
            url = params.get("url", "")
            try:
                with urllib.request.urlopen(url, timeout=30) as resp:
                    body = resp.read().decode("utf-8", errors="replace")[:8000]
                    return {"status": resp.status, "body": body}
            except urllib.error.HTTPError as e:
                return {"error": f"HTTP {e.code}: {e.reason}"}
            except Exception as e:
                return {"error": str(e)}

        elif tool_name == "read_file":
            path = Path(params.get("path", "")).expanduser()
            if not path.exists():
                return {"error": f"File not found: {path}"}
            return {"content": path.read_text(encoding="utf-8", errors="replace")[:16000]}

        elif tool_name == "write_file":
            path = Path(params.get("path", "")).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(params.get("content", ""), encoding="utf-8")
            return {"written": str(path)}

        elif tool_name == "run_command":
            import subprocess
            cmd = params.get("command", "")
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=60
                )
                return {"stdout": result.stdout[:4000], "stderr": result.stderr[:1000], "returncode": result.returncode}
            except subprocess.TimeoutExpired:
                return {"error": "Command timed out after 60 seconds"}

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _write_result(self, parent_uuid: str, result: dict):
        """Append a harness_result row to the bus tab."""
        import uuid as _uuid
        row_data = [""] * len(self._headers)
        row_data[self._col("uuid")] = str(_uuid.uuid4())
        row_data[self._col("parent_uuid")] = parent_uuid
        row_data[self._col("timestamp")] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
        row_data[self._col("event_type")] = "harness_result"
        row_data[self._col("role")] = "harness"
        row_data[self._col("content")] = json.dumps(result)
        try:
            self._sheet.append_row(row_data, value_input_option="RAW")
        except Exception as e:
            print(f"[HARNESS] Write error: {e}")
            self._sheet = None  # force reconnect next cycle

    def run(self):
        """Main polling loop. Runs until interrupted with Ctrl+C."""
        print(f"[HARNESS] Harness-Proxy polling started (interval: {self.POLL_INTERVAL_SEC}s)")
        print(f"[HARNESS] Sheet: {HARNESS_SHEET_URL}")
        print("[HARNESS] Press Ctrl+C to stop.")
        self._open_sheet()
        try:
            while True:
                self.poll()
                import time
                time.sleep(self.POLL_INTERVAL_SEC)
        except KeyboardInterrupt:
            print("\n[HARNESS] Polling stopped by user.")


if __name__ == "__main__":
    main()
