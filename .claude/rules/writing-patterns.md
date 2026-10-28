# Writing Patterns

This reference stores reusable writing issues discovered from annotated academic-paper PDFs and technical-writing guidelines. Use it together with `.claude/skills/ai-detector/references/ai_writing_patterns.md` when checking papers, essays, or long-form technical writing.

Only add patterns that generalize beyond one sentence. Do not store private reviewer identities, one-off task state, unpublished factual claims, or project-specific TODOs.

---

## Current Patterns

### 1. Unclear Deictic Reference

**Signals**

- Sentences rely on `this`, `it`, `they`, `these`, `those`, or `such` when the antecedent is not immediately obvious.
- A paragraph starts with a pronoun that could refer to multiple prior concepts.

**Check**
Search for `this`, `it`, `they`, `these`, `those`, and `such`, and read the surrounding sentence pair. In TeX papers, inspect abstract, introduction, and method sections first because ambiguity there affects the reader's model.

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

### 6. Avoid Colons in Prose

**Signals**

- Colons introduce explanations, elaborations, or short clauses that could be expressed as a new sentence or subordinate clause.
- Colons appear where "as", "where", or a period would be more natural.

**Check**
Search for `:` in prose text (excluding math environments, `\label{}`, `\ref{}`, and algorithm pseudocode).

**Fix**

- Explanation after colon → split into a new sentence, or use ", as" / ", where". Use ", because" only when the causal relation is non-obvious (see Pattern 26).
- List after colon → use "including" or "such as" and restructure.
- For equation lead-ins, see Pattern 39.

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

- In prose, use passive voice: "X is defined as...", "The system is evaluated..." Algorithm steps follow the imperative style in Pattern 38.
- Use the system/method as subject: "The algorithm selects..."
- Use impersonal constructions: "This approach yields...", "The results indicate..."
- Replace possessive framing with objective nouns: "our model" → "the model", "our evaluation" → "the evaluation", "in our experiments" → "in the experiments" or "experimental results show".
- When related work needs a specific contrast, use "the proposed X" instead of "our X".
- Keep occasional "We" for genuine authorial decisions (e.g., "We chose X over Y because...").

---

### 8. Avoid Semicolons in Prose

**Signals**

- Semicolons join two independent clauses that would be clearer as separate sentences.
- Multiple semicolons appear in a single paragraph.
- Semicolons separate items in a list that already contains commas.

**Check**
Search for `;` in prose (excluding math and algorithm pseudocode). Count semicolons per paragraph. Identify clause-joining semicolons and list separators.

**Fix**

- Clause-joining semicolon → use a period, or ", while" / ", whereas" when the clauses contrast.
- List item containing commas → restructure the list or use parentheses.
- Keep semicolons only in math and code.

---

### 9. Use En Dashes for Numeric Ranges Instead of Hyphens

**Signals**

- A hyphen `-` is used between two numeric values to express a range, including percent forms and unit-bearing forms with surrounding spaces (e.g., `5-10$\times$`, `10-20\%`, `10\% - 20\%`, `5 ms - 10 ms`).

**Check**
Search for a hyphen between two numeric endpoints in text mode or in a range phrase. Confirm from context that the hyphen denotes a range rather than a minus sign. Range cues include a following unit, a range word such as "lines" or "to", or a percentage pair. Endpoints may contain decimal points or thousands separators (`1.5-2.5`, `1,000-2,000`), and those ranges still take an en dash.

**Fix**
Replace the hyphen with an en dash, written as `--` in text mode, and remove the surrounding spaces. Close the math group before the dash when an expression carries units or an operator. Examples:

- `5-10$\times$` → `5--10$\times$`
- `10\% - 20\%` → `10\%--20\%`
- `5 ms - 10 ms` → `5--10 ms`
- `$2-3$ hours` → `$2$--$3$ hours`

---

### 10. Define and Use Metrics, Algorithms, Baselines, and Symbols Consistently

**Signals**

- A metric (e.g., F1, recall, AUC, p99 latency), algorithm acronym (e.g., SGD, PCA, KNN), or baseline label is used without explanation.
- A mathematical symbol is never defined, or its definition is far from first use, or the same symbol denotes two different quantities.
- A dimensional quantity is defined without a unit, or the same quantity carries inconsistent units.
- A dimensionless quantity is not identified as dimensionless.
- The reader cannot understand the term from surrounding text without external knowledge or a prior paper.

