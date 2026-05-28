import os
import re
from collections import Counter
from typing import Dict, Iterable, List, Optional


def normalize_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", (title or "").lower())
    return " ".join(normalized.split())


def safe_token(text: str, max_length: int = 120) -> str:
    token = re.sub(r"\s+", "_", normalize_title(text))
    return token[:max_length] if len(token) > max_length else token


def normalize_doi(doi: Optional[str]) -> str:
    value = (doi or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value.strip(" ./")


def _id_suffix(value: Optional[str]) -> str:
    text = (value or "").strip().rstrip("/")
    if not text:
        return ""
    return text.split("/")[-1].lower()


def _id_token(prefix: str, value: str) -> str:
    return prefix + re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def build_record_id(paper: Dict) -> str:
    doi = normalize_doi(paper.get("doi"))
    if doi:
        return _id_token("doi_", doi)
    arxiv_id = (paper.get("arxiv_id") or "").strip().lower()
    if arxiv_id:
        return _id_token("arxiv_", arxiv_id)
    openalex_id = _id_suffix(paper.get("openalex_id"))
    if openalex_id:
        return _id_token("openalex_", openalex_id)
    semantic_id = _id_suffix(paper.get("semantic_scholar_id"))
    if semantic_id:
        return _id_token("s2_", semantic_id)
    return "title_" + safe_token(paper.get("title") or "untitled")


def dedup_keys(paper: Dict) -> List[str]:
    keys: List[str] = []
    doi = normalize_doi(paper.get("doi"))
    if doi:
        keys.append(f"doi:{doi}")
    for field in ("arxiv_id", "openalex_id", "semantic_scholar_id"):
        value = _id_suffix(paper.get(field))
        if value:
            keys.append(f"{field}:{value}")
    title = normalize_title(paper.get("title") or "")
    if title:
        keys.append("title:" + title)
    return keys or ["title:"]


def dedup_key(paper: Dict) -> str:
    return dedup_keys(paper)[0]


def _provider_record(paper: Dict) -> Dict:
    provider = paper.get("provider") or paper.get("source") or "unknown"
    return {
        "provider": provider,
        "provider_id": paper.get("provider_id") or paper.get("openalex_id") or paper.get("arxiv_id") or paper.get("semantic_scholar_id") or "",
        "source_url": paper.get("source_url") or "",
        "pdf_url": paper.get("pdf_url") or "",
        "doi": normalize_doi(paper.get("doi")),
    }


def merge_papers(existing: Dict, incoming: Dict) -> Dict:
    merged = dict(existing)
    provider = incoming.get("provider") or incoming.get("source") or "unknown"
    providers = list(merged.get("providers") or [])
    if provider not in providers:
        providers.append(provider)
    merged["providers"] = providers

    records = list(merged.get("provider_records") or [])
    records.append(_provider_record(incoming))
    merged["provider_records"] = records

    for field in (
        "title",
        "abstract",
        "publication_date",
        "venue",
        "source_url",
        "pdf_url",
        "doi",
        "arxiv_id",
        "openalex_id",
        "semantic_scholar_id",
        "provider_id",
    ):
        if not merged.get(field) and incoming.get(field):
            merged[field] = incoming[field]

    if incoming.get("abstract") and len(incoming.get("abstract", "")) > len(merged.get("abstract", "")):
        merged["abstract"] = incoming["abstract"]
    if incoming.get("pdf_url") and provider in {"arxiv", "usenix"}:
        merged["pdf_url"] = incoming["pdf_url"]
    if incoming.get("cited_by_count", 0) > merged.get("cited_by_count", 0):
        merged["cited_by_count"] = incoming["cited_by_count"]
    merged["record_id"] = build_record_id(merged)
    return merged


def prepare_single_provider_paper(paper: Dict) -> Dict:
    prepared = dict(paper)
    provider = prepared.get("provider") or prepared.get("source") or "unknown"
    prepared["provider"] = provider
    prepared["source"] = provider
    prepared["providers"] = [provider]
    prepared["provider_records"] = [_provider_record(prepared)]
    prepared["record_id"] = build_record_id(prepared)
    return prepared


def deduplicate_papers(papers: Iterable[Dict]) -> List[Dict]:
    by_key: Dict[str, Dict] = {}
    canonical_keys: List[str] = []
    for paper in papers:
        prepared = prepare_single_provider_paper(paper)
        keys = dedup_keys(prepared)
        existing_key = next((key for key in keys if key in by_key), None)
        if existing_key is None:
            canonical_key = keys[0]
            by_key[canonical_key] = prepared
            canonical_keys.append(canonical_key)
            for key in keys[1:]:
                by_key[key] = prepared
            continue

        merged = merge_papers(by_key[existing_key], prepared)
        merged_keys = dedup_keys(merged)
        for key in set(keys + merged_keys):
            by_key[key] = merged
        for index, canonical_key in enumerate(canonical_keys):
            if by_key.get(canonical_key) is by_key[existing_key]:
                canonical_keys[index] = merged_keys[0]
                break
        if merged_keys[0] not in canonical_keys:
            canonical_keys.append(merged_keys[0])
        by_key[merged_keys[0]] = merged

    result: List[Dict] = []
    seen_ids = set()
    for key in canonical_keys:
        paper = by_key[key]
        identity = id(paper)
        if identity not in seen_ids:
            result.append(paper)
            seen_ids.add(identity)
    return result


def provider_counts_for(papers: Iterable[Dict]) -> Dict[str, int]:
    counts: Counter = Counter()
    for paper in papers:
        providers = paper.get("providers") or [paper.get("provider") or paper.get("source") or "unknown"]
        for provider in providers:
            counts[provider] += 1
    return dict(counts)


def save_abstract(base_dir: str, paper: Dict) -> str:
    abstracts_dir = os.path.join(base_dir, "abstracts")
    os.makedirs(abstracts_dir, exist_ok=True)
    token = paper.get("record_id") or build_record_id(paper)
    path = os.path.join(abstracts_dir, f"{token}.txt")
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write(f"Title: {paper.get('title', '')}\n\n")
        file_obj.write(f"Authors: {', '.join(paper.get('authors') or [])}\n\n")
        file_obj.write(f"Venue: {paper.get('venue', '')}\n\n")
        if paper.get("publication_date"):
            file_obj.write(f"Publication Date: {paper['publication_date']}\n\n")
        if paper.get("doi"):
            file_obj.write(f"DOI: {paper['doi']}\n\n")
        if paper.get("source_url"):
            file_obj.write(f"Source URL: {paper['source_url']}\n\n")
        file_obj.write("Abstract:\n")
        file_obj.write((paper.get("abstract") or "") + "\n")
    return path
