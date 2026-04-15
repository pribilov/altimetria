"""
Boeing 767 — Altimetry System Test  (LATAM / LAN)
TASK 34-11-00-730-816-001  |  AD-B767-34-A2383 PART2

USAGE
-----
  pip install streamlit pandas openpyxl
  streamlit run altimetry_test_app.py

Or deploy for free at https://share.streamlit.io
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="767 Altimetry Test",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .pass  { background:#d4edda; color:#155724; padding:6px 14px;
           border-radius:5px; font-weight:bold; text-align:center; }
  .fail  { background:#f8d7da; color:#721c24; padding:6px 14px;
           border-radius:5px; font-weight:bold; text-align:center; }
  .pend  { background:#fff3cd; color:#856404; padding:6px 14px;
           border-radius:5px; font-weight:bold; text-align:center; }
  .sect  { font-size:1.05rem; font-weight:600; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR  — configuration
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    side = st.radio(
        "ADC Position",
        ["CAPT  (Left – L ADC)", "F/O  (Right – R ADC)"],
        help="Select which Air Data Computer is being tested.",
    )

    unit = st.radio(
        "Measurement Units",
        ["inHg  (Inches of Mercury)", "mb  (Millibars)"],
    )

    fmt = st.radio(
        "ARINC Bus Analyzer output",
        ["Binary  (bits 28 → 13)", "Hexadecimal  (4 hex digits)", "Decimal"],
        help=(
            "Choose the format your bus analyzer displays.\n\n"
            "Binary = 16 bits (28 down to 13).\n"
            "Hex = 4-digit hex value of those same 16 bits.\n"
            "Decimal = the decimal integer directly."
        ),
    )

    st.markdown("---")
    use_354 = st.checkbox(
        "Static label = **354** instead of 246",
        value=False,
        help=(
            "For ADC models:\n"
            "4040800-901 / -902 / -904 / -905 / -906 / -912 / -914\n\n"
            "Label 354 uses bits 28→11 (18 bits).\n"
            "Default is Label 246 (bits 28→13, 16 bits)."
        ),
    )

    st.markdown("---")
    st.markdown("### 📝 ADC Info  *(Step B.2)*")
    adc_pn    = st.text_input("Part Number (P/N)", placeholder="e.g. 4040800-905")
    adc_sn    = st.text_input("Serial Number (S/N)", placeholder="e.g. SN12345")
    aircraft  = st.text_input("Aircraft Reg.", placeholder="e.g. CC-CXJ")
    test_date = st.date_input("Test Date", value=date.today())
    option_n  = st.text_input("Test Setup Option", placeholder="OPTION 1 or OPTION 2")


# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS derived from sidebar
# ──────────────────────────────────────────────────────────────────────────────
is_capt = "CAPT" in side
is_inhg = "inHg" in unit
is_bin  = "Binary"  in fmt
is_hex  = "Hexadec" in fmt

# Test-point target pressures & tolerances
if is_inhg:
    TEST_PTS   = [29.917, 13.584, 5.611, 13.584, 29.917]
    TP_TOL     = 0.029   # ± tolerance on the input static pressure
    TOL_PITOT  = 0.029
    TOL_STATIC = 0.018
    UNIT_S     = "inHg"
    FMT_V      = ".4f"   # for f-strings
    FMT_NI     = "%.4f"  # for number_input
    # Label 242/246 → inHg
    CF_242_246 = 0.0009228
    # Label 354  → inHg
    CF_354     = 0.0002441368
else:
    TEST_PTS   = [1013.0, 460.0, 190.0, 460.0, 1013.0]
    TP_TOL     = 1.0
    TOL_PITOT  = 1.0
    TOL_STATIC = 0.6
    UNIT_S     = "mb"
    FMT_V      = ".2f"
    FMT_NI     = "%.2f"
    CF_242_246 = 0.03125
    CF_354     = 0.008266

# Static label
if use_354:
    CF_STATIC     = CF_354
    STATIC_LABEL  = "Label 354"
    STATIC_BITS   = 18
else:
    CF_STATIC     = CF_242_246
    STATIC_LABEL  = "Label 246"
    STATIC_BITS   = 16

# Figure reference
FIG_MAP = {
    (True,  True ): "Figure 57",
    (True,  False): "Figure 58",
    (False, True ): "Figure 59",
    (False, False): "Figure 60",
}
FIG_REF  = FIG_MAP[(is_capt, is_inhg)]
ADC_NAME = "Left ADC"  if is_capt else "Right ADC"
ADC_POS  = "CAPT"      if is_capt else "F/O"

# Placeholder text for ARINC input fields
if is_bin:
    PH_242  = "16 bits  e.g. 0111111010100000"
    PH_STAT = ("18 bits  e.g. 011111101010000000"
               if use_354 else "16 bits  e.g. 0111111010100000")
elif is_hex:
    PH_242  = "4 hex digits  e.g. 7EA0"
    PH_STAT = "5 hex digits (18-bit)" if use_354 else "4 hex digits  e.g. 7EA0"
else:
    PH_242  = "decimal  e.g. 32416"
    PH_STAT = "decimal  e.g. 32416"


# ──────────────────────────────────────────────────────────────────────────────
# CONVERSION HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def _binary_to_pressure(raw: str, n_bits: int, factor: float):
    bits = raw.replace(" ", "").replace("_", "")
    if not all(c in "01" for c in bits):
        return None, None, "❗ Only 0 and 1 allowed in binary input"
    if len(bits) != n_bits:
        return None, None, f"❗ Expected {n_bits} bits, got {len(bits)}"
    dec = int(bits, 2)
    return dec, dec * factor, None


def _hex_to_pressure(raw: str, factor: float):
    h = raw.strip().upper().replace("0X", "").replace(" ", "")
    if not all(c in "0123456789ABCDEF" for c in h) or len(h) == 0:
        return None, None, "❗ Invalid hexadecimal value"
    dec = int(h, 16)
    return dec, dec * factor, None


def _dec_to_pressure(raw: str, factor: float):
    try:
        dec = int(float(raw.strip()))
        return dec, dec * factor, None
    except Exception:
        return None, None, "❗ Invalid decimal value"


def convert(raw: str, n_bits: int, factor: float):
    """Return (decimal, pressure, error_msg).  error_msg is None on success."""
    if not raw or not raw.strip():
        return None, None, None   # empty → pending
    if is_bin:
        return _binary_to_pressure(raw, n_bits, factor)
    elif is_hex:
        return _hex_to_pressure(raw, factor)
    else:
        return _dec_to_pressure(raw, factor)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.title("✈️  Boeing 767 — Altimetry System Test")
st.markdown(
    f"**TASK 34-11-00-730-816-001** &nbsp;|&nbsp; **{FIG_REF}** &nbsp;|&nbsp; "
    f"**{ADC_NAME}** &nbsp;|&nbsp; **{UNIT_S}** &nbsp;|&nbsp; "
    f"P/N: `{adc_pn or '—'}` &nbsp; S/N: `{adc_sn or '—'}` &nbsp; "
    f"A/C: `{aircraft or '—'}` &nbsp; Date: `{test_date}` &nbsp; "
    f"Setup: `{option_n or '—'}`"
)
st.caption(
    f"Pitot tolerance (Label 242): **±{TOL_PITOT} {UNIT_S}** &nbsp;|&nbsp; "
    f"Static tolerance ({STATIC_LABEL}): **±{TOL_STATIC} {UNIT_S}** &nbsp;|&nbsp; "
    f"Static label: **{STATIC_LABEL}**  ({STATIC_BITS} bits)"
)
st.divider()


# ──────────────────────────────────────────────────────────────────────────────
# TEST-POINT DATA ENTRY
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📋 Test Data Entry")

summary_rows = []   # will be used for summary table & export

for i, tp in enumerate(TEST_PTS):
    tp_n = i + 1

    with st.expander(
        f"**Test Point {tp_n}**  —  Static pressure: **{tp} ± {TP_TOL} {UNIT_S}**",
        expanded=True,
    ):
        # ── 4 columns: pitot input | static input | pitot result | static result
        c_inp_pit, c_inp_sta, c_res_pit, c_res_sta = st.columns([2.3, 2.3, 1.7, 1.7])

        # ── PITOT INPUT (Label 242) ─────────────────────────────────────────
        with c_inp_pit:
            st.markdown('<p class="sect">🔵 Total (Pitot) — Label 242</p>',
                        unsafe_allow_html=True)
            dps_a = st.number_input(
                f"DPS Static Output  Col A  ({UNIT_S})",
                key=f"a_{i}",
                value=float(tp),
                step=0.001 if is_inhg else 0.1,
                format=FMT_NI,
                help="Value read directly from the Air Data Test Set (COM-1914).",
            )
            raw_242 = st.text_input(
                "Label 242  (ARINC raw)",
                key=f"r242_{i}",
                placeholder=PH_242,
                help="Value shown on the ARINC 429 bus analyzer for Label 242.",
            )

        # ── STATIC INPUT ────────────────────────────────────────────────────
        with c_inp_sta:
            st.markdown(f'<p class="sect">🟢 Static Pressure — {STATIC_LABEL}</p>',
                        unsafe_allow_html=True)
            dps_e = st.number_input(
                f"DPS Static Output  Col E  ({UNIT_S})",
                key=f"e_{i}",
                value=float(tp),
                step=0.001 if is_inhg else 0.1,
                format=FMT_NI,
                help="Value read directly from the Air Data Test Set (COM-1914).",
            )
            raw_st = st.text_input(
                f"{STATIC_LABEL}  (ARINC raw)",
                key=f"rst_{i}",
                placeholder=PH_STAT,
                help=f"Value shown on the ARINC 429 bus analyzer for {STATIC_LABEL}.",
            )

        # ── CONVERSIONS ─────────────────────────────────────────────────────
        dec_242, p_242, err_242 = convert(raw_242, 16,           CF_242_246)
        dec_st,  p_st,  err_st  = convert(raw_st,  STATIC_BITS,  CF_STATIC)

        diff_pit = (dps_a - p_242) if p_242 is not None else None
        diff_sta = (dps_e - p_st)  if p_st  is not None else None

        ok_pit = (abs(diff_pit) <= TOL_PITOT)  if diff_pit is not None else None
        ok_sta = (abs(diff_sta) <= TOL_STATIC) if diff_sta is not None else None

        # ── RESULT DISPLAY helper ────────────────────────────────────────────
        def show_result(col, title, dec_v, press_v, diff_v, tol, ok, err):
            with col:
                st.markdown(f'<p class="sect">{title}</p>', unsafe_allow_html=True)
                if err:
                    st.error(err)
                elif press_v is not None:
                    st.write(f"**Decimal:** `{dec_v}`")
                    st.write(f"**Converted:** `{press_v:{FMT_V}}` {UNIT_S}")
                    diff_color = "🔴" if not ok else "🟢"
                    st.write(f"**Diff:** {diff_color} `{diff_v:+{FMT_V}}` {UNIT_S}")
                    st.write(f"**Tolerance:** `±{tol}` {UNIT_S}")
                    if ok:
                        st.markdown('<div class="pass">✅  PASS</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="fail">❌  FAIL</div>',
                                    unsafe_allow_html=True)
                else:
                    st.markdown('<div class="pend">— pending —</div>',
                                unsafe_allow_html=True)

        show_result(c_res_pit, "Label 242 → Result",
                    dec_242, p_242, diff_pit, TOL_PITOT, ok_pit, err_242)
        show_result(c_res_sta, f"{STATIC_LABEL} → Result",
                    dec_st,  p_st,  diff_sta, TOL_STATIC, ok_sta, err_st)

        # ── Collect row for summary table ────────────────────────────────────
        def _fmt(v):
            return f"{v:{FMT_V}}" if v is not None else "—"

        def _verdict(ok_val):
            if ok_val is True:  return "✅ PASS"
            if ok_val is False: return "❌ FAIL"
            return "⏳"

        summary_rows.append({
            "TP": tp_n,
            f"Target ({UNIT_S})": f"{tp:{FMT_V}}",
            "Label-242 raw":      raw_242 or "—",
            "L-242 decimal":      dec_242 if dec_242 is not None else "—",
            f"Col A ({UNIT_S})":  _fmt(dps_a),
            f"Col B ({UNIT_S})":  _fmt(p_242),
            f"Diff A−B":          (f"{diff_pit:+{FMT_V}}" if diff_pit is not None else "—"),
            f"±{TOL_PITOT}":      _verdict(ok_pit),
            f"{STATIC_LABEL} raw": raw_st or "—",
            f"{STATIC_LABEL} decimal": dec_st if dec_st is not None else "—",
            f"Col E ({UNIT_S})":  _fmt(dps_e),
            f"Col F ({UNIT_S})":  _fmt(p_st),
            f"Diff E−F":          (f"{diff_sta:+{FMT_V}}" if diff_sta is not None else "—"),
            f"±{TOL_STATIC}":     _verdict(ok_sta),
        })


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY TABLE
# ──────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📑 Test Summary")

df_summary = pd.DataFrame(summary_rows)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

# Overall verdict
pit_col = f"±{TOL_PITOT}"
sta_col = f"±{TOL_STATIC}"
all_vals = [r[pit_col] for r in summary_rows] + [r[sta_col] for r in summary_rows]

if "⏳" in all_vals:
    st.warning("⏳  Test incomplete — enter ARINC values for all test points.")
elif all(v == "✅ PASS" for v in all_vals):
    st.success(
        f"🎉  **OVERALL RESULT: PASS** — "
        f"{ADC_NAME} ({ADC_POS} ADC) P/N {adc_pn or '—'} S/N {adc_sn or '—'} is serviceable."
    )
else:
    st.error(
        "❌  **OVERALL RESULT: FAIL** — "
        "One or more test points are out of tolerance. "
        "Replace ADC per AMM 34-12-01/401 and repeat the test."
    )


# ──────────────────────────────────────────────────────────────────────────────
# EXPORT
# ──────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📥 Export")

# Build export dataframe with header info
export_hdr = {
    "Aircraft": aircraft,
    "Date": str(test_date),
    "ADC P/N": adc_pn,
    "ADC S/N": adc_sn,
    "ADC Position": ADC_POS,
    "Table": FIG_REF,
    "Units": UNIT_S,
    "Test Setup": option_n,
    "Static Label": STATIC_LABEL,
}
export_rows = [{**export_hdr, **r} for r in summary_rows]
df_export = pd.DataFrame(export_rows)

# Attempt Excel first, fall back to CSV
try:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False,
                           sheet_name=f"AltTest_{FIG_REF.replace(' ', '_')}")
    fname = (
        f"AltimetryTest_{aircraft or 'AC'}_{adc_pn or 'ADC'}_"
        f"{ADC_POS}_{UNIT_S}_{test_date}.xlsx"
    )
    st.download_button(
        "📊 Download Excel (.xlsx)",
        data=out.getvalue(),
        file_name=fname,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except ImportError:
    csv_data = df_export.to_csv(index=False)
    fname = (
        f"AltimetryTest_{aircraft or 'AC'}_{adc_pn or 'ADC'}_"
        f"{ADC_POS}_{UNIT_S}_{test_date}.csv"
    )
    st.download_button(
        "📄 Download CSV",
        data=csv_data,
        file_name=fname,
        mime="text/csv",
    )


# ──────────────────────────────────────────────────────────────────────────────
# CONVERSION REFERENCE  (collapsible)
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("📚 Conversion Reference  (Figure 213 / Appendix A)"):
    st.markdown("""
    ### Label 242 / 246  — standard ADC
    **Data bits:** 28 → 13  (16 bits, bit-28 = MSB, bit-13 = LSB)

    | Decimal | Factor | Result |
    |---------|--------|--------|
    | 32 416 | × 0.03125   | **1 013 mb**   |
    | 14 720 | × 0.03125   | **460 mb**     |
    | 6 080  | × 0.03125   | **190 mb**     |
    | 32 416 | × 0.0009228 | **29.9135 inHg** |
    | 14 720 | × 0.0009228 | **13.5836 inHg** |
    | 6 080  | × 0.0009228 | **5.6106 inHg**  |

    ```
    pressure_mb   = decimal × 0.03125
    pressure_inHg = decimal × 0.0009228
    ```

    ---
    ### Label 354  — ADC models -901/-902/-904/-905/-906/-912/-914
    **Data bits:** 28 → 11  (18 bits, bit-28 = MSB, bit-11 = LSB)

    | Decimal | Factor        | Result |
    |---------|---------------|--------|
    | 122 624 | × 0.0002441368 | **29.937 inHg** |
    | 55 640  | × 0.0002441368 | **13.5838 inHg** |
    | 22 976  | × 0.0002441368 | **5.6093 inHg**  |
    | 122 624 | × 0.008266     | **1 013.7 mb**   |
    | 55 640  | × 0.008266     | **459.9 mb**     |
    | 22 976  | × 0.008266     | **189.9 mb**     |

    ```
    pressure_inHg = decimal × 0.0002441368
    pressure_mb   = decimal × 0.008266
    ```

    ---
    ### Binary → Decimal quick reminder
    Input bits 28 down to 13 as a 16-digit binary string.  
    Example: `0111 1110 1010 0000` → 32 416 → × 0.03125 = **1 013 mb**

    ### Hex → Decimal quick reminder
    `7EA0` (hex) = 32 416 (decimal) → × 0.03125 = **1 013 mb**
    """)

st.divider()
st.caption(
    "Boeing 767 AMM Rev 147 — 22 Dec 2025  |  "
    "ECCN 9E991 Boeing PROPRIETARY  |  "
    "TASK 34-11-00-730-816-001  LAN ALL"
)
