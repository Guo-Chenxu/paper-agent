# Method Overview Template

`Overview usually includes setting, core contribution, optional figure pointer, and subsection map.`

```latex
% Overview
% One or two sentences for setting
%% Example 1: Given a stream of service events and deployment records, our goal is to identify which change most likely caused a reliability regression.
%% Example 2: Given a code review containing generated suggestions, our goal is to help reviewers inspect the evidence behind each suggestion.

% One or two sentences for core contribution
%% Example 1: We introduce a change-attribution mechanism that links event shifts to dependency changes and ranks candidate causes by temporal and structural evidence.
%% Example 2: We design an inline explanation interface that reveals rationale only when the reviewer requests or hesitates on a suggestion.
%% Example 3: We present a type-directed checker that converts source programs into constraints, simplifies the constraints, and reports source-level blame slices.

% If a figure helps, point to it
%% Example: Figure 3 overviews the analysis workflow and the state maintained between reviews.

% Explain what Section 3.1 covers
%% Example 1: Section 3.1 defines the event and dependency model used by the attribution mechanism.
%% Example 2: Section 3.1 describes the interface states and interaction triggers.

% Explain what Section 3.2 covers
%% Example 1: Section 3.2 presents the ranking algorithm and its update procedure.
%% Example 2: Section 3.2 describes how explanations are generated from reviewer-visible evidence.

% Explain what Section 3.3 covers
%% Example: Section 3.3 discusses implementation choices, assumptions, and failure modes.
```
