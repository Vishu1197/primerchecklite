"""Report serialization helpers."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


def write_json_report(data: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _primer_html(title: str, primer: dict[str, Any]) -> str:
    warnings = "".join(f"<li>{escape(w)}</li>" for w in primer["warnings"]) or "<li>No configured screening warnings.</li>"
    return f"""
    <section class="card">
      <h2>{escape(title)}</h2>
      <p class="sequence">{escape(primer['sequence'])}</p>
      <dl>
        <dt>Length</dt><dd>{primer['length']} nt</dd>
        <dt>GC</dt><dd>{primer['gc_percent']:.2f}%</dd>
        <dt>Estimated Tm</dt><dd>{primer['tm_celsius']:.2f} °C</dd>
        <dt>Hairpin Tm</dt><dd>{primer['hairpin_tm_celsius']:.2f} °C</dd>
        <dt>Self-dimer Tm</dt><dd>{primer['homodimer_tm_celsius']:.2f} °C</dd>
        <dt>Longest homopolymer</dt><dd>{primer['longest_homopolymer']} × {escape(primer['homopolymer_base'])}</dd>
        <dt>Last five bases</dt><dd>{escape(primer['three_prime_end'])}</dd>
      </dl>
      <h3>Warnings</h3><ul>{warnings}</ul>
    </section>"""


def write_html_report(data: dict[str, Any], path: str | Path) -> Path:
    pair_warnings = "".join(f"<li>{escape(w)}</li>" for w in data["pair_warnings"]) or "<li>No pair-level screening warnings.</li>"
    limitations = "".join(f"<li>{escape(w)}</li>" for w in data["limitations"])
    amp = "Not evaluated"
    if data["amplicon_length"] is not None:
        amp = f"{data['amplicon_length']} bp"
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PrimerCheck Lite report</title>
<style>
:root {{ color-scheme: light; --ink:#182230; --muted:#526174; --line:#d8e0e8; --panel:#f5f8fb; --accent:#155eef; }}
body {{ margin:0; background:#f7f9fc; color:var(--ink); font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif; }}
main {{ max-width:1000px; margin:0 auto; padding:2rem 1rem 4rem; }}
h1 {{ margin-bottom:.25rem; }} .muted {{ color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1rem; }}
.card {{ background:white; border:1px solid var(--line); border-radius:14px; padding:1.1rem; margin:1rem 0; overflow-wrap:anywhere; }}
.sequence {{ font-family:ui-monospace,SFMono-Regular,Consolas,monospace; background:var(--panel); padding:.75rem; border-radius:8px; }}
dl {{ display:grid; grid-template-columns:1fr auto; gap:.3rem 1rem; }} dt {{ color:var(--muted); }} dd {{ margin:0; text-align:right; font-variant-numeric:tabular-nums; }}
a {{ color:var(--accent); }} li {{ margin:.35rem 0; }} footer {{ color:var(--muted); font-size:.9rem; margin-top:2rem; }}
</style></head>
<body><main>
<h1>PrimerCheck Lite</h1>
<p class="muted">Primer pair screening report. Generated from the supplied sequences and settings.</p>
<div class="grid">
{_primer_html("Forward primer", data["forward"])}
{_primer_html("Reverse primer", data["reverse"])}
</div>
<section class="card"><h2>Pair-level checks</h2>
<dl><dt>Forward/reverse Tm difference</dt><dd>{data['tm_difference_celsius']:.2f} °C</dd>
<dt>Heterodimer Tm</dt><dd>{data['heterodimer_tm_celsius']:.2f} °C</dd>
<dt>Amplicon length</dt><dd>{escape(amp)}</dd></dl>
<h3>Warnings</h3><ul>{pair_warnings}</ul></section>
<section class="card"><h2>Calculation settings</h2><pre>{escape(__import__('json').dumps(data['settings'], indent=2))}</pre></section>
<section class="card"><h2>Limitations</h2><ul>{limitations}</ul></section>
<footer>PrimerCheck Lite is a research aid. Review parameters and validate primer performance experimentally.</footer>
</main></body></html>"""
    target = Path(path)
    target.write_text(html, encoding="utf-8")
    return target
