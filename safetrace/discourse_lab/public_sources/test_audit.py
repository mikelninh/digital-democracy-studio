import copy
import unittest
from audit import load_catalog, validate, source_independence

class DocumentationSourceTests(unittest.TestCase):
    def setUp(self):
        self.data = load_catalog()
    def test_valid_verified_catalogue(self):
        self.assertEqual(validate(self.data), [])
    def test_no_live_ingestion_claim(self):
        self.assertIs(self.data['meta']['api_fetch_executed'], False)
        self.assertEqual(self.data['meta']['real_parliamentary_documents_ingested'], 0)
    def test_berlin_api_pages_share_upstream_origin(self):
        self.assertEqual(source_independence(self.data, 'C2')['publisher_families'], 1)
    def test_unknown_reference_fails(self):
        broken=copy.deepcopy(self.data);broken['claims'][0]['sources']=['X0']
        self.assertTrue(validate(broken))
    def test_block_unsupported_claim(self):
        self.assertEqual(self.data['claims'][-1]['status'], 'not-supported')
        self.assertEqual(self.data['claims'][-1]['id'], 'C5')
    def test_license_attribution_present(self):
        self.assertIn('dl-de/by-2-0',self.data['meta']['attribution'])
        self.assertIn('Abgeordnetenhaus',self.data['meta']['attribution'])

if __name__ == '__main__': unittest.main()
