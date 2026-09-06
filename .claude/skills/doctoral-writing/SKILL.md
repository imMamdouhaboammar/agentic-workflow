---
name: doctoral-writing
description: Doctoral dissertation and thesis writing skill. Delivers academic prose combining rigorous scholarly standards with high readability. Supports academic conventions across the humanities, social sciences, and natural sciences. Use when the user requests "write in thesis style", "academic writing", "doctoral prose", "polish academic sentences", "refine with scholarly phrasing", or related tasks. Applies to dissertations, journal submissions, research reports, and conference papers.
---

# Doctoral Academic Writing (Doctoral Writing)

## Overview

This skill systematically supports doctoral-level dissertation and thesis writing that unites scholarly rigor with stylistic clarity. It accommodates academic conventions across the humanities, social sciences, and natural sciences.

Core philosophy: **"Clear and concise" writing is not "simple and short" writing. It is writing that conveys complex ideas with maximum efficiency.** It strips away extraneous verbal clutter to reveal the core thesis with uncompromising precision.

## When to Use This Skill

- Reviewing, drafting, and revising doctoral dissertation and master's thesis chapters
- Polishing and refining manuscripts for peer-reviewed journal submission
- Composing research reports, policy monographs, and academic conference presentations
- Providing pedagogical feedback and structural evaluations on academic prose
- Elevating scholarly register and stylistic voice in multilingual research contexts
- **Primary Use Case**: Baseline standard for the Writing Phase in doctoral research workflows

## Absolute Criteria

### Absolute Criterion 1: Academic Quality of the Final Manuscript

> **Speed, token cost, workload, and length limits are completely ignored.**
> The sole criterion for every writing and revision decision is the **academic quality of the final manuscript — rigor, clarity, and depth of argumentation**.
> Rather than expediting completion by reducing revision passes, choose repeated refinement to maximize quality.
> Never sacrifice scholarly depth or conceptual nuance for superficial brevity.

### Absolute Criterion 2: Manuscript Consistency — Single SOT + Hierarchical Structure

> **Consistency in terminology, argumentation, citation, and style across the entire manuscript is the bedrock of academic credibility.**
> The manuscript itself constitutes a single SOT (Single Source of Truth); every edit must preserve the structural integrity and coherence of the whole work.

Design implications of this rule:
- **Terminology SOT**: Once a specialized construct or acronym is defined upon first appearance, it must be used identically throughout. Avoid arbitrary synonym substitution ("elegant variation").
- **Argumentation SOT**: The research questions and hypotheses established in Chapter 1 form a continuous axis traversing methodology, results, and discussion. Revisions in one section must not contradict or undermine arguments in another.
- **Citation SOT**: Maintain a single citation style (APA, Chicago, CSE, etc.) uniformly across the manuscript. In-text citations and bibliographic entries must maintain strict 1:1 correspondence.
- **Style SOT**: Decisions regarding authorial person (first vs. third person), tense, and voice must be applied consistently according to disciplinary conventions.

```
Bad:  Chapter 1 defines "self-efficacy";
      Chapter 3 arbitrarily alternates with "perceived capability sense"  → Terminological inconsistency, degraded credibility
Good: Chapter 1 defines "self-efficacy";
      Maintained uniformly as "self-efficacy" across all chapters  → Single Terminology SOT
```

### Absolute Criterion 3: Code Change Protocol (CCP)

> **In the application domain of this skill (academic writing), this criterion is N/A.**

However, when modifying the files of this skill itself (`SKILL.md`, `references/` files), Absolute Criterion 3 strictly applies. Refer to `AGENTS.md` for the full protocol.

### Priority Among Absolute Criteria

> **Absolute Criterion 1 (Quality) is paramount. Absolute Criterion 2 (Consistency) and Absolute Criterion 3 (CCP) are co-equal means to guarantee quality.**
> Revisions that impair academic accuracy or argumentative quality solely to enforce rigid uniformity are strictly prohibited.
> Consistency serves quality; it must never constrain quality.

