# Prompt Crystallization Request

## Input

[Paste existing AI agent instructions here]

## Crystallization Instructions

Compress these instructions according to the following principles:

1. **Preserve Intent**: The fundamental purpose (WHY) of each instruction must be maintained
2. **High-Resolution Tokenization**:
   - Long explanations → Replace with core domain concepts, key figures, or framework references
   - Example: Long negotiation strategy explanation → "BATNA principle"
3. **Leverage Implicit Knowledge**:
   - For concepts the LLM already knows, provide only activation signals ("Apply", "Reference", "According to the principle of")
   - Point to concepts rather than explaining them
4. **Conditional Expansion Structure**:
   - Format details as "[Condition] → [Action]"
   - Utilize the "Generate on demand if needed" pattern
5. **Deduplication**: Consolidate identical intents repeated across different expressions

## Output Format

### Compressed Prompt

[Compression Result]

### Compression Map

| Original Section | Compressed Form | High-Resolution Token Used | Activated Semantic Network |
| ---------------- | --------------- | -------------------------- | -------------------------- |

### Meta-Analysis

- Compression Ratio: X%
- Potential Information Loss Areas:
- Verification Requirements:
