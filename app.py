"""Colorful, guided Streamlit interface for PrimerCheck Lite."""
from __future__ import annotations

import json
import streamlit as st
import pandas as pd

from primerchecklite.core import (
    analyze_pair, default_settings, default_threshold_values, DEFAULT_THRESHOLDS
)
from primerchecklite.reporting import to_html, to_json

st.set_page_config(page_title="PrimerCheck Lite", page_icon="🧬", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(145deg,#f4f7ff 0%,#f7fbff 48%,#f2fff9 100%); }
.block-container { max-width: 1250px; padding-top: 1.4rem; }
.hero { padding: 1.5rem 1.7rem; border-radius: 22px; color: white;
        background: linear-gradient(115deg,#4338ca,#7c3aed 55%,#0891b2);
        box-shadow: 0 12px 35px rgba(67,56,202,.18); margin-bottom: 1.2rem; }
.hero h1 { color: white; margin: 0; font-size: 2.25rem; }
.hero p { color: #eef2ff; margin-bottom: 0; font-size: 1.03rem; }
div[data-testid="stMetric"] { background: white; border: 1px solid #dbeafe;
    padding: 1rem; border-radius: 15px; box-shadow: 0 5px 18px rgba(30,64,175,.06); }
div[data-testid="stForm"] { background: white; padding: 1rem; border-radius: 16px; }
div[data-testid="stExpander"] { background: rgba(255,255,255,.86); border-radius: 12px; }
.tip { padding: .8rem 1rem; background:#eef2ff; border-left:5px solid #6366f1;
       border-radius:8px; color:#312e81; margin:.5rem 0 1rem; }
.good { padding:.8rem 1rem; background:#dcfce7; border-radius:10px; color:#166534; }
.warn { padding:.8rem 1rem; background:#fee2e2; border-radius:10px; color:#991b1b; }
.small-note { color:#475569; font-size:.9rem; }
</style>
<div class="hero">
  <h1>PrimerCheck Lite</h1>
  <p>A friendly first check for PCR and qRT-PCR primers. Understand the numbers before you go to the bench.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="tip"><b>How to use:</b> paste both primer sequences in the 5′ to 3′ direction, review the threshold settings, then run the screening. Values are guides, not universal rules.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Assay conditions")
    st.caption("These values affect the thermodynamic estimates. Use your reaction conditions where known.")
    settings = {
        "mv_conc": st.number_input("Monovalent salt (mM)", min_value=0.0, value=50.0, step=1.0,
                                  help="Approximate monovalent cation concentration, often related to KCl or NaCl."),
        "dv_conc": st.number_input("Magnesium / divalent salt (mM)", min_value=0.0, value=1.5, step=0.1,
                                  help="Divalent ion concentration can affect duplex stability."),
        "dntp_conc": st.number_input("dNTP concentration (mM)", min_value=0.0, value=0.2, step=0.05),
        "dna_conc": st.number_input("Primer concentration (nM)", min_value=0.1, value=50.0, step=5.0),
    }
    st.caption("Primer3 estimates depend on these settings. Check the assumptions used by your assay.")

left, right = st.columns(2, gap="large")
with left:
    st.subheader("1. Enter your primers")
    forward = st.text_area("Forward primer (5′ to 3′)", placeholder="Example: ATGACCTACTTCGACGACGA", height=100,
                           help="Paste the forward primer sequence only. Spaces and FASTA headers are ignored.")
with right:
    st.subheader("2. Enter your primers")
    reverse = st.text_area("Reverse primer (5′ to 3′)", placeholder="Example: TCAGGATCTTGTCGATGTCG", height=100,
                           help="Enter the reverse primer as ordered, written 5′ to 3′. Do not reverse-complement it yourself.")

with st.expander("Optional: add your target template"):
    st.caption("Paste a template DNA sequence or FASTA. The template check only searches for exact matches and is not a specificity search.")
    template = st.text_area("Template sequence", height=130, placeholder=">target\nACGT...")
with st.expander("3. Set acceptable ranges for every screening metric", expanded=True):
    st.markdown("Adjust the lower and upper limits to match your protocol. Leave a limit blank when it does not apply.")
    thresholds = {}
    cols = st.columns(2)
    for i, (key, default) in enumerate(DEFAULT_THRESHOLDS.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{key.replace('_', ' ').title()}**")
                st.caption(default.description)
                c1, c2 = st.columns(2)
                use_min = c1.checkbox("Set minimum", value=default.minimum is not None, key=f"{key}_use_min")
                use_max = c2.checkbox("Set maximum", value=default.maximum is not None, key=f"{key}_use_max")
                minimum = None
                maximum = None
                if use_min:
                    minimum = c1.number_input(
                        "Minimum value",
                        value=float(default.minimum if default.minimum is not None else 0.0),
                        key=f"{key}_min", help=f"Unit: {default.unit}"
                    )
                if use_max:
                    maximum = c2.number_input(
                        "Maximum value",
                        value=float(default.maximum if default.maximum is not None else 10.0),
                        key=f"{key}_max", help=f"Unit: {default.unit}"
                    )
                if minimum is not None and maximum is not None and minimum > maximum:
                    st.error("Minimum must be less than or equal to maximum.")
                thresholds[key] = {"minimum": minimum, "maximum": maximum, "unit": default.unit,
                                   "description": default.description}

run = st.button("Analyze primer pair", type="primary", use_container_width=True)

if run:
    if not forward.strip() or not reverse.strip():
        st.error("Enter both a forward primer and a reverse primer.")
    else:
        try:
            result = analyze_pair(forward, reverse, template or None, settings, thresholds)
            st.session_state["primer_result"] = result
        except Exception as exc:
            st.error(f"Could not analyze these inputs: {exc}")

result = st.session_state.get("primer_result")
if result:
    st.subheader("Screening results")
    f, r, pair = result["forward"], result["reverse"], result["pair"]
    cards = st.columns(4)
    cards[0].metric("Forward Tm", f'{f["tm_c"]:.2f} °C')
    cards[1].metric("Reverse Tm", f'{r["tm_c"]:.2f} °C')
    cards[2].metric("Tm difference", f'{pair["tm_difference_c"]:.2f} °C')
    cards[3].metric("Warnings", str(len(result["warnings"])))
    tab1, tab2, tab3, tab4 = st.tabs(["Primer details", "What needs review", "Template check", "Download reports"])
    with tab1:
        for label, primer in (("Forward primer", f), ("Reverse primer", r)):
            st.markdown(f"#### {label}")
            st.code(primer["sequence"], language=None)
            data = []
            for key, value in primer.items():
                if key in ("sequence", "statuses"):
                    continue
                status = primer.get("statuses", {}).get(key, "not_evaluated")
                t = thresholds.get(key, {})
                data.append({"Parameter": key.replace("_", " ").title(), "Value": value,
                             "Unit": t.get("unit", ""), "Status": "Review" if status == "review" else "Within range"})
            st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)
    with tab2:
        if result["warnings"]:
            st.markdown('<div class="warn"><b>Review these values before using the primers.</b> A warning means a value is outside the limits you configured, not that PCR will necessarily fail.</div>', unsafe_allow_html=True)
            for warning in result["warnings"]:
                st.write(f"• {warning}")
        else:
            st.markdown('<div class="good"><b>No configured threshold warnings.</b> This does not prove specificity or experimental success.</div>', unsafe_allow_html=True)
        with st.expander("Why these parameters matter"):
            st.write("Length and GC content are basic sequence checks. Tm estimates describe duplex stability under stated conditions. Hairpin and dimer estimates describe possible competing structures. A long repeated base run can be a sequence design concern. These values should be interpreted together and in the context of your assay.")
    with tab3:
        if result["amplicon"]:
            st.json(result["amplicon"])
            st.warning("Exact matching is not genome-wide specificity analysis.")
        else:
            st.info("No template was supplied. Add a template above and run the analysis to check for an exact inward-facing product.")
    with tab4:
        st.download_button("Download JSON", to_json(result), "primerchecklite-report.json", "application/json", use_container_width=True)
        st.download_button("Download HTML report", to_html(result), "primerchecklite-report.html", "text/html", use_container_width=True)
        st.download_button("Download threshold settings", json.dumps(thresholds, indent=2), "primerchecklite-thresholds.json", "application/json", use_container_width=True)
    with st.expander("Read before using the results"):
        for item in result["limitations"]:
            st.write(f"• {item}")
        st.markdown("For genome-wide specificity checks, use [NCBI Primer BLAST](https://www.ncbi.nlm.nih.gov/tools/primer-blast/) or a suitable in silico PCR tool. Validate primers under your laboratory's assay conditions.")
else:
    st.info("Your results will appear here after you analyze a primer pair.")
