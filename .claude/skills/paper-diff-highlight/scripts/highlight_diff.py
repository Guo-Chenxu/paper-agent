#!/usr/bin/env python3
"""Copy a LaTeX file and highlight the text changed since a git revision."""

from __future__ import annotations

import argparse
import bisect
import difflib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path, PurePosixPath
from typing import NamedTuple

ENCODING = "utf-8"
ERRORS = "surrogateescape"
SUFFIX = "_highlighted"
MAX_SNIPPETS = 60

# Environments whose bodies are raw text and must never be tokenized as LaTeX.
VERBATIM_ENVS: tuple[str, ...] = (
    "verbatim", "verbatim*", "Verbatim", "Verbatim*", "BVerbatim", "lstlisting",
    "minted", "comment", "filecontents", "filecontents*",
)
_VENV = "|".join(re.escape(e) for e in VERBATIM_ENVS)
_CJK = "\u2e80-\u2fff\u3000-\u303f\u3040-\u30ff\u3100-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef"

TOKEN_RE = re.compile(
    r"(?P<comment>%[^\n]*)"
    rf"|(?P<verbenv>\\begin\{{(?P<venv>{_VENV})\}}[\s\S]*?\\end\{{(?P=venv)\}})"
    r"|(?P<verb>\\verb\*?(?P<vd>[^A-Za-z\s*])[^\n]*?(?P=vd))"
    r"|(?P<lstinline>\\lstinline(?:\[[^\]\n]*\])?(?:\{[^}\n]*\}|(?P<ld>[^A-Za-z\s\[{])[^\n]*?(?P=ld)))"
    r"|(?P<url>\\(?:url|nolinkurl|path)\s*\{[^}\n]*\})"
    r"|(?P<href>\\href\s*\{[^}\n]*\})"
    r"|(?P<cs>\\[A-Za-z@]+)"
    r"|(?P<csym>\\[\s\S])"
    r"|(?P<dollar2>\$\$)"
    r"|(?P<dollar>\$)"
    r"|(?P<lbrace>\{)|(?P<rbrace>\})|(?P<lbrack>\[)|(?P<rbrack>\])"
    r"|(?P<amp>&)|(?P<tie>~)"
    r"|(?P<ws>\s+)"
    rf"|(?P<cjk>[{_CJK}])"
    r"|(?P<num>\d+(?:[.,]\d+)+)"
    rf"|(?P<word>(?:(?![{_CJK}])[^\W_])+)"
    r"|(?P<punct>[\s\S])"
)
PAR_RE = re.compile(r"\n[ \t\r]*\n")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

# Token kinds ignored when comparing old and new text.
NON_CMP_KINDS = frozenset({"ws", "par", "tie", "comment"})
# Token kinds reported when a change to them cannot be highlighted.
CONTENT_KINDS = frozenset({"word", "num", "cjk", "punct", "verbenv", "verb", "lstinline", "url", "href"})

