"""
Boeing 767 — Altimetry System Test  v4
TASK 34-11-00-730-816-001  |  AD-B767-34-A2383 PART2  |  LAN ALL

Correr:
    pip install streamlit pandas openpyxl
    streamlit run altimetry_test_app.py
"""
import math
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="767 Altimetry Test",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# NAVY BLUE CORPORATE THEME
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Background ── */
.stApp, .main { background-color:#0b1a2e !important; }
.block-container { padding-top:1.2rem !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color:#071220 !important;
    border-right:1px solid #1b3558;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color:#b8cfe0 !important; }
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color:#7ab8e0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color:#0e2540 !important;
    color:#93c5fd !important;
    border:1px solid #1b3558 !important;
    border-radius:8px !important;
    font-weight:600 !important;
}
.streamlit-expanderContent {
    background-color:#0d2035 !important;
    border:1px solid #1b3558 !important;
    border-top:none !important;
    border-radius:0 0 8px 8px !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background-color:#112847 !important;
    border-radius:8px;
    padding:10px 14px;
    border:1px solid #1e3d63;
}
div[data-testid="stMetricLabel"] > div { color:#7ab8e0 !important; font-size:0.76rem !important; }
div[data-testid="stMetricValue"] > div { color:#e8f4ff !important; font-size:1.05rem !important; font-weight:700 !important; }

/* ── Text inputs ── */
.stTextInput input, .stNumberInput input {
    background-color:#0f2540 !important;
    color:#e8f4ff !important;
    border:1px solid #2a5080 !important;
    border-radius:6px !important;
}
div[data-baseweb="select"] > div {
    background-color:#0f2540 !important;
    border-color:#2a5080 !important;
    color:#e8f4ff !important;
}
label { color:#8ab8d8 !important; font-size:0.82rem !important; }

/* ── Buttons ── */
.stDownloadButton button {
    background-color:#1a4a8e !important;
    color:#ffffff !important;
    border:1px solid #2a6abf !important;
    border-radius:6px !important;
    font-weight:600 !important;
    padding: 10px 24px !important;
}
.stDownloadButton button:hover { background-color:#2a5abf !important; }

/* ── Divider ── */
hr { border-color:#1b3558 !important; }

/* ── DataFrames ── */
div[data-testid="stDataFrame"] {
    border-radius:8px;
    overflow:hidden;
    border:1px solid #1b3558;
}

/* ── Global text ── */
p, span, div { color:#dde6f0; }
h1,h2,h3,h4 { color:#e8f4ff !important; }

/* ── Status badges ── */
.pass {
    background:#0d3320; color:#4ade80;
    padding:10px 20px; border-radius:7px;
    font-weight:700; text-align:center;
    border:1px solid #166534; font-size:1rem; margin-top:10px;
}
.fail {
    background:#3b0a0a; color:#f87171;
    padding:10px 20px; border-radius:7px;
    font-weight:700; text-align:center;
    border:1px solid #7f1d1d; font-size:1rem; margin-top:10px;
}
.pend {
    background:#1a1505; color:#fbbf24;
    padding:10px 20px; border-radius:7px;
    font-weight:700; text-align:center;
    border:1px solid #854d0e; font-size:0.88rem; margin-top:10px;
}
.overall-pass {
    background:linear-gradient(90deg,#064e3b,#065f46);
    color:#4ade80; padding:18px 28px; border-radius:10px;
    font-weight:700; text-align:center;
    border:1px solid #059669; font-size:1.15rem; margin-top:14px;
}
.overall-fail {
    background:linear-gradient(90deg,#450a0a,#7f1d1d);
    color:#fca5a5; padding:18px 28px; border-radius:10px;
    font-weight:700; text-align:center;
    border:1px solid #b91c1c; font-size:1.15rem; margin-top:14px;
}

/* ── Boxes ── */
.boxDPS {
    background:#0b2540; border-left:4px solid #3b82f6;
    padding:12px 14px; border-radius:0 6px 6px 0; margin-bottom:10px;
}
.boxARINC {
    background:#0b2d1a; border-left:4px solid #22c55e;
    padding:12px 14px; border-radius:0 6px 6px 0; margin-bottom:10px;
}
.convbox {
    background:#081828; border:1px solid #1b3558;
    border-radius:8px; padding:12px 14px; margin-top:8px;
}
.sect { color:#7ab8e0; font-size:0.9rem; font-weight:600; margin:0 0 4px 0; }
.ft-ref { color:#64748b; font-size:0.8rem; font-style:italic; margin-top:6px; }

/* ── Title bar ── */
.titlebar {
    background:linear-gradient(90deg,#0a2d5e,#1a4a8e);
    padding:18px 26px; border-radius:10px; margin-bottom:18px;
    border:1px solid #2a5a9e;
}
.titlebar h2 { color:#ffffff !important; margin:0 0 6px 0; font-size:1.45rem; }
.titlebar p  { color:#93c5fd !important; margin:0; font-size:0.88rem; }

/* ── Section title (summary) ── */
.sec-title {
    color:#7ab8e0; font-weight:700; font-size:0.92rem;
    letter-spacing:0.04em; margin-bottom:6px;
    text-transform:uppercase;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
MB_TO_INHG  = 1.0 / 33.8639    # 1 mb = 0.029530 inHg
INHG_TO_MB  = 33.8639

# Label 242 / 246  (bits 28→13, 16 bits)
CF_242_MB   = 0.03125
CF_242_INHG = 0.0009228

# Label 354  (bits 28→11, 18 bits)
CF_354_MB   = 0.008266
CF_354_INHG = 0.0002441368


# ─────────────────────────────────────────────────────────────────────────────
# ISA ALTITUDE
# ─────────────────────────────────────────────────────────────────────────────
def mb_to_ft_isa(p_mb: float) -> float:
    """Standard atmosphere ISA: mb → ft"""
    p_pa   = p_mb * 100.0
    p0     = 101325.0
    T0     = 288.15
    L      = 0.0065
    p_trop = 22632.1   # Pa at 11 000 m tropopause
    if p_pa >= p_trop:
        exp_v = 0.190263          # R·L / (g·M)
        h_m = (T0 / L) * (1.0 - (p_pa / p0) ** exp_v)
    else:
        h_m = 11000.0 + math.log(p_trop / p_pa) / 0.0001576883
    return h_m * 3.28084


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSION ENGINE
# ─────────────────────────────────────────────────────────────────────────────
FMT_OPTIONS = [
    "Hex — palabra ARINC completa (6-8 dígitos)",
    "Hex — campo datos (4 dígitos)",
    "Binario",
    "mb directo",
    "inHg directo",
]

PLACEHOLDERS = {
    "Hex — palabra ARINC completa (6-8 dígitos)": "ej: E7EA36  →  1013 mb",
    "Hex — campo datos (4 dígitos)":              "ej: 7EA0  →  1013 mb",
    "Binario":                                    "ej: 0111111010100000  (16 bits L-242)",
    "mb directo":                                 "ej: 1013.10",
    "inHg directo":                               "ej: 29.917",
}


def raw_to_mb_inhg(raw: str, fmt: str, use_354: bool):
    """
    Parse raw ARINC bus value → (mb, inHg, error_str).
    Returns (None, None, None) if raw is empty (pending).
    """
    raw = raw.strip()
    if not raw:
        return None, None, None

    cf_mb   = CF_354_MB   if use_354 else CF_242_MB
    cf_inhg = CF_354_INHG if use_354 else CF_242_INHG
    n_bits  = 18 if use_354 else 16

    # ── Hex helpers ──────────────────────────────────────────────────────────
    def clean_hex(s):
        s = s.upper().replace("0X", "").replace(" ", "")
        if not s or not all(c in "0123456789ABCDEF" for c in s):
            return None, "Valor hexadecimal inválido."
        return s, None

    if fmt == "Hex — palabra ARINC completa (6-8 dígitos)":
        h, err = clean_hex(raw)
        if err:
            return None, None, err
        if len(h) < 5:
            return None, None, f"Se esperan ≥6 hex chars; se recibieron {len(h)}."
        # Data bits 28-13 live in nibbles [1:5] of the 6+ char word
        dec = int(h[1:5], 16)
        return dec * cf_mb, dec * cf_inhg, None

    elif fmt == "Hex — campo datos (4 dígitos)":
        h, err = clean_hex(raw)
        if err:
            return None, None, err
        dec = int(h, 16)
        return dec * cf_mb, dec * cf_inhg, None

    elif fmt == "Binario":
        bits = raw.replace(" ", "").replace("_", "")
        if not all(c in "01" for c in bits):
            return None, None, "Solo se permiten 0 y 1."
        if len(bits) != n_bits:
            return None, None, f"Se esperan {n_bits} bits; se recibieron {len(bits)}."
        dec = int(bits, 2)
        return dec * cf_mb, dec * cf_inhg, None

    elif fmt == "mb directo":
        try:
            val = float(raw)
            return val, val * MB_TO_INHG, None
        except Exception:
            return None, None, "Valor numérico inválido."

    elif fmt == "inHg directo":
        try:
            val = float(raw)
            return val * INHG_TO_MB, val, None
        except Exception:
            return None, None, "Valor numérico inválido."

    return None, None, "Formato no reconocido."


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ Configuración del Test")
    st.markdown("---")

    side = st.radio(
        "Posición del ADC",
        ["CAPT  (Left — L ADC)", "F/O  (Right — R ADC)"],
    )

    unit = st.radio(
        "Tabla / Unidad de medida",
        ["mb  —  Fig 58 / Fig 60", "inHg  —  Fig 57 / Fig 59"],
    )

    use_354 = st.checkbox(
        "Static label = **354**  (no Label 246)",
        value=False,
        help=(
            "Activar para ADC: 4040800-901/-902/-904/-905/-906/-912/-914\n\n"
            "Label 354 → bits 28→11, 18 bits.\n"
            "Label 246 → bits 28→13, 16 bits."
        ),
    )

    st.markdown("---")
    st.markdown("### 📋 Datos del ADC")
    adc_pn    = st.text_input("Part Number (P/N)",   placeholder="4040800-905")
    adc_sn    = st.text_input("Serial Number (S/N)", placeholder="SN-12345")
    aircraft  = st.text_input("Matrícula A/C",       placeholder="CC-CXJ")
    test_date = st.date_input("Fecha del test", value=date.today())
    option_n  = st.text_input("Test Setup",     placeholder="OPTION 1 / OPTION 2")

    st.markdown("---")
    st.markdown("### 💡 Referencia hex completa")
    st.code(
        "Ej: E7EA36\n"
        "Nibbles[1:5] → 7EA3\n"
        "7EA3 hex = 32 419 dec\n"
        "32 419 × 0.03125\n"
        "= 1 013.09 mb  ✅",
        language=None,
    )


# ─────────────────────────────────────────────────────────────────────────────
# DERIVED CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
is_capt = "CAPT" in side
is_inhg = "inHg" in unit

if is_inhg:
    TEST_PTS    = [29.917, 13.584, 5.611, 13.584, 29.917]
    TP_TOL      = 0.029
    TOL_PIT     = 0.029
    TOL_STA     = 0.018
    UNIT_S      = "inHg"
    FMT_V       = ".4f"
    FMT_NI      = "%.4f"
else:
    TEST_PTS    = [1013.0, 460.0, 190.0, 460.0, 1013.0]
    TP_TOL      = 1.0
    TOL_PIT     = 1.0
    TOL_STA     = 0.6
    UNIT_S      = "mb"
    FMT_V       = ".2f"
    FMT_NI      = "%.2f"

STATIC_LABEL = "Label 354" if use_354 else "Label 246"
STATIC_BITS  = 18          if use_354 else 16

FIG_REF  = {(True, True ): "Fig 57",
            (True, False): "Fig 58",
            (False, True ): "Fig 59",
            (False, False): "Fig 60"}[(is_capt, is_inhg)]

ADC_NAME = "Left ADC"  if is_capt else "Right ADC"
ADC_POS  = "CAPT"      if is_capt else "F/O"

# Pre-compute ISA reference altitudes for the 5 test points
ISA_FT = []
for tp in TEST_PTS:
    tp_mb = tp * INHG_TO_MB if is_inhg else tp
    ISA_FT.append(mb_to_ft_isa(tp_mb))


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def to_table_unit(mb_val, inhg_val):
    """Return value in the selected table unit (mb or inHg)."""
    if mb_val is None:
        return None
    return inhg_val if is_inhg else mb_val

def fv(v):
    """Format float for display."""
    return f"{v:{FMT_V}}" if v is not None else "—"

def verdict(ok):
    if ok is True:  return "✅ PASS"
    if ok is False: return "❌ FAIL"
    return "⏳"


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="titlebar">
  <h2>✈️  Boeing 767 — Altimetry System Test</h2>
  <p>
    TASK&nbsp;34-11-00-730-816-001 &nbsp;|&nbsp;
    <b>{FIG_REF}</b> &nbsp;|&nbsp;
    <b>{ADC_NAME}</b> &nbsp;|&nbsp;
    <b>{UNIT_S}</b> &nbsp;|&nbsp;
    P/N:&nbsp;<code>{adc_pn or "—"}</code> &nbsp;
    S/N:&nbsp;<code>{adc_sn or "—"}</code> &nbsp;
    A/C:&nbsp;<code>{aircraft or "—"}</code> &nbsp;
    Fecha:&nbsp;<code>{test_date}</code> &nbsp;
    Setup:&nbsp;<code>{option_n or "—"}</code>
  </p>
</div>
""", unsafe_allow_html=True)

hc1, hc2, hc3, hc4 = st.columns(4)
hc1.metric("Posición ADC", ADC_POS)
hc2.metric("Tabla / Unidad", f"{FIG_REF} / {UNIT_S}")
hc3.metric("Tol. Pitot (L-242)", f"±{TOL_PIT} {UNIT_S}")
hc4.metric(f"Tol. Static ({STATIC_LABEL})", f"±{TOL_STA} {UNIT_S}")
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# TEST POINT DATA ENTRY
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("📋 Ingreso de Datos — 5 Test Points")

pit_rows = []   # for summary table
sta_rows = []

for i, tp in enumerate(TEST_PTS):
    tp_n = i + 1
    isa  = ISA_FT[i]

    with st.expander(
        f"Test Point {tp_n}  ·  {tp:{FMT_V}} {UNIT_S}  ·  ISA ≈ {isa:,.0f} ft",
        expanded=(tp_n == 1),
    ):
        left, right = st.columns(2)

        # ═══ PITOT  (Label 242) ══════════════════════════════════════════════
        with left:
            st.markdown("#### 🔵 Total (Pitot) — Label 242")

            fmt_pit = st.selectbox(
                "Formato de salida del ARINC Analyzer",
                FMT_OPTIONS,
                key=f"fp_{i}",
            )

            # Col A — DPS
            st.markdown(
                '<div class="boxDPS">'
                '<p class="sect">📟  Col A — Salida del Air Data Test Set (COM-1914 / DPS)</p>'
                'Lee este valor <b>directamente en la pantalla del equipo</b>. '
                'Es la presión estática que está siendo inyectada al sistema.',
                unsafe_allow_html=True,
            )
            col_a = st.number_input(
                f"Col A  ({UNIT_S})",
                key=f"a_{i}",
                value=float(tp),
                step=0.001 if is_inhg else 0.1,
                format=FMT_NI,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Col B — ARINC
            st.markdown(
                '<div class="boxARINC">'
                '<p class="sect">📡  Col B — Salida del ARINC 429 Bus Analyzer (COM-1562) · Label 242</p>'
                'Ingresa el valor RAW que muestra el analizador. '
                'Puede ser binario, hexadecimal, mb o inHg.',
                unsafe_allow_html=True,
            )
            raw_242 = st.text_input(
                f"Label 242  [{fmt_pit}]",
                key=f"r242_{i}",
                placeholder=PLACEHOLDERS[fmt_pit],
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Convert
            mb_242, inhg_242, err_242 = raw_to_mb_inhg(raw_242, fmt_pit, False)
            b_pit  = to_table_unit(mb_242, inhg_242)   # Col B in table unit
            diff_p = (col_a - b_pit) if b_pit is not None else None
            ok_p   = (abs(diff_p) <= TOL_PIT) if diff_p is not None else None

            # Results display
            if err_242:
                st.error(f"⚠️  {err_242}")
            elif b_pit is not None:
                st.markdown('<div class="convbox">', unsafe_allow_html=True)
                st.markdown('<p class="sect">Conversión del valor ARINC:</p>',
                            unsafe_allow_html=True)
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("mb", f"{mb_242:.2f}")
                rc2.metric("inHg", f"{inhg_242:.4f}")
                rc3.metric("ft ISA (ref)", f"{mb_to_ft_isa(mb_242):,.0f}")
                st.markdown(
                    f'<p class="ft-ref">▸ Valor Col B en tabla '
                    f'({UNIT_S}): <b>{b_pit:{FMT_V}}</b></p>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                d1, d2 = st.columns(2)
                d1.metric(f"C = A − B  ({UNIT_S})", f"{diff_p:+{FMT_V}}", delta_color="off")
                d2.metric(f"D — Tolerancia", f"±{TOL_PIT} {UNIT_S}")
                tag, cls = ("✅  PITOT — PASS", "pass") if ok_p else ("❌  PITOT — FAIL", "fail")
                st.markdown(f'<div class="{cls}">{tag}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="pend">— ingresa el valor del ARINC —</div>',
                            unsafe_allow_html=True)

        # ═══ STATIC  (Label 246 / 354) ═══════════════════════════════════════
        with right:
            st.markdown(f"#### 🟢 Static — {STATIC_LABEL}")

            fmt_sta = st.selectbox(
                "Formato de salida del ARINC Analyzer",
                FMT_OPTIONS,
                key=f"fs_{i}",
            )

            # Col E — DPS
            st.markdown(
                '<div class="boxDPS">'
                '<p class="sect">📟  Col E — Salida del Air Data Test Set (COM-1914 / DPS)</p>'
                'Lee este valor <b>directamente en la pantalla del equipo</b>. '
                'Normalmente coincide con Col A.',
                unsafe_allow_html=True,
            )
            col_e = st.number_input(
                f"Col E  ({UNIT_S})",
                key=f"e_{i}",
                value=float(tp),
                step=0.001 if is_inhg else 0.1,
                format=FMT_NI,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Col F — ARINC
            st.markdown(
                f'<div class="boxARINC">'
                f'<p class="sect">📡  Col F — Salida del ARINC 429 Bus Analyzer (COM-1562) · {STATIC_LABEL}</p>'
                f'Ingresa el valor RAW para <b>{STATIC_LABEL}</b>.',
                unsafe_allow_html=True,
            )
            raw_st = st.text_input(
                f"{STATIC_LABEL}  [{fmt_sta}]",
                key=f"rst_{i}",
                placeholder=PLACEHOLDERS[fmt_sta],
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Convert
            mb_st, inhg_st, err_st = raw_to_mb_inhg(raw_st, fmt_sta, use_354)
            f_sta  = to_table_unit(mb_st, inhg_st)
            diff_s = (col_e - f_sta) if f_sta is not None else None
            ok_s   = (abs(diff_s) <= TOL_STA) if diff_s is not None else None

            if err_st:
                st.error(f"⚠️  {err_st}")
            elif f_sta is not None:
                st.markdown('<div class="convbox">', unsafe_allow_html=True)
                st.markdown('<p class="sect">Conversión del valor ARINC:</p>',
                            unsafe_allow_html=True)
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("mb",     f"{mb_st:.2f}")
                rc2.metric("inHg",   f"{inhg_st:.4f}")
                rc3.metric("ft ISA (ref)", f"{mb_to_ft_isa(mb_st):,.0f}")
                st.markdown(
                    f'<p class="ft-ref">▸ Valor Col F en tabla '
                    f'({UNIT_S}): <b>{f_sta:{FMT_V}}</b></p>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                d1, d2 = st.columns(2)
                d1.metric(f"G = E − F  ({UNIT_S})", f"{diff_s:+{FMT_V}}", delta_color="off")
                d2.metric("H — Tolerancia", f"±{TOL_STA} {UNIT_S}")
                tag, cls = ("✅  STATIC — PASS", "pass") if ok_s else ("❌  STATIC — FAIL", "fail")
                st.markdown(f'<div class="{cls}">{tag}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="pend">— ingresa el valor del ARINC —</div>',
                            unsafe_allow_html=True)

        # ── store for summary ─────────────────────────────────────────────────
        pit_rows.append({
            "TP":                f"{tp_n}",
            f"A — DPS ({UNIT_S})":          fv(col_a),
            f"B — ARINC L-242 ({UNIT_S})":  fv(b_pit)  if mb_242 is not None else "—",
            f"C = A−B":                     f"{diff_p:+{FMT_V}}" if diff_p is not None else "—",
            f"D  ±{TOL_PIT} {UNIT_S}":      verdict(ok_p),
        })
        sta_rows.append({
            "TP":                f"{tp_n}",
            f"E — DPS ({UNIT_S})":          fv(col_e),
            f"F — {STATIC_LABEL} ({UNIT_S})": fv(f_sta) if mb_st is not None else "—",
            f"G = E−F":                     f"{diff_s:+{FMT_V}}" if diff_s is not None else "—",
            f"H  ±{TOL_STA} {UNIT_S}":      verdict(ok_s),
        })


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY TABLE  (matches Fig 57-60)
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader(f"📑 Tabla de Resultados — {FIG_REF}  ·  {ADC_NAME}  ·  {UNIT_S}")

s1, s2 = st.columns(2)
with s1:
    st.markdown(
        '<p class="sec-title">Total (Pitot) Pressure — Label 242</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(pd.DataFrame(pit_rows), use_container_width=True, hide_index=True)

with s2:
    st.markdown(
        f'<p class="sec-title">Static Pressure — {STATIC_LABEL}</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(pd.DataFrame(sta_rows), use_container_width=True, hide_index=True)

# Overall result
pit_col = f"D  ±{TOL_PIT} {UNIT_S}"
sta_col = f"H  ±{TOL_STA} {UNIT_S}"
all_v   = [r[pit_col] for r in pit_rows] + [r[sta_col] for r in sta_rows]

if "⏳" in all_v:
    st.warning("⏳  Test incompleto — ingresa todos los valores del ARINC para ver el resultado final.")
elif all(v == "✅ PASS" for v in all_v):
    st.markdown(
        f'<div class="overall-pass">'
        f'🎉  RESULTADO FINAL: PASS &nbsp;·&nbsp; '
        f'{ADC_NAME} ({ADC_POS}) &nbsp; '
        f'P/N {adc_pn or "—"} &nbsp; S/N {adc_sn or "—"} &nbsp; '
        f'A/C {aircraft or "—"} &nbsp; Fecha {test_date} — ADC SERVICEABLE'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="overall-fail">'
        '❌  RESULTADO FINAL: FAIL — Uno o más test points fuera de tolerancia.<br>'
        'Reemplazar ADC per AMM 34-12-01/401 y repetir el test.'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📥 Exportar resultados")

hdr = {
    "Aircraft": aircraft, "Date": str(test_date), "P/N": adc_pn, "S/N": adc_sn,
    "ADC Pos": ADC_POS, "Table": FIG_REF, "Units": UNIT_S,
    "Setup": option_n, "Static Label": STATIC_LABEL,
}

df_pit_exp = pd.DataFrame([{**hdr, "Section": "Pitot-L242",    **r} for r in pit_rows])
df_sta_exp = pd.DataFrame([{**hdr, "Section": f"Static-{STATIC_LABEL}", **r} for r in sta_rows])

try:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_pit_exp.to_excel(w, index=False, sheet_name="Pitot_Label242")
        df_sta_exp.to_excel(w, index=False, sheet_name=f"Static_{STATIC_LABEL.replace(' ','')}") 
    fname = (
        f"AltTest_{aircraft or 'AC'}_{adc_pn or 'ADC'}"
        f"_{ADC_POS}_{UNIT_S}_{test_date}.xlsx"
    )
    st.download_button(
        "📊 Descargar Excel (.xlsx)",
        data=buf.getvalue(),
        file_name=fname,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except ImportError:
    df_all = pd.concat([df_pit_exp, df_sta_exp], ignore_index=True)
    fname  = f"AltTest_{aircraft or 'AC'}_{ADC_POS}_{UNIT_S}_{test_date}.csv"
    st.download_button("📄 Descargar CSV", data=df_all.to_csv(index=False),
                       file_name=fname, mime="text/csv")


# ─────────────────────────────────────────────────────────────────────────────
# QUICK REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📚 Referencia rápida de conversión — Figure 213 / Appendix A"):
    st.markdown(f"""
### Formatos de entrada — Label 242 / 246 / 354

| Formato | Cómo usarlo | Ejemplo → 1013 mb |
|---------|-------------|-------------------|
| **Hex palabra completa (6-8 chars)** | Palabra ARINC completa del analizador; extrae nibbles[1:5] | `E7EA36` → `7EA3` = 32 419 → **1013.09 mb** ✅ |
| **Hex campo datos (4 chars)** | Solo los 4 hex chars del campo de datos | `7EA0` = 32 416 → **1013.00 mb** |
| **Binario** | 16 bits Lbl 242/246, 18 bits Lbl 354 | `0111111010100000` → **1013.00 mb** |
| **mb directo** | El equipo ya muestra milibares | `1013.10` |
| **inHg directo** | El equipo ya muestra pulgadas de mercurio | `29.917` |

---
### Factores de conversión

| Label | Bits | Factor → mb | Factor → inHg |
|-------|------|-------------|---------------|
| 242 / 246 | 28→13 (16 bits) | × 0.03125 | × 0.0009228 |
| 354 | 28→11 (18 bits) | × 0.008266 | × 0.0002441368 |

---
### Altitudes ISA de referencia (presiones del test)

| mb | inHg | ft ISA (aprox) |
|-----|-------|----------------|
| 1013 | 29.917 | 0 ft — nivel del mar |
| 460  | 13.584 | ~20 300 ft |
| 190  | 5.611  | ~39 700 ft |

---
### Cómo extraer datos del hex completo ARINC

```
Palabra de 6 chars:   E   7   E   A   3   6
Índice (0-based):     0   1   2   3   4   5
                          └───────────┘
                          nibbles [1:5] = "7EA3"
                          7EA3 hex = 32 419 decimal
                          × 0.03125 = 1 013.09 mb ✅
```
    """)

st.divider()
st.caption(
    "Boeing 767 AMM Rev 147 — 22 Dec 2025  |  "
    "TASK 34-11-00-730-816-001  |  LATAM / LAN ALL  |  "
    "ECCN 9E991 Boeing PROPRIETARY"
)
