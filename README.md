# SMS Character Concatenation & Cost Optimization Calculator

> Stop getting billed triple for marketing SMS. Detect non-GSM Unicode characters and calculate exact SMS segments instantly.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Format: STATIC_INTERACTIVE_TOOL](https://img.shields.io/badge/Format-STATIC--INTERACTIVE--TOOL-green.svg)](#)
[![Tier: 2](https://img.shields.io/badge/Tier-2-orange.svg)](#)
[![Region: MENA](https://img.shields.io/badge/Region-Egypt%20%7C%20GCC%20%7C%20Saudi-purple.svg)](#)
[![Tests: Passing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#)
[![Owner: mahmoudabdelnaby1](https://img.shields.io/badge/Owner-mahmoudabdelnaby1-blue.svg)](https://github.com/mahmoudabdelnaby1)

---

## 📌 Problem Statement & Target Persona

### Target Persona
**BOTH** operating in high-growth e-commerce, digital publishing, and direct-response marketing across Saudi Arabia, UAE, and Egypt.

### Core Problem
Build an open-source SMS character and encoding cost calculator: 1) Single-file responsive HTML/JS tool (`sms_calculator.html`) with real-time character counter, GSM-7 vs UCS-2 encoding detection, segment count split (160/153 vs 70/67), and highlighting of offending non-GSM characters, 2) Python CLI script (`sms_linter.py`) for automated batch testing, 3) Cost estimation worksheet.

---

## 🛠️ Repository Architecture & Deliverables

This repository provides self-contained, documented implementations and specifications:

- `docs/gsm7-vs-ucs2-explanation.md`
- `examples/cost_overage_scenarios.json`
- `index.html`
- `LICENSE`
- `README.md`
- `src/sms_calculator.py`
- `src/sms_linter.py`
- `tests/test_calculator.py`
- `tests/test_linter.py`
- `tools/sms_calculator.html`


---

## 🚀 Quick Start & How to Run Locally

### Run Test Suite Locally
```bash
# Ensure no bytecode generation
export PYTHONDONTWRITEBYTECODE=1  # Linux / macOS
$env:PYTHONDONTWRITEBYTECODE="1"  # Windows PowerShell

# Run Python unittest discovery
python -m unittest discover -s tests
```

### Run CLI Script
```bash
# Analyze SMS message with custom unit rate and currency
python src/sms_calculator.py --text "عزيزي العميل، تم تجهيز طلبك رقم 123 بنجاح وسيصلك غداً." --rate 0.15 --currency SAR

# Or run the batch linter directly
python src/sms_linter.py --help
```

### Interactive Browser Tool
Open `index.html` (or `tools/sms_calculator.html`) directly in your web browser (Chrome, Edge, Safari) to use the local interactive calculator. Operates 100% client-side with zero external network calls.

---

## 📊 Sample Input & Output Fixtures

> **Data Disclosure:** Any included sample data is illustrative and may be synthetic; it is not a measured customer result or market benchmark unless a source and collection method are stated alongside it. These files run offline with standard libraries and require no paid third-party API credentials.

```json
{
  "text": "عزيزي العميل، تم تجهيز طلبك رقم 123 بنجاح وسيصلك غداً 🚀.",
  "char_count": 57,
  "utf16_units": 58,
  "weighted_units": 58,
  "encoding": "UCS-2",
  "has_arabic": true,
  "has_surrogate_pairs": true,
  "extension_chars_count": 0,
  "segments": 1,
  "max_segment_limit": 70,
  "units_remaining_in_last_segment": 12,
  "cost_per_segment": 0.15,
  "currency": "SAR",
  "total_cost": 0.15
}
```

---

## ⚠️ Known Technical & Domain Constraints

- **3GPP GSM 03.38 Concatenation:** Single GSM-7 messages allow up to 160 characters. Concatenated multi-part messages require a 7-byte UDH header, reducing payload capacity to 153 characters per segment.
- **UCS-2 Arabic Multi-Part Limits:** Single Arabic messages allow up to 70 characters. Concatenated messages reduce payload capacity to 67 characters per segment.
- **Unicode Supplementary Plane & Surrogate Pairs:** Characters outside the Basic Multilingual Plane (> U+FFFF, such as emojis 🚀, 🎉) require 2 UTF-16 code units (surrogate pair) in UCS-2 transmission, consuming 2 units towards the 70 / 67 segment limit.
- **Escape Character Double-Weighting:** GSM 03.38 extension characters (| ^ € { } [ ] ~ \) require an escape octet (0x1B), consuming 2 characters from the segment limit.
- **Dynamic Pricing Reliance:** Carrier SMS costs vary across Saudi Arabia, UAE, and Egypt; calculation relies strictly on the user-provided per-segment unit rate.

---

## 📚 Primary Documentation & Verifiable References

- [3GPP TS 23.038 Specification](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=750) - Official alphabets and language-specific information (GSM 7-bit default alphabet and UCS-2).
- [Unicode Standard - Arabic Script Technical Notes](https://www.unicode.org/charts/PDF/U0600.pdf) - Character mappings and Unicode encoding specifications.
- [Twilio Technical Guide: SMS Character Limits and Concatenation](https://help.twilio.com/articles/223133267) - Standard carrier concatenation and escape character segmentation rules.

---


## 👤 Maintainer & License

- **Author & Maintainer:** [Mahmoud Abdelnaby](https://github.com/mahmoudabdelnaby1) (`@mahmoudabdelnaby1`)
- **License:** [MIT License](LICENSE) - Open-source, auditable, and freely adaptable for internal enterprise or commercial use.
