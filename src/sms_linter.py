"""
SMS Character Encoding & Multi-Part Concatenation Calculator
Implements standard 3GPP TS 23.038 / GSM 03.38 character set rules:
- GSM 7-bit basic alphabet detection
- GSM 7-bit extension characters (| ^ € { } [ ] ~ \\) requiring 2 septets (escaped)
- UCS-2 encoding fallback for Arabic, Cyrillic, or supplementary characters (e.g. emojis)
- UTF-16 surrogate pair detection for code points outside Basic Multilingual Plane (U+FFFF)
- Multi-part message concatenation segmentation (153 units for GSM-7, 67 units for UCS-2)
- Transparent cost calculation based strictly on user-supplied per-segment rate
"""
import math
import json
import argparse
from typing import Dict, Any

# Standard 7-bit GSM 03.38 Basic Character Set
GSM_BASIC = set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&\'()*+,-./0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà"
)

# GSM 03.38 Extension Table Characters (Each counts as 2 characters due to 0x1B escape)
GSM_EXTENDED = set(["|", "^", "€", "{", "}", "[", "]", "~", "\\"])

def count_utf16_units(text: str) -> int:
    """
    Computes exact UTF-16 code units (16-bit half-words).
    BMP characters (<= U+FFFF) take 1 code unit.
    Supplementary characters (> U+FFFF, such as emojis) require surrogate pairs (2 code units).
    Matches len(text.encode('utf-16-be')) // 2 and JavaScript String.prototype.length.
    """
    return len(text.encode("utf-16-be")) // 2

def analyze_sms_text(text: str, cost_per_segment: float = 0.05, currency: str = "USD") -> Dict[str, Any]:
    if not text:
        return {
            "text": "",
            "char_count": 0,
            "utf16_units": 0,
            "weighted_units": 0,
            "encoding": "GSM-7",
            "segments": 0,
            "total_cost": 0.0,
            "currency": currency,
            "has_arabic": False,
            "has_surrogate_pairs": False,
            "extension_chars_count": 0,
            "max_segment_limit": 160,
            "units_remaining_in_last_segment": 0,
            "cost_per_segment": cost_per_segment
        }
        
    has_non_gsm = False
    has_arabic = False
    has_surrogate_pairs = False
    extension_chars_count = 0
    weighted_gsm_length = 0
    
    for c in text:
        code_point = ord(c)
        if code_point > 0xFFFF:
            has_surrogate_pairs = True
            has_non_gsm = True
        elif "\u0600" <= c <= "\u06FF" or "\u0750" <= c <= "\u077F":
            has_arabic = True
            has_non_gsm = True
        elif c in GSM_EXTENDED:
            extension_chars_count += 1
            weighted_gsm_length += 2  # Counts as 2 units in GSM-7
        elif c in GSM_BASIC:
            weighted_gsm_length += 1
        else:
            has_non_gsm = True
            
    char_len = len(text)
    utf16_units = count_utf16_units(text)
    
    if has_non_gsm:
        encoding = "UCS-2"
        # In UCS-2 / UTF-16 SMS transmission, limits are measured in 16-bit code units
        # Single message: 70 code units. Concatenated: 67 code units per segment.
        if utf16_units <= 70:
            segments = 1 if utf16_units > 0 else 0
            max_in_segment = 70
        else:
            segments = math.ceil(utf16_units / 67)
            max_in_segment = 67
        effective_units = utf16_units
    else:
        encoding = "GSM-7"
        if weighted_gsm_length <= 160:
            segments = 1 if weighted_gsm_length > 0 else 0
            max_in_segment = 160
        else:
            segments = math.ceil(weighted_gsm_length / 153)
            max_in_segment = 153
        effective_units = weighted_gsm_length
        
    total_cost = round(segments * cost_per_segment, 4)
    remaining_in_last = (segments * max_in_segment) - effective_units if segments > 0 else 0
    
    return {
        "text": text,
        "char_count": char_len,
        "utf16_units": utf16_units,
        "weighted_units": effective_units,
        "encoding": encoding,
        "has_arabic": has_arabic,
        "has_surrogate_pairs": has_surrogate_pairs,
        "extension_chars_count": extension_chars_count,
        "segments": segments,
        "max_segment_limit": max_in_segment,
        "units_remaining_in_last_segment": remaining_in_last,
        "cost_per_segment": cost_per_segment,
        "currency": currency,
        "total_cost": total_cost
    }

def main():
    parser = argparse.ArgumentParser(description="SMS Character & Concatenation Calculator")
    parser.add_argument("--text", help="Message text to analyze")
    parser.add_argument("--rate", type=float, default=0.05, help="Cost per segment (user-defined)")
    parser.add_argument("--currency", default="USD", help="Currency code")
    args = parser.parse_args()
    
    sample_text = args.text or "عزيزي العميل، تم تجهيز طلبك رقم 123 بنجاح وسيصلك غداً 🚀."
    res = analyze_sms_text(sample_text, cost_per_segment=args.rate, currency=args.currency)
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