**Check**
List every metric, algorithm acronym, baseline label, and mathematical symbol in the paper. For each first occurrence, confirm a concise definition appears nearby; a trailing "where" clause immediately after the equation counts as the definition (see Pattern 39). Check that each symbol keeps one meaning. Check units for dimensional quantities and identify dimensionless quantities explicitly. Pay extra attention to evaluation sections where metrics and baselines are introduced in bulk.

**Fix**
On first use, add a brief definition. For metrics, state what they measure and their range. For algorithms, give the core idea in one sentence. For baselines, describe what each assumes or optimizes so the contrast with the proposed method is clear. For symbols, state what the symbol denotes, give the unit for a dimensional quantity, and mark a dimensionless quantity as such. Keep notation consistent.

---

### 11. Inconsistency Across Abstract, Introduction, Method, and Conclusion

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

- A non-trivial proposed component is introduced without reporting its cost (measured runtime, memory, or analytical complexity).
- The reader cannot judge whether the method is practical or whether gains are offset by overhead.
- Overhead is mentioned qualitatively (e.g., "low overhead", "negligible cost") without a measured value.

**Check**
For each non-trivial proposed component, look for a sentence or paragraph reporting its overhead. For an empirical system, check for measured latency, throughput impact, memory footprint, or runtime fraction. For a theoretical method, check for analytical time or space complexity. Flag qualitative overhead claims with no supporting figure or bound.

**Fix**
Add a brief overhead analysis per component. If overhead is negligible, state the measured cost or the analytical bound. If significant, quantify the trade-off and show it is accounted for in the evaluation.

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
Read the first sentence of each paragraph in isolation. A topic-first structure is required unless the paragraph deliberately builds to its point. Flag a paragraph whose opening sentence is a transitional phrase, a background detail, or a subordinate observation.

**Fix**
Restructure: lead with a short, direct sentence that states the paragraph's claim or purpose. Follow with supporting explanation, evidence, or elaboration. The reader should grasp the paragraph's role from the first sentence alone.

---

### 19. Sentence Rhythm and Length Variation

**Signals**

- Multiple consecutive long sentences (more than 25 words each) with no short sentence breaking the rhythm.
- A single sentence exceeds about 30 words (typically more than three typeset lines).
- Sentences overloaded with adjectives, adverbs, or stacked prepositional phrases.
- The prose feels monotonous or dense because every sentence has similar length and structure.

**Check**
Scan paragraphs for runs of three or more long sentences. Flag any sentence longer than 30 words (typically more than three typeset lines). Flag sentences with more than three adjectives or modifiers on a single noun phrase. Check whether any short sentence (under 12 words) appears between longer ones to provide rhythm.

**Fix**
Break adjective-heavy sentences into shorter ones. Split long sentences at a clause boundary (see Pattern 2). Alternate short and long sentences within each paragraph. A short sentence after a complex one gives the reader a place to rest. Prefer: short declarative sentence → longer explanatory sentence → short concluding sentence.

---

### 20. No Coined or Invented Terminology

**Signals**

- A technical term appears that has no established usage in the field's literature.
- A compound noun or phrase is created ad hoc to label a concept (e.g., "read-wire edge" when no prior work uses this term).
- The reader cannot find the term in standard references or related papers.

**Check**
For each technical term, verify it appears in prior published work, textbooks, or standard references. Pay special attention to compound nouns and hyphenated phrases. If a term cannot be found in existing literature, it is likely coined. The proposed system's proper name is exempt; check only that it is defined on first use.

**Fix**
Replace coined terms with established terminology from the field. If no single existing term captures the concept, describe it using known terms (e.g., "the latency of reading from the edge cache" instead of inventing "read-edge latency"). If a new term is genuinely necessary, define it explicitly on first use and justify why existing vocabulary is insufficient. Proper names of the proposed system are exempt; define the system name on first use and use it consistently (see Pattern 29).

---

### 21. Polysemous Word Ambiguity

**Signals**

- A word that has multiple parts of speech or multiple technical meanings is used without syntactic cues to disambiguate (e.g., "read" as noun vs. verb, "edge" as graph edge vs. network edge, "wire" as noun vs. verb).
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
- Overly casual connectors (e.g., "also" at sentence start, "plus").

**Check**
Search for common informal markers: contractions, phrasal verbs that have single-word formal equivalents, hedging fillers, and colloquial intensifiers. Flag any word or phrase that would sound natural in spoken conversation but not in a published journal paper.

