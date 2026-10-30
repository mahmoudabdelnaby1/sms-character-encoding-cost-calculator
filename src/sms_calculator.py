#!/usr/bin/env python3
"""
SMS Character Encoding & Multi-Part Cost Calculator
Unified module supporting both CLI execution and programmatic analysis.
Implements 3GPP TS 23.038 / GSM 03.38 standard and UCS-2 / UTF-16 concatenation rules.
Calculates cost strictly from user-supplied per-segment rate.
Accurately accounts for surrogate pairs (2 units per emoji > U+FFFF).
"""
import sys
import argparse
import json
from pathlib import Path

# Ensure repo root and src are importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    from src.sms_linter import analyze_sms_text, count_utf16_units, GSM_BASIC, GSM_EXTENDED
except ImportError:
    from sms_linter import analyze_sms_text, count_utf16_units, GSM_BASIC, GSM_EXTENDED

def calculate_sms_segments(text: str, cost_per_segment: float = 0.05, currency: str = "USD"):
    """
    Programmatic helper for calculating SMS encoding and concatenation segments.
    Cost is calculated dynamically based on user-supplied cost_per_segment.
    Returns exact character count and UTF-16 code units for supplementary characters/emojis.
    """
    return analyze_sms_text(text, cost_per_segment=cost_per_segment, currency=currency)

def main():
    parser = argparse.ArgumentParser(description="SMS Character & Concatenation Calculator")
    parser.add_argument("--text", help="Message text to analyze")
    parser.add_argument("--rate", type=float, default=0.05, help="Cost per segment (user-defined)")
    parser.add_argument("--currency", default="USD", help="Currency code (e.g. USD, SAR, EGP)")
    args = parser.parse_args()
    
    sample_text = args.text or "عزيزي العميل، تم تجهيز طلبك رقم 123 بنجاح وسيصلك غداً 🚀."
    res = analyze_sms_text(sample_text, cost_per_segment=args.rate, currency=args.currency)
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