# Argument specs: s = optional star, o = optional [..], m = opaque {..}, T = text {..} parsed recursively.
TEXT_ARG_CMDS: dict[str, str] = {
    **{name: "soT" for name in (
        "part", "chapter", "section", "subsection", "subsubsection", "paragraph", "subparagraph",
    )},
    "caption": "oT", "subcaption": "oT", "captionof": "smoT",
    "footnote": "oT", "footnotetext": "oT", "thanks": "T", "title": "oT", "subtitle": "T",
    "keywords": "T", "Comment": "T", "multicolumn": "mmT", "multirow": "momoT", "textcolor": "omT", "colorbox": "omT",
}
# Inline formatting commands with one text argument; wrapped as a whole when fully changed.
FMT_CMDS: frozenset[str] = frozenset({
    "textbf", "textit", "emph", "texttt", "textsc", "textsf", "textrm", "textmd", "textup", "textsl",
    "textnormal", "underline", "uline", "mbox", "enquote", "textsuperscript", "textsubscript",
})
# Commands highlighted as one unit together with their arguments.
ATOM_CMDS: dict[str, str] = {
    **{name: "soom" for name in (
        "cite", "citep", "citet", "citealp", "citealt", "citeauthor", "citeyear", "citeyearpar",
        "Citep", "Citet", "Citeauthor", "parencite", "Parencite", "textcite", "Textcite",
        "autocite", "Autocite", "footcite", "fullcite",
    )},
    **{name: "sm" for name in (
        "ref", "eqref", "autoref", "Autoref", "cref", "Cref", "cpageref", "Cpageref", "pageref",
        "nameref", "vref", "Vref",
    )},
    **{name: "m" for name in ("c", "v", "u", "H", "r", "d", "b", "t", "k")},
    "footnotemark": "o", "hyperref": "om",
    "num": "om", "si": "om", "SI": "omom", "qty": "omm", "unit": "om", "ang": "om",
}
# Argument-free commands that print text.
NOARG_TEXT_MACROS: frozenset[str] = frozenset({
    "LaTeX", "TeX", "LaTeXe", "BibTeX", "ldots", "dots", "textellipsis", "textendash", "textemdash",
    "textquotedblleft", "textquotedblright", "textquoteleft", "textquoteright", "textasciitilde",
    "textbackslash", "textbar", "textless", "textgreater", "textdegree", "texttimes", "textregistered",
    "texttrademark", "copyright", "S", "P", "dag", "ddag", "textbullet", "textperiodcentered", "textpm",
    "textmu", "euro", "checkmark", "eg", "ie", "etal", "cf", "vs", "etc", "wrt",
})
# Commands that never print highlightable text; value is the argument spec to skip.
BARRIER_SPECS: dict[str, str] = {
    **{name: "" for name in (
        "noindent", "indent", "centering", "raggedright", "raggedleft", "par", "newline", "medskip",
        "smallskip", "bigskip", "clearpage", "newpage", "cleardoublepage", "maketitle", "appendix",
        "hline", "toprule", "midrule", "bottomrule", "bf", "it", "em", "rm", "sf", "tt", "sc", "sl",
        "bfseries", "itshape", "mdseries", "normalfont", "upshape", "scshape", "slshape", "rmfamily",
        "sffamily", "ttfamily", "tiny", "scriptsize", "footnotesize", "small", "normalsize", "large",
        "Large", "LARGE", "huge", "Huge", "quad", "qquad", "sloppy", "fussy", "protect", "relax",
        "selectfont", "hfill", "vfill", "break", "nobreak", "allowbreak", "tableofcontents",
        "listoffigures", "listoftables", "IEEEpeerreviewmaketitle", "and",
    )},
    **{name: "o" for name in ("item", "linebreak", "pagebreak", "nolinebreak", "nopagebreak")},
}
INPUT_CMDS: frozenset[str] = frozenset({"input", "include", "subfile"})
PAREN_ARG_CMDS: frozenset[str] = frozenset({"cmidrule"})
DISPLAY_MATH_ENVS: frozenset[str] = frozenset({
    "equation", "equation*", "align", "align*", "alignat", "alignat*", "flalign", "flalign*",
    "gather", "gather*", "multline", "multline*", "eqnarray", "eqnarray*", "displaymath",
    "dmath", "dmath*", "IEEEeqnarray", "IEEEeqnarray*",
})
INLINE_MATH_ENVS: frozenset[str] = frozenset({"math"})
OPAQUE_ENVS: frozenset[str] = frozenset({
    "tikzpicture", "pgfpicture", "axis", "semilogxaxis", "semilogyaxis", "loglogaxis", "groupplot",
    "picture", "forest", "tikzcd", "pspicture",
})
TEXT_ESCAPES: frozenset[str] = frozenset({
    "\\%", "\\&", "\\#", "\\_", "\\$", "\\{", "\\}", "\\ ", "\\,", "\\-", "\\/", "\\@",
})
ACCENT_CHARS = "'`\"^~=."
# siunitx commands break ulem, so hl mode puts them in a colored box.
BOX_CMDS: frozenset[str] = frozenset({"num", "si", "SI", "qty", "unit", "ang"})

NEWCOMMAND_RE = re.compile(r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)\*?\s*"
                           r"\{?\s*\\([A-Za-z]+)\s*\}?\s*(?:\[\s*(\d+)\s*\])?\s*(\[[^\]]*\]\s*)?(?=\{)")
DEF_RE = re.compile(r"\\[gex]?def\s*\\([A-Za-z]+)\s*(?=\{)")
# A macro body with any of these commands produces layout, not inline text.
LAYOUT_BODY_RE = re.compile(
    r"\\(?:par|vspace|vskip|addvspace|bigskip|medskip|smallskip|part|chapter|section|subsection|"
    r"subsubsection|paragraph|begin|end|item|newpage|clearpage|pagebreak|hrule|noindent|centering|"
    r"label|includegraphics|maketitle|input|include)(?![A-Za-z])")
PREAMBLE_INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}|\\usepackage\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")

PREAMBLE_COMMON = r"""\usepackage{xcolor}
\colorlet{diffhlfg}{%(color)s}
\makeatletter
\DeclareRobustCommand{\DiffHlOn}{\ifvmode\leavevmode\fi\color{diffhlfg}}
\DeclareRobustCommand{\DiffHlBlock}{\color{diffhlfg}}
\AtBeginDocument{\@ifundefined{pdfstringdefDisableCommands}{}{%%
  \pdfstringdefDisableCommands{\let\DiffHlOn\relax\let\DiffHlBlock\relax
    \let\DiffHlText\@firstofone\let\DiffHlBox\@firstofone}}}
\makeatother
"""
# hl mode: ulem draws a background band that breaks across lines; xeCJKfntef makes ulem handle CJK.
PREAMBLE_HL = r"""\makeatletter
\@ifpackageloaded{ulem}{}{\usepackage[normalem]{ulem}}
\@ifpackageloaded{xeCJK}{\@ifpackageloaded{xeCJKfntef}{}{\usepackage{xeCJKfntef}}}{}
\makeatother
\colorlet{diffhlbg}{%(hl_color)s}
\DeclareRobustCommand{\DiffHlText}[1]{\bgroup
  \markoverwith{\textcolor{diffhlbg}{\rule[-.3\baselineskip]{.5pt}{\baselineskip}}}\ULon{#1}}
\DeclareRobustCommand{\DiffHlBox}[1]{{\setlength{\fboxsep}{0pt}\colorbox{diffhlbg}{\strut #1}}}
"""
PREAMBLE_COLOR = r"""\DeclareRobustCommand{\DiffHlText}[1]{{\DiffHlOn #1}}
\DeclareRobustCommand{\DiffHlBox}[1]{{\DiffHlOn #1}}
"""
WRAP_OPEN: dict[str, str] = {
    "color": "{\\DiffHlOn ", "block": "{\\DiffHlBlock ", "text": "\\DiffHlText{", "box": "\\DiffHlBox{",
}
# Display math ignores the following space; the extra closing brace would otherwise expose it.
WRAP_CLOSE: dict[str, str] = {"color": "}", "block": "}\\ignorespaces ", "text": "}", "box": "}"}


