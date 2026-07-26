"""Static accessibility and privacy checks for the public series page.

This is a release guard, not a WCAG conformance claim.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"

REQUIRED_MARKERS = (
    '<html lang="de">',
    'class="skip-link"',
    'href="#main-content"',
    '<main id="main-content"',
    'aria-label="Hauptnavigation"',
    'aria-live="polite"',
    'type="button"',
    ':focus-visible',
    'prefers-reduced-motion',
    'Korrektur melden',
    'Beschwerde einreichen',
    'keine vertraulichen',
)

PROHIBITED_MARKERS = (
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "autoplay",
    "<marquee",
)


def main() -> int:
    try:
        html = INDEX.read_text(encoding="utf-8")
        missing = [marker for marker in REQUIRED_MARKERS if marker not in html]
        prohibited = [marker for marker in PROHIBITED_MARKERS if marker in html]
        if missing or prohibited:
            raise ValueError(
                json.dumps(
                    {"missing": missing, "prohibited": prohibited},
                    ensure_ascii=False,
                )
            )
    except (OSError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "invalid",
                    "error": str(exc),
                    "wcag_conformance_claimed": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "status": "valid",
                "static_checks": len(REQUIRED_MARKERS),
                "third_party_fonts": False,
                "wcag_target": "2.2 AA",
                "wcag_conformance_claimed": False,
                "external_user_testing_complete": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
