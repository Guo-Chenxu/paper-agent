# Memory Index

This file indexes all memory files for the paper-agent project. Each memory captures persistent project requirements, user preferences, or workflow constraints.

## Project Memories

- [Paper Requirements Template](paper-requirements.template.md) — Template for paper writing requirements (research direction, page allocation, reference constraints)

## Usage

When starting a new research project, the agent will:
1. Gather user requirements
2. Create `paper-requirements.md` based on the template
3. Add an entry here pointing to the new memory file
4. All subsequent stages will reference the memory file for constraints
