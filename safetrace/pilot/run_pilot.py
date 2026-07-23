from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from safetrace.pilot.model import evaluate_pilot, load_pilot


def build_public_report(input_path: Path, output_dir: Path) -> dict:
    pilot = load_pilot(input_path)
    evaluation = evaluate_pilot(pilot)
    payload = {
        "schema_version": "safetrace.pilot-evaluation/1.0",
        "pilot": {
            "pilot_id": pilot.pilot_id,
            "label": pilot.label,
            "case_id": pilot.case_id,
            "pilot_type": pilot.pilot_type,
            "data_classification": pilot.data_classification,
            "real_world_validation": pilot.real_world_validation,
            "notes": pilot.notes,
        },
        "metrics": {
            **pilot.metrics.__dict__,
            "time_saved_ratio": pilot.metrics.time_saved_ratio,
            "source_coverage": pilot.metrics.source_coverage,
            "human_review_coverage": pilot.metrics.human_review_coverage,
        },
        "evaluation": evaluation.to_dict(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    gate_rows = "".join(
        f"<tr><td>{html.escape(g.id)}</td><td>{'PASS' if g.passed else 'BLOCK'}</td>"
        f"<td>{html.escape(str(g.observed))}</td><td>{html.escape(str(g.target))}</td>"
        f"<td>{html.escape(g.explanation)}</td></tr>"
        for g in evaluation.gates
    )
    page = f"""<!doctype html>
<html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>SafeTrace v1.0 Pilot Readiness</title>
<style>body{{font-family:system-ui;max-width:980px;margin:auto;padding:40px;background:#f3f1e9;color:#171915}}main{{background:#fffdf7;padding:32px;border-radius:22px}}.badge{{display:inline-block;padding:7px 11px;border-radius:999px;background:#d4ed82;font-weight:800}}table{{width:100%;border-collapse:collapse;margin-top:24px}}td,th{{padding:10px;border-bottom:1px solid #ddd;text-align:left}}.warning{{padding:16px;background:#f3c46d;border-radius:14px}}</style>
<main><p class=\"badge\">{html.escape(evaluation.decision)}</p><h1>SafeTrace v1.0 — pilot-ready, not live-validated</h1>
<p class=\"warning\"><strong>Important:</strong> This is a synthetic benchmark. It does not claim partner-validated real-world impact and it does not authorise real victim data.</p>
<p>{evaluation.passed_gates}/{evaluation.total_gates} synthetic release gates passed.</p>
<table><thead><tr><th>Gate</th><th>Status</th><th>Observed</th><th>Target</th><th>Meaning</th></tr></thead><tbody>{gate_rows}</tbody></table>
<h2>Next boundary</h2><p>A real restricted partner pilot remains NO-GO until security, privacy, legal and partner agreements are completed.</p>
<p><a href=\"status.json\">Machine-readable status</a> · <a href=\"../\">SafeTrace portal</a></p></main></html>"""
    (output_dir / "index.html").write_text(page, encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path(__file__).parent / "data/synthetic_pilot.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "public")
    args = parser.parse_args()
    build_public_report(args.input, args.output)


if __name__ == "__main__":
    main()
