"""Command line interface."""
from pathlib import Path
import json
import typer
from rich.console import Console
from rich.table import Table
from .core import analyze_pair, default_settings, default_threshold_values
from .reporting import write_html, write_json

app = typer.Typer(help="Beginner-friendly PCR/qRT-PCR primer screening.")
console = Console()


@app.command()
def check(
    forward: str = typer.Option(..., "--forward", help="Forward primer sequence, 5′ to 3′."),
    reverse: str = typer.Option(..., "--reverse", help="Reverse primer sequence, 5′ to 3′."),
    template: Path | None = typer.Option(None, "--template", exists=True, readable=True),
    json_out: Path = typer.Option(Path("primerchecklite-report.json"), "--json-out"),
    html_out: Path = typer.Option(Path("primerchecklite-report.html"), "--html-out"),
    mv_conc: float = typer.Option(50.0, help="Monovalent salt concentration in mM."),
    dv_conc: float = typer.Option(1.5, help="Divalent salt concentration in mM."),
    dntp_conc: float = typer.Option(0.2, help="dNTP concentration in mM."),
    dna_conc: float = typer.Option(50.0, help="Primer concentration in nM."),
):
    """Analyze a primer pair and save JSON and HTML reports."""
    settings = {"mv_conc": mv_conc, "dv_conc": dv_conc, "dntp_conc": dntp_conc, "dna_conc": dna_conc}
    template_text = template.read_text(encoding="utf-8") if template else None
    result = analyze_pair(forward, reverse, template_text, settings, default_threshold_values())
    write_json(result, json_out)
    write_html(result, html_out)
    table = Table(title="PrimerCheck Lite results")
    table.add_column("Primer")
    table.add_column("Length")
    table.add_column("GC %")
    table.add_column("Tm °C")
    for name in ("forward", "reverse"):
        p = result[name]
        table.add_row(name.title(), str(p["length"]), str(p["gc_percent"]), str(p["tm_c"]))
    console.print(table)
    if result["warnings"]:
        console.print("[yellow]Review these configured threshold warnings:[/yellow]")
        for warning in result["warnings"]:
            console.print(f"• {warning}")
    else:
        console.print("[green]All evaluated metrics are within configured thresholds.[/green]")
    console.print(f"JSON report: {json_out.resolve()}")
    console.print(f"HTML report: {html_out.resolve()}")


if __name__ == "__main__":
    app()
