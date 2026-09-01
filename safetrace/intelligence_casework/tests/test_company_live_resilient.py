from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from safetrace.intelligence_casework.company_live_resilient import _normalise_live_fact, investigate_resilient


class CompanyLiveResilientTests(unittest.TestCase):
    def test_german_euro_share_capital_is_not_inflated_by_100x(self):
        fact = _normalise_live_fact({
            "field": "share_capital_eur", "status": "extracted",
            "value": "2500000", "raw_value": "25.000,00 EUR",
        })
        self.assertEqual(fact["value"], "25000")

    def test_blocked_secondary_source_is_recorded_while_case_continues(self):
        case = {
            "case": {
                "id": "TEST-RESILIENT",
                "title": "Resilient live test",
                "question": "What survives source failure?",
                "executive_judgement_template": "Found {claims} facts, {contradictions} contradictions, {unresolved} unresolved."
            },
            "sources": [
                {
                    "id": "official", "title": "Official", "publisher": "Acme", "url": "https://example.com/",
                    "source_type": "company_official_website", "source_rank": "primary_official", "authority": 0.95,
                    "jurisdiction": "DE", "update_cadence": "manual",
                    "extract": [
                        {"field": "legal_name", "pattern": "(Acme GmbH)", "required": True},
                        {"field": "address", "pattern": "(Main Street 1)", "required": True}
                    ]
                },
                {
                    "id": "blocked", "title": "Blocked mirror", "publisher": "Mirror", "url": "https://blocked.example/record",
                    "source_type": "public_register_aggregator", "source_rank": "reputable_secondary", "authority": 0.7,
                    "jurisdiction": "DE", "update_cadence": "manual",
                    "extract": [{"field": "register_id", "pattern": "(HRB 12345)"}]
                }
            ],
            "required_questions": [
                {"field": "legal_name", "title": "Legal identity", "reason": "required", "next_step": "verify"},
                {"field": "register_id", "title": "Register ID", "reason": "not established", "next_step": "retrieve official record"}
            ]
        }

        def fake_fetch(url, allowed_hosts, timeout=25):
            if "blocked.example" in url:
                raise HTTPError(url, 403, "Forbidden", hdrs=None, fp=None)
            return b"<html><h1>Acme GmbH</h1></html>", "text/html", url

        with tempfile.TemporaryDirectory() as td, patch("safetrace.intelligence_casework.company_live_resilient.fetch_source", side_effect=fake_fetch):
            root = Path(td)
            case_path = root / "case.json"
            out = root / "out"
            case_path.write_text(json.dumps(case), encoding="utf-8")
            result = investigate_resilient(case_path, out, now="2026-09-01T08:00:00+00:00")
            self.assertEqual(result["integrity"]["status"], "pass")
            self.assertEqual(result["metrics"]["sources_requested"], 2)
            self.assertEqual(result["metrics"]["sources_acquired"], 1)
            self.assertEqual(result["metrics"]["source_failures"], 1)
            self.assertEqual(result["metrics"]["extraction_gaps"], 1)
            self.assertTrue(any(c["field"] == "legal_name" for c in result["claims"]))
            self.assertTrue(any(g["status"] == "source_unavailable" for g in result["unresolved_questions"]))
            self.assertTrue(any(g["status"] == "extraction_gap" and "address" in g["field"] for g in result["unresolved_questions"]))
            self.assertTrue(any(g["field"] == "register_id" for g in result["unresolved_questions"]))
            self.assertIn("source-access failure", result["bottom_line"])
            report = (out / "report.md").read_text(encoding="utf-8")
            self.assertIn("unavailable HTTP 403", report)
            self.assertNotIn("403 equivalent success", report)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("Still unknown", html)
            self.assertIn("UNAVAILABLE", html)
            self.assertIn("parser gaps", html)


if __name__ == "__main__":
    unittest.main()
