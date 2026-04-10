# Shared Principles Registry Template

Use this skeleton when generating `_Registry_SharedPrinciples.md` at the user's Drive root (above individual gem folders). This file is optional — only needed when a user has 2+ gems and wants learnings to compound across them.

**Purpose:** Prevent siloed knowledge. When Gem A discovers that "always verify VRAM before suggesting models", that rule shouldn't have to be re-learned by Gem B. The Shared Principles Registry is the cross-gem memory layer that makes the entire gem ecosystem smarter over time.

---

## Template

```markdown
# Shared Principles Registry

> **Version:** 1.0.0
> **Last updated:** [Date]
> **Owner:** [User name]
> **Scope:** All gems at [Drive root path]

---

## Active Principles

Rules validated across multiple gems or explicitly promoted by the user. Every gem that has this file in its Knowledge sources should check these before answering.

| Principle | Source Gem | Added | Applied To | Notes |
|-----------|-----------|-------|-----------|-------|
| _(empty at creation — principles are promoted from individual gem memory hubs)_ | — | — | — | — |

---

## Candidate Principles (pending cross-gem validation)

Principles observed in one gem that might apply more broadly. Promoted to Active after confirmed useful in a second gem.

- _(empty at creation)_

---

## Gem Registry

> See `_Registry_GemInventory.md` at the Drive root for the full gem inventory (includes Tier, Engine, Last Audit columns).

---

## Promotion Rules

**Gem Memory Hub § → Shared Principles:**
1. A principle appears in §2 or §8 of one gem
2. The user or Claude notices it would apply to another gem
3. Claude proposes promotion via a direct edit (not MEMORY_UPDATE — this file is registry-level, not gem-level)
4. User confirms
5. Principle added here + seeded into the target gem's §2 or §8 at next session

**Demotion:** If a principle is overridden in 2+ gems, it moves to Retired with a note.

---

## Retired Principles

| Principle | Retired | Reason |
|-----------|---------|--------|
| _(empty at creation)_ | — | — |

---

## Multi-Gem ADK Architecture (Tier 3 — Advanced)

> **Read this only if you're building a Tier 3 multi-agent setup (ADK/API). Skip for consumer gem (Tier 1) or Opal (Tier 2).**

When multiple gems are orchestrated via the Google Agent Development Kit (ADK), the Shared Principles Registry becomes the shared context injected into all sub-agents. Architecture pattern:

```
Orchestrator Agent
├── Reads _Registry_SharedPrinciples.md (shared context for all)
├── Sub-Agent: [Gem A] — specialized domain advisor
│   ├── Reads GemA_MemoryHub_Active.md
│   └── Reports back to orchestrator
├── Sub-Agent: [Gem B] — specialized domain advisor
│   ├── Reads GemB_MemoryHub_Active.md
│   └── Reports back to orchestrator
└── Synthesis: orchestrator merges outputs, applies shared principles, delivers unified response
```

**Key rules for ADK multi-gem setups:**
- The Shared Principles Registry is the only file read by the orchestrator — individual gem memory hubs stay private to each sub-agent
- Thought Signatures are mandatory in Gemini 3 API multi-step calls (see §16 in `references/gemini-gems-specs-and-limits.md`) — pass the `thought_signature` from each response back in the next request
- Max 3 active sub-agents per orchestration call (context overhead — same limit as personas per gem)
- Cross-agent MEMORY_UPDATEs go through the orchestrator — never let sub-agents update each other's memory hubs directly
- All hard limits from the gem architecture still apply per sub-agent: 2,500-char system prompt, 2 notebooks (Standard) or up to 5 (Research), monolithic memory hub

**When to use ADK vs Opal vs consumer gem:**
- Gem needs web search, spreadsheets, or code execution → Opal (Tier 2, no code required)
- Multiple specialist gems need to collaborate in real time → ADK orchestration (Tier 3)
- Everything else → consumer gem on gemini.google.com (Tier 1)
```

---

## Notes for Generation

When generating this file for a user:

- **Only create if user has 2+ gems** — single-gem users don't need this file
- **File location:** Drive root above individual gem folders, not inside any gem's folder
- **File naming:** `_Registry_SharedPrinciples.md` — the leading underscore keeps it at the top of Drive folder listings
- **Attachment:** This file CAN be attached to gems as a Knowledge source (unlike the Heuristics Pool). Add it as the gem's Drive folder file alongside the Memory Hub — though it counts against the Knowledge slot budget, so only attach if the user has multiple gems where cross-pollination is high-value
- **Seeding from existing gems:** When creating this file for a user who already has gems, scan each existing gem's §2 and §8 for principles that could generalize. Propose them as candidates — don't assume they apply everywhere
- **Cross-reference:** After creating this file, note its path in the new gem's system prompt: "Check `_Registry_SharedPrinciples.md` at [Drive root] for cross-gem rules before answering."