**Fix**
Replace with formal equivalents: "figure out" → "determine", "get rid of" → "eliminate", "a lot of" → "numerous" or a specific quantity, "deal with" → "handle" or "address", "basically" → remove or replace with precise qualifier. Expand all contractions. Use single-word verbs over phrasal verbs where a precise equivalent exists.

---

### 23. No Colloquial "so" or ", so"

**Signals**

- A comma followed by "so" joins two clauses as a loose consequence ("The dataset is small, so we augment it").
- "So" opens a sentence as a conversational connector ("So the method fails when...").
- "So" is used as a filler or emphasis word ("so good", "so much faster") in place of a precise qualifier.

**Check**
Search case-insensitively for `\bso\b` in prose (excluding math, code, and fixed phrases such as "so that" and "so as to"). For each occurrence, confirm whether it introduces a consequence, opens a sentence, or acts as an intensifier. Flag every instance that reads as spoken rather than written English.

**Fix**

- Consequence clause → split into two sentences, or use a formal connector when the link is non-obvious (see Pattern 26).
- Sentence-initial "so" → remove it and start with the subject.
- Intensifier "so" → replace with a precise qualifier: "so fast" → "fast enough to meet the latency budget" or a measured value.
- Keep "so that" and "so as to" only when they express purpose and no cleaner construction exists.

---

### 24. No Defensive Writing with "Rather Than" or Negation-Contrast Patterns

**Signals**

- Phrases such as "X rather than Y", "X instead of Y", "not Y but X", "is X, not Y" that defensively position the work against an imagined objection.
- The sentence structure assumes the reader will confuse X with Y and preemptively rebuts a misunderstanding that was not raised.
- The prose spends more words on what the method is NOT than on what it IS.

**Check**
Search for `rather than`, `instead of`, `not .* but`, `is .*, not`, and similar two-option contrasts. For each occurrence, determine whether the contrast addresses a genuine ambiguity in the immediate context or whether it defensively anticipates an objection. Flag sentences where the positive claim alone would be clearer. This pattern covers two-option contrasts. Bare negation with no contrasted alternative belongs to Pattern 25.

**Fix**

- State what the method IS directly: "X uses approach A" rather than "X uses approach A rather than approach B".
- If a contrast is necessary to resolve genuine ambiguity, present both options neutrally first, then state the choice. "Two approaches, A and B, exist. This work adopts A because [reason]."
- Remove negation clauses that assume a misunderstanding the text has not invited. Trust the reader to understand the positive claim without preemptive rebuttal.
- Keep contrasts only when comparing to a specific baseline, prior work, or alternative that the reader already knows and might reasonably assume applies here.

---

### 25. Direct Affirmative Statement Over Negation-First Construction

**Signals**

- Sentences begin with "It is not the case that", "X does not mean Y", "We do not claim", or other negation-first structures.
- The sentence structure is: [what it is NOT] followed by [what it IS].
- The reader must parse the negation before arriving at the actual claim.

**Check**
Search for negation-first constructions and their markers: `\bNot\b`, `\bNo\b`, `does not`, `do not`, `is not`, `are not`, `cannot`, `It is not`. For each, check whether the sentence leads with the negation and whether the affirmative is subordinate or absent. Flag sentences where the negation is the main clause. This pattern covers negation with no contrasted alternative. Two-option contrasts such as "not X but Y" belong to Pattern 24.

**Fix**

- Lead with the affirmative: "X achieves Y" instead of "X does not fail to achieve Y" or "It is not the case that X fails; rather, X achieves Y".
- If a negation is necessary to correct a specific misconception from prior text, state it briefly and move immediately to the affirmative: "Although prior work assumed A, this work demonstrates B."
- Remove double negatives and negation chains. Prefer the simplest affirmative form that conveys the intended meaning.

---

### 26. Overused Logical Connectors

**Signals**

- `therefore`, `thus`, `consequently`, `because`, or `so that` appears in most paragraphs, including places where the relation is evident from sentence order.
- A causal connector joins two clauses that are merely sequential.
- Sequential narration uses ornate transitions such as "Initially, ... Next, ... And then, ... After that, ... Subsequently, ...".

**Check**
Search for causal and purposive connectors. Flag the connector when the sentence reads the same without it or when the two clauses are only sequential.

**Fix**
Reserve connectors for non-obvious logical relations. Use "First, Second, Third" for plain sequences. State a causal mechanism with a concrete verb instead of stacking connectors.

---

### 27. Article, Number, and Preposition Errors

**Signals**

