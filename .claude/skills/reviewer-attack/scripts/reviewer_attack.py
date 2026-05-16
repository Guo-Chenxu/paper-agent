#!/usr/bin/env python3
"""Generate adversarial academic reviews with the configured REVIEWER_ATTACK_* LLM."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


DEFAULT_ENV_FILE = ".env"
DEFAULT_OUTPUT = "reports/simulated_review_report.md"
DEFAULT_REVIEWS_DIR = "reviews"
DEFAULT_MAX_CONTEXT_CHARS = 60000


SYSTEM_PROMPT = """You are an adversarial but fair academic peer reviewer.
Attack the paper as a real conference reviewer would: look for fatal flaws,
unsupported claims, missing baselines, weak evaluation, theoretical gaps,
metric artifacts, unclear definitions, and reproducibility risks.
Ground criticism in the provided paper text. Do not invent experiments,
citations, tables, or claims. If evidence is missing, state that as a
missing-evidence issue. Return plain Markdown only, with no code fences."""


PERSONAS = {
    "strict": {
        "label": "Strict Reviewer",
        "focus": (
            "Prioritize technical correctness, methodological rigor, theory, "
            "experimental sufficiency, baselines, ablations, statistical validity, "
            "and reproducibility. Be willing to recommend rejection if the evidence "
            "does not support the claims."
        ),
    },
    "constructive": {
        "label": "Constructive Reviewer",
        "focus": (
            "Prioritize novelty, positioning against related work, usefulness of the "
            "core idea, and a concrete path to make the paper publishable. Criticize "
            "hard, but include actionable fixes."
        ),
    },
    "newbie": {
        "label": "Newcomer Reviewer",
        "focus": (
            "Prioritize readability, motivation, definitions, figure/table clarity, "
            "paper organization, and whether a non-expert reviewer can understand "
            "the contribution without guessing."
        ),
    },
}


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            values[key] = value
    return values


def env_value(env_file_values: dict[str, str], key: str, default: str = "") -> str:
    return os.environ.get(key) or env_file_values.get(key) or default


def first_env_value(env_file_values: dict[str, str], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = env_value(env_file_values, key)
        if value:
            return value
    return default


def api_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    clean_path = path.lstrip("/")
    if base.endswith("/v1") and clean_path.startswith("v1/"):
        clean_path = clean_path[len("v1/"):]
    return f"{base}/{clean_path}"


def redact_secrets(text: str) -> str:
    text = re.sub(r"key=([^&\s]+)", "key=<redacted>", text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer <redacted>", text)
    text = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-<redacted>", text)
    return text


def curl_config_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def curl_post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    body_path: Path | None = None
    config_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as body_file:
            json.dump(payload, body_file)
            body_path = Path(body_file.name)

        config_lines = [
            f'url = "{curl_config_quote(url)}"',
            'request = "POST"',
            f'max-time = "{timeout}"',
            "silent",
            "show-error",
            "location",
            f'data-binary = "@{curl_config_quote(str(body_path))}"',
        ]
        for key, value in headers.items():
            config_lines.append(f'header = "{curl_config_quote(f"{key}: {value}")}"')

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as config_file:
            config_file.write("\n".join(config_lines) + "\n")
            config_path = Path(config_file.name)
        config_path.chmod(0o600)

        result = subprocess.run(
            ["curl", "--config", str(config_path), "--write-out", "\n%{http_code}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("curl fallback is unavailable because curl is not installed") from exc
    finally:
        for path in (body_path, config_path):
            if path is not None:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass

    if result.returncode != 0:
        raise RuntimeError(f"curl fallback failed: {redact_secrets(result.stderr.strip())}")
    if "\n" not in result.stdout:
        raise RuntimeError(f"curl fallback returned unexpected output: {result.stdout[:500]}")

    body, status_text = result.stdout.rsplit("\n", 1)
    try:
        status_code = int(status_text)
    except ValueError as exc:
        raise RuntimeError(f"curl fallback returned invalid HTTP status: {status_text}") from exc
    if status_code >= 400:
        raise RuntimeError(f"Reviewer API request failed with HTTP {status_code}: {redact_secrets(body[:1200])}")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Reviewer API returned non-JSON response: {body[:500]}") from exc


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    merged_headers = {"Content-Type": "application/json", **headers}
    transport_errors: list[str] = []
    try:
        import requests
    except ImportError:
        requests = None

    if requests is not None:
        try:
            response = requests.post(url, json=payload, headers=merged_headers, timeout=timeout)
        except requests.RequestException as exc:
            transport_errors.append(redact_secrets(str(exc)))
        else:
            if response.status_code >= 400:
                raise RuntimeError(
                    f"Reviewer API request failed with HTTP {response.status_code}: "
                    f"{redact_secrets(response.text[:1200])}"
                )
            try:
                return response.json()
            except ValueError as exc:
                raise RuntimeError(f"Reviewer API returned non-JSON response: {response.text[:500]}") from exc

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=merged_headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Reviewer API request failed with HTTP {exc.code}: {redact_secrets(detail[:1200])}"
        ) from exc
    except urllib.error.URLError as exc:
        transport_errors.append(redact_secrets(str(exc.reason)))
    else:
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Reviewer API returned non-JSON response: {body[:500]}") from exc

    try:
        return curl_post_json(url, payload, merged_headers, timeout)
    except RuntimeError as exc:
        prefix = "; ".join(transport_errors)
        if prefix:
            raise RuntimeError(f"{exc} (previous transport errors: {prefix})") from exc
        raise


def normalize_vendor(vendor: str, model: str) -> str:
    clean_vendor = vendor.strip().lower().replace("_", "-")
    clean_model = model.strip().lower()
    if clean_vendor in {"openai", "gpt", "gpt-compatible", "openai-compatible"}:
        return "openai"
    if clean_vendor in {"gemini", "google"}:
        return "gemini"
    if clean_vendor:
        return clean_vendor
    if clean_model.startswith("gemini"):
        return "gemini"
    return "openai"


def default_base_url(vendor: str) -> str:
    if vendor == "gemini":
        return "https://generativelanguage.googleapis.com"
    return "https://api.openai.com"


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    return str(content)


def extract_openai_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("OpenAI-compatible response did not contain choices")
    message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
    content = message.get("content")
    if content is None:
        content = choices[0].get("text") if isinstance(choices[0], dict) else None
    if content is None:
        raise RuntimeError("OpenAI-compatible response did not contain text content")
    return content_to_text(content).strip()


def extract_gemini_text(response: dict[str, Any]) -> str:
    candidates = response.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError("Gemini response did not contain candidates")
    content = candidates[0].get("content", {}) if isinstance(candidates[0], dict) else {}
    parts = content.get("parts", []) if isinstance(content, dict) else []
    texts = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
    if not texts:
        raise RuntimeError("Gemini response did not contain text parts")
    return "\n".join(texts).strip()


def call_openai_compatible(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    response = post_json(
        api_url(base_url, "v1/chat/completions"),
        payload,
        {"Authorization": f"Bearer {api_key}"},
        timeout,
    )
    return extract_openai_text(response)


def call_gemini(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> str:
    model_path = urllib.parse.quote(model, safe="")
    url = api_url(base_url, f"v1beta/models/{model_path}:generateContent")
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    response = post_json(url, payload, {"x-goog-api-key": api_key} if api_key else {}, timeout)
    return extract_gemini_text(response)


def read_context_file(path: Path, max_chars: int) -> str:
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Context truncated because it exceeded the configured limit.]"


def strip_outer_markdown_fence(markdown: str) -> str:
    text = markdown.strip()
    match = re.fullmatch(r"```(?:markdown|md)?\s*\n(.*)\n```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip().lower()).strip("._")
    if not slug:
        raise ValueError("reviewer name must contain at least one filename-safe character")
    return slug


def build_context(args: argparse.Namespace) -> str:
    blocks: list[str] = []
    paper_path = Path(args.paper)
    blocks.append(f"## Paper File: {paper_path}\n\n{read_context_file(paper_path, args.max_context_chars)}")

    for bib_file in args.bib:
        path = Path(bib_file)
        if path.exists():
            blocks.append(f"## Bibliography File: {path}\n\n{read_context_file(path, args.max_context_chars // 2)}")

    for context_file in args.context_file:
        path = Path(context_file)
        blocks.append(f"## Extra Context File: {path}\n\n{read_context_file(path, args.max_context_chars)}")

    if args.context:
        blocks.append(f"## Inline Context\n\n{args.context.strip()}")

    return "\n\n".join(blocks)


def build_review_prompt(args: argparse.Namespace, reviewer: str, context: str) -> str:
    persona = PERSONAS[reviewer]
    return f"""# Review Task

