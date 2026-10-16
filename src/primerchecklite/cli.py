"""Command line interface."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from primerchecklite import __version__
from primerchecklite.core import analyze_pair
from primerchecklite.reporting import write_html_report, write_json_report

app = typer.Typer(
    name="primerchecklite",
    help="Screen PCR primer pairs with interpretable local checks.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"PrimerCheck Lite {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """PrimerCheck Lite: fast local primer screening, not genome-wide specificity analysis."""


@app.command()
def check(
    forward: str = typer.Option(..., "--forward", "-f", help="Forward primer, 5' to 3'."),
    reverse: str = typer.Option(..., "--reverse", "-r", help="Reverse primer, 5' to 3'."),
    template_file: Optional[Path] = typer.Option(None, "--template", help="Optional FASTA or plain-text template file."),
    json_out: Path = typer.Option(Path("primerchecklite-report.json"), "--json-out", help="JSON report path."),
    html_out: Path = typer.Option(Path("primerchecklite-report.html"), "--html-out", help="HTML report path."),
    min_amplicon: int = typer.Option(100, "--min-amplicon", min=1),
    max_amplicon: int = typer.Option(1000, "--max-amplicon", min=1),
    min_tm: float = typer.Option(57.0, "--min-tm"),
    max_tm: float = typer.Option(63.0, "--max-tm"),
    monovalent_salt: float = typer.Option(50.0, "--monovalent-salt", help="Monovalent salt concentration in mM."),
    divalent_salt: float = typer.Option(1.5, "--divalent-salt", help="Divalent salt concentration in mM."),
    dntp: float = typer.Option(0.6, "--dntp", help="dNTP concentration in mM."),
    primer_conc: float = typer.Option(250.0, "--primer-conc", help="Primer concentration in nM."),
) -> None:
    """Analyze a primer pair and save JSON and HTML reports."""
    if min_amplicon > max_amplicon:
        raise typer.BadParameter("--min-amplicon must be less than or equal to --max-amplicon.")
    if min_tm > max_tm:
        raise typer.BadParameter("--min-tm must be less than or equal to --max-tm.")
    template = None
    if template_file:
        if not template_file.is_file():
            raise typer.BadParameter(f"Template file not found: {template_file}")
        raw = template_file.read_text(encoding="utf-8")
        template = "".join(line.strip() for line in raw.splitlines() if not line.startswith(">"))
    try:
        report = analyze_pair(
            forward, reverse, template=template,
            min_amplicon_length=min_amplicon, max_amplicon_length=max_amplicon,
            target_tm_min=min_tm, target_tm_max=max_tm,
            monovalent_salt_mM=monovalent_salt,
            divalent_salt_mM=divalent_salt,
            dntp_mM=dntp,
            primer_nM=primer_conc,
        ).to_dict()
    except (ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    write_json_report(report, json_out)
    write_html_report(report, html_out)
    table = Table(title="PrimerCheck Lite screening")
    table.add_column("Metric")
    table.add_column("Forward")
    table.add_column("Reverse")
    for key, label, fmt in [
        ("length", "Length (nt)", lambda x: str(x)),
        ("gc_percent", "GC (%)", lambda x: f"{x:.1f}"),
        ("tm_celsius", "Estimated Tm (°C)", lambda x: f"{x:.1f}"),
        ("hairpin_tm_celsius", "Hairpin Tm (°C)", lambda x: f"{x:.1f}"),
        ("homodimer_tm_celsius", "Self-dimer Tm (°C)", lambda x: f"{x:.1f}"),
    ]:
        table.add_row(label, fmt(report["forward"][key]), fmt(report["reverse"][key]))
    console.print(table)
    console.print(f"Pair Tm difference: {report['tm_difference_celsius']:.2f} °C")
    console.print(f"Heterodimer Tm: {report['heterodimer_tm_celsius']:.2f} °C")
    if report["amplicon_length"] is not None:
        console.print(f"Exact-match amplicon: {report['amplicon_length']} bp")
    for warning in report["forward"]["warnings"] + report["reverse"]["warnings"] + report["pair_warnings"]:
        console.print(f"[yellow]Warning:[/yellow] {warning}")
    console.print(f"JSON report: {json_out}")
    console.print(f"HTML report: {html_out}")


if __name__ == "__main__":
    app()