class HlLevel(IntEnum):
    """How an item can be highlighted in hl mode; a group of items takes the highest level."""
    FLOW = 0  # inside the ulem background band, which breaks across lines
    BOX = 1  # inside an unbreakable colored box
    COLOR = 2  # colored text only, because the item cannot be a macro argument (e.g., \url)


HL_WRAP_KIND: dict[HlLevel, str] = {HlLevel.FLOW: "text", HlLevel.BOX: "box", HlLevel.COLOR: "color"}


class Token(NamedTuple):
    kind: str
    text: str
    start: int
    end: int


@dataclass
class Hunk:
    new_start: int
    new_count: int
    old_text: str


@dataclass
class Item:
    kind: str  # ws | text | atom | fmt | block | barrier
    start: int  # first token index
    end: int  # token index after the item
    changed: bool = False
    full: bool = False
    level: HlLevel = HlLevel.FLOW
    children: list[list[Item]] = field(default_factory=list)


@dataclass
class Wrap:
    start: int  # char offset in the new file
    end: int
    kind: str  # color | text | block


@dataclass
class InputRef:
    path: str
    start: int  # char offsets of the path text inside the braces
    end: int


@dataclass
class Options:
    style: str
    color: str
    hl_color: str
    merge_gap: int
    text_cmds: frozenset[str]
    follow_inputs: bool


@dataclass
class FileResult:
    source: Path
    output: Path
    wraps: list[Wrap]
    missed_lines: dict[str, list[int]]
    snippets: list[tuple[int, str]]
    deletions: list[int]
    children: list[FileResult] = field(default_factory=list)
    written: bool = False


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup or "punct"
        if kind == "ws" and PAR_RE.search(m.group()):
            kind = "par"
        tokens.append(Token(kind, m.group(), m.start(), m.end()))
    return tokens


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding=ENCODING, errors=ERRORS)


def parse_hunks(diff_text: str) -> list[Hunk]:
    hunks: list[Hunk] = []
    lines = diff_text.split("\n")
    i = 0
    while i < len(lines):
        m = HUNK_RE.match(lines[i])
        i += 1
        if not m:
            continue
        rem_old = int(m.group(2)) if m.group(2) is not None else 1
        rem_new = int(m.group(4)) if m.group(4) is not None else 1
        hunk = Hunk(int(m.group(3)), rem_new, "")
        old_lines: list[str] = []
        while i < len(lines) and (rem_old > 0 or rem_new > 0 or lines[i].startswith("\\")):
            line = lines[i]
            if line.startswith("-"):
                old_lines.append(line[1:])
                rem_old -= 1
            elif line.startswith("+"):
                rem_new -= 1
            elif line.startswith(" "):
                rem_old -= 1
                rem_new -= 1
            elif not line.startswith("\\"):
                break
            i += 1
        hunk.old_text = "\n".join(old_lines)
        hunks.append(hunk)
    return hunks


class GitSource:
    """Reads the new version of a file and its diff hunks against the base revision."""

    def __init__(self, base: str, to: str | None) -> None:
        self.base = base
        self.to = to

    def read_new(self, path: Path) -> str | None:
        if self.to is None:
            if not path.is_file():
                return None
            with open(path, encoding=ENCODING, errors=ERRORS, newline="") as f:
                return f.read()
        result = run_git(["show", f"{self.to}:./{path.name}"], path.parent)
        return result.stdout if result.returncode == 0 else None

    def hunks(self, path: Path) -> list[Hunk] | None:
        """Return diff hunks, or None when the file does not exist in the base revision."""
        if run_git(["cat-file", "-e", f"{self.base}:./{path.name}"], path.parent).returncode != 0:
            return None
        args = ["diff", "--no-color", "--no-ext-diff", "--no-textconv", "-U0", self.base]
        if self.to:
            args.append(self.to)
        result = run_git([*args, "--", path.name], path.parent)
        if result.returncode != 0:
            sys.exit(f"git diff failed for {path}: {result.stderr.strip()}")
        return parse_hunks(result.stdout)


def diff_flags(old: list[str], new: list[str], merge_gap: int) -> tuple[list[bool], list[int]]:
    """Flag changed new tokens and return the new-token indices where old tokens were only deleted.

    Short unchanged runs between two changes are absorbed into the change.
    """
    ops = difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()
    grow = ("replace", "insert")
    flags = [False] * len(new)
    deleted_at = [j1 for tag, _, _, j1, _ in ops if tag == "delete"]
    for idx, (tag, _, _, j1, j2) in enumerate(ops):
        absorb = (tag == "equal" and j2 - j1 <= merge_gap and 0 < idx < len(ops) - 1
                  and ops[idx - 1][0] in grow and ops[idx + 1][0] in grow)
        if tag in grow or absorb:
            flags[j1:j2] = [True] * (j2 - j1)
    return flags, deleted_at