Review the supplied academic paper for {args.target_venue}.

# Reviewer Persona

{persona["label"]}: {persona["focus"]}

# Required Output

Use this Markdown structure:

## Overall Evaluation
- Paper summary:
- Overall recommendation: Accept / Weak Accept / Weak Reject / Reject
- Confidence:
- Scores:
  - Novelty:
  - Technical soundness:
  - Evaluation:
  - Clarity:
  - Reproducibility:

## Strengths

## Major Issues

For every major issue, include:
- Evidence from the paper or a clear missing-evidence statement.
- Why it threatens acceptance.
- Required fix.
- Rebuttal question the authors must answer.

## Minor Issues

## Actionable Revision Plan

## Final Verdict

Be specific and adversarial. Avoid generic comments.

# Paper And Context

{context}

Return only the final Markdown review."""


def dry_run_review(reviewer: str, args: argparse.Namespace) -> str:
    persona = PERSONAS[reviewer]
    return f"""## Overall Evaluation
- Paper summary: Dry-run placeholder for `{args.paper}`.
- Overall recommendation: Weak Reject
- Confidence: Medium
- Scores:
  - Novelty: 6/10
  - Technical soundness: 5/10
  - Evaluation: 4/10
  - Clarity: 6/10
  - Reproducibility: 4/10

