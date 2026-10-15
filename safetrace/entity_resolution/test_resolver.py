import json
from pathlib import Path
from resolver import evaluate, resolve_pair

HERE = Path(__file__).parent
RECORDS = json.loads((HERE / "benchmark.json").read_text(encoding="utf-8"))["records"]


def by_id(record_id):
    return next(r for r in RECORDS if r["record_id"] == record_id)


def test_obvious_alias_auto_merges():
    result = resolve_pair(by_id("r01"), by_id("r04"))
    assert result.decision == "auto_merge"
    assert result.score >= 0.95


def test_parent_and_subsidiary_do_not_merge():
    result = resolve_pair(by_id("r01"), by_id("r05"))
    assert result.decision != "auto_merge"


def test_ambiguous_abbreviation_requires_review():
    result = resolve_pair(by_id("r37"), by_id("r39"))
    assert result.decision == "human_review"


def test_benchmark_has_zero_false_positive_auto_merges():
    report = evaluate(RECORDS)
    assert report["confusion_matrix"]["fp"] == 0
    assert report["precision"] == 1.0
    assert report["recall"] >= 0.9