def changed_intervals(new_text: str, hunks: list[Hunk] | None,
                      merge_gap: int) -> tuple[list[tuple[int, int]], list[int]]:
    """Return changed char intervals in the new text and line numbers where text was only deleted."""
    if hunks is None:
        return [(0, len(new_text))], []
    line_starts = [0] + [m.end() for m in re.finditer("\n", new_text)]

    def offset(line_idx: int) -> int:
        return line_starts[line_idx] if line_idx < len(line_starts) else len(new_text)

    intervals: list[tuple[int, int]] = []
    deletions: list[int] = []
    for hunk in hunks:
        if hunk.new_count == 0:
            if any(t.kind not in NON_CMP_KINDS for t in tokenize(hunk.old_text)):
                deletions.append(max(hunk.new_start, 1))
            continue
        a, b = offset(hunk.new_start - 1), offset(hunk.new_start - 1 + hunk.new_count)
        old = [t.text for t in tokenize(hunk.old_text) if t.kind not in NON_CMP_KINDS]
        new = [t for t in tokenize(new_text[a:b]) if t.kind not in NON_CMP_KINDS]
        flags, deleted_at = diff_flags(old, [t.text for t in new], merge_gap)
        intervals.extend((a + t.start, a + t.end) for t, flag in zip(new, flags) if flag)
        for j in deleted_at:
            pos = a + (new[j].start if j < len(new) else len(new_text[a:b].rstrip("\n")))
            deletions.append(new_text.count("\n", 0, pos) + 1)
    return intervals, deletions


