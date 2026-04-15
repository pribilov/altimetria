"""
Boeing 767 — Altimetry System Test
TASK 34-11-00-730-816-001  |  AD-B767-34-A2383 PART2  |  LAN ALL

Run:
    pip install streamlit pandas openpyxl
    streamlit run altimetry_test_app.py
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

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
         border-radius:5px; font-weight:bold; text-align:center; margin-top:6px;}
.fail  { background:#f8d7da; color:#721c24; padding:6px 14px;
         border-radius:5px; font-weight:bold; text-align:center; margin-top:6px;}
.pend  { background:#fff3cd; color:#856404; padding:6px 14px;
         border-radius:5px; font-weight:bold; text-align:center; margin-top:6px;}
.sect  { font-size:1.0rem; font-weight:600; margin-bottom:4px; }
.boxA  { background:#ddeeff; padding:10px 12px; border-radius:7px; margin-bottom:8px;}
.boxB  { background:#ddf5dd; padding:10px 12px; border-radius:7px; margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# CONVERSION HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def parse_binary(raw: str, n_bits: int, factor: float):
    bits = raw.replace(" ", "").replace("_", "")
    if not all(c in "01" for c in bits):
        return None, None, "Solo se permiten 0 y 1."
    if len(bits) != n_bits:
        return None, None, f"Se esperan {n_bits} bits, se recibieron {len(bits)}."
    dec = int(bits, 2)
    return dec, dec * factor, None


def parse_hex_data(raw: str, factor: float):
    """4-hex-digit data field (bits 28-13 directly)."""
    h = raw.strip().upper().replace("0X", "").replace(" ", "")
    if not all(c in "0123456789ABCDEF" for c in h) or not h:
        return None, None, "Valor hexadecimal inválido."
    dec = int(h, 16)
    return dec, dec * factor, None


def parse_hex_full_arinc(raw: str, factor: float):
    """Full ARINC-word hex (6 or 8 hex chars).
    Extracts bits 28-13 from nibbles [1:5] (0-indexed).
    Example: E7EA36 -> nibbles[1:5] = '7EA3' = 32419 -> 1013.09 mb
    """
    h = raw.strip().upper().replace("0X", "").replace(" ", "")
    if not all(c in "0123456789ABCDEF" for c in h) or not h:
        return None, None, "Valor hexadecimal inválido."
    if len(h) < 5:
        return None, None, f"Se esperan al menos 6 dígitos hex; se recibieron {len(h)}."
    data_nibbles = h[1:5]
    dec = int(data_nibbles, 16)
    return dec, dec * factor, None


def parse_decimal(raw: str, factor: float):
    try:
        dec = int(float(raw.strip()))
        return dec, dec * factor, None
    except Exception:
        return None, None, "Valor decimal inválido."


FMT_OPTIONS = [
    "Hex — palabra ARINC completa (6-8 dígitos)",
    "Hex — campo datos (4 dígitos)",
    "Binario",
    "Decimal",
]


def convert(raw: str, fmt: str, n_bits: int, factor: float):
    if not raw or not raw.strip():
        return None, None, None
    if fmt == "Binario":
        return parse_binary(raw, n_bits, factor)
    elif fmt == "Hex — campo datos (4 dígitos)":
        return parse_hex_data(raw, factor)
    elif fmt == "Hex — palabra ARINC completa (6-8 dígitos)":
        return parse_hex_full_arinc(raw, factor)
    else:
        return parse_decimal(raw, factor)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
PH = {
    "Hex — palabra ARINC completa (6-8 dígitos)": {
        "16": "ej: E7EA36  (→ 1013 mb)",
        "18": "ej: E7EA3600",
    },
    "Hex — campo datos (4 dígitos)": {
        "16": "ej: 7EA0",
        "18": "ej: 1FA80",
    },
    "Binario": {
        "16": "16 bits  ej: 0111111010100000",
        "18": "18 bits  ej: 011111101010000000",
    },
    "Decimal": {
        "16": "ej: 32416",
        "18": "ej: 122624",
    },
}

with st.sidebar:
    st.markdown("## ⚙️ Configuración")

    side = st.radio("Posición del ADC",
                    ["CAPT  (Left — L ADC)", "F/O  (Right — R ADC)"])

    unit = st.radio("Unidad de medida", ["mb  (Millibars)", "inHg"])

    use_354 = st.checkbox(
        "Static label = **354** (no 246)",
        value=False,
        help="Para ADC 4040800-901/-902/-904/-905/-906/-912/-914. "
             "Label 354 usa 18 bits (28→11). Default Label 246 usa 16 bits (28→13).",
    )

    st.markdown("---")
    st.markdown("### 📝 Datos del ADC")
    adc_pn    = st.text_input("Part Number (P/N)",  placeholder="e.g. 4040800-905")
    adc_sn    = st.text_input("Serial Number (S/N)", placeholder="e.g. SN12345")
    aircraft  = st.text_input("Matrícula A/C",       placeholder="e.g. CC-CXJ")
    test_date = st.date_input("Fecha",          value=date.today())
    option_n  = st.text_input("Setup utilizado", placeholder="OPTION 1 / OPTION 2")

    st.markdown("---")
    st.info(
        "**Hex completa — ejemplo:**\n\n"
        "`E7EA36` → nibbles[1:5] = `7EA3`\n\n"
        "`7EA3` = 32 419 dec\n\n"
        "32 419 × 0.03125 = **1 013.09 mb ✅**"
    )


# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
is_capt = "CAPT" in side
is_inhg = unit == "inHg"

if is_inhg:
    TEST_PTS   = [29.917, 13.584, 5.611, 13.584, 29.917]
    TP_TOL, TOL_PITOT, TOL_STATIC = 0.029, 0.029, 0.018
    UNIT_S, FMT_V, FMT_NI = "inHg", ".4f", "%.4f"
    CF_242_246, CF_354 = 0.0009228, 0.0002441368
else:
    TEST_PTS   = [1013.0, 460.0, 190.0, 460.0, 1013.0]
    TP_TOL, TOL_PITOT, TOL_STATIC = 1.0, 1.0, 0.6
    UNIT_S, FMT_V, FMT_NI = "mb", ".2f", "%.2f"
    CF_242_246, CF_354 = 0.03125, 0.008266

CF_STATIC    = CF_354     if use_354 else CF_242_246
STATIC_LABEL = "Label 354" if use_354 else "Label 246"
STATIC_BITS  = 18          if use_354 else 16

FIG_REF  = {(True, True): "Fig 57", (True, False): "Fig 58",
            (False, True): "Fig 59", (False, False): "Fig 60"}[(is_capt, is_inhg)]
ADC_NAME = "Left ADC"  if is_capt else "Right ADC"
ADC_POS  = "CAPT"      if is_capt else "F/O"


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.title("✈️  Boeing 767 — Altimetry System Test")
st.markdown(
    f"**TASK 34-11-00-730-816-001** &nbsp;|&nbsp; **{FIG_REF}** &nbsp;|&nbsp; "
    f"**{ADC_NAME}** &nbsp;|&nbsp; **{UNIT_S}** &nbsp;|&nbsp; "
    f"P/N: `{adc_pn or '—'}` &nbsp; S/N: `{adc_sn or '—'}` &nbsp; "
    f"A/C: `{aircraft or '—'}` &nbsp; Fecha: `{test_date}` &nbsp; "
    f"Setup: `{option_n or '—'}`"
)
st.caption(
    f"Pitot (Label 242) tol: **±{TOL_PITOT} {UNIT_S}** &nbsp;|&nbsp; "
    f"Static ({STATIC_LABEL}) tol: **±{TOL_STATIC} {UNIT_S}** &nbsp;|&nbsp; "
    f"Static bits: **{STATIC_BITS}**"
)
st.divider()


# ──────────────────────────────────────────────────────────────────────────────
# TEST POINTS
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📋 Ingreso de Datos — 5 Test Points")
summary_rows = []

for i, tp in enumerate(TEST_PTS):
    tp_n = i + 1

    with st.expander(
        f"**Test Point {tp_n}**  ·  Target: **{tp:{FMT_V}} ± {TP_TOL} {UNIT_S}**",
        expanded=(tp_n == 1),
    ):
        left, right = st.columns(2)

        # ═══════════════ PITOT ═══════════════
        with left:
            st.markdown(f"#### 🔵 Total (Pitot) — Label 242  →  {ADC_NAME}")

            fmt_pit = st.selectbox(
                "Formato ARINC — Label 242",
                FMT_OPTIONS,
                key=f"fmt_pit_{i}",
            )

            # Col A — DPS
            st.markdown(
                '<div class="boxA">'
                '<p class="sect">📟  Col A — Salida del Air Data Test Set (DPS / COM-1914)</p>'
                'Lee este valor <b>directamente en la pantalla del equipo</b>. '
                'Es la presión estática que el equipo está inyectando.',
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

            # Col B — ARINC bus
            st.markdown(
                '<div class="boxB">'
                '<p class="sect">📡  Col B — Salida del ARINC 429 Bus Analyzer (COM-1562) · Label 242</p>'
                'Ingresa el valor RAW que muestra el analizador para <b>Label 242</b>. '
                'Puede ser binario, hex completa o hex campo de datos.',
                unsafe_allow_html=True,
            )
            raw_242 = st.text_input(
                f"Label 242  [{fmt_pit}]",
                key=f"r242_{i}",
                placeholder=PH[fmt_pit]["16"],
            )
            st.markdown("</div>", unsafe_allow_html=True)

            dec_242, p_242, err_242 = convert(raw_242, fmt_pit, 16, CF_242_246)
            diff_pit = (col_a - p_242) if p_242 is not None else None
            ok_pit   = (abs(diff_pit) <= TOL_PITOT) if diff_pit is not None else None

            if err_242:
                st.error(f"⚠️  {err_242}")
            elif p_242 is not None:
                m1, m2, m3 = st.columns(3)
                m1.metric("Decimal", f"{dec_242:,}")
                m2.metric(f"Col B ({UNIT_S})", f"{p_242:{FMT_V}}")
                diff_label = f"A − B  (tol ±{TOL_PITOT})"
                m3.metric(diff_label, f"{diff_pit:+{FMT_V}}")
                tag = "✅  PITOT — PASS" if ok_pit else "❌  PITOT — FAIL"
                cls = "pass" if ok_pit else "fail"
                st.markdown(f'<div class="{cls}">{tag}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="pend">— pendiente —</div>', unsafe_allow_html=True)

        # ═══════════════ STATIC ═══════════════
        with right:
            st.markdown(f"#### 🟢 Static — {STATIC_LABEL}  →  {ADC_NAME}")

            fmt_sta = st.selectbox(
                f"Formato ARINC — {STATIC_LABEL}",
                FMT_OPTIONS,
                key=f"fmt_sta_{i}",
            )
            sta_bit_key = "18" if use_354 else "16"

            # Col E — DPS
            st.markdown(
                '<div class="boxA">'
                '<p class="sect">📟  Col E — Salida del Air Data Test Set (DPS / COM-1914)</p>'
                'Lee este valor <b>directamente en la pantalla del equipo</b>. '
                'Normalmente es igual al Col A (misma presión estática).',
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
                f'<div class="boxB">'
                f'<p class="sect">📡  Col F — Salida del ARINC 429 Bus Analyzer (COM-1562) · {STATIC_LABEL}</p>'
                f'Ingresa el valor RAW para <b>{STATIC_LABEL}</b>.',
                unsafe_allow_html=True,
            )
            raw_st = st.text_input(
                f"{STATIC_LABEL}  [{fmt_sta}]",
                key=f"rst_{i}",
                placeholder=PH[fmt_sta][sta_bit_key],
            )
            st.markdown("</div>", unsafe_allow_html=True)

            dec_st, p_st, err_st = convert(raw_st, fmt_sta, STATIC_BITS, CF_STATIC)
            diff_sta = (col_e - p_st) if p_st is not None else None
            ok_sta   = (abs(diff_sta) <= TOL_STATIC) if diff_sta is not None else None

            if err_st:
                st.error(f"⚠️  {err_st}")
            elif p_st is not None:
                m1, m2, m3 = st.columns(3)
                m1.metric("Decimal", f"{dec_st:,}")
                m2.metric(f"Col F ({UNIT_S})", f"{p_st:{FMT_V}}")
                m3.metric(f"E − F  (tol ±{TOL_STATIC})", f"{diff_sta:+{FMT_V}}")
                tag = "✅  STATIC — PASS" if ok_sta else "❌  STATIC — FAIL"
                cls = "pass" if ok_sta else "fail"
                st.markdown(f'<div class="{cls}">{tag}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="pend">— pendiente —</div>', unsafe_allow_html=True)

        # summary row
        def _f(v):  return f"{v:{FMT_V}}" if v is not None else "—"
        def _v(ok): return ("✅ PASS" if ok else "❌ FAIL") if ok is not None else "⏳"

        summary_rows.append({
            "TP": tp_n,
            f"Target({UNIT_S})": f"{tp:{FMT_V}}",
            "L242 raw": raw_242 or "—",
            "L242 dec": dec_242 if dec_242 is not None else "—",
            f"ColA({UNIT_S})": _f(col_a),
            f"ColB({UNIT_S})": _f(p_242),
            "A−B": f"{diff_pit:+{FMT_V}}" if diff_pit is not None else "—",
            f"±{TOL_PITOT}": _v(ok_pit),
            f"{STATIC_LABEL} raw": raw_st or "—",
            f"{STATIC_LABEL} dec": dec_st if dec_st is not None else "—",
            f"ColE({UNIT_S})": _f(col_e),
            f"ColF({UNIT_S})": _f(p_st),
            "E−F": f"{diff_sta:+{FMT_V}}" if diff_sta is not None else "—",
            f"±{TOL_STATIC}": _v(ok_sta),
        })


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📑 Resumen")
st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

pit_col = f"±{TOL_PITOT}"
sta_col = f"±{TOL_STATIC}"
all_vals = [r[pit_col] for r in summary_rows] + [r[sta_col] for r in summary_rows]

if "⏳" in all_vals:
    st.warning("⏳  Ingresa todos los valores ARINC para ver el resultado final.")
elif all(v == "✅ PASS" for v in all_vals):
    st.success(
        f"🎉  **RESULTADO FINAL: PASS** — {ADC_NAME} ({ADC_POS}) "
        f"P/N `{adc_pn or '—'}` S/N `{adc_sn or '—'}` es **SERVICEABLE**."
    )
else:
    st.error(
        "❌  **RESULTADO FINAL: FAIL** — "
        "Uno o más test points fuera de tolerancia. "
        "Reemplazar ADC per AMM 34-12-01/401 y repetir."
    )


# ──────────────────────────────────────────────────────────────────────────────
# EXPORT
# ──────────────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("📥 Exportar resultados")

hdr = {"Aircraft": aircraft, "Date": str(test_date), "P/N": adc_pn, "S/N": adc_sn,
       "Pos": ADC_POS, "Table": FIG_REF, "Units": UNIT_S,
       "Setup": option_n, "StaticLabel": STATIC_LABEL}
df_exp = pd.DataFrame([{**hdr, **r} for r in summary_rows])

try:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_exp.to_excel(w, index=False, sheet_name=FIG_REF.replace(" ", "_"))
    fname = f"AltTest_{aircraft or 'AC'}_{adc_pn or 'ADC'}_{ADC_POS}_{UNIT_S}_{test_date}.xlsx"
    st.download_button("📊 Descargar Excel (.xlsx)", data=buf.getvalue(),
                       file_name=fname,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
except ImportError:
    csv = df_exp.to_csv(index=False)
    fname = f"AltTest_{aircraft or 'AC'}_{ADC_POS}_{UNIT_S}_{test_date}.csv"
    st.download_button("📄 Descargar CSV", data=csv, file_name=fname, mime="text/csv")


# ──────────────────────────────────────────────────────────────────────────────
# REFERENCE
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("📚 Referencia de conversión — Figure 213 / Appendix A"):
    st.markdown("""
