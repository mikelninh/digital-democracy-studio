"""stdlib-only regression checks; run python -m unittest discover -s tests -v."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import load_case, validate_case, claim_packet, discourse_summary, search_sources


class DiscourseLabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load_case()

    def test_source_referential_integrity(self):
        self.assertEqual(validate_case(self.case), [])

    def test_case_exact_counts(self):
        report = discourse_summary(self.case)
        self.assertEqual((report['message_count'], report['source_count'], report['claim_count']), (20, 9, 5))

    def test_42_percent_has_single_briefing_as_origination(self):
        posts = [p for p in self.case['posts'] if p['claim']=='c2' and p['date'] < '2026-07-19']
        self.assertGreaterEqual(len({p['actor'] for p in posts}), 3)
        self.assertEqual({p['source'] for p in posts}, {'s3'})

    def test_source_chain_preserves_non_confirmation(self):
        packet = claim_packet(self.case,'c2')
        self.assertIn('s4', [s['id'] for s in packet['challenging_evidence']])
        self.assertTrue(packet['human_review_required'])
        self.assertIn('not established', packet['claim']['limitation'])

    def test_budget_claim_distinguishes_authorisation_and_outlay(self):
        packet = claim_packet(self.case,'c1')
        self.assertEqual(packet['claim']['stance'],'contested')
        self.assertEqual([s['id'] for s in packet['challenging_evidence']], ['s2'])
        self.assertIn('€1.9', packet['challenging_evidence'][0]['excerpt'])

    def test_search_has_precise_source_and_anchor(self):
        results = search_sources(self.case,'42% near misses')
        self.assertEqual(results[0]['source_id'], 's3')
        self.assertTrue(results[0]['anchor'])
        self.assertTrue(results[0]['exact_excerpt'])

    def test_no_evidence_means_no_retrieval(self):
        self.assertEqual(search_sources(self.case, 'xyzunfindable'), [])
        self.assertEqual(search_sources(self.case, ''), [])

    def test_unknown_claim_fails_closed(self):
        with self.assertRaises(KeyError):
            claim_packet(self.case, 'c-does-not-exist')

    def test_does_not_claim_real_world_impact(self):
        self.assertEqual(discourse_summary(self.case)['fixture_type'], 'fully_synthetic')
        self.assertIn('fictional', self.case['case']['dataset'].lower()+' fictional')

    def test_reject_unknown_evidence_link(self):
        import copy
        modified = copy.deepcopy(self.case)
        modified['claims'][0]['support'].append('missing')
        self.assertTrue(validate_case(modified))

if __name__ == '__main__':
    unittest.main()
