from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

SCHEMA_VERSION = "safetrace.case-pack/0.8"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_pack(data_dir: Path, generated_at: str | None = None) -> dict[str, Any]:
    recommendations = load_json(data_dir / "recommendations.json")
    review = load_json(data_dir / "review.json")
    unresolved = load_json(data_dir / "unresolved_questions.json")
    sources = load_json(data_dir / "sources.json")
    counts = Counter(item["status"] for item in recommendations["recommendations"])

    findings = [
        {
            "id": f"greco-{item['id']}",
            "title": item["title"],
            "statement": item["status_reason"],
            "evidence_state": "verified_fact",
            "official_status": item["status"],
            "responsible_institutions": item["responsible_institutions"],
            "source_anchor": item["source_anchor"],
            "limitations": "Responsible-institution mapping is SafeTrace editorial navigation, not a formal GRECO assignment.",
        }
        for item in recommendations["recommendations"]
    ]

    pack: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pack_id": "safetrace-case-001-public",
        "version": "0.8.0",
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "edition": "public_redacted",
        "case": {
            "id": "case-001",
            "title": "Germany's 14 Anti-Corruption Promises",
            "jurisdiction": "Germany",
            "purpose": "Make GRECO implementation status reproducible and understandable without alleging individual criminal conduct.",
        },
        "executive_summary": {
            "implemented_satisfactorily": counts["implemented_satisfactorily"],
            "partly_implemented": counts["partly_implemented"],
            "not_implemented": counts["not_implemented"],
            "key_gap": unresolved["questions"][0]["question"],
            "interpretation": unresolved["questions"][0]["safe_interpretation"],
        },
        "chronology": [
            {"date": "2020-10-29", "event": "GRECO adopted Germany's Fifth Round Evaluation Report.", "evidence_state": "verified_fact", "source_id": "greco-germany-2020-evaluation"},
            {"date": "2025-03-19", "event": "GRECO adopted the Second Compliance Report.", "evidence_state": "verified_fact", "source_id": "greco-germany-2025-second-compliance"},
            {"date": "2025-08-08", "event": "The Second Compliance Report was made public.", "evidence_state": "verified_fact", "source_id": "greco-germany-2025-second-compliance"},
            {"date": "2026-03-31", "event": "GRECO's requested deadline for Germany's progress report.", "evidence_state": "verified_fact", "source_id": "greco-germany-2025-second-compliance"},
            {"date": "2026-07-23", "event": "SafeTrace manual check found no newer public Fifth Round report on GRECO's Germany page.", "evidence_state": "unresolved_gap", "source_id": "greco-germany-fifth-round-page"},
        ],
        "findings": findings,
        "unresolved_questions": unresolved["questions"],
        "source_manifest": sources["sources"],
        "review": review,
        "redaction_profile": {
            "edition": "public_redacted",
            "personal_data_included": False,
            "victim_or_witness_data_included": False,
            "private_addresses_included": False,
        },
        "limitations": [
            "This pack reports institutional implementation statuses, not criminal guilt.",
            "No conclusion of bribery, corruption or unlawful influence is made.",
            "The absence of a newer public GRECO report does not prove non-submission.",
            "Restricted partner editions should include retained source bytes, hashes and access logs.",
            "This public prototype is not a certified court exhibit or official police report.",
        ],
    }
    validate_pack(pack)
    return pack


def validate_pack(pack: dict[str, Any]) -> None:
    required = {
        "schema_version", "pack_id", "version", "generated_at", "edition", "case",
        "executive_summary", "chronology", "findings", "unresolved_questions",
        "source_manifest", "review", "redaction_profile", "limitations",
    }
    missing = required - set(pack)
    if missing:
        raise ValueError(f"Missing pack fields: {sorted(missing)}")
    if pack["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unexpected schema version")
    if len(pack["findings"]) != 14:
        raise ValueError("Case 001 must contain 14 findings")
    summary = pack["executive_summary"]
    totals = (
        summary["implemented_satisfactorily"],
        summary["partly_implemented"],
        summary["not_implemented"],
    )
    if totals != (4, 6, 4):
        raise ValueError(f"Unexpected GRECO totals: {totals}")
    redaction = pack["redaction_profile"]
    if pack["edition"] == "public_redacted" and any(
        redaction[key] for key in (
            "personal_data_included", "victim_or_witness_data_included", "private_addresses_included"
        )
    ):
        raise ValueError("Public-redacted pack cannot include sensitive personal data")
    source_ids = {item["source_id"] for item in pack["source_manifest"]}
    for event in pack["chronology"]:
        if event["source_id"] not in source_ids:
            raise ValueError(f"Chronology event has unknown source: {event['source_id']}")
    for finding in pack["findings"]:
        if not finding.get("source_anchor") or not finding.get("evidence_state"):
            raise ValueError(f"Finding lacks provenance: {finding.get('id')}")


