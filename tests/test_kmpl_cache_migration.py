import hashlib
import json
import unittest

import kmpl_ranges as k


def encode_legacy(cache, schema="kmpl-range-2"):
    raw = json.dumps(cache, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    chunks = [raw[i:i+30000] for i in range(0, len(raw), 30000)]
    return [[schema, cache["depot"], len(chunks), hashlib.sha256(raw.encode()).hexdigest()]] + [[v] for v in chunks]


class CacheMigrationTests(unittest.TestCase):
    def test_v2_cache_is_intentionally_reset_before_live_refetch(self):
        legacy = {"schema": "kmpl-range-2", "depot": "PRODDUTUR",
                  "months": {"2026-08": {"DRIVER_MONTH": {"stale": True}}}, "errors": {}}
        self.assertEqual(k.decode(encode_legacy(legacy), "PRODDUTUR"), k.new_cache("PRODDUTUR"))

    def test_unknown_schema_is_rejected(self):
        legacy = {"schema": "kmpl-range-1", "depot": "PRODDUTUR", "months": {}, "errors": {}}
        with self.assertRaisesRegex(ValueError, "identity/schema mismatch"):
            k.decode(encode_legacy(legacy, "kmpl-range-1"), "PRODDUTUR")

    def test_legacy_cache_checksum_and_depot_are_still_enforced(self):
        legacy = {"schema": "kmpl-range-2", "depot": "PRODDUTUR", "months": {}, "errors": {}}
        rows = encode_legacy(legacy)
        rows[1][0] += "x"
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            k.decode(rows, "PRODDUTUR")
        with self.assertRaisesRegex(ValueError, "identity/schema mismatch"):
            k.decode(encode_legacy(legacy), "RAJAMPET")


if __name__ == "__main__":
    unittest.main()
