# ✈️ Boeing 767 — Altimetry System Test App
**TASK 34-11-00-730-816-001 | AD-B767-34-A2383 PART2 | LAN ALL**

---

## What this app does
Fills the altimetry test tables (Figures 57 / 58 / 59 / 60 from the JIC) automatically.
You paste the raw value from your ARINC 429 bus analyzer and it:
1. Converts binary or hex → decimal → pressure (mb or inHg)
2. Calculates the differential pressure (Col A − Col B, Col E − Col F)
3. Shows PASS / FAIL against the tolerance
4. Exports a filled Excel sheet for your records

---

## How to run locally

```bash
# 1. Install dependencies (once)
pip install -r requirements.txt

# 2. Run the app
streamlit run altimetry_test_app.py
```
The browser will open automatically at http://localhost:8501

---

## How to share (free, no server needed)

1. Create a free account at https://share.streamlit.io
2. Push this folder to a GitHub repository
3. Click "New app" → connect your repo → deploy

Everyone on the team can use the link from any browser/phone.

---

## Conversion formulas used

### Label 242 / 246  (standard ADC)
- Data bits: 28 → 13  (16 bits)
- `pressure_mb   = decimal × 0.03125`
- `pressure_inHg = decimal × 0.0009228`

### Label 354  (ADC 4040800-901/902/904/905/906/912/914)
- Data bits: 28 → 11  (18 bits)
- `pressure_inHg = decimal × 0.0002441368`
- `pressure_mb   = decimal × 0.008266`

---

## Input format examples

| Format | Label 242 example (= 1013 mb) |
|--------|-------------------------------|
| Binary (16 bits 28→13) | `0111111010100000` |
| Hexadecimal (4 digits) | `7EA0` |
| Decimal                | `32416` |

---

*Boeing 767 AMM Rev 147 — 22 Dec 2025 | ECCN 9E991 Boeing PROPRIETARY*