### Formatos de entrada disponibles (por fila, independiente)

| Modo | Descripción | Ej. → 1013 mb |
|------|-------------|---------------|
| **Hex — palabra ARINC completa** | 6-8 chars del analizador; extrae nibbles [1:5] | `E7EA36` → `7EA3` → 32 419 → **1013.09 mb ✅** |
| **Hex — campo datos (4 dígitos)** | Solo el campo de datos de 16 bits | `7EA0` → 32 416 → **1013.00 mb** |
| **Binario** | 16 bits (Lbl 242/246) ó 18 bits (Lbl 354) | `0111111010100000` |
| **Decimal** | Entero decimal | `32416` |

---
### Factores de conversión

| Label | Bits | Factor → mb | Factor → inHg |
|-------|------|-------------|---------------|
| 242 / 246 | 28→13 (16 bits) | × 0.03125 | × 0.0009228 |
| 354       | 28→11 (18 bits) | × 0.008266 | × 0.0002441368 |

---
### Cómo se extraen los datos del hex completo

```
Palabra ARINC (6 chars ejemplo):  E  7  E  A  3  6
Índice (0-based):                  0  1  2  3  4  5
                                      └──────────┘
                                      nibbles [1:5] = "7EA3"
                                      = 32 419 dec
                                      × 0.03125 = 1013.09 mb ✅
```
    """)

st.divider()
st.caption("Boeing 767 AMM Rev 147 — 22 Dec 2025  |  TASK 34-11-00-730-816-001  |  LATAM / LAN ALL")
