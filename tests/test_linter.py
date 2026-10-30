"""
Unit tests for SMS Linter Character Set & GSM 03.38 Concatenation
Includes emoji supplementary plane surrogate pair tests.
"""
import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.sms_linter import analyze_sms_text, GSM_EXTENDED

class TestSMSLinter(unittest.TestCase):
    def test_empty_string(self):
        res = analyze_sms_text("")
        self.assertEqual(res["char_count"], 0)
        self.assertEqual(res["utf16_units"], 0)
        self.assertEqual(res["segments"], 0)
        self.assertEqual(res["total_cost"], 0.0)

    def test_gsm_multipart_boundary(self):
        # 160 characters fits in 1 segment
        text_160 = "a" * 160
        res_160 = analyze_sms_text(text_160)
        self.assertEqual(res_160["segments"], 1)

        # 161 characters requires 2 segments (split into 153-char chunks)
        text_161 = "a" * 161
        res_161 = analyze_sms_text(text_161)
        self.assertEqual(res_161["segments"], 2)
        self.assertEqual(res_161["max_segment_limit"], 153)

    def test_all_extension_characters_recognized(self):
        # Each GSM extension character (| ^ € { } [ ] ~ \) should count as 2 units
        ext_sample = "|^€{}[~]\\"
        res = analyze_sms_text(ext_sample)
        self.assertEqual(res["encoding"], "GSM-7")
        self.assertEqual(res["extension_chars_count"], len(ext_sample))
        self.assertEqual(res["weighted_units"], len(ext_sample) * 2)

    def test_emoji_outside_bmp_counts_as_two_utf16_units(self):
        # A single emoji > U+FFFF counts as 2 UTF-16 units
        res = analyze_sms_text("🎉")
        self.assertEqual(res["encoding"], "UCS-2")
        self.assertTrue(res["has_surrogate_pairs"])
        self.assertEqual(res["char_count"], 1)
        self.assertEqual(res["utf16_units"], 2)
        self.assertEqual(res["weighted_units"], 2)
        self.assertEqual(res["segments"], 1)

    def test_arabic_with_extended_forces_ucs2(self):
        # When Arabic and extension characters mix, UCS-2 takes precedence
        mixed = "تخفيض [50%]"
        res = analyze_sms_text(mixed)
        self.assertEqual(res["encoding"], "UCS-2")
        self.assertTrue(res["has_arabic"])

if __name__ == "__main__":
    unittest.main()
