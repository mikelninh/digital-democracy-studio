from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from safetrace.law_fairness.model import load_case
from .model import (
    DISCIPLINES, Exercise, Finding, ReadinessDecision, ReviewPacket, ReviewSlot,
    StudyProtocol, plain,
)

NOW = "2026-07-24T18:00:00+00:00"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_hashes(safetrace_root: Path) -> dict[str, str]:
    repo_root = safetrace_root.parent
    candidates = {
        "constitution": safetrace_root / "CONSTITUTION.md",
        "investigation_os": safetrace_root / "INVESTIGATION_OS.md",
        "methodology": safetrace_root / "METHODOLOGY.md",
        "core_schema": safetrace_root / "core/schemas/safetrace-core-1.2.schema.json",
        "vault_report": safetrace_root / "evidence_vault/artifacts/release-report.json",
        "ledger_report": safetrace_root / "claim_ledger/artifacts/release-report.json",
        "agent_report": safetrace_root / "agent_queue/artifacts/release-report.json",
        "desk_report": safetrace_root / "investigation_desk/artifacts/release-report.json",
        "case004_reference": safetrace_root / "case_004_reference/artifacts/case-004-reference-pack.json",
        "release_status_source": safetrace_root / "v1/release.py",
    }
    missing = [name for name, path in candidates.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Review inputs missing: {missing}")
    return {name: sha256_file(path) for name, path in candidates.items()}


def review_slots() -> list[ReviewSlot]:
    definitions = {
        "investigative_editorial": (
            "Assess evidence wording, public-interest necessity, fairness and right-of-reply readiness.",
            "Experienced investigative journalist or editor with accountability reporting experience.",
        ),
        "privacy": (
            "Assess data minimisation, lawful basis assumptions, retention, deletion and data-subject risk.",
            "Qualified privacy professional with GDPR and DPIA experience.",
        ),
        "legal": (
            "Assess defamation, due process, publication risk, corrections and right-of-reply procedures.",
            "Qualified German lawyer with media, public or data-protection law experience.",
        ),
        "security": (
            "Assess threat model, access controls, audit integrity, recovery and incident response.",
            "Independent application-security specialist with threat-modelling and testing experience.",
        ),
        "domain": (
            "Assess German tax, social-policy and political-attribution methodology for Case 004.",
            "Independent subject-matter expert in German public finance or social policy.",
        ),
        "accessibility": (
            "Assess keyboard, screen-reader, contrast, language and cognitive accessibility requirements.",
            "Accessibility specialist familiar with WCAG and public-information services.",
        ),
        "public_comprehension": (
            "Assess whether citizens can distinguish facts, forecasts, attribution and value judgments.",
            "Researcher or practitioner experienced in public comprehension or civic communication.",
        ),
    }
    slots = [ReviewSlot(key, *definitions[key], True) for key in sorted(definitions)]
    for slot in slots:
        slot.validate()
    return slots


def packet_questions(discipline: str) -> tuple[str, ...]:
    common = (
        "Which claims or controls are unsupported by the supplied artifacts?",
        "Which failure could create the greatest harm to an affected person or the public?",
        "Which finding must block a pilot or publication until remediated?",
        "Which limitation should be disclosed publicly?",
    )
    specific = {
        "investigative_editorial": (
            "Are allegations, facts, red flags and unresolved gaps consistently separated?",
            "Is right of reply triggered at the correct threshold?",
        ),
        "privacy": (
            "Does every planned data field have a necessary purpose and retention rule?",
            "Which processing requires a DPIA or different lawful basis?",
        ),
        "legal": (
            "Could any wording imply guilt, causation or misconduct beyond the evidence?",
            "Are correction and withdrawal duties operationally adequate?",
        ),
        "security": (
            "Can an attacker alter evidence, decisions or exports without detection?",
            "Which production controls are absent or insufficiently tested?",
        ),
        "domain": (
            "Are legal status, political origin and distributional effects classified correctly?",
            "Which economic effects remain forecasts rather than observed outcomes?",
        ),
        "accessibility": (
            "Can all core workflows be completed with keyboard and assistive technology?",
            "Are uncertainty and status labels understandable without relying on colour?",
        ),
        "public_comprehension": (
            "Can non-experts distinguish nominal from real effects and direct from indirect effects?",
            "Does the overall verdict preserve nuance without becoming evasive?",
        ),
    }
    return common + specific[discipline]


def build_packets(hashes: dict[str, str]) -> list[ReviewPacket]:
    packets = []
    for discipline in sorted(DISCIPLINES):
        packet = ReviewPacket(
            f"review-packet:{discipline}",
            discipline,
            f"Independent {discipline.replace('_', ' ')} review of SafeTrace v1.8 readiness and Case 004 reference boundaries.",
            hashes,
            packet_questions(discipline),
            (
                "Signed conflict-of-interest declaration",
                "Structured finding register entries",
                "Written go/no-go recommendation for the reviewed scope",
                "Public-disclosure recommendation for each finding",
            ),
            NOW,
        )
        packet.validate()
        packets.append(packet)
    return packets


def seed_findings() -> list[Finding]:
    findings = [
        Finding(
            "finding:production-auth", "security",
            "Production identity, MFA and session revocation are not configured",
            "critical", "open", "security-owner",
            "Implement and independently test production identity, MFA, revocation and access review before any partner pilot.",
            "public", NOW, False,
            evidence_refs=("safetrace/investigation_desk/README.md",),
        ),
        Finding(
            "finding:case004-originals", "investigative_editorial",
            "Case 004 original source bytes are not retained in the Evidence Vault",
            "high", "open", "evidence-owner",
            "Run controlled source backfill, retain hashes and parser manifests, then re-review every material claim.",
            "public", NOW, False,
            evidence_refs=("safetrace/case_004_reference/README.md",),
        ),
        Finding(
            "finding:independent-security", "security",
            "No independent penetration test or security review has been completed",
            "high", "open", "security-owner",
            "Commission independent security assessment and remediate all critical and high findings.",
            "public_after_remediation", NOW, False,
        ),
        Finding(
            "finding:privacy-docs", "privacy",
            "Partner-specific lawful basis, DPIA and retention terms do not exist",
            "high", "open", "privacy-owner",
            "Create partner-specific processing map, lawful basis, DPIA, retention, deletion and escalation terms.",
            "public", NOW, False,
        ),
        Finding(
            "finding:accessibility", "accessibility",
            "No external accessibility audit has been completed",
            "medium", "open", "product-owner",
            "Conduct WCAG-focused external review and remediate blocking keyboard, screen-reader and comprehension issues.",
            "public_after_remediation", NOW, False,
        ),
        Finding(
            "finding:comprehension-study", "public_comprehension",
            "Citizen comprehension instrument has zero external participants",
            "medium", "open", "research-owner",
            "Obtain consented participants, collect minimised anonymised results and publish limitations.",
            "public", NOW, False,
        ),
        Finding(
            "finding:workflow-benchmark", "investigative_editorial",
            "Workflow improvement is based on synthetic operation counts rather than observed staff time",
            "medium", "open", "research-owner",
            "Run a controlled paired benchmark with qualified reviewers and compare time, errors and review burden.",
            "public", NOW, False,
        ),
    ]
    for finding in findings:
        finding.validate()
    return findings


def exercises() -> list[Exercise]:
    items = [
        Exercise(
            "exercise:threat-model", "threat_model_workshop",
            "A malicious public source contains prompt-injection text designed to alter claims and trigger publication.",
            (
                "Identify trust boundaries", "Identify assets and threat actors",
                "Map preventive and detective controls", "Record unresolved risks",
            ),
            (
                "Inject hostile source fixture", "Trace Source Registry to Agent Queue",
                "Verify proposal-only boundary", "Verify audit and public-export controls",
            ),
            (
                "External red-team validation is still required",
                "Production model-provider isolation is not configured",
            ),
            NOW, "synthetic_dry_run", False,
        ),
        Exercise(
            "exercise:publication-incident", "incident_tabletop",
            "A reviewed public claim is later shown to rely on an incorrect entity match.",
            (
                "Stop downstream publication", "Mark affected outputs stale",
                "Preserve evidence and decision history", "Prepare correction and notifications",
            ),
            (
                "Open incident", "Identify affected claim versions and exports",
                "Apply visible correction", "Test recovery and communication checklist",
            ),
            (
                "No real partner notification channel is configured",
                "External legal observer has not reviewed the procedure",
            ),
            NOW, "synthetic_dry_run", False,
        ),
        Exercise(
            "exercise:recovery", "recovery_drill",
            "The primary evidence storage becomes unavailable during an active review.",
            (
                "Restore from verified backup", "Verify object and receipt integrity",
                "Prevent work on unverified evidence", "Document recovery time and gaps",
            ),
            (
                "Declare outage", "Restore synthetic Vault backup", "Run integrity checks",
                "Resume only after verification",
            ),
            (
                "Production recovery-time objective is not yet observed",
                "Partner-specific backup location and encryption are not configured",
            ),
            NOW, "synthetic_dry_run", False,
        ),
    ]
    for item in items:
        item.validate()
    return items


def study_protocols() -> list[StudyProtocol]:
    protocols = [
        StudyProtocol(
            "protocol:workflow", "workflow_benchmark",
            "Measure whether SafeTrace reduces qualified review time without increasing errors, missed contradictions or publication risk.",
            (
                "Qualified investigator or reviewer", "Informed consent",
                "Comparable baseline and assisted tasks",
            ),
            True,
            ("task duration", "corrections", "missed evidence", "reviewer confidence", "workflow burden"),
            ("special-category personal data", "private addresses", "unnecessary free-text identifiers"),
            ("median time", "error rate", "contradiction recall", "review effort", "participant preference"),
            (
                "Stop on privacy or security incident", "Stop if task scope becomes non-comparable",
                "Do not report impact with fewer than the preregistered minimum participants",
            ),
            "ready_for_ethics_privacy_review",
        ),
        StudyProtocol(
            "protocol:comprehension", "citizen_comprehension",
            "Measure whether citizens correctly distinguish facts, forecasts, attribution, causation and value judgments.",
            (
                "Adult participant with informed consent", "German comprehension sufficient for the instrument",
                "No requirement to disclose political affiliation",
            ),
            True,
            ("question responses", "completion time", "optional clarity feedback", "coarse demographic bands"),
            ("name", "exact address", "political party membership", "health data", "device fingerprint"),
            ("correct-answer rate", "confidence calibration", "misinterpretation rate", "completion rate"),
            (
                "Stop on distress or data-protection concern", "Do not collect identifying political data",
                "Do not claim population representativeness without a valid sample",
            ),
            "ready_for_ethics_privacy_review",
        ),
    ]
    for protocol in protocols:
        protocol.validate()
    return protocols


def source_backfill_plan(safetrace_root: Path) -> dict[str, Any]:
    case = load_case(safetrace_root / "law_fairness/data/case_004.json")
    return {
        "schema_version": "safetrace.source-backfill-plan/1.8",
        "case_id": "case-004",
        "sources": [
            {
                "source_id": source.id,
                "url": source.url,
                "expected_publisher": source.publisher,
                "source_type": source.source_type,
                "status": "pending_controlled_acquisition",
                "required_outputs": [
                    "original bytes", "SHA-256 receipt", "retrieval timestamp",
                    "content type", "parser manifest", "exact claim anchors",
                ],
            }
            for source in case["sources"]
        ],
        "automatic_publication_after_backfill": False,
        "renewed_human_review_required": True,
    }


def make_pdf(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(
        str(output), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="SafeTrace v1.8 Independent Review Readiness Dossier",
        author="SafeTrace / Digital Democracy Studio",
    )
    story = [
        Paragraph("SAFETRACE v1.8", styles["Heading3"]),
        Paragraph("Independent Review Readiness Dossier", styles["Title"]),
        Paragraph(report["truthful_status"], styles["BodyText"]),
        Spacer(1, 7 * mm),
        Paragraph("Review disciplines", styles["Heading2"]),
        Paragraph(", ".join(report["review"]["disciplines"]), styles["BodyText"]),
        Spacer(1, 6 * mm),
        Paragraph("Open findings", styles["Heading2"]),
    ]
    rows = [["Severity", "Finding", "Owner", "Status"]]
    for finding in report["findings"]["items"]:
        rows.append([
            finding["severity"],
            Paragraph(finding["title"], styles["BodyText"]),
            finding["owner"],
            finding["status"],
        ])
    table = Table(rows, colWidths=[22 * mm, 95 * mm, 33 * mm, 28 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151d18")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8d5ca")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1efe8")]),
    ]))
    story += [table, Spacer(1, 7 * mm), Paragraph("Decision", styles["Heading2"])]
    story.append(Paragraph(
        "Ready to invite independent reviewers. Not approved for a partner pilot or restricted data.",
        styles["BodyText"],
    ))
    document.build(story)


