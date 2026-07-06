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

---

### 10. Define Metrics, Algorithms, and Baselines on First Use

**Signals**

- A metric (e.g., F1, recall, AUC, p99 latency), algorithm acronym (e.g., SGD, PCA, KNN), or baseline label is used without explanation.
- The reader cannot understand the term from surrounding text without external knowledge or a prior paper.

**Check**
List every metric, algorithm acronym, and baseline label in the paper. For each first occurrence, confirm a concise definition or intuition appears nearby. Pay extra attention to evaluation sections where metrics and baselines are introduced in bulk.

**Fix**
On first use, add a brief definition. For metrics, state what they measure and their range/meaning. For algorithms, give the core idea in one sentence. For baselines, describe what each assumes or optimizes so the contrast with the proposed method is clear.

---

### 11. Inconsistency Across Introduction, Method, and Conclusion

**Signals**

- The introduction or conclusion describes a single algorithm, but the method section actually uses a hybrid or extended version (or vice versa).
- A component named in the introduction is dropped, renamed, or contradicted in the method or conclusion.
- The conclusion claims a property (e.g., "no offline training", "online only", "parameter-free") that the method section qualifies or contradicts.

**Check**
For each contribution and algorithm, compare how it is described across the abstract, introduction, method, and conclusion. Confirm names, components, and scope match end-to-end.

**Fix**
Pick one canonical description and propagate it across all sections. If a hybrid method is used, say so in the introduction and conclusion, not only inside the method section.

---

### 12. Echo Contributions in the Conclusion

**Signals**

- The conclusion summarizes numerical results but does not revisit the contributions stated in the introduction.
- The introduction lists N contributions, but the conclusion discusses only a subset or introduces new claims.

**Check**
Copy the contribution list from the introduction. Check that the conclusion explicitly restates each contribution and ties it to the reported outcome. Flag conclusions that focus on results without structurally mirroring the intro.

**Fix**
Restructure the conclusion to mirror the introduction's contribution list: restate each contribution, report its outcome, and avoid introducing claims not foreshadowed earlier. Headline results should support contributions, not replace them.

---

### 13. Contribution-Centric Narrative Throughout

**Signals**

- The paper dives into implementation details without reminding the reader which contribution each part supports.
- A reviewer can follow individual sentences but loses the thread connecting sections to the stated contributions.
- Sections read as a sequence of technical choices rather than a sustained argument for the contributions.

**Check**
For each section, note which contribution it advances. Flag sections where the connection to the contribution list is implicit for more than a paragraph. Look for places where the contribution is assumed obvious rather than restated.

**Fix**
At section transitions and key subsection openings, briefly restate which contribution the upcoming material addresses. When a design choice serves a specific contribution, say so explicitly. Stand in the reader's position: the contribution list should be visible from any page, not only the introduction.

---

### 14. Precise Terminology Scope

**Signals**

- A term implying a hardware/software scope (e.g., "cluster", "node", "machine", "device", "distributed", "edge") is used when the actual setup differs in scope.
- The reader may infer a different topology, cost model, or deployment than intended.
- A cost model silently excludes or includes a scope the terminology does not signal.

**Check**
Identify terms that imply a scope. Verify the scope matches the actual setup. If a broader term is kept while the scope is narrower (or vice versa), confirm the cost model covers the gap or state what is excluded.

**Fix**
Either use the precise term, or explicitly state what is included. For example, if a broader deployment term (e.g., "cluster") is kept while the system actually targets components within a single node, state whether inter-node costs are part of the model.

---

### 15. Discuss Method Overhead

**Signals**

- A non-trivial proposed component is introduced without reporting its runtime, memory, or system cost.
- The reader cannot judge whether the method is practical or whether gains are offset by overhead.
- Overhead is mentioned qualitatively (e.g., "low overhead", "negligible cost") without a measured value.

**Check**
For each non-trivial proposed component, look for a sentence or paragraph reporting its overhead (latency, throughput impact, memory footprint, or fraction of total runtime). Flag qualitative overhead claims with no number nearby.

**Fix**
Add a brief overhead analysis per component. If overhead is negligible, state the measured cost. If significant, quantify the trade-off and show it is accounted for in the evaluation.

---

### 16. Avoid Leading with Experimental Results in the Introduction

**Signals**

- The introduction foregrounds specific percentage improvements or experiment figures before the problem and approach are established.
- Numerical results (e.g., "reduces X by Y%") appear as the main content of an introduction paragraph rather than as a brief headline.

**Check**
Read each introduction paragraph. Flag sentences reporting detailed numeric improvements that appear before the approach is sketched. Leading an introduction with experiment results is unusual and shifts focus away from motivation.

**Fix**
Keep the introduction focused on problem, motivation, and approach. Move detailed quantitative results to the evaluation section. A single brief headline result is acceptable only after the approach is introduced.

---

### 17. Clarify Which State or Timepoint a Value Refers To

