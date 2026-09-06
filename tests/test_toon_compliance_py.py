#!/usr/bin/env python3
"""
test_toon_compliance_py.py — Comprehensive TOON Specification v4.1 Test Suite for Python

Verifies:
1. Canonical numeric normalization (§2)
2. Minimal string quoting heuristics (§7)
3. Inline primitive arrays [N]: v1,v2... (§9.1)
4. Tabular arrays for uniform objects key[N]{f1,f2}: (§9.3)
5. Keyed tabular objects key[N:]{f1,f2}: (§9.5)
6. Indentation-based hierarchical objects (§8)
7. Full-line comment handling and decoding (§5.1)
8. Token savings estimation (>30% reduction vs JSON)
9. Dialogue turns formatting for LLM context injection
"""

import unittest
from core.engine_py.toon_adapter import (
    encode_toon, decode_toon, calculate_token_savings,
    format_conversation_turns, ToonEncoder, ToonDecoder
)


class TestToonCompliance(unittest.TestCase):

    def test_canonical_numbers(self):
        encoder = ToonEncoder()
        # Canonical decimal normalization per §2
        self.assertEqual(encoder._format_number(0), "0")
        self.assertEqual(encoder._format_number(-0.0), "0")
        self.assertEqual(encoder._format_number(42), "42")
        self.assertEqual(encoder._format_number(1.5000), "1.5")
        self.assertEqual(encoder._format_number(100.0), "100")
        self.assertEqual(encoder._format_number(-3.14), "-3.14")

    def test_string_quoting_heuristics(self):
        encoder = ToonEncoder()
        # Quoting required per §7
        self.assertTrue(encoder._should_quote(""))
        self.assertTrue(encoder._should_quote("true"))
        self.assertTrue(encoder._should_quote("null"))
        self.assertTrue(encoder._should_quote("05"))  # forbidden leading zero
        self.assertTrue(encoder._should_quote("hello,world"))  # delimiter
        self.assertTrue(encoder._should_quote("name:value"))  # colon
        self.assertTrue(encoder._should_quote("#hashtag"))  # comment char
        self.assertTrue(encoder._should_quote(" items "))  # leading/trailing space

        # Quoting NOT required
        self.assertFalse(encoder._should_quote("hello"))
        self.assertFalse(encoder._should_quote("engineer"))
        self.assertFalse(encoder._should_quote("my_task_id"))

    def test_inline_primitive_array(self):
        data = {"tags": ["alpha", "beta", "gamma"]}
        encoded = encode_toon(data)
        self.assertIn("tags[3]: alpha,beta,gamma", encoded)

        decoded = decode_toon(encoded)
        self.assertEqual(decoded, data)

    def test_tabular_uniform_objects(self):
        data = {
            "users": [
                {"id": 1, "name": "Ada", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"}
            ]
        }
        encoded = encode_toon(data)
        expected_header = "users[2]{id,name,role}:"
        self.assertIn(expected_header, encoded)
        self.assertIn("  1,Ada,admin", encoded)
        self.assertIn("  2,Bob,user", encoded)

        decoded = decode_toon(encoded)
        self.assertEqual(decoded, data)

    def test_keyed_tabular_uniform_mappings(self):
        data = {
            "services": {
                "web": {"port": 8080, "status": "active"},
                "db": {"port": 5432, "status": "active"}
            }
        }
        encoded = encode_toon(data)
        self.assertIn("services[2:]{port,status}:", encoded)
        self.assertIn("  web: 8080,active", encoded)
        self.assertIn("  db: 5432,active", encoded)

        decoded = decode_toon(encoded)
        self.assertEqual(decoded, data)

    def test_comment_stripping(self):
        toon_with_comments = """
# Header comment explaining data
users[2]{id,name}:
  # In-scope comment
  1,Alice
  2,Charlie
"""
        decoded = decode_toon(toon_with_comments)
        self.assertEqual(len(decoded.get("users", [])), 2)
        self.assertEqual(decoded["users"][0]["name"], "Alice")
        self.assertEqual(decoded["users"][1]["name"], "Charlie")

    def test_token_savings_benchmark(self):
        data = {
            "agents": [
                {"id": f"agent-{i}", "role": "engineer", "status": "active", "score": 90 + i}
                for i in range(1, 15)
            ]
        }
        stats = calculate_token_savings(data)
        # Verify that TOON achieves >30% token reduction
        self.assertGreaterEqual(stats["savings_percent"], 30)
        self.assertLess(stats["toon_chars"], stats["json_chars"])

    def test_conversation_turns_formatting(self):
        turns = [
            {"role": "user", "content": "Start workflow analysis"},
            {"role": "assistant", "content": "Initialized 3 workers"}
        ]
        dialogue_toon = format_conversation_turns(turns)
        self.assertIn("dialogue[2]{idx,role,content}:", dialogue_toon)
        self.assertIn("  1,user,Start workflow analysis", dialogue_toon)
        self.assertIn("  2,assistant,Initialized 3 workers", dialogue_toon)


if __name__ == "__main__":
    unittest.main()
