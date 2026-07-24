import json, unittest
from pathlib import Path
from safetrace.mcp_server import server
from safetrace.policy_platform.validate import validate
ROOT=Path(__file__).resolve().parents[2]
class PlatformTests(unittest.TestCase):
    def test_release_contract(self):
        report=validate(ROOT); self.assertEqual(report["status"],"pass",report["errors"]); self.assertGreaterEqual(report["counts"]["systems"],5); self.assertGreaterEqual(report["counts"]["indicators"],8)
    def test_mcp_query_layer(self):
        self.assertEqual(server._get_system("energy-abundance")["domain"],"energy"); self.assertTrue(server._search("Bundesnetzagentur")); self.assertIn("not a single score",server._compare(["citizen-capital","ai-robotics-dividend"])["warning"])
    def test_static_api_is_read_only(self):
        spec=json.loads((ROOT/"open_policy_api/v1/openapi.json").read_text()); methods={m for path in spec["paths"].values() for m in path}; self.assertEqual(methods,{"get"})
    def test_dashboard_has_no_tracking(self):
        text=(ROOT/"deutschland_dashboard/index.html").read_text().lower(); [self.assertNotIn(token,text) for token in ["google-analytics","gtag(","segment.io","mixpanel","posthog"]]
if __name__=="__main__":unittest.main()
