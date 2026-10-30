"""
Unit tests for SMS Character & Encoding Calculator (Unified src.sms_calculator)
Including rigorous UTF-16 surrogate pair verification for emojis (> U+FFFF).
"""
import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.sms_calculator import calculate_sms_segments
from src.sms_linter import analyze_sms_text, count_utf16_units

class TestSMSCalculatorUnified(unittest.TestCase):
    def test_gsm_basic_single_part(self):
        text = "Hello, your order is ready for pickup."
        res = calculate_sms_segments(text, cost_per_segment=0.10, currency="USD")
        self.assertEqual(res["encoding"], "GSM-7")
        self.assertEqual(res["segments"], 1)
        self.assertEqual(res["extension_chars_count"], 0)
        self.assertEqual(res["total_cost"], 0.10)
        self.assertEqual(res["currency"], "USD")

    def test_gsm_extended_characters_weight(self):
        # The characters '[' and ']' are extended characters, each weighted as 2
        text = "Order [123]"
        res = calculate_sms_segments(text, cost_per_segment=0.05)
        self.assertEqual(res["encoding"], "GSM-7")
        self.assertEqual(res["extension_chars_count"], 2)
        # raw len is 11, weighted is 11 + 2 = 13
        self.assertEqual(res["weighted_units"], 13)

    def test_arabic_triggers_ucs2_and_segmentation(self):
        # Arabic characters are in BMP (<= U+FFFF) so each takes 1 UTF-16 unit
        text = "مرحباً"
        res = calculate_sms_segments(text, cost_per_segment=0.20, currency="SAR")
        self.assertEqual(res["encoding"], "UCS-2")
        self.assertTrue(res["has_arabic"])
        self.assertFalse(res["has_surrogate_pairs"])
        self.assertEqual(res["char_count"], 6)
        self.assertEqual(res["utf16_units"], 6)
        self.assertEqual(res["segments"], 1)
        self.assertEqual(res["total_cost"], 0.20)

    def test_emoji_surrogate_pair_units(self):
        # Emojis outside Basic Multilingual Plane (> U+FFFF) require 2 UTF-16 code units (surrogate pair)
        # '🚀' (U+1F680) is 1 Unicode character, but 2 UTF-16 units (4 bytes)
        emoji_text = "🚀"
        res = calculate_sms_segments(emoji_text, cost_per_segment=0.05, currency="USD")
        self.assertEqual(res["encoding"], "UCS-2")
        self.assertTrue(res["has_surrogate_pairs"])
        self.assertEqual(res["char_count"], 1)
        self.assertEqual(res["utf16_units"], 2)
        self.assertEqual(res["weighted_units"], 2)
        self.assertEqual(res["segments"], 1)
        self.assertEqual(res["units_remaining_in_last_segment"], 68)

    def test_emoji_segmentation_boundaries(self):
        # 35 emojis = 35 chars, 35 * 2 = 70 UTF-16 units -> exactly fills single UCS-2 message
        text_35_emojis = "🚀" * 35
        res_35 = calculate_sms_segments(text_35_emojis, cost_per_segment=0.10)
        self.assertEqual(res_35["char_count"], 35)
        self.assertEqual(res_35["utf16_units"], 70)
        self.assertEqual(res_35["segments"], 1)
        self.assertEqual(res_35["max_segment_limit"], 70)
        self.assertEqual(res_35["units_remaining_in_last_segment"], 0)

        # 36 emojis = 36 chars, 36 * 2 = 72 UTF-16 units -> exceeds 70 limit
        # Concatenated messages hold max 67 units per segment -> ceil(72 / 67) = 2 segments
        text_36_emojis = "🚀" * 36
        res_36 = calculate_sms_segments(text_36_emojis, cost_per_segment=0.10)
        self.assertEqual(res_36["char_count"], 36)
        self.assertEqual(res_36["utf16_units"], 72)
        self.assertEqual(res_36["segments"], 2)
        self.assertEqual(res_36["max_segment_limit"], 67)
        # 2 segments * 67 = 134 capacity; 134 - 72 = 62 remaining
        self.assertEqual(res_36["units_remaining_in_last_segment"], 62)
        self.assertEqual(res_36["total_cost"], 0.20)

    def test_mixed_arabic_and_emoji_units(self):
        # Arabic (1 unit each) + Space (1 unit) + Emoji (2 units)
        text = "عرض خاص 🚀"
        res = calculate_sms_segments(text, cost_per_segment=0.05)
        # 'عرض خاص ' = 8 characters (8 units) + '🚀' = 1 character (2 units) -> 9 chars, 10 units
        self.assertEqual(res["char_count"], 9)
        self.assertEqual(res["utf16_units"], 10)
        self.assertEqual(res["weighted_units"], 10)
        self.assertTrue(res["has_arabic"])
        self.assertTrue(res["has_surrogate_pairs"])

    def test_utf16_units_matches_standard_encoding(self):
        # Test count_utf16_units strictly equals len(text.encode('utf-16-be')) // 2
        samples = [
            "Hello World",
            "عزيزي العميل، تم تجهيز طلبك",
            "Flash Sale 🔥🎉🚀 Don't miss out!",
            "🇸🇦 🇪🇬 🇦🇪",
            "Code: [SAVE-50]"
        ]
        for s in samples:
            expected = len(s.encode("utf-16-be")) // 2
            self.assertEqual(count_utf16_units(s), expected, f"Failed for sample: {s}")

    def test_cost_calculation_uses_inputted_rate_not_fixed(self):
        text = "Standard test message"
        res1 = calculate_sms_segments(text, cost_per_segment=0.045, currency="USD")
        self.assertEqual(res1["total_cost"], 0.045)
        self.assertEqual(res1["currency"], "USD")

        res2 = calculate_sms_segments(text, cost_per_segment=0.12, currency="EGP")
        self.assertEqual(res2["total_cost"], 0.12)
        self.assertEqual(res2["currency"], "EGP")

    def test_sms_linter_and_calculator_parity(self):
        # Parity between sms_calculator and sms_linter across emojis, extended GSM, and Arabic
        test_strings = [
            "Order [12345] is ready | pickup now",
            "عروضنا مستمرة بمناسبة يوم التأسيس 🇸🇦",
            "Super Mega Deal! 🚀💥 Only 5 items left: https://shop.sa"
        ]
        for sample in test_strings:
            res_calc = calculate_sms_segments(sample, cost_per_segment=0.08, currency="USD")
            res_lint = analyze_sms_text(sample, cost_per_segment=0.08, currency="USD")
            self.assertEqual(res_calc, res_lint, f"Parity mismatch on string: {sample}")

if __name__ == "__main__":
    unittest.main()
