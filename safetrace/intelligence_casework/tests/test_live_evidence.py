from __future__ import annotations
import unittest
from pathlib import Path
from safetrace.intelligence_casework.live_evidence import build_registry, name_score, parse_uksl_csv, screen_records

ROOT=Path(__file__).resolve().parents[1]
FIX=(ROOT/"data"/"uksl_fixture.csv").read_bytes()

class LiveEvidenceTests(unittest.TestCase):
    def test_registry_is_valid_and_official(self):
        r=build_registry(reviewed_at="2026-09-01T08:00:00+00:00")
        e=r.get("uk-fcdo-sanctions-list-csv")
        self.assertEqual(e.source_rank,"primary_official")
        self.assertTrue(e.canonical_url.startswith("https://sanctionslist.fcdo.gov.uk/"))

    def test_parser_reads_fixture(self):
        rows=parse_uksl_csv(FIX)
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[0]["unique_id"],"SYN001")
        self.assertEqual(rows[0]["name"],"Marek Vostryk")

    def test_name_scoring_handles_middle_names(self):
        self.assertGreaterEqual(name_score("Vladimir Putin","Vladimir Vladimirovich Putin"),.98)

    def test_screening_never_auto_confirms_identity(self):
        rows=parse_uksl_csv(FIX)
        c=screen_records(rows,"Marek Vostrik",dob="12/04/1983",nationality="DE",threshold=.8)
        self.assertEqual(len(c),1)
        self.assertEqual(c[0]["identity_status"],"REVIEW_REQUIRED")
        self.assertIn("dob",c[0]["identifier_conflicts"])
        self.assertIn("nationality",c[0]["identifier_conflicts"])

    def test_alias_rows_collapse_by_unique_id(self):
        rows=parse_uksl_csv(FIX)
        c=screen_records(rows,"Anya Example",threshold=.6)
        self.assertEqual(len([x for x in c if x["unique_id"]=="SYN002"]),1)

if __name__=="__main__": unittest.main()
