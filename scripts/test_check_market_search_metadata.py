from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check-market-search-metadata.py")
SPEC = importlib.util.spec_from_file_location("check_market_search_metadata", SCRIPT)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class MarketSearchMetadataTests(unittest.TestCase):
    def test_accepts_readiness_nested_under_pieverse(self):
        lines = """name: venue
metadata:
  pieverse:
    marketSearch: true
    marketCost:
      perpetual:
        publicTakerFeeBps: 5
        sourceUrl: https://venue.example/fees
        asOf: 2026-09-03
    tradeReady:
      env:
        - [VENUE_API_KEY]
""".splitlines()

        self.assertEqual(checker.validate(Path("venue/SKILL.md"), lines), [])

    def test_rejects_market_search_nested_under_another_metadata_key(self):
        lines = """name: venue
metadata:
  other:
    marketSearch: true
    tradeReady:
      env:
        - [VENUE_API_KEY]
""".splitlines()

        self.assertEqual(
            checker.validate(Path("venue/SKILL.md"), lines),
            ["venue/SKILL.md: marketSearch must be nested under metadata.pieverse"],
        )

    def test_requires_public_market_cost_metadata(self):
        lines = """name: venue
metadata:
  pieverse:
    marketSearch: true
    tradeReady:
      env:
        - [VENUE_API_KEY]
""".splitlines()

        self.assertEqual(
            checker.validate(Path("venue/SKILL.md"), lines),
            ["venue/SKILL.md: marketSearch venue is missing metadata.pieverse.marketCost"],
        )

    def test_rejects_untrusted_or_incomplete_fee_evidence(self):
        lines = """name: venue
metadata:
  pieverse:
    marketSearch: true
    marketCost:
      Perpetual:
        publicTakerFeeBps: -1
        sourceUrl: http://venue.example/fees
    tradeReady:
      env:
        - [VENUE_API_KEY]
""".splitlines()

        self.assertEqual(
            checker.validate(Path("venue/SKILL.md"), lines),
            [
                "venue/SKILL.md: invalid marketCost product 'Perpetual'",
                "venue/SKILL.md: marketCost.Perpetual must declare exactly "
                "publicTakerFeeBps, sourceUrl, and asOf",
            ],
        )


if __name__ == "__main__":
    unittest.main()