- A singular countable noun appears without `a`, `an`, or `the` ("Task is scheduled on active server").
- A mass noun is pluralized ("Related Works").
- A plural generic ("Users submit tasks to servers in data centers") is used where a singular generic noun is more precise.
- A preposition is missing or does not match the standard collocation ("discuss about the problem", "in the server").
- An article is chosen by spelling instead of pronunciation ("a NP-hard problem").

**Check**
For each noun phrase, decide whether the noun is countable, whether it refers to a specific instance, any instance, or the whole class, and which article that requires. Treat "work" as a mass noun in "related work" and "much work". Check each prepositional phrase against the standard collocation ("discuss the problem", "on the server"). Check article choice before abbreviations ("an NP-hard problem", "a URL").

**Fix**
Add the required article. Prefer a singular generic noun when one instance represents the class. Keep "work" singular for research. Replace a wrong preposition with the one required by the standard collocation.

---

### 28. Inconsistent Tense Across Sections

**Signals**

- The literature review uses simple present for a cited action, or mixes past and present within the same functional block, unless the venue style guide requires present tense ("Smith et al. investigate the problem").
- An existing method is described in past tense inside a present-tense sentence ("was developed, which used ...").
- The paper's own contribution is described in past tense ("this paper proposed", "the experiments were conducted").

**Check**
Classify each sentence by function. Unless the venue requires present tense, literature review reports an action by prior authors in simple past. Properties of an existing method that still hold take present tense. The paper's own contributions and claims take present tense.

**Fix**
Use "Smith et al. investigated" for the cited action and "the algorithm uses" for the method's property. Use "this paper proposes" and "the experiments evaluate" for the current work. Keep the chosen tense consistent within each functional block.

---

### 29. Word and Sentence-Structure Repetition

**Signals**

- A non-technical content word repeats within a paragraph or across adjacent paragraphs.
- Consecutive sentences share the same opening or template ("X is ... X is ...").
- The same verb describes every contribution, most often "propose".

**Check**
Count non-technical content-word occurrences per paragraph. Exclude defined terms, metrics, and the system name. Compare the first three words of consecutive sentences. List the verbs used for contributions.

**Fix**
Vary verbs according to the actual action (develop, design, introduce, formulate, derive, evaluate). Restructure sentence openings so that subject and construction alternate. For non-technical repetition, vary the wording. Do not replace defined technical terms, metrics, or the system name with synonyms. For repeated first-person openings, see Pattern 7.

---

### 30. Redundant Restatement of the Same Explanation

**Signals**

- The same definition, motivation, or limitation is explained in full more than once.
- A later section repeats the complete explanation instead of referring back.
- The introduction, method, and conclusion restate identical sentences.

**Check**
Track each key concept and count its full explanations. The first occurrence carries the definition. From the second full mention onward, a back-reference is required.

**Fix**
Keep one full explanation at first use and use a back-reference such as "the aforementioned X" from the second full mention onward. The condensed contribution echo in the conclusion is the single exception; see Pattern 12.

---

### 31. Unclear Sentence Structure

**Signals**

- The main verb lacks an identifiable agent where the agent matters for the claim.
- The object is implied but never stated.
- A modifier is placed far from the element it modifies.
- Heavy nominalization hides the action ("the optimization of the configuration is performed").

**Check**
For each sentence, write down subject, verb, object, and any adverbial in plain form. If a required element is missing or ambiguous, rewrite the sentence. Check that each adverbial sits next to the element it modifies. In passive sentences, confirm that the logical agent is clear from context or an explicit by-phrase, or that the agent is deliberately irrelevant, and check that the voice matches the intended emphasis. For pronoun subjects, see Pattern 1.

**Fix**
Name the agent and, when the verb requires one, the affected object. Replace nominalizations with verbs ("the scheduler optimizes the configuration"). Place each adverbial next to the element it modifies. Keep passive voice when the agent is irrelevant or already established.

---

### 32. Data and Evidence Without an Argument

**Signals**

- A paragraph lists many numbers, equations, or table rows without stating what they show.
- A figure is described element by element instead of explained as an argument.
- A claim is followed by data with no sentence explaining why the data support the claim.
- A design choice is described without the problem it solves.

**Check**
For each paragraph, label every substantive sentence as claim, evidence, or reasoning; mark definitions, background, and transitions as context. Flag paragraphs with many values but no stated takeaway, with claims and evidence but no reasoning, or with reasoning but no evidence. For each figure, check whether the text explains the trend and its cause.

