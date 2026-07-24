from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from safetrace.investigation_desk.desk import InvestigationDesk
from safetrace.investigation_desk.model import (
    DeskCase, DeskDecision, DeskRecord, SessionContext, plain,
)
from safetrace.investigation_desk.views import workspace_manifest
from safetrace.law_fairness.model import build_public_assessment, load_case

NOW = "2026-07-24T13:00:00+00:00"


def session(subject: str, role: str, zone: str = "sensitive_internal") -> SessionContext:
    return SessionContext(
        subject, role, True, "synthetic-ci-identity", f"session:{subject}", zone, NOW,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comprehension_instrument() -> dict[str, Any]:
    questions = [
        {
            "id": "fact-vs-forecast",
            "concept": "fact_vs_forecast",
            "question": "Ist eine erwartete Beschäftigungswirkung bereits ein gemessener Fakt?",
            "answer": "Nein. Erwartete indirekte Wirkungen bleiben Prognosen, bis sie empirisch gemessen wurden.",
        },
        {
            "id": "enacted-vs-in-force",
            "concept": "legal_status",
            "question": "Ist eine für 2028 beschlossene Steuersenkung im Jahr 2026 bereits in Kraft?",
            "answer": "Nein. Sie ist beschlossen, aber ihr Wirksamkeitsdatum liegt in der Zukunft.",
        },
        {
            "id": "attribution-child-benefit",
            "concept": "political_attribution",
            "question": "Kann die Kindergelderhöhung 2026 der Regierung Merz zugerechnet werden?",
            "answer": "Nicht als neue Maßnahme. Sie wurde bereits im Dezember 2024 beschlossen.",
        },
        {
            "id": "nominal-vs-real",
            "concept": "nominal_vs_real",
            "question": "Ist ein nominal unveränderter Regelsatz dasselbe wie eine nominale Kürzung?",
            "answer": "Nein. Eine mögliche reale Kaufkraftminderung ist von einer nominalen Kürzung zu unterscheiden.",
        },
        {
            "id": "direct-vs-indirect",
            "concept": "direct_vs_indirect",
            "question": "Werden mögliche Wachstumswirkungen direkt durch das Gesetz ausgezahlt?",
            "answer": "Nein. Sie sind indirekte, modellabhängige Wirkungen.",
        },
        {
            "id": "lobbying-causation",
            "concept": "association_vs_causation",
            "question": "Beweist eine dokumentierte Lobbyposition, dass eine Entscheidung gekauft wurde?",
            "answer": "Nein. Dokumentierte Interessenvertretung beweist keine Bestechung oder Kausalität.",
        },
        {
            "id": "overall-verdict",
            "concept": "bounded_verdict",
            "question": "Warum lautet das Gesamturteil nicht einfach wahr oder falsch?",
            "answer": "Weil einzelne Teilbehauptungen unterschiedlich gut belegt und politisch zurechenbar sind.",
        },
        {
            "id": "value-judgment",
            "concept": "evidence_vs_value_judgment",
            "question": "Entscheidet SafeTrace, ob eine Verteilungswirkung moralisch gerecht ist?",
            "answer": "Nein. Es zeigt Wirkungen und Evidenz; normative Bewertung bleibt eine demokratische Wertentscheidung.",
        },
    ]
    return {
        "schema_version": "safetrace.comprehension-instrument/1.7",
        "questions": questions,
        "concepts": sorted({item["concept"] for item in questions}),
        "participant_count": 0,
        "observed_study_completed": False,
        "status": "instrument_ready_external_study_pending",
    }


def controlled_benchmark() -> dict[str, Any]:
    manual_steps = 70
    assisted_steps = 38
    reduction = round((manual_steps - assisted_steps) / manual_steps * 100, 1)
    return {
        "schema_version": "safetrace.workflow-benchmark/1.7",
        "mode": "controlled_synthetic_operation_count",
        "manual_baseline_steps": manual_steps,
        "safetrace_assisted_steps": assisted_steps,
        "step_reduction_percent": reduction,
        "target_percent": 30,
        "target_met_in_fixture": reduction >= 30,
        "observed_human_time_measurement": False,
        "real_partner_impact_claimed": False,
        "limitations": [
            "Operation counts are a deterministic workflow fixture, not observed staff time.",
            "A real partner benchmark must replace this fixture before v2.0 impact claims.",
        ],
    }


def make_pdf(pack: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="SafeTrace Case 004 Technical Reference Pack",
        author="SafeTrace / Digital Democracy Studio",
    )
    story = [
        Paragraph("SAFETRACE v1.7 · TECHNICAL REFERENCE", styles["Heading3"]),
        Paragraph(pack["case"]["title"], styles["Title"]),
        Paragraph(pack["case"]["question"], styles["Heading2"]),
        Paragraph(pack["overall_explanation"], styles["BodyText"]),
        Spacer(1, 8 * mm),
        Paragraph("Publication boundary", styles["Heading2"]),
        Paragraph(pack["publication_boundary"], styles["BodyText"]),
        Spacer(1, 6 * mm),
        Paragraph("Claim tests", styles["Heading2"]),
    ]
    rows = [["Claim", "Verdict", "Reasoning"]]
    for claim in pack["claims"]:
        rows.append([
            Paragraph(claim["claim"], styles["BodyText"]),
            Paragraph(claim["verdict"].replace("_", " "), styles["BodyText"]),
            Paragraph(claim["reasoning"], styles["BodyText"]),
        ])
    table = Table(rows, colWidths=[55 * mm, 30 * mm, 86 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151d18")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8d5ca")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1efe8")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [table, Spacer(1, 8 * mm), Paragraph("Source backfill", styles["Heading2"])]
    story.append(Paragraph(
        f"{pack['source_backfill']['original_bytes_backfilled']} of "
        f"{pack['source_backfill']['sources_registered']} original source files are stored in the Evidence Vault. "
        "This technical reference pack is not a newly verified public publication.",
        styles["BodyText"],
    ))
    document.build(story)


def build(safetrace_root: Path, output_root: Path) -> dict[str, Any]:
    data_path = safetrace_root / "law_fairness/data/case_004.json"
    loaded = load_case(data_path)
    public_assessment = build_public_assessment(loaded)
    sources = loaded["sources"]
    measures = loaded["measures"]
    claim_tests = loaded["claim_tests"]

    desk = InvestigationDesk()
    investigator = session("user:case004-investigator", "investigator")
    reviewer = session("user:case004-reviewer", "reviewer")
    admin = session("user:case004-admin", "admin")

    case = DeskCase(
        "case-004",
        loaded["title"],
        loaded["question"],
        "triage",
        investigator.subject_id,
        "public",
        "The distributional and attribution claims concern enacted German public policy.",
        "This v1.7 pack is a technical reference using reviewed repository records; new public publication remains blocked until original source bytes are backfilled.",
        NOW,
        NOW,
    )
    desk.create_case(investigator, case)
    desk.transition_case(
        investigator, case.id, "accept_case", "2026-07-24T13:01:00+00:00",
        "Case 004 has a bounded question, named sources and an explicit publication boundary.",
    )

    for index, source in enumerate(sources, start=1):
        desk.add_record(
            investigator,
            DeskRecord(
                f"desk-source:{source.id}", case.id, "source", source.title,
                "registered_missing_original_bytes", "public", investigator.subject_id,
                f"2026-07-24T13:{index + 1:02d}:00+00:00",
                {
                    "source_id": source.id,
                    "publisher": source.publisher,
                    "url": source.url,
                    "source_type": source.source_type,
                    "evidence_vault_receipt_id": None,
                },
            ),
        )

    groups: set[str] = set()
    for measure in measures:
        desk.add_record(
            investigator,
            DeskRecord(
                f"event:{measure.id}", case.id, "event", measure.title,
                measure.status, "public", investigator.subject_id, NOW,
                {
                    "date": measure.effective_date,
                    "origin": measure.origin,
                    "attributable_to_current_government": measure.attributable_to_current_government,
                    "description": measure.description,
                },
                tuple(f"desk-source:{source_id}" for source_id in measure.source_ids),
            ),
        )
        for impact in measure.impacts:
            groups.add(impact.group)
            entity_id = f"entity:group:{impact.group}"
            if entity_id not in desk.records:
                desk.add_record(
                    investigator,
                    DeskRecord(
                        entity_id, case.id, "entity", impact.group.replace("_", " ").title(),
                        "documented_group", "public", investigator.subject_id, NOW,
                        {"entity_type": "affected_group"},
                    ),
                )
            desk.add_record(
                investigator,
                DeskRecord(
                    f"relationship:{measure.id}:{impact.dimension}:{impact.group}",
                    case.id, "relationship",
                    f"{measure.title} → {impact.group.replace('_', ' ')}",
                    "documented_impact_channel", "public", investigator.subject_id, NOW,
                    {
                        "measure_id": measure.id,
                        "target_entity_id": entity_id,
                        "dimension": impact.dimension,
                        "effect": impact.effect,
                        "confidence": impact.confidence,
                        "directness": impact.directness,
                        "explanation": impact.explanation,
                        "causation_boundary": "Documented or assessed impact channel; not proof of every realised outcome.",
                    },
                    tuple(f"desk-source:{source_id}" for source_id in measure.source_ids),
                ),
            )

    measure_by_id = {measure.id: measure for measure in measures}
    claim_source_coverage: dict[str, list[str]] = {}
    for index, claim in enumerate(claim_tests, start=1):
        source_ids = sorted({
            source_id
            for measure_id in claim.measure_ids
            for source_id in measure_by_id[measure_id].source_ids
        })
        claim_source_coverage[claim.id] = source_ids
        record = DeskRecord(
            f"desk-claim:{claim.id}", case.id, "claim", claim.claim,
            "legacy_reference_review", "public", investigator.subject_id,
            f"2026-07-24T14:{index:02d}:00+00:00",
            {
                "claim_id": claim.id,
                "claim": claim.claim,
                "verdict": claim.verdict,
                "reasoning": claim.reasoning,
                "measure_ids": list(claim.measure_ids),
                "original_byte_backfill_complete": False,
                "publication_allowed": False,
            },
            tuple(f"desk-source:{source_id}" for source_id in source_ids),
        )
        desk.add_record(investigator, record)
        desk.submit_review(investigator, record.id, f"2026-07-24T14:{index + 10:02d}:00+00:00")
        desk.decide_review(
            reviewer,
            DeskDecision(
                f"decision:{claim.id}", case.id, record.id,
                "repository_consistency_review", "approved", reviewer.subject_id,
                "The claim matches the reviewed Case 004 repository record; original source-byte verification remains pending and publication is blocked.",
                f"2026-07-24T15:{index:02d}:00+00:00",
            ),
        )

    agent_types = ("skeptic", "quant", "legal_status", "guardian")
    for index, agent_type in enumerate(agent_types, start=1):
        proposal = DeskRecord(
            f"proposal:case004:{agent_type}", case.id, "agent_proposal",
            f"{agent_type.replace('_', ' ').title()} proposal",
            "proposal_ready", "public", investigator.subject_id,
            f"2026-07-24T16:{index:02d}:00+00:00",
            {
                "agent_type": agent_type,
                "run_id": f"run:case004:{agent_type}",
                "proposal_only": True,
                "auto_approved": False,
                "result": {
                    "skeptic": "The words exclusively and nominal cut overstate the reviewed evidence.",
                    "quant": "Direct company relief and public-revenue effects must be separated from indirect growth forecasts.",
                    "legal_status": "Measures are separated into in-force, enacted and inherited statuses.",
                    "guardian": "No person-level blame, guilt score or causal lobbying allegation is permitted.",
                }[agent_type],
            },
            tuple(f"desk-source:{source.id}" for source in sources[:2]),
        )
        desk.add_record(investigator, proposal)
        desk.accept_agent_proposal(
            investigator, proposal.id, f"2026-07-24T16:{index + 10:02d}:00+00:00",
            "The bounded proposal may inform human review but cannot change the public record.",
        )

    workspace = workspace_manifest(desk, admin, "2026-07-24T17:00:00+00:00")
    audit = desk.verify_audit_chain()
    source_backfill = {
        "sources_registered": len(sources),
        "original_bytes_backfilled": 0,
        "coverage_percent": 0.0,
        "repository_dataset_sha256": sha256_file(data_path),
        "status": "original_source_backfill_required",
        "publication_allowed": False,
        "items": [
            {
                "source_id": source.id,
                "url": source.url,
                "registry_record_present": True,
                "original_vault_receipt_present": False,
            }
            for source in sources
        ],
    }
    benchmark = controlled_benchmark()
    comprehension = comprehension_instrument()
    monitoring = {
        "schema_version": "safetrace.case004-monitoring/1.7",
        "sources": [
            {"source_id": source.id, "url": source.url, "live_check_status": "not_run_in_deterministic_release"}
            for source in sources
        ],
        "automatic_public_effect": False,
        "human_review_required": True,
    }
    reference_pack = {
        "schema_version": "safetrace.case004-reference-pack/1.7",
        "edition": "technical_reference_not_new_publication",
        "case": {
            "id": loaded["case_id"],
            "title": loaded["title"],
            "question": loaded["question"],
        },
        "overall_verdict": loaded["overall_claim_verdict"],
        "overall_explanation": loaded["overall_explanation"],
        "publication_boundary": case.publication_boundary,
        "measures": public_assessment["measures"],
        "claims": public_assessment["claim_tests"],
        "sources": public_assessment["sources"],
        "source_backfill": source_backfill,
        "workflow": {
            "views": sorted(workspace["views"]),
            "audit": audit,
            "human_reviewed_claims": len(claim_tests),
            "agent_proposals_accepted_for_review": len(agent_types),
            "publication_requests": 0,
        },
        "benchmark": benchmark,
        "comprehension": comprehension,
        "monitoring": monitoring,
        "limitations": [
            "The repository dataset is reviewed but is not a substitute for retained original source bytes.",
            "The workflow benchmark uses deterministic operation counts, not observed human time.",
            "The comprehension instrument is ready, but no external participants have completed it.",
            "No new public publication is authorised by this technical reference release.",
        ],
    }

    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "case-004-reference-pack.json"
    json_path.write_text(
        json.dumps(reference_pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    pdf_path = output_root / "case-004-reference-pack.pdf"
    make_pdf(reference_pack, pdf_path)
    (output_root / "comprehension-instrument.json").write_text(
        json.dumps(comprehension, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "monitoring-manifest.json").write_text(
        json.dumps(monitoring, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report_status = "pass" if (
        len(sources) == 11
        and len(measures) == 5
        and len(claim_tests) == 5
        and all(claim_source_coverage.values())
        and len(workspace["views"]) == 11
        and audit["status"] == "pass"
        and all(desk.records[f"desk-claim:{claim.id}"].review_state == "approved" for claim in claim_tests)
        and all(desk.records[f"proposal:case004:{agent}"].status == "accepted_for_review" for agent in agent_types)
        and source_backfill["publication_allowed"] is False
        and source_backfill["original_bytes_backfilled"] == 0
        and benchmark["target_met_in_fixture"] is True
        and benchmark["observed_human_time_measurement"] is False
        and comprehension["participant_count"] == 0
        and comprehension["observed_study_completed"] is False
        and pdf_path.exists()
        and json_path.exists()
    ) else "fail"

    report = {
        "schema_version": "safetrace.case004-reference-release/1.7",
        "status": report_status,
        "counts": {
            "sources": len(sources),
            "measures": len(measures),
            "claims": len(claim_tests),
            "affected_groups": len(groups),
            "agent_proposals": len(agent_types),
            "desk_views": len(workspace["views"]),
        },
        "source_backfill": source_backfill,
        "workflow": reference_pack["workflow"],
        "benchmark": benchmark,
        "comprehension": comprehension,
        "artifacts": {
            "json": str(json_path),
            "pdf": str(pdf_path),
            "monitoring": str(output_root / "monitoring-manifest.json"),
        },
        "boundaries": {
            "technical_reference_complete": True,
            "new_publication_allowed": False,
            "real_partner_impact_claimed": False,
            "external_comprehension_study_completed": False,
            "restricted_partner_data": False,
        },
    }
    (output_root / "release-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--safetrace-root", type=Path, default=Path("safetrace"))
    parser.add_argument("--output-root", type=Path, default=Path("safetrace/case_004_reference/artifacts"))
    args = parser.parse_args()
    result = build(args.safetrace_root, args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
