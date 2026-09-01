from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from safetrace.intelligence_casework.company_live import html_to_text, investigate, reconcile_facts


class CompanyLiveTests(unittest.TestCase):
    def test_html_parser_removes_script_and_keeps_visible_text(self):
        payload = b"<html><script>bad()</script><h1>Acme GmbH</h1><p>HRB 12345</p></html>"
        text = html_to_text(payload)
        self.assertIn("Acme GmbH", text)
        self.assertIn("HRB 12345", text)
        self.assertNotIn("bad()", text)

    def test_conflicting_sources_are_not_silently_resolved(self):
        facts = [
            {"field": "share_capital_eur", "status": "extracted", "value": "25000", "source_id": "a", "confidence": 0.9, "evidence": "25,000"},
            {"field": "share_capital_eur", "status": "extracted", "value": "50000", "source_id": "b", "confidence": 0.7, "evidence": "50,000"},
        ]
        sources = {"a": {"authority": 0.9}, "b": {"authority": 0.7}}
        claims, contradictions = reconcile_facts(facts, sources)
        self.assertEqual(claims, [])
        self.assertEqual(len(contradictions), 1)
        self.assertEqual(contradictions[0]["status"], "unresolved")

    def test_live_case_generates_evidence_backed_outputs_and_keeps_ownership_gap_open(self):
        case = {
            "case": {
                "id": "TEST-LIVE",
                "title": "Acme live test",
                "question": "What is established?",
                "executive_judgement_template": "Found {claims} facts, {contradictions} contradictions, {unresolved} unresolved."
            },
            "sources": [
                {
                    "id": "official", "title": "Official", "publisher": "Acme", "url": "https://example.com/",
                    "source_type": "company_official_website", "source_rank": "primary_official", "authority": 0.95, "jurisdiction": "DE", "update_cadence": "manual",
                    "extract": [
                        {"field": "legal_name", "pattern": "(Acme GmbH)", "required": True},
                        {"field": "address", "pattern": "(Main Street 1 10115 Berlin)", "required": True}
                    ]
                },
                {
                    "id": "registry", "title": "Registry", "publisher": "Registry mirror", "url": "https://registry.example/record",
                    "source_type": "public_register_aggregator", "source_rank": "reputable_secondary", "authority": 0.8, "jurisdiction": "DE", "update_cadence": "manual",
                    "extract": [
                        {"field": "legal_name", "pattern": "(Acme GmbH)"},
                        {"field": "register_id", "pattern": "(HRB 12345)", "required": True}
                    ]
                }
            ],
            "required_questions": [
                {"field": "legal_name", "title": "Legal identity", "reason": "required", "next_step": "verify"},
                {"field": "shareholders", "title": "Ownership", "reason": "not in sources", "next_step": "obtain shareholder list"}
            ]
        }
        payloads = {
            "https://example.com/": b"<html><h1>Acme GmbH</h1><p>Main Street 1 10115 Berlin</p></html>",
            "https://registry.example/record": b"<html><h1>Acme GmbH</h1><p>HRB 12345</p></html>",
        }

        def fake_fetch(url, allowed_hosts, timeout=25):
            return payloads[url], "text/html", url

        with tempfile.TemporaryDirectory() as td, patch("safetrace.intelligence_casework.company_live.fetch_source", side_effect=fake_fetch):
            root = Path(td)
            case_path = root / "case.json"
            out = root / "out"
            case_path.write_text(json.dumps(case), encoding="utf-8")
            result = investigate(case_path, out, now="2026-09-01T08:00:00+00:00")
            self.assertEqual(result["integrity"]["status"], "pass")
            self.assertEqual(result["metrics"]["sources_acquired"], 2)
            self.assertTrue(any(c["field"] == "legal_name" and c["status"] == "corroborated" for c in result["claims"]))
            self.assertTrue(any(g["field"] == "shareholders" and g["status"] == "not_established" for g in result["unresolved_questions"]))
            self.assertIn("absence of evidence", result["bottom_line"])
            self.assertTrue((out / "result.json").exists())
            self.assertTrue((out / "report.md").exists())
            self.assertTrue((out / "index.html").exists())
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("What the investigation found", html)
            self.assertIn("Still unknown", html)


if __name__ == "__main__":
    unittest.main()