**Fix**
State the claim first and cite one or two representative values as evidence. Add the reasoning sentence that links each value to the claim ("the reduction in tail latency indicates that the scheduler prevents queue buildup"). State the problem before describing the design choice that addresses it. Move the full data to a table or appendix, and describe the logic of the figure instead of reading out every element.

---

### 33. Title Lacks Problem or Technique

**Signals**

- The title stacks several research areas without naming the problem.
- The title is a topic label with no technique.
- A word repeats within the title.

**Check**
Confirm that the title names the problem and the technique that addresses it. The achievement and application are optional but should appear when space allows. Count repeated words and check that the title stays near ten words.

**Fix**
Compress the title to the problem and the technique that addresses it, with the outcome or application when space allows. Remove repeated words and compress as needed ("Processor configuration optimization of edge servers in mobile edge computing" → "Server configuration optimization in mobile edge computing").

---

### 34. Abstract Omits Required Components

**Signals**

- The abstract describes only background and approach.
- No result or significance appears, or an empirical claim lacks a comparison.
- The abstract reads as an introduction rather than a condensed paper.

**Check**
Confirm that the abstract covers background and motivation, the problem, the solution, the main results, and the significance. Main results may be theorems, analytical findings, or measured performance. Check that each component occupies at least one sentence and that an empirical comparison names a baseline.

**Fix**
Add the missing component in one or two sentences. Report the main result, whether a theorem, an analytical finding, or measured performance. Close with the theoretical or practical significance.

---

### 35. Related Work Lacks Categorization and Critical Comparison

**Signals**

- Prior work is summarized paper by paper with no grouping.
- Each summary stops at what the paper did and never states its limitation.
- The section never connects those limitations to the proposed approach.

**Check**
Confirm five elements. The categories follow the paper's contributions, each category names its key papers, each category states its difference or weakness, each group's gap is tied to the proposed method, and the section ends with an explicit statement of novelty and significance. Check tense against Pattern 28.

**Fix**
Group work by the dimension the paper addresses. For each group, state what it assumes or cannot handle. Close each group with the gap that the proposed method fills, and state why the gap matters. End the section with one sentence that states the novelty and significance relative to the grouped work. Keep the section concise and avoid repeating the introduction.

---

### 36. Non-Parallel Lists and Missing Serial Comma

**Signals**

- Bullet items mix full sentences, fragments, and gerunds.
- List items switch between active and passive voice.
- A list of three or more items omits the comma before the final "and".

**Check**
Read each list item in isolation and compare grammatical form. Search for the pattern "A, B and C" in running text and in lists.

**Fix**
Give every item the same grammatical form, usually a verb-first fragment under a shared stem ("This work" followed by "constructs ...", "develops ...", "evaluates ..."; see Pattern 7). Insert the serial comma in lists of three or more unless the venue style guide forbids it.

---

### 37. Citation, Cross-Reference, and Front-Matter Formatting

**Signals**

- Author mentions include first names or initials ("John Smith et al.", "J. Smith et al.").
- References are introduced as "In literature [25]" or "In reference [25]".
- An author name is attached to a citation without a space ("Lin[20]").
- Cross-references omit spaces or use inconsistent abbreviations ("Fig.1", "Eq.2", "Table1", "Alg.3", "formula (1)").
- Algorithm names are capitalized inconsistently ("Dijkstra Algorithm", "the algorithm HEFT").
- Keywords are not in alphabetical order.

**Check**
Verify author mentions, reference phrasing, spacing before citations, every figure, table, equation, algorithm, and section reference, citation grouping, and reference order against the conventions below. Check keyword order.

**Fix**

- One author: "Chen presented ...". Two authors: "Li and Wang described ...". Three or more: "Zhang et al. studied ...". Use the last name only, except for universally recognized names conventionally given in full (e.g., Isaac Newton). Set "et al." in italics (see Pattern 40).
- Cite as "In [25]" or "In Ref. [25]". Never use "In literature [25]" or "In reference [25]".
- Put a space between an author name and the citation ("Lin [20]").
- Use "Fig. 1" in parenthetical references and "Figure 2" at the start of a sentence. Use "Fig. 3(a)" and "Figs. 4(a) and 4(b)" for subfigures. Keep one table numeral system ("Table 1" or "Table III") throughout.
- Use "Equation (1)" at the start of a sentence and "Eq. (2)" elsewhere. Use "Eqs. (3) and (4)" for multiple equations, never "formula (1)" or "Eq.2".
- Use "Algorithm 1" for the paper's numbered algorithms. For a named algorithm, use "Dijkstra's algorithm", "the HEFT algorithm", or "Algorithm HEFT", and choose one named form for each named algorithm and use it consistently throughout the paper. Write "Tables 4 and 5".
- Use "Section 2.3" and "Step 1".
- Group multiple citations in one bracket in ascending order ("[12, 34, 56, 78]").
- Arrange keywords in alphabetical order unless the venue specifies another order. Order references alphabetically by first author unless the venue requires citation order.