```
Conflict Scenario 1 — Conceptual Accuracy vs. Terminological Consistency:
  Chapter 1 employed "structural inequality", but Chapter 4 analysis reveals that
  "systemic inequality" is the more precise theoretical construct.
  → Absolute Criterion 1 takes precedence: Adopt the more accurate construct,
    and retroactively revise Chapter 1 to restore manuscript-wide consistency.

Conflict Scenario 2 — Style Consistency vs. Argumentative Quality:
  Third person has been maintained throughout, but in a qualitative reflexivity section,
  first person substantially elevates authorial authenticity and critical depth.
  → Absolute Criterion 1 takes precedence: Permit first person in that specific section,
    explicitly stating the methodological justification.
```

All Absolute Criteria supersede the core writing principles below. When principles conflict, Absolute Criteria govern; when Absolute Criteria conflict, the priority order is **Absolute Criterion 1 > (Absolute Criterion 2, Absolute Criterion 3)**.

---

## Core Writing Principles

> The four core principles below are subordinate to **all Absolute Criteria (1. Quality, 2. Consistency, 3. Code Change Protocol)**. If principles conflict with an Absolute Criterion, the Absolute Criterion prevails.

### 1. Clarity

Communicate core ideas with exactitude so that the reader never has to guess authorial intent.

**Key Requirements**:
- Subject-predicate alignment is transparent and immediately discernible.
- Key constructs and controlling claims are stated explicitly.
- Specialized terms are formally defined upon first appearance.
- Active voice is preferred where appropriate.
- Words are selected for exact semantic precision.

**Common Issues**:
- Ambiguous pronouns and demonstratives ("this shows that", "it means").
- Syntactic confusion caused by stacked subordinate clauses.
- Undefined technical jargon or unexplained acronyms.
- Obscure grammatical antecedents in complex sentences.

### 2. Conciseness

Express ideas using the minimum number of words necessary without forfeiting semantic depth or nuance.

**Key Requirements**:
- One Sentence, One Idea: Maintain single-proposition focus per sentence.
- Three-tier sentence length guidelines:
  - **Recommended**: 15–25 words
  - **Caution**: Sentences exceeding 25 words warrant evaluation for splitting
  - **Maximum**: 30 words — mandatory division into multiple sentences
- Eliminate empty modifiers, filler adverbs, and pleonastic adjectives.
- Replace bloated multi-word idioms with direct lexical equivalents.

**Common Issues**:
- Sprawling sentences overloaded with parenthetical qualifications and sub-clauses.
- Tautological expressions (e.g., "past history", "final outcome").
- Overuse of expletive constructions ("There is/are", "It is known that").
- Stacking of prepositional phrases.

### 3. Academic Rigor

Uphold scholarly standards and intellectual precision while ensuring prose remains accessible to the target peer audience.

**Key Requirements**:
- Restrict technical vocabulary to necessary disciplinary constructs.
- Formally define foundational concepts upon first introduction.
- Respect established disciplinary conventions.
- Substantiate all theoretical assertions and empirical claims with citations or data.
- Maintain a formal, dignified scholarly register (predominantly third-person framing).
- Employ precise analytical verbs that accurately characterize relationships and actions.

### 4. Logical Flow

Develop ideas in an orderly, logical sequence with explicit signposting between sentences and paragraphs.

**Key Requirements**:
- Dedicate each paragraph to developing a single core theme.
- Open each paragraph with an authoritative Topic Sentence.
- Deploy effective, conceptually precise transitional expressions.
- Maintain a coherent, cumulative argumentative trajectory.
- Make the logical connection between premise and conclusion explicit.

---

## Quick Reference: Practical Transformation Rules

### Expressions to Eliminate

