from __future__ import annotations

import unittest
from urllib.error import HTTPError

from safetrace.intelligence_casework.company_live_production import fetch_with_retry


class CompanyLiveProductionTests(unittest.TestCase):
    def test_transient_503_is_retried_then_succeeds(self):
        calls = []

        def flaky(url, allowed_hosts, timeout=25):
            calls.append(url)
            if len(calls) < 3:
                raise HTTPError(url, 503, "Service Temporarily Unavailable", hdrs=None, fp=None)
            return b"<html>ok</html>", "text/html", url

        sleeps = []
        payload, ctype, resolved = fetch_with_retry(
            "https://example.com/record", {"example.com"}, attempts=3,
            base_fetch=flaky, sleeper=sleeps.append,
        )
        self.assertEqual(payload, b"<html>ok</html>")
        self.assertEqual(ctype, "text/html")
        self.assertEqual(resolved, "https://example.com/record")
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_403_is_not_retried_or_browser_bypassed(self):
        calls = []

        def denied(url, allowed_hosts, timeout=25):
            calls.append(url)
            raise HTTPError(url, 403, "Forbidden", hdrs=None, fp=None)

        with self.assertRaises(HTTPError):
            fetch_with_retry(
                "https://example.com/record", {"example.com"}, attempts=3,
                base_fetch=denied, sleeper=lambda _: None,
            )
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