def build(safetrace_root: Path, output_root: Path) -> dict[str, Any]:
    hashes = artifact_hashes(safetrace_root)
    slots = review_slots()
    packets = build_packets(hashes)
    findings = seed_findings()
    exercise_items = exercises()
    protocols = study_protocols()
    backfill = source_backfill_plan(safetrace_root)

    unresolved_critical = sum(item.severity == "critical" and item.status != "resolved" for item in findings)
    unresolved_high = sum(item.severity == "high" and item.status != "resolved" for item in findings)
    decision = ReadinessDecision(
        "ready_to_invite_external_reviewers",
        external_reviews_completed=0,
        external_approvals=0,
        unresolved_critical_findings=unresolved_critical,
        unresolved_high_findings=unresolved_high,
        ready_to_invite_reviewers=True,
        restricted_data_gate_open=False,
        partner_pilot_gate_open=False,
        reasons=(
            "All seven review packets are generated and artifact-hashed.",
            "External review slots remain unassigned and no approval is fabricated.",
            "Production authentication and independent security assessment remain open critical/high findings.",
            "Case 004 original-source backfill remains pending.",
        ),
    )
    report = {
        "schema_version": "safetrace.review-readiness-release/1.8",
        "status": "pass",
        "truthful_status": (
            "SafeTrace v1.8 is ready to invite independent reviewers with structured, hashed review packets, "
            "a finding register, synthetic exercises and consent-based study protocols. No external review, approval, "
            "partner pilot permission or restricted-data permission has been granted."
        ),
        "review": {
            "disciplines": sorted(DISCIPLINES),
            "slots": [plain(item) for item in slots],
            "packets": [plain(item) for item in packets],
            "external_reviews_completed": 0,
            "external_approvals": 0,
            "conflict_declarations_received": 0,
        },
        "findings": {
            "items": [plain(item) for item in findings],
            "open_total": sum(item.status != "resolved" for item in findings),
            "unresolved_critical": unresolved_critical,
            "unresolved_high": unresolved_high,
        },
        "exercises": {
            "items": [plain(item) for item in exercise_items],
            "synthetic_dry_runs": len(exercise_items),
            "externally_observed": 0,
        },
        "study_protocols": [plain(item) for item in protocols],
        "source_backfill": backfill,
        "decision": plain(decision),
        "artifact_hashes": hashes,
        "boundaries": {
            "independent_review_completed": False,
            "external_approval_present": False,
            "partner_named": False,
            "partner_pilot_gate_open": False,
            "restricted_data_gate_open": False,
            "production_security_approved": False,
        },
    }
    if not (
        len(slots) == 7
        and len(packets) == 7
        and all(slot.status == "unassigned" and slot.external_reviewer_id is None for slot in slots)
        and report["review"]["external_reviews_completed"] == 0
        and report["review"]["external_approvals"] == 0
        and unresolved_critical >= 1
        and unresolved_high >= 1
        and len(exercise_items) == 3
        and all(item.mode == "synthetic_dry_run" for item in exercise_items)
        and len(protocols) == 2
        and all(item.status == "ready_for_ethics_privacy_review" for item in protocols)
        and len(backfill["sources"]) == 11
        and report["decision"]["ready_to_invite_reviewers"] is True
        and report["decision"]["partner_pilot_gate_open"] is False
        and report["decision"]["restricted_data_gate_open"] is False
    ):
        report["status"] = "fail"

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "review-readiness-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "finding-register.json").write_text(
        json.dumps(report["findings"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "source-backfill-plan.json").write_text(
        json.dumps(backfill, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "study-protocols.json").write_text(
        json.dumps(report["study_protocols"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "review-packets.json").write_text(
        json.dumps(report["review"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    make_pdf(report, output_root / "review-readiness-dossier.pdf")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--safetrace-root", type=Path, default=Path("safetrace"))
    parser.add_argument("--output-root", type=Path, default=Path("safetrace/review_readiness/artifacts"))
    args = parser.parse_args()
    report = build(args.safetrace_root, args.output_root)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
