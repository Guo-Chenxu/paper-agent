#!/usr/bin/env python3
"""Generate a paper figure with an image model and export PNG + PDF."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import struct
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("figures")


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


def safe_stem(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._")
    if not stem:
        raise ValueError(
            "--name must contain at least one filename-safe character")
    return stem


def api_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    clean_path = path.lstrip("/")
    if base.endswith("/v1") and clean_path.startswith("v1/"):
        clean_path = clean_path[len("v1/"):]
    return f"{base}/{clean_path}"


def redact_secrets(text: str) -> str:
    text = re.sub(r"key=([^&\s]+)", "key=<redacted>", text)
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
            config_lines.append(
                f'header = "{curl_config_quote(f"{key}: {value}")}"')

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as config_file:
            config_file.write("\n".join(config_lines) + "\n")
            config_path = Path(config_file.name)
        config_path.chmod(0o600)

        result = subprocess.run(
            ["curl", "--config", str(config_path),
             "--write-out", "\n%{http_code}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "curl fallback is unavailable because curl is not installed") from exc
    finally:
        for path in (body_path, config_path):
            if path is not None:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass

    if result.returncode != 0:
        raise RuntimeError(
            f"curl fallback failed: {redact_secrets(result.stderr.strip())}")
    if "\n" not in result.stdout:
        raise RuntimeError(
            f"curl fallback returned unexpected output: {result.stdout[:500]}")

    body, status_text = result.stdout.rsplit("\n", 1)
    try:
        status_code = int(status_text)
    except ValueError as exc:
        raise RuntimeError(
            f"curl fallback returned invalid HTTP status: {status_text}") from exc
    if status_code >= 400:
        raise RuntimeError(
            f"Image API request failed with HTTP {status_code}: {redact_secrets(body[:1200])}")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Image API returned non-JSON response: {body[:500]}") from exc


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    merged_headers = {"Content-Type": "application/json", **headers}
    transport_errors: list[str] = []
    try:
        import requests
    except ImportError:
        requests = None

    if requests is not None:
        try:
            response = requests.post(
                url, json=payload, headers=merged_headers, timeout=timeout)
        except requests.RequestException as exc:
            transport_errors.append(redact_secrets(str(exc)))
        else:
            if response.status_code >= 400:
                raise RuntimeError(
                    f"Image API request failed with HTTP {response.status_code}: "
                    f"{redact_secrets(response.text[:1200])}"
                )
            try:
                return response.json()
            except ValueError as exc:
                raise RuntimeError(
                    f"Image API returned non-JSON response: {response.text[:500]}") from exc

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
            f"Image API request failed with HTTP {exc.code}: {redact_secrets(detail[:1200])}"
        ) from exc
    except urllib.error.URLError as exc:
        transport_errors.append(redact_secrets(str(exc.reason)))
    else:
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Image API returned non-JSON response: {body[:500]}") from exc

    try:
        return curl_post_json(url, payload, merged_headers, timeout)
    except RuntimeError as exc:
        prefix = "; ".join(transport_errors)
        if prefix:
            raise RuntimeError(
                f"{exc} (previous transport errors: {prefix})") from exc
        raise


def download_url(url: str, timeout: int) -> tuple[bytes, str]:
    try:
        import requests
    except ImportError:
        requests = None

    if requests is not None:
        try:
            response = requests.get(
                url, headers={"User-Agent": "paper-machine-image-gen/1.0"}, timeout=timeout)
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to download generated image URL: {exc}") from exc
        if response.status_code >= 400:
            raise RuntimeError(
                f"Failed to download generated image URL: HTTP {response.status_code}")
        return response.content, response.headers.get("Content-Type", "")

    request = urllib.request.Request(
        url, headers={"User-Agent": "paper-machine-image-gen/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            return response.read(), content_type
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Failed to download generated image URL: {redact_secrets(str(exc.reason))}") from exc


def decode_data_url(value: str) -> tuple[bytes, str]:
    header, encoded = value.split(",", 1)
    mime = header.split(";", 1)[0].removeprefix("data:")
    return base64.b64decode(encoded), mime


def extract_data_url_from_text(text: str) -> tuple[bytes, str] | None:
    match = re.search(
        r"data:(image/[A-Za-z0-9.+-]+);base64,([A-Za-z0-9+/=\s]+)", text)
    if not match:
        return None
    return base64.b64decode(re.sub(r"\s+", "", match.group(2))), match.group(1)


def decode_base64_image(value: str, mime: str = "image/png") -> tuple[bytes, str]:
    if value.startswith("data:image/"):
        return decode_data_url(value)
    return base64.b64decode(value), mime


def make_placeholder_png(width: int = 512, height: int = 512) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + (b"\xFF\xFF\xFF" * width)
    pixels = zlib.compress(row * height)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


def extension_for_mime(mime: str) -> str:
    if not mime:
        return ".png"
    if mime == "image/jpeg":
        return ".jpg"
    return mimetypes.guess_extension(mime.split(";")[0]) or ".png"


def extract_openai_image(response: dict[str, Any], timeout: int) -> tuple[bytes, str]:
    for item in response.get("data", []):
        if isinstance(item, dict):
            if item.get("b64_json"):
                return decode_base64_image(item["b64_json"])
            if item.get("url"):
                return download_url(item["url"], timeout)
    raise RuntimeError(
        "OpenAI-compatible response did not contain b64_json or url image data")


def iter_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(iter_dicts(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(iter_dicts(child))
    return found


def iter_strings(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            found.extend(iter_strings(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(iter_strings(child))
    return found


def extract_gemini_image(response: dict[str, Any]) -> tuple[bytes, str]:
    for obj in iter_dicts(response):
        inline_data = obj.get("inlineData") or obj.get("inline_data")
        if isinstance(inline_data, dict) and inline_data.get("data"):
            mime = inline_data.get("mimeType") or inline_data.get(
                "mime_type") or "image/png"
            return decode_base64_image(inline_data["data"], mime)

        image_url = obj.get("image_url")
        if isinstance(image_url, dict) and isinstance(image_url.get("url"), str):
            url = image_url["url"]
            if url.startswith("data:image/"):
                return decode_data_url(url)

    for text in iter_strings(response):
        extracted = extract_data_url_from_text(text)
        if extracted:
            return extracted

    raise RuntimeError("Gemini response did not contain inline image data")


def generate_with_openai_images(
    *,
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    size: str,
    quality: str,
    timeout: int,
) -> tuple[bytes, str]:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    if quality and quality != "auto":
        payload["quality"] = quality

    response = post_json(
        api_url(base_url, "v1/images/generations"),
        payload,
        {"Authorization": f"Bearer {api_key}"},
        timeout,
    )
    return extract_openai_image(response, timeout)


def generate_with_gemini(
    *,
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    timeout: int,
) -> tuple[bytes, str]:
    model_path = urllib.parse.quote(model, safe="")
    url = api_url(base_url, f"v1beta/models/{model_path}:generateContent")

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    response = post_json(
        url, payload, {"x-goog-api-key": api_key} if api_key else {}, timeout)
    return extract_gemini_image(response)


def generate_with_openai_chat_image(
    *,
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    timeout: int,
) -> tuple[bytes, str]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    response = post_json(
        api_url(base_url, "v1/chat/completions"),
        payload,
        {"Authorization": f"Bearer {api_key}"},
        timeout,
    )
    return extract_gemini_image(response)


def convert_image_to_pdf(image_path: Path, pdf_path: Path) -> None:
    try:
        import img2pdf
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install img2pdf") from exc

    with open(pdf_path, "wb") as handle:
        handle.write(img2pdf.convert(image_path))


def write_outputs(image_bytes: bytes, mime: str, output_dir: Path, name: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_stem(name)
    image_path = output_dir / f"{stem}{extension_for_mime(mime)}"
    pdf_path = output_dir / f"{stem}.pdf"
    image_path.write_bytes(image_bytes)
    convert_image_to_pdf(image_path, pdf_path)
    return image_path, pdf_path


def build_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    return args.prompt.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a paper figure using IMAGE_GEN_* settings from .env, then convert it to PDF."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Image generation prompt")
    prompt_group.add_argument(
        "--prompt-file", help="Path to a UTF-8 text file containing the prompt")
    parser.add_argument("--name", required=True,
                        help="Output filename stem, e.g. fig_architecture")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR),
                        help="Output directory for image and PDF")
    parser.add_argument("--env-file", default=".env",
                        help="Path to dotenv file with IMAGE_GEN_* values")
    parser.add_argument("--vendor", help="Override IMAGE_GEN_VENDOR")
    parser.add_argument("--model", help="Override IMAGE_GEN_MODEL")
    parser.add_argument("--base-url", help="Override IMAGE_GEN_BASE_URL")
    parser.add_argument("--api-key", help="Override IMAGE_GEN_API_KEY")
    parser.add_argument("--size", default="1024x1024",
                        help="Image size for gpt-image/OpenAI-compatible providers")
    parser.add_argument("--quality", default="auto",
                        help="Image quality for providers that support it")
    parser.add_argument("--timeout", type=int, default=180,
                        help="HTTP timeout in seconds")
    parser.add_argument("--dry-run", action="store_true",
                        help="Write a tiny placeholder PNG and PDF without calling an API")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_file_values = load_env_file(Path(args.env_file))
    vendor = (args.vendor or env_value(
        env_file_values, "IMAGE_GEN_VENDOR")).strip().lower()
    model = (args.model or env_value(
        env_file_values, "IMAGE_GEN_MODEL")).strip()
    base_url = (args.base_url or env_value(
        env_file_values, "IMAGE_GEN_BASE_URL")).strip()
    api_key = (args.api_key or env_value(
        env_file_values, "IMAGE_GEN_API_KEY")).strip()
    prompt = build_prompt(args)

    try:
        if args.dry_run:
            image_bytes, mime = make_placeholder_png(), "image/png"
        else:
            missing = [
                name
                for name, value in {
                    "IMAGE_GEN_API_KEY": api_key,
                    "IMAGE_GEN_BASE_URL": base_url,
                    "IMAGE_GEN_MODEL": model,
                    "IMAGE_GEN_VENDOR": vendor,
                }.items()
                if not value
            ]
            if missing:
                raise RuntimeError(
                    f"Missing required image generation config: {', '.join(missing)}")

            if vendor in {"openai", "gpt-image", "gpt_image"} or model.startswith("gpt-image"):
                image_bytes, mime = generate_with_openai_images(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    prompt=prompt,
                    size=args.size,
                    quality=args.quality,
                    timeout=args.timeout,
                )
            elif vendor in {"gemini", "google"} or model.startswith("gemini"):
                image_bytes, mime = generate_with_gemini(
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                    prompt=prompt,
                    timeout=args.timeout,
                )
            else:
                raise RuntimeError(
                    f"Unsupported IMAGE_GEN_VENDOR '{vendor}'. Use 'gemini', 'openai', or 'gpt-image'."
                )

        image_path, pdf_path = write_outputs(
            image_bytes, mime, Path(args.output_dir), args.name)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "image": str(image_path),
                "pdf": str(pdf_path),
                "model": model or "dry-run",
                "vendor": vendor or "dry-run",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
