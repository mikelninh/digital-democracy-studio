"""SafeTrace Entity Resolution Mode.

Deterministic, explainable pair scoring for noisy organisation records.
No external packages are required.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import itertools
import json
import re
from pathlib import Path
from typing import Any

AUTO_MERGE_THRESHOLD = 0.72
REVIEW_THRESHOLD = 0.58
LEGAL_SUFFIXES = r"\b(gmbh|ggmbh|ag|se|eg|mbh)\b"


def normalize(text: str) -> str:
    text = (text or "").lower()
    for src, dst in {"ß":"ss","ä":"ae","ö":"oe","ü":"ue"}.items():
        text = text.replace(src, dst)
    text = re.sub(LEGAL_SUFFIXES, " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _root_domain(domain: str) -> str:
    domain = (domain or "").lower().removeprefix("www.")
    parts = domain.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else domain


def _postcode(address: str) -> str:
    match = re.search(r"\b\d{5}\b", address or "")
    return match.group(0) if match else ""


def _jaccard(left: str, right: str) -> float:
    a, b = set(normalize(left).split()), set(normalize(right).split())
    return len(a & b) / len(a | b) if a | b else 0.0


def _name_similarity(left: str, right: str) -> float:
    a, b = normalize(left), normalize(right)
    return max(SequenceMatcher(None, a, b).ratio(), _jaccard(left, right))


def _director_overlap(left: list[str], right: list[str]) -> float:
    for la in left:
        a = [t for t in normalize(la).split() if t != "dr"]
        for rb in right:
            b = [t for t in normalize(rb).split() if t != "dr"]
            if a and b and a[-1] == b[-1] and a[0][0] == b[0][0]:
                return 1.0
    return 0.0


@dataclass(frozen=True)
class Resolution:
    left: str
    right: str
    score: float
    decision: str
    evidence: dict[str, Any]


def resolve_pair(left: dict[str, Any], right: dict[str, Any]) -> Resolution:
    name = _name_similarity(left["name"], right["name"])
    left_domain = left.get("domain", "").lower().removeprefix("www.")
    right_domain = right.get("domain", "").lower().removeprefix("www.")
    exact_domain = bool(left_domain and right_domain) and left_domain == right_domain
    root_domain = bool(left_domain and right_domain) and _root_domain(left_domain) == _root_domain(right_domain)
    address = _jaccard(left.get("address", ""), right.get("address", ""))
    postcode = bool(_postcode(left.get("address", ""))) and _postcode(left.get("address", "")) == _postcode(right.get("address", ""))
    director = _director_overlap(left.get("directors", []), right.get("directors", []))

    score = (
        0.45 * name
        + 0.20 * float(exact_domain)
        + 0.10 * float(root_domain)
        + 0.15 * address
        + 0.05 * float(postcode)
        + 0.05 * director
    )

    decision = "auto_merge" if score >= AUTO_MERGE_THRESHOLD else "human_review" if score >= REVIEW_THRESHOLD else "reject"
    evidence = {
        "name_similarity": round(name, 3),
        "exact_domain": exact_domain,
        "shared_root_domain": root_domain,
        "address_similarity": round(address, 3),
        "postcode_match": postcode,
        "director_overlap": bool(director),
        "left_source": left.get("source"),
        "right_source": right.get("source"),
    }
    return Resolution(left["record_id"], right["record_id"], round(score, 3), decision, evidence)


def evaluate(records: list[dict[str, Any]]) -> dict[str, Any]:
    tp = fp = fn = tn = 0
    decisions: list[dict[str, Any]] = []
    for left, right in itertools.combinations(records, 2):
        resolution = resolve_pair(left, right)
        gold = left["entity_id"] == right["entity_id"]
        predicted = resolution.decision == "auto_merge"
        if predicted and gold: tp += 1
        elif predicted and not gold: fp += 1
        elif not predicted and gold: fn += 1
        else: tn += 1
        row = asdict(resolution)
        row.update({"gold_match": gold, "left_name": left["name"], "right_name": right["name"]})
        decisions.append(row)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "records": len(records),
        "ground_truth_entities": len({r["entity_id"] for r in records}),
        "candidate_pairs": len(decisions),
        "thresholds": {"auto_merge": AUTO_MERGE_THRESHOLD, "human_review": REVIEW_THRESHOLD},
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "human_review_pairs": sum(d["decision"] == "human_review" for d in decisions),
        "review_queue": [d for d in decisions if d["decision"] == "human_review"],
        "false_negatives": [d for d in decisions if d["gold_match"] and d["decision"] != "auto_merge"],
        "auto_merge_examples": [d for d in decisions if d["decision"] == "auto_merge"][:8],
    }


def main() -> None:
    here = Path(__file__).parent
    data = json.loads((here / "benchmark.json").read_text(encoding="utf-8"))
    print(json.dumps(evaluate(data["records"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