## Strengths

- The dry run confirms the {persona["label"]} persona can be selected.
- No API call was made.

## Major Issues

1. Missing-evidence attack point: dry-run mode does not inspect model reasoning.
   - Evidence: API calls are disabled.
   - Why it threatens acceptance: this is only a local validation artifact.
   - Required fix: run without `--dry-run` after configuring `.env`.
   - Rebuttal question: which experiments or claims does the real reviewer identify as weakest?

## Minor Issues

- Confirm output paths and report aggregation before using real reviews.

## Actionable Revision Plan

1. Configure `REVIEWER_ATTACK_*` settings in `.env`.
2. Run the script without `--dry-run`.
3. Use generated major issues to revise `paper/paper.tex` and draft `paper/rebuttal.tex`.

## Final Verdict

Weak Reject
"""


def call_reviewer_api(
    *,
    vendor: str,
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> str:
    if vendor == "openai":
        return call_openai_compatible(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
    if vendor == "gemini":
        return call_gemini(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
    raise RuntimeError(f"Unsupported REVIEWER_ATTACK_VENDOR '{vendor}'. Use openai, gpt, openai-compatible, or gemini.")


def extract_recommendation(review: str) -> str:
    patterns = [
        r"Overall recommendation:\s*([A-Za-z ]+)",
        r"Final Verdict\s*\n+\s*([A-Za-z ]+)",
        r"recommendation\**:\s*\**([A-Za-z ]+)",
        r"verdict\**:\s*\**([A-Za-z ]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, review, flags=re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            value = re.split(r"[\n\r|,.;]", value, maxsplit=1)[0].strip()
            if value:
                return value
    return "Unknown"


def write_review(path: Path, reviewer: str, review: str) -> None:
    persona = PERSONAS[reviewer]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {persona['label']}\n\n{strip_outer_markdown_fence(review).rstrip()}\n", encoding="utf-8")


def build_aggregate_report(args: argparse.Namespace, reviews: dict[str, str], model: str, vendor: str) -> str:
    lines = [
        "# Simulated Review Report",
        "",
        f"**Paper**: `{args.paper}`",
        f"**Target venue**: {args.target_venue}",
        f"**Reviewer model**: {model or 'dry-run'}",
        f"**Vendor**: {vendor or 'dry-run'}",
        "",
        "## Verdict Summary",
        "",
    ]
    for reviewer, review in reviews.items():
        label = PERSONAS[reviewer]["label"]
        lines.append(f"- **{label}**: {extract_recommendation(review)}")

    lines.extend(["", "## Full Reviews", ""])
    for index, (reviewer, review) in enumerate(reviews.items(), start=1):
        label = PERSONAS[reviewer]["label"]
        lines.extend(
            [
                f"### Reviewer {index}: {label}",
                "",
                strip_outer_markdown_fence(review).rstrip(),
                "",
            ]
        )

    lines.extend(
        [
            "## Next-Step Checklist",
            "",
            "1. Merge duplicate major issues across reviewers.",
            "2. Revise `paper/paper.tex` issue by issue.",
            "3. Write `paper/rebuttal.tex` with one response per reviewer concern.",
            "4. Recompile `paper/paper.pdf` and verify claims, figures, tables, and citations remain consistent.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run adversarial paper reviews using REVIEWER_ATTACK_* settings from .env."
    )
    parser.add_argument("--paper", default="paper/paper.tex", help="Path to the LaTeX paper")
    parser.add_argument("--bib", action="append", default=[], help="Bibliography file to include. Can be repeated.")
    parser.add_argument("--context-file", action="append", default=[], help="Extra UTF-8 context file. Can be repeated.")
    parser.add_argument("--context", help="Inline context for reviewers")
    parser.add_argument("--target-venue", default="top-tier systems or architecture conference")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Aggregate Markdown report path")
    parser.add_argument("--reviews-dir", default=DEFAULT_REVIEWS_DIR, help="Directory for individual review files")
    parser.add_argument(
        "--reviewer",
        action="append",
        choices=sorted(PERSONAS.keys()),
        help="Reviewer persona to run. Defaults to all personas. Can be repeated.",
    )
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, help="Path to dotenv file")
    parser.add_argument("--vendor", help="Override REVIEWER_ATTACK_VENDOR or REVIEWER_ATTACK_API_VENDOR")
    parser.add_argument("--model", help="Override REVIEWER_ATTACK_MODEL")
    parser.add_argument("--base-url", help="Override REVIEWER_ATTACK_BASE_URL")
    parser.add_argument("--api-key", help="Override REVIEWER_ATTACK_API_KEY")
    parser.add_argument("--temperature", type=float, default=0.25)
    parser.add_argument("--max-tokens", type=int, default=3500)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-context-chars", type=int, default=DEFAULT_MAX_CONTEXT_CHARS)
    parser.add_argument("--dry-run", action="store_true", help="Validate locally without calling an API")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_file_values = load_env_file(Path(args.env_file))
    model = (
        args.model
        or first_env_value(env_file_values, ["REVIEWER_ATTACK_MODEL", "REVIEW_MODEL"])
    ).strip()
    vendor = normalize_vendor(
        args.vendor
        or first_env_value(
            env_file_values,
            ["REVIEWER_ATTACK_VENDOR", "REVIEWER_ATTACK_API_VENDOR", "REVIEW_VENDOR"],
        ),
        model,
    )
    base_url = (
        args.base_url
        or first_env_value(env_file_values, ["REVIEWER_ATTACK_BASE_URL", "REVIEW_BASE_URL"])
        or default_base_url(vendor)
    ).strip()
    api_key = (
        args.api_key
        or first_env_value(env_file_values, ["REVIEWER_ATTACK_API_KEY", "REVIEW_API_KEY"])
    ).strip()
    reviewers = args.reviewer or list(PERSONAS.keys())

    try:
        if not Path(args.paper).exists():
            raise RuntimeError(f"Paper file does not exist: {args.paper}")

        reviews: dict[str, str] = {}
        if args.dry_run:
            for reviewer in reviewers:
                reviews[reviewer] = dry_run_review(reviewer, args)
        else:
            missing = [
                name
                for name, value in {
                    "REVIEWER_ATTACK_API_KEY": api_key,
                    "REVIEWER_ATTACK_MODEL": model,
                }.items()
                if not value
            ]
            if missing:
                raise RuntimeError(f"Missing required reviewer config: {', '.join(missing)}")

            context = build_context(args)
            futures = {}
            with ThreadPoolExecutor(max_workers=len(reviewers)) as executor:
                for reviewer in reviewers:
                    prompt = build_review_prompt(args, reviewer, context)
                    future = executor.submit(
                        call_reviewer_api,
                        vendor=vendor,
                        api_key=api_key,
                        base_url=base_url,
                        model=model,
                        system_prompt=SYSTEM_PROMPT,
                        user_prompt=prompt,
                        temperature=args.temperature,
                        max_tokens=args.max_tokens,
                        timeout=args.timeout,
                    )
                    futures[future] = reviewer

                completed_reviews: dict[str, str] = {}
                for future in as_completed(futures):
                    reviewer = futures[future]
                    try:
                        completed_reviews[reviewer] = future.result()
                    except Exception as exc:
                        label = PERSONAS[reviewer]["label"]
                        raise RuntimeError(f"{label} request failed: {exc}") from exc

            for reviewer in reviewers:
                reviews[reviewer] = completed_reviews[reviewer]

        reviews_dir = Path(args.reviews_dir)
        for reviewer, review in reviews.items():
            write_review(reviews_dir / f"review_{safe_slug(reviewer)}.md", reviewer, review)

        report = build_aggregate_report(args, reviews, model, vendor)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    except Exception as exc:
        print(f"error: {redact_secrets(str(exc))}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "output": str(output_path),
                "reviews": [str(reviews_dir / f"review_{safe_slug(reviewer)}.md") for reviewer in reviews],
                "model": model or "dry-run",
                "vendor": vendor or "dry-run",
                "dry_run": args.dry_run,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
