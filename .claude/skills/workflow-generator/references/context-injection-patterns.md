# Context Injection Patterns for Sub-Agents

Three patterns for passing context to a Sub-agent or Agent Team within a workflow.
The optimal pattern is selected based on the scale and information density of the input data.

> **The selection criterion is quality.** Choose the pattern that yields the highest final deliverable quality, not speed or token cost.

---

## Pattern A: Full Delegation (Default)

Pass only the file path to the agent; the agent reads and processes it directly.

```markdown
### 2. Data Analysis
- **Agent**: `@analyzer`
- **Input**: `research/collected-data.md` (pass file path)
- **Task**: Read the file directly and derive core insights
- **Output**: `analysis/insights.md`
```

**When to use:**
- 1-3 input files, each small in size (< 50KB)
- The agent requires full context
- Information density: O(1) — core information is independent of input size

**Sub-agent vs Agent Team:**
- **Sub-agent**: When a single specialist conducts in-depth analysis while maintaining context
- **Agent Team**: Not applicable (excessive structure for small inputs)

---

## Pattern B: Filtered Delegation (RLM Code-based Filtering)

A pre-processing script extracts only the relevant portions from the input and passes them to the agent.

```markdown
### 2. Target Section Analysis
- **Pre-processing**: `scripts/extract_sections.py`
  - Input: `raw-document.md` (200KB)
  - Processing: Extract only "## Results" through "## Discussion" sections using regex
  - Output: `temp/filtered-sections.md` (15KB)
- **Agent**: `@deep-analyzer`
- **Input**: `temp/filtered-sections.md` (refined input)
- **Task**: Perform in-depth analysis on extracted sections
- **Output**: `analysis/section-analysis.md`
- **Post-processing**: `scripts/validate_references.py`
  - Verify that references in the analysis match the source
```

**When to use:**
- Large input (> 50KB), where only a portion is relevant
- The agent must focus on specific patterns or sections
- Information density: O(N) — core information scales proportionally with input size

**Pre-processing Script Design (P1 Compliance):**

| Filtering Type | Process in Python | Process in Agent |
|---|---|---|
| Date/keyword filter | O | X |
| Section extraction (regex) | O | X |
| Deduplication (hash) | O | X |
| Format conversion (HTML→MD) | O | X |
| Semantic relevance judgment | X | O |
| Quality/importance evaluation | X | O |

**Sub-agent vs Agent Team:**
- **Sub-agent**: When maintaining deep context over the filtered data is critical
- **Agent Team**: When different specialists analyze different types of filtered results

---

## Pattern C: Recursive Decomposition (RLM Recursive Sub-call)

The Orchestrator splits the input into N chunks, delegates each chunk to parallel agents, and merges the results.

```markdown
### 2. (team) Large-Scale Document Analysis
- **Pre-processing**: `scripts/chunk_document.py`
  - Input: `corpus/full-dataset.md` (500KB)
  - Processing: Split into N chunks along logical units (respecting section/chapter boundaries)
  - Output: `temp/chunk-001.md` ~ `temp/chunk-010.md`
- **Team**: `analysis-pipeline`
- **Tasks**:
  - `@analyst-1`: Analyze `temp/chunk-001.md` ~ `temp/chunk-003.md`
  - `@analyst-2`: Analyze `temp/chunk-004.md` ~ `temp/chunk-006.md`
  - `@analyst-3`: Analyze `temp/chunk-007.md` ~ `temp/chunk-010.md`
- **Join**: Team Lead merges results after all analyses complete
- **Post-processing**: `scripts/merge_analyses.py`
  - Synthesize analysis results per chunk
  - Deduplicate findings, link cross-references
- **Output**: `analysis/comprehensive-report.md`
```

**When to use:**
- Very large input (> 200KB), impossible for a single agent to process as a whole
- Partitionable structure (chapters, sections, records, etc.)
- Information density: O(N²) — high-density data requiring cross-references

**Chunk Partitioning Strategy (P1 Compliance):**