---

### 38. Algorithm Description Conventions

**Signals**

- An algorithm is described without its input and output.
- Steps begin with "We initialize", "Modifying", or a passive clause.
- Assignment statements use prose forms with semicolons ("x is calculated by Eq. (10);").

**Check**
Confirm that input and output are stated. Check that every step opens with an imperative verb. Check that assignment uses one notation consistently.

**Fix**

- State the input and output before the first step.
- Start each step with an imperative verb, not a gerund or a passive clause ("Initialize variable x to 0", "Modify the value of y", "Update the data structure z").
- Use "Set x to the value calculated by Eq. (10)" or "x ← y + z". Keep one assignment style throughout.

---

### 39. Equation Presentation in Prose

**Signals**

- An equation stands alone without a lead-in or trailing punctuation.
- Parameters are listed before the equation, or the list restarts after a capitalized "Where".
- A long equation is typeset inline.

**Check**
Read the sentence across the equation. Confirm that the lead-in ends with "given by" or another introducing phrase, that the equation closes with a comma when a lowercase "where" clause follows, and that definitions follow in lowercase "where". If the equation ends the sentence, start the next sentence with a subject other than "Where". Check whether a long equation should be displayed.

**Fix**
Write "The dynamic power consumption is given by [equation], where a is ...". Put long equations in display style. In running text, write a simple fraction in slash form with parenthesized numerator and denominator, as in `(a+b)/(c+d)`. Never capitalize "Where" to restart the sentence.

---

### 40. Mathematical and Typographic Conventions

**Signals**

- Italic words are produced with math mode ("$efficiency$").
- Multi-letter words inside an equation use math italic instead of roman text.
- A variable or node label in running text is set in roman type ("from node P to node Q").
- Spacing is missing or delimiters do not scale ("$xεS$", "$log n$", "$|x-\frac{1}{2}|$", "$x1,x2,x3,...$").
- A multi-term or fractional exponent is written directly as a superscript instead of with `\exp(...)`.
- A large fraction is stacked with a tall numerator or denominator that overflows the line.
- "e.g.", "i.e.", "etc.", "i.i.d.", and "et al." are punctuated or italicized inconsistently.

**Check**
Scan every math expression. Confirm that words use `\text{}` or roman font, that variables and node labels in running text use math mode, that each Greek letter and operator uses its dedicated command, that operators and relations have spacing, that delimiters scale with their contents, and that punctuation inside cases and sequences is correct. Check ordinal suffixes, exponent and fraction form, and abbreviations.

**Fix**

- Write words in roman or text font, as in `\text{Efficiency} = \frac{\text{Speedup}}{\text{Number of processors}}`.
- Set a variable or node label in running text with math mode (`from node $P$ to node $Q$`), and keep the surrounding words roman.
- Use proper spacing and dedicated commands, as in `$x \in S$`, `$\log n$`, `$\ln(a+b)$`, `$c \times d$`, `$\Delta t$`, `$\langle A, B, C \rangle$`, `$\phi$`, and `$y \bmod 2$`.
- Scale delimiters with `\left( ... \right)`, `\left| ... \right|`, or `\left. ... \right|`.
- Separate a sequence with commas and use `\cdots` in a sum, as in `$x_1, x_2, x_3, \dots$` and `$S = x_1 + x_2 + \cdots + x_n$`.
- Punctuate cases as a sentence ("1, if x > 0; 0, otherwise.").
- For a large fraction, keep the main fraction readable. Parenthesize a compound numerator, write a compound denominator as `\left( ... \right)^{-1}`, and use a parenthesized slash form when both parts are large.
- Use `\exp(...)` when the exponent contains a sum, a fraction, or several terms. Use roman subscripts for labels (`T_{\text{sequential}}`). Use `\vdots` and `\cdots` in matrices.
- Write the ordinal suffix in roman text. In running text, use the baseline form (`$i$th`) or the hyphenated form (`$j$-th`); inside an expression, use the superscript form (`$i^{\text{th}}$`). Do not mix forms within the same context.
- Write "e.g.,", "i.e.,", "etc.", "i.i.d.", and italic "et al." with correct punctuation.