| Category | Phrasing to Eliminate | Recommended Replacement / Treatment |
|----------|-----------------------|--------------------------------------|
| Empty Modifiers | various, numerous, all kinds of | Replace with specific counts or concrete categories |
| Adverb Abuse | very, considerably, somewhat, relatively | Replace with quantitative metrics or calibrated parameters |
| Habitual Passive | is being carried out, has been shown to be | Convert to direct active voice |
| Expletive Fillers | it is deemed that, the fact that | State the proposition directly |
| Redundancies | approximately around, first and foremost | Use a single exact term |

### Transformation Examples

```
❌ In this research, an attempt was made to derive conclusions through the analysis of diverse factors.
✅ This study analyzes three primary factors to establish causal relationships.

❌ In very numerous prior studies, this phenomenon has been found to be observed.
✅ Twelve empirical studies have documented this phenomenon.

❌ It is considered that relatively quite positive outcomes were obtained.
✅ With an effect size of d = 0.65, the intervention yielded moderate positive outcomes.
```

### Conjunction Usage Principles

**Permitted Conjunctions**:
- **Causal**: therefore, consequently, thus, accordingly
- **Contrast**: however, in contrast, whereas, conversely
- **Elaboration**: namely, specifically, that is to say
- **Sequential**: first/second, initially/subsequently

**Conjunctions to Minimize**:
- And (replace with coordinate or parallel structures)
- So (replace with therefore or consequently)
- Also / In addition (integrate sentences or eliminate)
- Furthermore / Moreover (use only when presenting an escalating argument)

```
❌ A survey was conducted. And interviews were also carried out. In addition, observations were performed.
✅ We conducted surveys, semi-structured interviews, and participant observations.
```

### Academic Vocabulary Selection

**Informal → Academic Written Register**:

| Informal / Colloquial | Academic Register |
|-----------------------|-------------------|
| look into / check | analyze, examine, investigate, evaluate |
| show | demonstrate, indicate, suggest, reveal |
| think | assess, evaluate, infer, posit |
| use | utilize, deploy, implement, apply |
| get | obtain, derive, acquire |

**Ambiguous → Concrete**:

| Ambiguous Descriptor | Concrete Scholarly Phrasing |
|----------------------|------------------------------|
| many studies | 37 empirical investigations |
| recently | since 2020 |
| most respondents | 78.3% of respondents |
| significant difference | t(45) = 2.31, p < .05 |

### Argumentative Tone

```
❌ I think this result is very important.
✅ This finding extends existing theoretical models.

❌ This is a truly surprising discovery.
✅ This observation diverges from patterns reported in prior literature.
```

**Epistemic Hedging Expressions** (Calibrated Usage):
- "suggests that" / "indicates the potential for"
- "is consistent with" / "points toward"
- "appears to mediate" / "the evidence indicates"

---

## Workflow

### Step 1: Understand the Context

Prior to editing or generating feedback, ascertain the following parameters:

1. **Document Type and Target Audience**:
   - Dissertation chapter, journal manuscript, conference paper, or research proposal?
   - Target journal, scholarly discipline, or examination committee profile?
   - Disciplinary domain (Humanities, Social Sciences, Natural Sciences & Engineering)?

2. **Scope of Engagement**:
   - Comprehensive manuscript revision?
   - Sentence- and paragraph-level polishing?
   - Formative developmental feedback?
   - Style guide compliance audit?

3. **Language and Disciplinary Standards**:
   - Academic English register?
   - Target style guide (APA, Chicago, MLA, CSE, IEEE)?
   - Subfield-specific conventions?

### Step 2: Apply Clarity Checklist

Load and execute the systematic verification items in `references/clarity-checklist.md`:
- Subject-verb alignment and physical proximity
- Sentence length boundaries (15–25 words)
- Explicit conceptual definitions for technical terms
- Logical transitions and paragraph unity
- Judicious balance between active and passive voice

### Step 3: Identify Common Issues

Consult `references/common-issues.md` to identify and rectify recurring errors:
- Wordiness, redundancy, and dead-weight idioms
- Weak verbs and excessive nominalization
- Vague demonstratives and dangling pronouns
- Prepositional chaining
- Uncalibrated or apologetic hedging

