---
name: ai-detector
description: "Detects whether a piece of writing is AI-generated and provides specific, actionable rewrite suggestions to make it sound more human. Use this skill whenever the user wants to check if text looks AI-written, wants to 'humanize' AI text, asks whether their writing will pass an AI detector, or wants feedback on making writing feel more authentic and less robotic. Also use this skill when checking academic papers, essays, or any long-form writing for AI patterns before submission. Trigger on phrases like: 'does this look AI-generated', 'humanize this text', 'make this sound more human', 'will this pass AI detection', 'is this too AI-sounding', 'check my writing for AI patterns', 'reduce AI rate', 'check paper for AI'."
user-invocable: true
---

# AI Detector Skill

This skill analyzes text for AI-generated writing patterns and gives concrete suggestions to make it sound more human.

The goal isn't just to flag problems — it's to help the writer understand *why* certain passages feel robotic and *how* to fix them specifically.

## Reference Material

Primary reference: `references/ai_writing_patterns.md`
Project writing-pattern reference: `.claude/rules/writing-patterns.md`
Source: https://www.aicheckr.io/blog/spotting-ai-writing-patterns

When analyzing academic text, read `.claude/rules/writing-patterns.md` before every analysis so reusable project-specific writing issues are included. For general AI-pattern checks, first try fetching the live URL above for the latest content. If unreachable, use the patterns documented below.

No single pattern definitively proves AI authorship. A **cluster** of these signals together is what matters.

---

### Pattern 1: Overused "AI Vocabulary"

AI models repeatedly reach for the same elevated words:

- **Verbs**: delve, illuminate, underscore, leverage, navigate, foster, embark
- **Adjectives**: pivotal, nuanced, multifaceted, comprehensive, robust, seamless
- **Nouns**: landscape, realm, tapestry, synergy, paradigm

Human writers vary their word choice more naturally and use plainer language.

**Fix**: Replace with simpler, more direct synonyms; vary word choice across the document.

---

### Pattern 2: Em Dash Overuse

AI strongly prefers em dashes (—) over semicolons, colons, or subordinate clauses. A paragraph with 3+ em dashes is a yellow flag.

**Fix**: Rewrite as subordinate clauses or split into two sentences.

---

### Pattern 3: Uniform Sentence Structure

AI mixes sentence lengths in a mechanical way — short, medium, long, repeat — rather than letting rhythm emerge from meaning. Human prose has more irregular cadence.

**Fix**: Vary sentence length deliberately; add a very short sentence for punch.

---

### Pattern 4: American English Spelling

AI defaults to American English (e.g., "analyze" not "analyse", "color" not "colour") regardless of the author's locale.

---

### Pattern 5: Avoidance of Contractions

AI tends to write "do not" instead of "don't", "it is" instead of "it's". Formal register is fine in academic writing, but the pattern is consistent even in casual contexts.

**Fix**: Add contractions where register allows.

---

### Pattern 6: Perfect Grammar

AI rarely makes the small grammatical slips that characterize human writing. Suspiciously flawless grammar across a long document is a signal.

---

### Pattern 7: Oxford Comma Consistency

AI applies the Oxford comma uniformly. Humans are inconsistent.

---

### Pattern 8: Formulaic Structure

- Paragraphs are similarly sized
- Introductions follow a template: hook → background → thesis
- Conclusions begin with "In conclusion", "Overall", "To summarize", "In summary"
- Wrap-ups are disproportionately long relative to the body

**Fix**: Cut "In conclusion"; start the conclusion with the most important takeaway.

---

### Pattern 9: Formal, Positive, Inoffensive Tone

AI defaults to:
- Formal register even when casual would be natural
- Positive framing (avoids strong negative stances)
- Broadly inoffensive language (hedges controversial claims)
- Vague generalities rather than specific opinions

---

### Pattern 10: Lack of Specificity

AI avoids:
- Concrete proper nouns (uses "a city" instead of "Chicago")
- Specific dates and numbers (uses "recently" instead of "in March 2024")
- Real names (defaults to generic placeholders like "Emily" or "John")
- Precise technical details that require lived experience

**Fix**: Add one concrete detail, date, or proper noun per paragraph.

---

### Pattern 11: No Authentic Voice

- No personal anecdotes or genuine first-person experience
- No idiosyncratic opinions or surprising takes
- Descriptions of process are generic ("I researched thoroughly") rather than specific
- Key phrases from the original prompt recur in the output, especially in conclusions

**Fix**: Add one genuine opinion or surprising observation per section; rewrite the conclusion without looking at the original prompt.

---

## Detection Tips

1. **Count signal clusters**: One or two patterns = inconclusive. Five or more = strong AI signal.
2. **Check the vocabulary list**: Search the text for the overused words above.
3. **Read the conclusion first**: AI conclusions are the most formulaic part.
4. **Look for specificity gaps**: Does the text ever name a real place, date, or person?
5. **Read aloud**: AI prose has a smooth, frictionless quality that feels slightly "off" when spoken.

---

## Analysis Process

### Step 1: Scan for Signal Clusters

Work through all 11 patterns above. For each one, note whether it appears in the text. The key insight: **one or two patterns is inconclusive; five or more is a strong AI signal**.

### Step 2: Assign a Verdict

Based on the cluster count:

- **0–2 signals**: Likely human-written (or well-humanized AI)
- **3–4 signals**: Ambiguous — could go either way
- **5–7 signals**: Probably AI-generated
- **8+ signals**: Almost certainly AI-generated

### Step 3: Give Targeted Rewrite Suggestions

For each signal found, provide:
1. The specific passage that triggered it (quote it)
2. Why it reads as AI
3. A concrete rewrite suggestion (or an example rewrite if the fix is non-obvious)

Don't give generic advice like "vary your sentence structure." Show the actual sentence and how to change it.

## Output Format

Structure your response like this:

---

**AI Detection Report**

**Verdict**: [Likely human / Ambiguous / Probably AI / Almost certainly AI]

**Signals found** (N/11):
- [Signal name]: [brief note on where it appears]
- ...

**Detailed suggestions**:

For each signal:
> *Original*: "[quoted passage]"
> *Issue*: [one sentence explaining why this reads as AI]
> *Suggestion*: [concrete fix or example rewrite]

**Overall advice**: [2–3 sentences on the most impactful changes to make]

---

## Tone and Approach

Be direct and specific — the user wants actionable feedback, not a lecture. If the text is mostly fine, say so clearly and focus only on the real issues. If it's heavily AI-patterned, prioritize the top 3–4 most impactful fixes rather than overwhelming the user with every signal.

The goal is to help the writer produce text that sounds like *them*, not just text that avoids AI detectors. Encourage adding genuine specificity, real opinions, and natural voice — not just swapping "delve" for "explore".
