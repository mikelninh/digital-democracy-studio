from __future__ import annotations

import re
from typing import Any


SOURCE_ID_RE = re.compile(r"\bS\d{2}\b")


def source_index(case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in case.get("source_records", [])}


def direct_origin(source: dict[str, Any]) -> str | None:
    """Return an explicitly referenced upstream source when a record is a mirror/republication."""
    text = " ".join([source.get("title", ""), *source.get("facts", [])])
    lowered = text.casefold()
    if not any(token in lowered for token in ("republishes", "mirror", "reprints", "copied from", "syndicated")):
        return None
    match = SOURCE_ID_RE.search(text)
    return match.group(0) if match else None


def root_origin(source_id: str, sources: dict[str, dict[str, Any]]) -> str:
    seen: set[str] = set()
    current = source_id
    while current not in seen:
        seen.add(current)
        source = sources.get(current)
        if source is None:
            return current
        upstream = direct_origin(source)
        if upstream is None or upstream not in sources:
            return current
        current = upstream
    return current


def cluster_sources(case: dict[str, Any], source_ids: list[str] | None = None) -> list[dict[str, Any]]:
    sources = source_index(case)
    ids = source_ids or sorted(sources)
    clusters: dict[str, list[str]] = {}
    for source_id in ids:
        root = root_origin(source_id, sources)
        clusters.setdefault(root, []).append(source_id)

    out: list[dict[str, Any]] = []
    for root, members in sorted(clusters.items()):
        root_source = sources.get(root, {})
        out.append({
            "origin_source_id": root,
            "origin_title": root_source.get("title", root),
            "source_ids": sorted(members),
            "reported_source_count": len(members),
            "independent_origin_count": 1,
            "quality": root_source.get("quality", "unknown"),
            "circular_reporting": len(members) > 1,
        })
    return out


def assess_claim(case: dict[str, Any], claim: str, supporting_source_ids: list[str]) -> dict[str, Any]:
    sources = source_index(case)
    roots = sorted({root_origin(source_id, sources) for source_id in supporting_source_ids})
    qualities = [sources.get(root, {}).get("quality", "unknown") for root in roots]
    return {
        "claim": claim,
        "reported_source_count": len(supporting_source_ids),
        "independent_origin_count": len(roots),
        "independent_origins": roots,
        "origin_qualities": qualities,
        "corroboration_warning": len(roots) < len(supporting_source_ids),
        "boundary": "Repeated publication does not create independent corroboration; evaluate the underlying origin and its evidence.",
    }