```python
# scripts/chunk_document.py design principles
#
# 1. Respect logical boundaries: do not split in the middle of sentences/paragraphs
# 2. Allow overlap: 1-2 paragraph overlap at boundaries between chunks → prevent context loss
# 3. Preserve metadata: include original source location info in each chunk
# 4. Balanced sizing: minimize size variance across chunks
```

**Sub-agent vs Agent Team:**
- **Sub-agent**: Sequential processing when strong dependencies exist between chunks (prioritizing context transfer accuracy)
- **Agent Team**: Parallel processing when chunks are independent (each specialist focuses 100% on their respective domain)

**SOT Invariants (when using Agent Team):**
- Only Team Lead writes to SOT (state.yaml)
- Each teammate produces analysis results as separate deliverable files
- Team Lead synthesizes deliverables and updates SOT

---

## Pattern Selection Guide

```
Input size < 50KB → Pattern A (Full Delegation)
Input size 50-200KB + identifiable relevant sections → Pattern B (Filtered)
Input size > 200KB or partitioning required → Pattern C (Recursive)
```

> **Absolute Criterion 1 Priority**: The guide above provides baseline recommendations. Even if the input is small, if Pattern B filtering increases the agent's analytical accuracy, use Pattern B. The selection criterion is always **the quality of the final deliverable**.

---

## Translation Considerations (English-First Execution)

In accordance with AGENTS.md §5.2, workflow execution is conducted in English, and text deliverables are translated into the target language by the `@translator` sub-agent. Translation handling differs across patterns.

### Translation Mapping by Pattern

| Pattern | Translation Timing | Glossary Management | Notes |
|---|---|---|---|
| **Pattern A** | Single invocation of `@translator` upon step completion | Single file — no conflicts | Simplest |
| **Pattern B** | Invoke `@translator` on filtered deliverable | Single file — no conflicts | Pre-processing outputs do not require translation |
| **Pattern C** | Invoke `@translator` on final merged deliverable **after Join** | Shared `translations/glossary.yaml` mandatory | See details below |

### Pattern C: Terminology Consistency Across Chunks

When parallel agents process independent chunks, if each agent translates identical domain terms differently, consistency of the final deliverable is compromised.

**Resolution Strategy: Join-then-Translate**

```markdown
### N. (team) Large-Scale Document Analysis
- **Team**: `analysis-pipeline`
- **Tasks**: (Each analyst performs analysis in English)
- **Join**: Team Lead merges English results → `analysis/report.md`
- **Translation**: `@translator`
  - Input: `analysis/report.md` (merged final English deliverable)
  - Glossary: `translations/glossary.yaml` (domain terminology consistency)
  - Output: `analysis/report.ko.md`
```

**Core Rules:**
1. Do not translate individual chunks separately — translating once after merging guarantees terminology consistency
2. Pre-define core domain terms in `translations/glossary.yaml` and pass to `@translator`
3. Intermediate deliverables (temp/ directory) are excluded from translation — translate only final deliverables

**Exception: When per-chunk translation is required**

In rare cases where intermediate deliverables of each chunk are directly delivered to users (e.g., independent chapter-by-chapter releases), pass the shared glossary to each agent to maintain consistency:

```markdown
- **Tasks**:
  - `@analyst-1`: Analyze chunk-001~003 + `@translator` (reference glossary)
  - `@analyst-2`: Analyze chunk-004~006 + `@translator` (reference glossary)
- **Glossary**: `translations/glossary.yaml` (all agents read the same glossary read-only)
```

---

## RLM Theoretical Foundation

These three patterns correspond to core patterns in the Recursive Language Models (MIT CSAIL, 2025) paper:

| RLM Pattern | Context Injection Mapping | Core Principle |
|---|---|---|
| Direct context access | Pattern A: Full Delegation | Process small inputs directly |
| Code-based Filtering | Pattern B: Filtered Delegation | Select relevant portions with code before passing to LM |
| Recursive Sub-call + Chunking | Pattern C: Recursive Decomposition | Partition input and process via recursive sub-LM calls |

> **Core Principle**: "Do not feed prompts directly into neural networks; treat them as external environment objects and explore them programmatically."
> In all patterns, Python (deterministic) refines data, and AI (probabilistic) focuses on reasoning over refined data (P1 principle).
