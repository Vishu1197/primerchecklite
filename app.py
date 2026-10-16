"""Streamlit UI for PrimerCheck Lite.

Run from the repository root with: streamlit run app.py
"""
from __future__ import annotations

import json
import streamlit as st

from primerchecklite.core import analyze_pair
from primerchecklite.reporting import write_html_report

st.set_page_config(page_title="PrimerCheck Lite", layout="wide")
st.title("PrimerCheck Lite")
st.caption("Fast, local primer pair screening with clear explanations. Not a genome-wide specificity checker.")

with st.sidebar:
    st.header("Assay settings")
    tm_min = st.number_input("Minimum target Tm (°C)", value=57.0, min_value=0.0, max_value=100.0, step=0.5)
    tm_max = st.number_input("Maximum target Tm (°C)", value=63.0, min_value=0.0, max_value=100.0, step=0.5)
    gc_min = st.number_input("Minimum GC (%)", value=40.0, min_value=0.0, max_value=100.0, step=1.0)
    gc_max = st.number_input("Maximum GC (%)", value=60.0, min_value=0.0, max_value=100.0, step=1.0)
    min_amp = st.number_input("Minimum amplicon (bp)", value=100, min_value=1, step=10)
    max_amp = st.number_input("Maximum amplicon (bp)", value=1000, min_value=1, step=50)
    mono = st.number_input("Monovalent salt (mM)", value=50.0, min_value=0.0, step=5.0)
    divalent = st.number_input("Divalent salt (mM)", value=1.5, min_value=0.0, step=0.1)
    dntp = st.number_input("dNTP concentration (mM)", value=0.6, min_value=0.0, step=0.1)
    primer_conc = st.number_input("Primer concentration (nM)", value=250.0, min_value=0.1, step=25.0)

col1, col2 = st.columns(2)
with col1:
    forward = st.text_area("Forward primer (5′ to 3′)", value="ATGACCTACTTCGACGACGA", height=100)
with col2:
    reverse = st.text_area("Reverse primer (5′ to 3′)", value="TCAGGATCTTGTCGATGTCG", height=100)

template_text = st.text_area(
    "Optional template sequence or FASTA",
    value="",
    height=130,
    help="If supplied, checks for one exact inward-facing amplicon on this sequence. This is not genome-wide specificity analysis.",
)

if st.button("Screen primer pair", type="primary", use_container_width=True):
    if tm_min > tm_max or gc_min > gc_max or min_amp > max_amp:
        st.error("Check ranges: each minimum must be less than or equal to its maximum.")
    else:
        template = "".join(
            line.strip() for line in template_text.splitlines()
            if not line.strip().startswith(">")
        ) or None
        try:
            report = analyze_pair(
                forward, reverse, template=template,
                min_amplicon_length=int(min_amp), max_amplicon_length=int(max_amp),
                target_tm_min=tm_min, target_tm_max=tm_max,
                target_gc_min=gc_min, target_gc_max=gc_max,
                monovalent_salt_mM=mono, divalent_salt_mM=divalent,
                dntp_mM=dntp, primer_nM=primer_conc,
            ).to_dict()
            st.session_state["primerchecklite_report"] = report
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))

report = st.session_state.get("primerchecklite_report")
if report:
    st.subheader("Results")
    left, right = st.columns(2)
    for col, title, data in [
        (left, "Forward primer", report["forward"]),
        (right, "Reverse primer", report["reverse"]),
    ]:
        with col:
            st.markdown(f"#### {title}")
            st.code(data["sequence"])
            m1, m2, m3 = st.columns(3)
            m1.metric("Length", f"{data['length']} nt")
            m2.metric("GC", f"{data['gc_percent']:.1f}%")
            m3.metric("Estimated Tm", f"{data['tm_celsius']:.1f} °C")
            st.write(f"Hairpin Tm: {data['hairpin_tm_celsius']:.1f} °C")
            st.write(f"Self-dimer Tm: {data['homodimer_tm_celsius']:.1f} °C")
            if data["warnings"]:
                for warning in data["warnings"]:
                    st.warning(warning)
            else:
                st.success("No warnings under the configured screening rules.")
    st.subheader("Pair-level checks")
    a, b, c = st.columns(3)
    a.metric("Tm difference", f"{report['tm_difference_celsius']:.1f} °C")
    b.metric("Heterodimer Tm", f"{report['heterodimer_tm_celsius']:.1f} °C")
    c.metric("Amplicon length", f"{report['amplicon_length']} bp" if report["amplicon_length"] else "Not identified")
    for warning in report["pair_warnings"]:
        st.warning(warning)
    with st.expander("Calculation settings and scientific limitations"):
        st.json(report["settings"])
        for limitation in report["limitations"]:
            st.write(f"- {limitation}")
    json_bytes = json.dumps(report, indent=2).encode("utf-8")
    st.download_button("Download JSON report", json_bytes, "primerchecklite-report.json", "application/json")
    # Generate report in memory, no persistent temp file required.
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", delete=True) as tmp:
        write_html_report(report, tmp.name)
        html_bytes = open(tmp.name, "rb").read()
    st.download_button("Download HTML report", html_bytes, "primerchecklite-report.html", "text/html")