### Step 4: Provide Revisions or Feedback

**When Revising Manuscript Text**:
- Provide side-by-side Before/After comparisons.
- Articulate the rationale for substantial structural edits.
- Preserve the author's intellectual voice and argumentative structure.
- Respect disciplinary terminology and methodological standards.

**When Providing Developmental Feedback**:
- Identify systemic error patterns rather than isolated typos.
- Explain why particular constructions impair cognitive processing.
- Point to concrete model revisions in `references/before-after-examples.md`.

**When Adapting to Specific Disciplines**:
- Consult disciplinary conventions in `references/discipline-guides.md`.
- Confirm citation formatting, voice conventions, and chapter organization.
- Respect established theoretical paradigms and empirical reporting formats.
- For rapid reference transformations, consult `references/academic-quick-reference.md`.

### Step 5: Verify Improvements

Following revisions, perform a two-tier verification:

**Absolute Criteria Verification (Highest Priority)**:
- ✓ **[Absolute Criterion 1]** Has academic quality improved (rigor, clarity, argumentative depth)?
- ✓ **[Absolute Criterion 2]** Does the revision maintain manuscript-wide consistency (Terminology, Argument, Citation, Style SOT)?
- ✓ **[Priority Rule]** Has quality been preserved without being sacrificed for superficial uniformity?

**Core Principles Verification**:
- ✓ Core meaning and conceptual nuances preserved
- ✓ Sentence-level clarity heightened
- ✓ Word count compressed and conciseness optimized
- ✓ Transitions and logical flow sharpened
- ✓ Style guide requirements fulfilled

---

## Key Techniques

### Sentence Structure Optimization

**Subject-Verb-Object Alignment**:
- Position the grammatical subject near the sentence opening.
- Minimize intervening words between subject and main verb (fewer than 7–8 words).
- Avoid lengthy parenthetical clauses between subject and predicate.
- Employ parallel grammatical structures for coordinate concepts.

**Example**:
- ❌ "The study, which was conducted over a period of three years in multiple locations across five different countries, examined the impact of..."
- ✅ "This three-year study examined the impact of... The research spanned five countries."

### Eliminating Wordiness: The Paramedic Method

1. Identify and circle prepositional phrases (of, in, for, with).
2. Locate linking verbs ("is", "are", "was", "were").
3. Uncover the real action and convert it into a strong active verb.
4. Reposition the grammatical subject directly adjacent to the main verb.
5. Purge superfluous modifiers and stock phrases.
6. Eliminate pleonasms and redundant pairings.

### Terminology Management

**Definition Upon First Appearance**:
- Provide an explicit definition when introducing specialized constructs.
- Spell out acronyms at first mention: "Structural Equation Modeling (SEM)".
- Situate specialized concepts within their broader theoretical framework.

**Consistency (Terminology SOT)**:
- Use identical terminology for identical constructs across all chapters.
- Eliminate arbitrary synonym variation for technical terms.
- Maintain alignment with cited canonical literature.

### Active vs. Passive Voice Selection

**Employ Active Voice**:
- When recounting the researcher's analytical decisions and empirical procedures.
- When formulating direct theoretical arguments.
- When maximizing clarity, directness, and economy of prose.

**Permissible Uses of Passive Voice** (Explicit Exceptions):
- When the agent is unknown, irrelevant, or obvious.
- When the recipient or outcome warrants primary emphasis over the actor.
- When dictated by disciplinary convention (e.g., experimental methods in STEM).
- **Results Reporting**: "A significant difference was observed" is standard when focusing on the data rather than the investigator.
- **Methodological Procedures**: "Participants were randomly assigned" appropriately highlights the experimental design.

> **Resolving Principle Conflicts (P9 Intersections)**: When the "preference for active voice" conflicts with established "disciplinary conventions", **disciplinary conventions take precedence**. Disciplinary accuracy is a higher-order requirement than general stylistic preference.

