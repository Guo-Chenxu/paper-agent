# Writing Patterns

This reference stores reusable writing issues discovered from annotated academic-paper PDFs. Use it together with `ai_writing_patterns.md` when checking papers, essays, or long-form technical writing.

Only add patterns that generalize beyond one sentence. Do not store private reviewer identities, one-off task state, unpublished factual claims, or project-specific TODOs.

---

## Current Patterns

### 1. Unclear Deictic Reference

**Signals**

- Sentences rely on `this`, `it`, `they`, `these`, or `such` when the antecedent is not immediately obvious.
- A paragraph starts with a pronoun that could refer to multiple prior concepts.

**Check**
Search for pronouns and read the surrounding sentence pair. In TeX papers, inspect abstract, introduction, and method sections first because ambiguity there affects the reader's model.

**Fix**
Replace the pronoun with the concrete object, method, metric, theorem, or experimental condition.

---

### 2. Overcompressed Technical Sentence

**Signals**

- One sentence carries setup, claim, caveat, and consequence at once.
- Multiple clauses are chained with `while`, `whereas`, `which`, semicolons, or repeated commas.
- The sentence is technically correct but hard to parse on first read.

**Check**
Scan long paragraphs and sentences containing multiple contrast or causality markers. Confirm that splitting the sentence will not separate a symbol from its definition.

**Fix**
Split into two sentences or reorder as: context → claim → limitation/consequence.

---

### 3. Unsupported Strength of Claim

**Signals**

- Phrases such as `guarantees`, `always`, `fully`, `eliminates`, `optimal`, or `significantly` appear without a theorem, citation, ablation, or measured value nearby.
- A qualitative observation is phrased as a universal result.

**Check**
For each strong claim, look for nearby evidence: theorem, proof sketch, experiment, citation, or numeric result.

**Fix**
Add the supporting condition/evidence or weaken the claim to match the demonstrated scope.

---

### 4. Missing Specific Technical Anchor

**Signals**

- Generic phrases such as `the method`, `the framework`, `the result`, or `the problem` appear where a concrete variable, dataset, metric, algorithm step, or figure reference would help.
- The prose is smooth but not anchored to paper-specific details.

**Check**
Read the paragraph and ask what exact object the reader should remember. Search repeated generic nouns in nearby sections.

**Fix**
Name the exact component, metric, dataset, assumption, section, or figure/table reference.

---

### 5. Avoid Em-Dashes

**Signals**

- `---` (or `—`) used anywhere in the document.

**Check**
Search for `---` or `—` in the document.

**Fix**

- Parenthetical aside → use commas or parentheses, or restructure as a separate sentence.
- Explanation/elaboration → split into a new sentence with a period.
- List introduction → use "including", "such as", or restructure.
- Do not use em-dashes. Always rewrite using the alternatives above.

---

### 6. Minimize Colons in Prose

**Signals**

- Colons used to introduce explanations, elaborations, or short clauses that could be expressed as a new sentence or subordinate clause.
- Colons used where "because", "where", "including", or a period would be more natural.

**Check**
Search for `:` in prose text (excluding math environments, `\label{}`, `\ref{}`, algorithm pseudocode, and formal definition introductions).

**Fix**

- Explanation after colon → split into a new sentence, or use ", because" / ", as" / ", where".
- List after colon → use "including" or "such as" and restructure.
- Keep colons only for introducing equations, formal definitions, and labeled list items.
- Default to avoiding colons. Use alternative constructions whenever possible.

---

### 7. Excessive Use of "We" in Academic Writing

**Signals**

- "We" appears as the subject of most sentences in a paragraph.
- "We define", "We propose", "We show", "We evaluate" used repeatedly without variation.
- Possessive first-person phrases such as "our experiments", "our model", "our evaluation", "our method", or "our system" frame technical objects as author-owned rather than paper-internal entities.
- The paper reads as a narrative of what the authors did rather than a description of the system/method.

**Check**
Search for `\bWe\b`, `\bwe\b`, `\bOur\b`, `\bour\b`, `\bus\b`, `\bUs\b`, `\bours\b`, `\bOurs\b`, and `\bourselves\b`. Count frequency per section. Flag paragraphs where "We" starts more than two consecutive sentences. For `our + noun`, check whether the noun can stand as `the`, `this`, or `the proposed` object without changing meaning.

**Fix**

- Use passive voice: "X is defined as...", "The system is evaluated..."
- Use the system/method as subject: "The algorithm selects..."
- Use impersonal constructions: "This approach yields...", "The results indicate..."
- Replace possessive framing with objective nouns: "our model" → "the model", "our evaluation" → "the evaluation", "in our experiments" → "in the experiments" or "experimental results show".
- When related work needs a specific contrast, use "the proposed X" instead of "our X".
- Keep occasional "We" for genuine authorial decisions (e.g., "We chose X over Y because...").

---

### 8. Semicolons Creating Run-On Compound Sentences

**Signals**

- Semicolons join two independent clauses that would be clearer as separate sentences.
- The second clause after the semicolon introduces a new idea rather than contrasting or extending the first.
- Multiple semicolons in a single paragraph.

**Check**
Search for `;` in prose (excluding math, algorithm pseudocode). For each, check whether the two clauses share a tight logical contrast or whether they are merely sequential.

**Fix**

- If the clauses contrast: use ", while" or ", whereas".
- If the second clause elaborates: use a period and start a new sentence.
- Keep semicolons only for tight parallel constructions or when separating items in a list that already contains commas.

---

### 9. Use `\sim` for Numeric Ranges Instead of Hyphens

**Signals**

- A hyphen `-` or en-dash `--` is used between two numbers to express a range or approximate multiplier (e.g., `5-10$\times$`, `10-20\%`).

**Check**
Search for patterns like `\d+-\d+` or `\d+--\d+` in text and math environments.

**Fix**
Replace the hyphen/en-dash with `\sim` inside math mode. Examples:

- `5-10$\times$` → `$5\sim10\times$`
- `10-20\%` → `$10\sim20\%$`
- `$2-3$ hours` → `$2\sim3$ hours`