def _status_label(status: str) -> str:
    return {
        "implemented_satisfactorily": "Implemented",
        "partly_implemented": "Partly implemented",
        "not_implemented": "Not implemented",
    }[status]


def make_pdf(pack: dict[str, Any], output: Path) -> None:
    validate_pack(pack)
    output.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    margin = 18 * mm
    frame = Frame(margin, 17 * mm, page_w - 2 * margin, page_h - 31 * mm, id="normal")

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d5d3ca"))
        canvas.line(margin, 13 * mm, page_w - margin, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#62675f"))
        canvas.drawString(margin, 8 * mm, "SafeTrace v0.8 - Public redacted case pack")
        canvas.drawRightString(page_w - margin, 8 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document = BaseDocTemplate(
        str(output), pagesize=A4, leftMargin=margin, rightMargin=margin,
        topMargin=15 * mm, bottomMargin=17 * mm,
        title=pack["case"]["title"], author="SafeTrace / Michael Ninh",
        subject="Public-interest accountability case pack",
    )
    document.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=header_footer))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="KickerX", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.HexColor("#315d48"), spaceAfter=5))
    styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=29, leading=31, textColor=colors.HexColor("#171915"), alignment=TA_LEFT, spaceAfter=13))
    styles.add(ParagraphStyle(name="LeadX", parent=styles["BodyText"], fontSize=11.5, leading=16, textColor=colors.HexColor("#454a43"), spaceAfter=13))
    styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=23, textColor=colors.HexColor("#171915"), spaceBefore=7, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=colors.HexColor("#171915"), spaceBefore=7, spaceAfter=5))
    styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=9.3, leading=13, textColor=colors.HexColor("#30342f"), spaceAfter=7))
    styles.add(ParagraphStyle(name="SmallX", parent=styles["BodyText"], fontSize=7.6, leading=10, textColor=colors.HexColor("#62675f"), spaceAfter=4))
    styles.add(ParagraphStyle(name="StatusX", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.4, leading=9, textColor=colors.HexColor("#171915")))

    story: list[Any] = [
        Spacer(1, 16 * mm),
        Paragraph("SAFETRACE CASE 001", styles["KickerX"]),
        Paragraph(pack["case"]["title"], styles["TitleX"]),
        Paragraph("Investigator-ready public baseline: official sources, reviewed findings, unresolved gaps and explicit limitations.", styles["LeadX"]),
    ]
    summary = pack["executive_summary"]
    metrics = Table(
        [
            [Paragraph("4", styles["TitleX"]), Paragraph("6", styles["TitleX"]), Paragraph("4", styles["TitleX"])],
            [Paragraph("Implemented", styles["SmallX"]), Paragraph("Partly implemented", styles["SmallX"]), Paragraph("Not implemented", styles["SmallX"])],
        ],
        colWidths=[52 * mm, 52 * mm, 52 * mm],
    )
    metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffdf7")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d5d3ca")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d5d3ca")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
    ]))
    story += [metrics, Spacer(1, 8 * mm)]
    gap = Table(
        [[Paragraph("KEY UNRESOLVED GAP", styles["KickerX"]), Paragraph(summary["key_gap"], styles["H2X"]), Paragraph(summary["interpretation"], styles["BodyX"])]],
        colWidths=[31 * mm, 61 * mm, 64 * mm],
    )
    gap.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e7b85d")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b98b31")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [gap, Spacer(1, 8 * mm), Paragraph("Publication boundary", styles["H2X"]), Paragraph(pack["case"]["purpose"], styles["BodyX"])]
    story += [Paragraph(f"- {item}", styles["BodyX"]) for item in pack["limitations"][:3]]
    story.append(PageBreak())

    story += [Paragraph("Chronology", styles["H1X"]), Paragraph("Only dated, source-backed events are included. A public absence is labelled as a gap, not proof of non-compliance.", styles["LeadX"])]
    chronology = [[Paragraph("Date", styles["StatusX"]), Paragraph("Event", styles["StatusX"]), Paragraph("State", styles["StatusX"]), Paragraph("Source", styles["StatusX"])]]
    for item in pack["chronology"]:
        chronology.append([
            Paragraph(item["date"], styles["SmallX"]), Paragraph(item["event"], styles["BodyX"]),
            Paragraph(item["evidence_state"].replace("_", " "), styles["SmallX"]), Paragraph(item["source_id"], styles["SmallX"]),
        ])
    chronology_table = Table(chronology, colWidths=[27 * mm, 82 * mm, 28 * mm, 31 * mm], repeatRows=1)
    chronology_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151d18")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5d3ca")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f3ec")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [chronology_table, Spacer(1, 8 * mm), Paragraph("Recommendation findings", styles["H1X"])]

    status_colours = {"Implemented": "#d4ed82", "Partly implemented": "#f1d89a", "Not implemented": "#efb0aa"}
    for finding in pack["findings"]:
        status = _status_label(finding["official_status"])
        heading = Table(
            [[Paragraph(finding["id"].upper(), styles["StatusX"]), Paragraph(finding["title"], styles["H2X"]), Paragraph(status, styles["StatusX"])]],
            colWidths=[22 * mm, 111 * mm, 35 * mm],
        )
        heading.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#315d48")), ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor(status_colours[status])),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5d3ca")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        details = Table([
            [Paragraph("Finding", styles["StatusX"]), Paragraph(finding["statement"], styles["BodyX"])],
            [Paragraph("Owner map", styles["StatusX"]), Paragraph("; ".join(finding["responsible_institutions"]), styles["SmallX"])],
            [Paragraph("Source", styles["StatusX"]), Paragraph(finding["source_anchor"], styles["SmallX"])],
            [Paragraph("Limitation", styles["StatusX"]), Paragraph(finding["limitations"], styles["SmallX"])],
        ], colWidths=[27 * mm, 141 * mm])
        details.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0eee6")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5d3ca")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(KeepTogether([heading, details, Spacer(1, 4 * mm)]))

    story += [PageBreak(), Paragraph("Source manifest", styles["H1X"]), Paragraph("The public pack names canonical official sources. Restricted partner editions should additionally include retained bytes, hashes and access logs.", styles["LeadX"])]
    source_rows = [[Paragraph("ID", styles["StatusX"]), Paragraph("Publisher / title", styles["StatusX"]), Paragraph("Canonical URL", styles["StatusX"])]]
    for source in pack["source_manifest"]:
        source_rows.append([
            Paragraph(source["source_id"], styles["SmallX"]),
            Paragraph(f"{source['publisher']}<br/>{source['title']}", styles["SmallX"]),
            Paragraph(source["url"], styles["SmallX"]),
        ])
    source_table = Table(source_rows, colWidths=[43 * mm, 57 * mm, 68 * mm], repeatRows=1)
    source_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151d18")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5d3ca")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    review = pack["review"]
    story += [source_table, Spacer(1, 8 * mm), Paragraph("Review and redaction", styles["H1X"])]
    story += [
        Paragraph(f"Review state: {review['state']}", styles["BodyX"]),
        Paragraph(f"Reviewer role: {review['reviewer_role']}", styles["BodyX"]),
        Paragraph(f"Reviewed at: {review['reviewed_at']}", styles["BodyX"]),
        Paragraph("This edition contains no victim, witness, private-address or other sensitive personal data.", styles["BodyX"]),
        Paragraph("Limitations", styles["H1X"]),
    ]
    story += [Paragraph(f"- {item}", styles["BodyX"]) for item in pack["limitations"]]
    story += [Spacer(1, 8 * mm), Paragraph("Core principle", styles["H2X"]), Paragraph("Brave enough to investigate. Disciplined enough not to prejudge. Compassionate enough never to forget the victims.", styles["LeadX"])]
    document.build(story)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--pdf-output", type=Path, required=True)
    args = parser.parse_args()
    pack = build_pack(args.data_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    make_pdf(pack, args.pdf_output)


if __name__ == "__main__":
    main()