---

## Academic Style Guidance

### Core Principles of International Doctoral English

- **Agentive Subject Selection**: Ensure every clause has an identifiable subject performing the action.
- **Word-Count Discipline**: Maintain average sentence length within 15–25 words; split clauses exceeding 30 words.
- **Formal Academic Register**: Avoid colloquialisms, contractions, informal idioms, and emotional qualifiers.
- **Expletive Elimination**: Eliminate dummy openings ("It is evident that", "There are several reasons why").
- **Nominalization Conversion**: Turn abstract noun endings (-tion, -ment, -ance) back into active verbs.

---

## Review Checklist (Quick Checklist)

Verify the draft against the following points post-writing:

- [ ] Does every sentence possess an immediately identifiable grammatical subject?
- [ ] Do sentence lengths conform to the 3-tier standard (recommended 15–25 words, max 30 words)?
- [ ] Have empty adjectives and dead-weight adverbs been eliminated?
- [ ] Have unnecessary passive constructions been converted to active voice?
- [ ] Have vague descriptions been replaced with concrete, quantifiable details?
- [ ] Have stock modifiers ("various", "diverse", "many") been grounded in numbers or categories?
- [ ] Have coordinating conjunctions ("and", "also") at clause heads been minimized?
- [ ] Does each paragraph develop a single core analytical proposition?
- [ ] Are technical terms formally defined upon first appearance?
- [ ] Is every empirical claim substantiated with data or peer-reviewed citations?
- [ ] Are target disciplinary conventions and citation standards followed throughout?

---

## Resources

### references/ Directory

Comprehensive reference suite accompanying this skill:

- **clarity-checklist.md**: Systematic verification checklist for evaluating clarity, conciseness, and academic rigor (VERIFY).
- **common-issues.md**: Diagnostic catalog of recurring academic writing weaknesses with before/after corrections (WHAT).
- **academic-quick-reference.md**: Section-by-section transformation patterns, disciplinary vocabulary tables, and frequent error corrections (HOW — Patterns).
- **before-after-examples.md**: Real-world dissertation revision case studies across all major manuscript sections (HOW — Practice).
- **discipline-guides.md**: Disciplinary writing conventions across the humanities, social sciences, and natural sciences (WHERE).

> **Division of Roles Among Files**:
> Several overarching concepts appear across multiple files. This reflects intentional functional specialization rather than redundant duplication:
> - **SKILL.md**: Governing principles and evaluation criteria (WHY)
> - **common-issues.md**: Systematic issue typology and remediation (WHAT)
> - **academic-quick-reference.md**: Rapid transformation pattern library (HOW — Patterns)
> - **before-after-examples.md**: Extended real-world revision cases (HOW — Practice)
> - **clarity-checklist.md**: Multi-pass verification checklist (VERIFY)
> - **discipline-guides.md**: Disciplinary conventions and style guides (WHERE)

Load reference files into context as needed during evaluation and revision workflows.

---

## Notes

- **Applying Absolute Criterion 1**: Prioritize substantive intellectual content over superficial brevity — never sacrifice nuance or precision for brevity. Iterate revision cycles as necessary.
- **Applying Absolute Criterion 2**: When editing any section of a manuscript, verify that changes do not create discrepancies in terminology, argumentation, citation, or voice in other sections.
- **Applying Absolute Criterion 3**: N/A for academic writing content. When editing `SKILL.md` or `references/` files, execute CCP (Understand Intent → Ripple Effect Analysis → Change Plan).
- Respect the author's intellectual voice and disciplinary traditions.
- Provide constructive, pedagogical feedback that elevates authorial autonomy and writing quality.
- When uncertain regarding a specific convention, consult the official style manual of the target journal or discipline.
- "Clear and concise" writing is not "simple and short" writing — it is the efficient, lucid communication of complex scholarly ideas.