def overlaps(intervals: list[tuple[int, int]], starts: list[int], s: int, e: int) -> bool:
    idx = bisect.bisect_right(starts, s) - 1
    if idx >= 0 and intervals[idx][1] > s:
        return True
    return idx + 1 < len(intervals) and intervals[idx + 1][0] < e


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def read_group(text: str, pos: int) -> str:
    """Return the balanced {...} group starting at pos, without the outer braces."""
    depth = 0
    for k in range(pos, len(text)):
        if text[k] == "\\":
            continue
        if text[k] == "{" and text[k - 1] != "\\":
            depth += 1
        elif text[k] == "}" and text[k - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[pos + 1:k]
    return text[pos + 1:]


def detect_user_macros(defs_text: str) -> dict[str, str]:
    """Map user macros that print inline text to argument specs; their calls are highlighted as one unit."""
    text = "".join(t.text for t in tokenize(defs_text) if t.kind != "comment")
    macros: dict[str, str] = {}
    for m in NEWCOMMAND_RE.finditer(text):
        if LAYOUT_BODY_RE.search(read_group(text, m.end())):
            macros.pop(m.group(1), None)
            continue
        n_args = int(m.group(2) or 0)
        macros[m.group(1)] = ("o" + "m" * (n_args - 1)) if m.group(3) and n_args else "m" * n_args
    for m in DEF_RE.finditer(text):
        if not LAYOUT_BODY_RE.search(read_group(text, m.end())):
            macros[m.group(1)] = ""
    return macros


def collect_macro_sources(text: str, root_dir: Path, source: GitSource, seen: set[Path], depth: int = 0) -> str:
    """Concatenate the preamble with local files it loads (\\input and local .sty) for macro detection."""
    parts = [text]
    if depth >= 3:
        return text
    clean = "".join(t.text for t in tokenize(text) if t.kind != "comment")
    for m in PREAMBLE_INPUT_RE.finditer(clean):
        names = [m.group(1)] if m.group(1) else [f"{n.strip()}.sty" for n in m.group(2).split(",")]
        for name in names:
            name = name.strip()
            candidates = [name] if name.endswith((".tex", ".sty")) else [f"{name}.tex", name]
            for cand in candidates:
                path = (root_dir / cand).resolve()
                if path in seen:
                    break
                content = source.read_new(path)
                if content is not None:
                    seen.add(path)
                    parts.append(collect_macro_sources(content, root_dir, source, seen, depth + 1))
                    break
    return "\n".join(parts)


class Parser:
    """Parses a LaTeX token stream into highlightable items and emits non-overlapping wraps."""

    def __init__(self, tokens: list[Token], changed: list[bool], comparable: list[bool],
                 opts: Options, user_macros: dict[str, str]) -> None:
        self.toks = tokens
        self.limit = len(tokens)
        self.opts = opts
        self.user_macros = user_macros
        self.chg_prefix = [0]
        self.cmp_prefix = [0]
        for c, p in zip(changed, comparable):
            self.chg_prefix.append(self.chg_prefix[-1] + int(c))
            self.cmp_prefix.append(self.cmp_prefix[-1] + int(p))
        self.wraps: list[Wrap] = []
        self.inputs: list[InputRef] = []
        self.env_name_toks: set[int] = set()

    # ---------- token helpers ----------
    def any_changed(self, a: int, b: int) -> bool:
        return self.chg_prefix[b] > self.chg_prefix[a]

    def all_changed(self, a: int, b: int) -> bool:
        n_chg = self.chg_prefix[b] - self.chg_prefix[a]
        return n_chg > 0 and n_chg == self.cmp_prefix[b] - self.cmp_prefix[a]

    def is_tok(self, i: int, kind: str, text: str | None = None) -> bool:
        return i < self.limit and self.toks[i].kind == kind and (text is None or self.toks[i].text == text)

    def skip_space(self, i: int) -> int:
        while self.is_tok(i, "ws"):
            i += 1
        return i

    def match_brace(self, i: int) -> int:
        depth = 0
        for j in range(i, self.limit):
            kind = self.toks[j].kind
            if kind == "lbrace":
                depth += 1
            elif kind == "rbrace":
                depth -= 1
                if depth == 0:
                    return j + 1
        return self.limit

    def match_closer(self, i: int, closer: str) -> int:
        """Match an optional argument opened at i; the closer must sit outside braces."""
        depth = 0
        for j in range(i + 1, self.limit):
            tok = self.toks[j]
            if tok.kind == "par":
                break
            if tok.kind == "lbrace":
                depth += 1
            elif tok.kind == "rbrace":
                depth -= 1
                if depth < 0:
                    break
            elif depth == 0 and tok.text == closer:
                return j + 1
        return i + 1

    def group_text(self, i: int) -> tuple[str | None, int]:
        """Read a {name} group such as an environment name and mark its tokens as structural."""
        i = self.skip_space(i)
        if not self.is_tok(i, "lbrace"):
            return None, i
        end = self.match_brace(i)
        self.env_name_toks.update(range(i, end))
        return "".join(t.text for t in self.toks[i + 1:end - 1]).strip(), end

    def take_args(self, j: int, spec: str) -> tuple[int, list[tuple[str, int, int]]]:
        args: list[tuple[str, int, int]] = []
        for ch in spec:
            k = self.skip_space(j)
            if ch == "s":
                if k == j and self.is_tok(k, "punct", "*"):
                    j = k + 1
            elif ch == "o":
                if self.is_tok(k, "lbrack"):
                    j = self.match_closer(k, "]")
                    args.append(("o", k, j))
            elif self.is_tok(k, "lbrace"):
                j = self.match_brace(k)
                args.append((ch, k, j))
            else:
                break
        return j, args

    def take_unknown_args(self, j: int, paren: bool = False, same_line: bool = False) -> int:
        """Skip arguments of an unknown command; with same_line, arguments must not start on a new line."""
        if self.is_tok(j, "punct", "*"):
            j += 1
        while True:
            k = self.skip_space(j)
            if same_line and any("\n" in self.toks[x].text for x in range(j, k)):
                return j
            if self.is_tok(k, "lbrace"):
                j = self.match_brace(k)
            elif self.is_tok(k, "lbrack"):
                j = self.match_closer(k, "]")
            elif paren and k == j and self.is_tok(k, "punct", "("):
                j = self.match_closer(k, ")")
            else:
                return j

    def find_inline_math_end(self, i: int) -> int | None:
        depth = 0
        for j in range(i + 1, self.limit):
            kind = self.toks[j].kind
            if kind == "par":
                return None
            if kind == "lbrace":
                depth += 1
            elif kind == "rbrace":
                depth -= 1
            elif kind == "dollar" and depth == 0:
                return j + 1
        return None

    def find_token(self, i: int, kind: str, text: str) -> int | None:
        for j in range(i + 1, self.limit):
            if self.toks[j].kind == kind and self.toks[j].text == text:
                return j + 1
        return None

    def find_env_end(self, i: int, name: str) -> int:
        depth = 1
        j = i
        while j < self.limit:
            tok = self.toks[j]
            if tok.kind == "cs" and tok.text in ("\\begin", "\\end"):
                env, after = self.group_text(j + 1)
                if env == name:
                    depth += 1 if tok.text == "\\begin" else -1
                    if depth == 0:
                        return after
                j = after if env is not None else j + 1
                continue
            j += 1
        return self.limit

    # ---------- item constructors ----------
    def text(self, a: int, b: int) -> Item:
        return Item("text", a, b, changed=self.any_changed(a, b))

    def atom(self, a: int, b: int, level: HlLevel | None = None) -> Item:
        """A unit highlighted whole; by default ulem accepts it unless a space sits outside its braces."""
        if level is None:
            level = HlLevel.BOX if self.has_top_level_space(a, b) else HlLevel.FLOW
        return Item("atom", a, b, changed=self.any_changed(a, b), level=level)

    def has_top_level_space(self, a: int, b: int) -> bool:
        """ulem splits its argument at top-level spaces, which breaks commands such as \\cite[p. 3]{x}."""
        depth = 0
        for tok in self.toks[a:b]:
            if tok.kind == "lbrace":
                depth += 1
            elif tok.kind == "rbrace":
                depth -= 1
            elif tok.kind == "ws" and depth == 0:
                return True
        return False

    def block(self, a: int, b: int) -> Item:
        return Item("block", a, b, changed=self.any_changed(a, b))

    def barrier(self, a: int, b: int, children: list[list[Item]] | None = None) -> Item:
        return Item("barrier", a, b, children=children or [])

    def fmt(self, a: int, b: int, children: list[list[Item]]) -> Item:
        return Item("fmt", a, b, changed=self.any_changed(a, b), full=self.all_changed(a, b), children=children)

    def arg_children(self, args: list[tuple[str, int, int]]) -> list[list[Item]]:
        return [self.parse_seq(a + 1, "}")[0] for kind, a, _ in args if kind == "T"]

    # ---------- parsing ----------
    def parse_seq(self, i: int, stop: str) -> tuple[list[Item], int]:
        """Parse until stop ('}' or 'env:<name>'); return items and the index of the stop token."""
        items: list[Item] = []
        while i < self.limit:
            tok = self.toks[i]
            if tok.kind == "rbrace":
                if stop == "}":
                    return items, i
                items.append(self.barrier(i, i + 1))
                i += 1
                continue
            if tok.kind == "cs" and tok.text == "\\end":
                name, after = self.group_text(i + 1)
                if stop == f"env:{name}":
                    return items, i
                items.append(self.barrier(i, after))
                i = after
                continue
            item = self.parse_item(i)
            items.append(item)
            i = item.end
        return items, i

    def parse_item(self, i: int) -> Item:
        tok = self.toks[i]
        kind = tok.kind
        if kind in ("ws", "tie"):
            return Item("ws", i, i + 1)
        if kind in ("word", "num", "lbrack", "rbrack", "cjk", "punct"):
            return self.text(i, i + 1)
        if kind == "url":
            return self.atom(i, i + 1, HlLevel.COLOR)
        if kind == "href":
            return self.atom(i, self.take_args(i + 1, "m")[0], HlLevel.COLOR)
        if kind == "dollar":
            end = self.find_inline_math_end(i)
            return self.atom(i, end, HlLevel.FLOW) if end else self.barrier(i, i + 1)
        if kind == "dollar2":
            end = self.find_token(i, "dollar2", "$$")
            return self.block(i, end) if end else self.barrier(i, i + 1)
        if kind == "lbrace":
            children, close = self.parse_seq(i + 1, "}")
            end = close + 1 if self.is_tok(close, "rbrace") else close
            return self.fmt(i, end, [children])
        if kind == "csym":
            return self.parse_csym(i)
        if kind == "cs":
            return self.parse_cs(i)
        return self.barrier(i, i + 1)

    def parse_csym(self, i: int) -> Item:
        text = self.toks[i].text
        if text == "\\(":
            end = self.find_token(i, "csym", "\\)")
            return self.atom(i, end, HlLevel.FLOW) if end else self.barrier(i, i + 1)
        if text == "\\[":
            end = self.find_token(i, "csym", "\\]")
            return self.block(i, end) if end else self.barrier(i, i + 1)
        if text == "\\\\":
            return self.barrier(i, self.take_args(i + 1, "so")[0])
        if text in TEXT_ESCAPES:
            return self.text(i, i + 1)
        if text[1] in ACCENT_CHARS:
            j = i + 1
            if self.is_tok(j, "lbrace"):
                j = self.match_brace(j)
            elif self.is_tok(j, "word"):
                j += 1
            return self.text(i, j)
        return self.barrier(i, i + 1)

    def parse_cs(self, i: int) -> Item:
        name = self.toks[i].text[1:]
        if name == "begin":
            return self.parse_env(i)
        if name in INPUT_CMDS:
            end, args = self.take_args(i + 1, "m")
            if args:
                _, a, b = args[0]
                if b - a >= 3:
                    self.inputs.append(InputRef("".join(t.text for t in self.toks[a + 1:b - 1]).strip(),
                                                self.toks[a + 1].start, self.toks[b - 2].end))
            return self.barrier(i, end)
        if name in TEXT_ARG_CMDS:
            end, args = self.take_args(i + 1, TEXT_ARG_CMDS[name])
            return self.barrier(i, end, self.arg_children(args))
        if name in FMT_CMDS or name in self.opts.text_cmds:
            end, args = self.take_args(i + 1, "s" + "o" * (name in self.opts.text_cmds) + "T")
            if not any(kind == "T" for kind, _, _ in args):
                return self.barrier(i, end)
            return self.fmt(i, end, self.arg_children(args))
        if name in ATOM_CMDS:
            end = self.take_args(i + 1, ATOM_CMDS[name])[0]
            return self.atom(i, end, HlLevel.BOX if name in BOX_CMDS else None)
        spec = "" if name in NOARG_TEXT_MACROS else self.user_macros.get(name)
        if spec is not None:
            end = self.take_args(i + 1, spec)[0]
            if not spec and self.is_tok(end, "lbrace") and self.is_tok(end + 1, "rbrace"):
                end += 2
            return self.atom(i, end)
        if name in BARRIER_SPECS:
            return self.barrier(i, self.take_args(i + 1, BARRIER_SPECS[name])[0])
        return self.barrier(i, self.take_unknown_args(i + 1, paren=name in PAREN_ARG_CMDS))

    def parse_env(self, i: int) -> Item:
        name, after = self.group_text(i + 1)
        if name is None:
            return self.barrier(i, i + 1)
        if name in DISPLAY_MATH_ENVS:
            return self.block(i, self.find_env_end(after, name))
        if name in INLINE_MATH_ENVS:
            return self.atom(i, self.find_env_end(after, name), HlLevel.BOX)
        if name in OPAQUE_ENVS:
            return self.barrier(i, self.find_env_end(after, name))
        children, close = self.parse_seq(self.take_unknown_args(after, same_line=True), f"env:{name}")
        end = self.group_text(close + 1)[1] if self.is_tok(close, "cs", "\\end") else close
        return self.barrier(i, end, [children])

    # ---------- wrap emission ----------
    def joinable(self, item: Item) -> bool:
        if not item.changed:
            return False
        if item.kind in ("text", "atom"):
            return True
        return item.kind == "fmt" and item.full and self.opts.style == "color"

    def add_wrap(self, items: list[Item], kind: str) -> None:
        while items and items[-1].kind == "ws":
            items.pop()
        if items:
            self.wraps.append(Wrap(self.toks[items[0].start].start, self.toks[items[-1].end - 1].end, kind))

    def flush(self, run: list[Item]) -> None:
        if self.opts.style == "color":
            self.add_wrap(run, "color")
            return
        # Items without whitespace between them print as one word, so a word takes its highest level.
        words: list[tuple[HlLevel, list[Item]]] = []
        for item in run:
            if item.kind == "ws":
                words[-1][1].append(item)
            elif words and words[-1][1][-1].kind != "ws":
                words[-1] = (max(words[-1][0], item.level), words[-1][1] + [item])
            else:
                words.append((item.level, [item]))
        # Adjacent words share a wrap, except boxes, which must stay short to allow line breaks.
        group: list[Item] = []
        group_level = HlLevel.FLOW
        for level, items in words:
            if group and (level != group_level or level == HlLevel.BOX):
                self.add_wrap(group, HL_WRAP_KIND[group_level])
                group = []
            group_level = level
            group.extend(items)
        self.add_wrap(group, HL_WRAP_KIND[group_level])

    def emit(self, items: list[Item]) -> None:
        run: list[Item] = []
        for item in items:
            if item.kind == "ws":
                if run:
                    run.append(item)
                continue
            if self.joinable(item):
                run.append(item)
                continue
            self.flush(run)
            run = []
            if item.kind == "block" and item.changed:
                self.add_wrap([item], "block")
            else:
                for child in item.children:
                    self.emit(child)
        self.flush(run)


def find_document_range(tokens: list[Token]) -> tuple[int, int] | None:
    """Return (index after \\begin{document}, char offset of \\begin) or None for a fragment file."""
    for i, tok in enumerate(tokens):
        if tok.kind == "cs" and tok.text == "\\begin":
            j = i + 1
            while j < len(tokens) and tokens[j].kind == "ws":
                j += 1
            if j + 2 < len(tokens) and tokens[j].kind == "lbrace" and tokens[j + 1].text == "document" \
                    and tokens[j + 2].kind == "rbrace":
                return j + 3, tok.start
    return None


def line_of(line_starts: list[int], offset: int) -> int:
    return bisect.bisect_right(line_starts, offset)


def compress_lines(lines: list[int]) -> str:
    spans: list[str] = []
    for line in sorted(set(lines)):
        if spans and spans[-1].split("-")[-1] == str(line - 1):
            spans[-1] = f"{spans[-1].split('-')[0]}-{line}"
        else:
            spans.append(str(line))
    return ", ".join(spans)


def output_name(path: Path) -> Path:
    return path.with_name(f"{path.stem}{SUFFIX}{path.suffix or '.tex'}")


def resolve_input(root_dir: Path, ref: str, source: GitSource) -> Path | None:
    """LaTeX resolves \\input paths against the compile directory, which is the root file's directory."""
    candidates = [ref] if ref.endswith(".tex") else [f"{ref}.tex", ref]
    for cand in candidates:
        path = (root_dir / cand).resolve()
        if source.read_new(path) is not None:
            return path
    return None


def process_file(path: Path, output: Path, root_dir: Path, source: GitSource, opts: Options,
                 inherited_macros: dict[str, str], visited: set[Path], is_root: bool) -> FileResult:
    """Highlight one file; a non-root file is written only when it or a file it inputs has highlights."""
    visited.add(path)
    new_text = source.read_new(path)
    if new_text is None:
        sys.exit(f"Cannot read the new version of {path}")
    raw_intervals, deletions = changed_intervals(new_text, source.hunks(path), opts.merge_gap)
    intervals = merge_intervals(raw_intervals)
    starts = [s for s, _ in intervals]
    tokens = tokenize(new_text)
    comparable = [t.kind not in NON_CMP_KINDS for t in tokens]
    changed = [c and overlaps(intervals, starts, t.start, t.end) for t, c in zip(tokens, comparable)]

    doc = find_document_range(tokens)
    body_start, begin_offset = doc if doc else (0, None)
    macros = dict(inherited_macros)
    if begin_offset is not None:
        macros.update(detect_user_macros(collect_macro_sources(new_text[:begin_offset], root_dir, source, {path})))
    parser = Parser(tokens, changed, comparable, opts, macros)
    items, body_end = parser.parse_seq(body_start, "env:document" if doc else "eof")
    parser.emit(items)

    line_starts = [0] + [m.end() for m in re.finditer("\n", new_text)]
    covered = merge_intervals([(w.start, w.end) for w in parser.wraps])
    covered_starts = [s for s, _ in covered]
    body_start_char = tokens[body_start].start if body_start < len(tokens) else len(new_text)
    body_end_char = tokens[body_end].start if body_end < len(tokens) else len(new_text)
    missed: dict[str, list[int]] = {}
    for idx, (tok, flag) in enumerate(zip(tokens, changed)):
        if not flag or tok.kind not in CONTENT_KINDS or idx in parser.env_name_toks:
            continue
        if not overlaps(covered, covered_starts, tok.start, tok.end):
            reason = ("preamble" if tok.start < body_start_char else
                      "after \\end{document}" if tok.start >= body_end_char else "structure/arguments")
            missed.setdefault(reason, []).append(line_of(line_starts, tok.start))

    edits: list[tuple[int, int, int, str]] = []  # (start, order, end, text)
    if begin_offset is not None:
        preamble = "%% >>> paper-diff-highlight\n" + PREAMBLE_COMMON % {"color": opts.color}
        preamble += (PREAMBLE_HL % {"hl_color": opts.hl_color}) if opts.style == "hl" else PREAMBLE_COLOR
        edits.append((begin_offset, -1, begin_offset, preamble + "%% <<< paper-diff-highlight\n"))
    for w in parser.wraps:
        edits.append((w.start, 1, w.start, WRAP_OPEN[w.kind]))
        edits.append((w.end, 0, w.end, WRAP_CLOSE[w.kind]))

    result = FileResult(path, output, parser.wraps, missed, [], deletions)
    for w in parser.wraps:
        snippet = " ".join(new_text[w.start:w.end].split())
        result.snippets.append((line_of(line_starts, w.start), snippet[:70] + ("..." if len(snippet) > 70 else "")))

    if opts.follow_inputs:
        for ref in parser.inputs:
            child = resolve_input(root_dir, ref.path, source)
            if child is None or child in visited:
                continue
            child_result = process_file(child, output_name(child), root_dir, source, opts, macros, visited, False)
            if not child_result.written:
                continue
            result.children.append(child_result)
            ref_path = PurePosixPath(ref.path)
            new_ref = str(ref_path.with_name(f"{ref_path.stem}{SUFFIX}{ref_path.suffix}"))
            edits.append((ref.start, 0, ref.end, new_ref))

    if not is_root and not parser.wraps and not result.children and not deletions and not missed:
        return result
    pieces: list[str] = []
    cursor = 0
    for start, _, end, text in sorted(edits, key=lambda e: (e[0], e[1])):
        pieces.append(new_text[cursor:start])
        pieces.append(text)
        cursor = max(cursor, end)
    pieces.append(new_text[cursor:])
    with open(output, "w", encoding=ENCODING, errors=ERRORS, newline="") as f:
        f.write("".join(pieces))
    result.written = True
    return result


def report(result: FileResult, root_dir: Path, indent: str = "") -> None:
    def rel(p: Path) -> str:
        try:
            return str(p.relative_to(root_dir))
        except ValueError:
            return str(p)

    kinds = {k: sum(w.kind == k for w in result.wraps) for k in ("text", "box", "color", "block")}
    print(f"{indent}{rel(result.source)} -> {rel(result.output)}")
    print(f"{indent}  highlighted regions: {len(result.wraps)} (background {kinds['text']}, boxed {kinds['box']}, "
          f"text color {kinds['color']}, display math {kinds['block']})")
    for line, snippet in result.snippets[:MAX_SNIPPETS]:
        print(f"{indent}    L{line}: {snippet}")
    if len(result.snippets) > MAX_SNIPPETS:
        print(f"{indent}    ... {len(result.snippets) - MAX_SNIPPETS} more")
    if result.deletions:
        print(f"{indent}  deleted text (invisible in the PDF): lines {compress_lines(result.deletions)}")
    for reason, lines in result.missed_lines.items():
        print(f"{indent}  changed but not highlighted [{reason}]: lines {compress_lines(lines)}")
    for child in result.children:
        report(child, root_dir, indent + "  ")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy a LaTeX file and highlight the text changed since a git revision.")
    parser.add_argument("tex", type=Path, help="Main .tex file of the revised paper")
    parser.add_argument("--base", default="HEAD", help="Git revision of the old version (default: HEAD)")
    parser.add_argument("--to", default=None, help="Git revision of the new version (default: working tree)")
    parser.add_argument("-o", "--output", type=Path, help="Output .tex path (default: <name>_highlighted.tex)")
    parser.add_argument("--style", choices=["hl", "color"], default="hl",
                        help="hl: background highlight (default); color: colored text only")
    parser.add_argument("--color", default="blue",
                        help="xcolor expression for colored text and hl fallbacks such as display math (default: blue)")
    parser.add_argument("--hl-color", default="yellow", help="xcolor expression for the hl background (default: yellow)")
    parser.add_argument("--merge-gap", type=int, default=2,
                        help="Highlight unchanged runs of at most N tokens between two changes (default: 2)")
    parser.add_argument("--text-cmd", action="append", default=[],
                        help="Extra command whose mandatory argument is text, e.g. --text-cmd revised")
    parser.add_argument("--no-follow-inputs", action="store_true", help="Do not process changed \\input/\\include files")
    args = parser.parse_args()

    tex = args.tex.resolve()
    if not tex.is_file() and args.to is None:
        sys.exit(f"File not found: {tex}")
    if run_git(["rev-parse", "--show-toplevel"], tex.parent).returncode != 0:
        sys.exit(f"{tex.parent} is not inside a git repository")
    for rev in filter(None, (args.base, args.to)):
        if run_git(["rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"], tex.parent).returncode != 0:
            sys.exit(f"Unknown git revision: {rev}")
    output = (args.output or output_name(tex)).resolve()
    if output == tex:
        sys.exit("Output path must differ from the source file")
    if output.parent != tex.parent:
        print("warning: output is outside the source directory; relative figure/bib/input paths may break")

    opts = Options(args.style, args.color, args.hl_color, args.merge_gap, frozenset(args.text_cmd),
                   not args.no_follow_inputs)
    source = GitSource(args.base, args.to)
    result = process_file(tex, output, tex.parent, source, opts, {}, set(), True)
    print(f"base: {args.base}  new: {args.to or 'working tree'}  style: {args.style}")
    report(result, tex.parent)
    total = len(result.wraps) + sum(len(c.wraps) for c in result.children)
    if total == 0:
        print("warning: no highlightable change found; check --base")


if __name__ == "__main__":
    main()