**Signals**

- A value, threshold, or measurement is given without specifying whether it refers to the state before or after an event (e.g., before/after a detected change point, before/after a triggered action, during a stable segment).
- A classification rule uses thresholds on variables without saying which window or timepoint the variables are sampled from.

**Check**
For each threshold, measured value, or classification condition tied to an event, confirm the text states whether the value is sampled before, during, or after the event. Pay attention to change-point detection, trigger conditions, and transition rules.

**Fix**
Add a phrase specifying the timepoint and window (e.g., "the metric measured in the window immediately after the detected event", "the signal averaged over the window preceding the trigger"). Make classification rules explicit about which segment of the signal feeds the condition.

---

### 18. Topic-First Paragraph Structure

**Signals**

- A paragraph dives into details without a clear opening sentence that summarizes the point.
- The reader must finish the entire paragraph to understand its purpose.
- The topic sentence is buried in the middle or appears at the end.

**Check**
Read the first sentence of each paragraph in isolation. If the first sentence does not convey the paragraph's main point, the structure needs revision. Flag paragraphs where the opening sentence is a transitional phrase, a background detail, or a subordinate observation.

**Fix**
Restructure: lead with a short, direct sentence that states the paragraph's claim or purpose. Follow with supporting explanation, evidence, or elaboration. The reader should grasp the paragraph's role from the first sentence alone.

---

### 19. Sentence Rhythm and Length Variation

**Signals**

- Multiple consecutive long sentences (more than 25 words each) with no short sentence breaking the rhythm.
- Sentences overloaded with adjectives, adverbs, or stacked prepositional phrases.
- The prose feels monotonous or dense because every sentence has similar length and structure.

**Check**
Scan paragraphs for runs of three or more long sentences. Flag sentences with more than three adjectives or modifiers on a single noun phrase. Check whether any short sentence (under 12 words) appears between longer ones to provide rhythm.

**Fix**
Break adjective-heavy sentences into shorter ones. Alternate short and long sentences within each paragraph. A short sentence after a complex one gives the reader a place to rest. Prefer: short declarative sentence → longer explanatory sentence → short concluding sentence.

---

### 20. No Coined or Invented Terminology

**Signals**

- A technical term appears that has no established usage in the field's literature.
- A compound noun or phrase is created ad hoc to label a concept (e.g., "read-wire edge" when no prior work uses this term).
- The reader cannot find the term in standard references or related papers.

**Check**
For each technical term, verify it appears in prior published work, textbooks, or standard references. Pay special attention to compound nouns and hyphenated phrases. If a term cannot be found in existing literature, it is likely coined.

**Fix**
Replace coined terms with established terminology from the field. If no single existing term captures the concept, describe it using known terms (e.g., "the latency of reading from the edge cache" instead of inventing "read-edge latency"). If a new term is genuinely necessary, define it explicitly on first use and justify why existing vocabulary is insufficient.

---

### 21. Polysemous Word Ambiguity

**Signals**

- A word that can serve as multiple parts of speech (noun, verb, adjective) is used without syntactic cues to disambiguate (e.g., "read" as noun vs. verb, "edge" as graph edge vs. network edge, "wire" as noun vs. verb).
- The reader must guess the intended part of speech or meaning from context alone.
- The sentence parses differently depending on which meaning is assumed.

**Check**
Search for common polysemous words in the domain (read, write, edge, wire, cache, block, page, frame, state, model, train, test, set, run, match, switch, port, host, pipe, fork, flag, trace, register, mount, link, route, patch, pool, lock, watch, probe, map, address, bus, chip, stack, queue, process). For each occurrence, read the sentence and confirm only one parsing is natural.

**Fix**
Add syntactic disambiguation: use articles ("a read operation" vs. "to read"), prepositions, or rephrase to make the part of speech unambiguous. If a word has multiple technical meanings in the same paper (e.g., "edge" for both graph topology and network edge), define each meaning on first use and prefer different terms where possible.

---

### 22. Formal Register in Academic Writing

**Signals**

- Colloquial or conversational phrasing appears (e.g., "basically", "kind of", "a lot of", "stuff", "get rid of", "figure out", "deal with").
- Contractions in prose (e.g., "doesn't", "can't", "it's" for "it is").
- Overly casual connectors (e.g., "so", "also" at sentence start, "plus").

**Check**
Search for common informal markers: contractions, phrasal verbs that have single-word formal equivalents, hedging fillers, and colloquial intensifiers. Flag any word or phrase that would sound natural in spoken conversation but not in a published journal paper.

**Fix**
Replace with formal equivalents: "figure out" → "determine", "get rid of" → "eliminate", "a lot of" → "numerous" or a specific quantity, "deal with" → "handle" or "address", "basically" → remove or replace with precise qualifier. Expand all contractions. Use single-word verbs over phrasal verbs where a precise equivalent exists.
