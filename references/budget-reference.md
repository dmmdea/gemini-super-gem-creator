# 32K Per-Turn Budget Breakdown (Informational)

The consumer Gemini web app allocates ~32,000 tokens per turn. Every component competes for this budget. Understanding it explains WHY size limits matter.

## Budget Allocation (Approximate)

| Component | Loaded How | Typical Cost | Notes |
|-----------|-----------|-------------|-------|
| System prompt | **IN FULL every turn** | ~420–700 tokens (1,500–2,500 chars) | Most expensive — never trimmed. This is why ≤2,000 chars matters. |
| Notebooks (each) | Grounding layer (RAG) | ~3,000–5,000 tokens per notebook | Standard = 2 NBs (~6–10K). Research = up to 5 (~15–25K). |
| Knowledge files (Drive) | RAG retrieval | ~1,000–3,000 tokens (chunks, not full files) | Cheaper than notebooks. File size affects chunk quality, not total cost. |
| Conversation history | Sliding window | Variable — grows per turn | Gemini manages automatically; older turns dropped. |
| Model reasoning + output | Generation | Remainder of budget | What's left after all inputs loaded. |

## Standard Gem Budget Math

- System prompt (2,000 chars): ~560 tokens
- 2 notebooks: ~6,000–10,000 tokens
- Knowledge files (Hub + tri-file): ~1,500–3,000 tokens
- Conversation history: ~5,000–10,000 tokens
- **Remaining for reasoning + output: ~9,000–19,000 tokens**

## Research Gem Budget Math

- System prompt (1,500 chars): ~420 tokens
- 5 notebooks: ~15,000–25,000 tokens
- Knowledge files: ~1,500–3,000 tokens
- Conversation history: ~3,000–5,000 tokens
- **Remaining for reasoning + output: ~0–12,000 tokens** ← Why Research needs lean prompt + lean hub

## Key Takeaway

Every KB added to the memory hub, every file in Knowledge, and every character in the prompt directly reduces tokens available for the gem's reasoning and response quality. Size limits protect the gem's ability to think.
