# PrimerCheck Lite

Local-first screening of PCR primer pairs with interpretable metrics, adjustable thresholds, and downloadable reports.

PrimerCheck Lite helps researchers inspect an existing forward and reverse primer pair before moving to more complete target-specificity checks or wet-lab validation. It reports sequence length, GC percentage, estimated melting temperature, homopolymer runs, predicted hairpin and dimer metrics, Tm difference, and optional exact-match amplicon length on a supplied template.

**Scope:** PrimerCheck Lite is a first-pass screening aid. It does not perform genome-wide specificity analysis and does not replace [NCBI Primer-BLAST](https://www.ncbi.nlm.nih.gov/tools/primer-blast/), in silico PCR against a suitable reference, or experimental validation.

## Why this tool?

For the narrow task of checking a primer pair already in hand, the goal is to make the workflow quick and understandable:
- Paste both primers on one screen.
- See metrics and plain-language warnings together.
- Adjust common thresholds and concentration assumptions.
- Save a self-contained HTML report or machine-readable JSON.
- Keep unpublished sequences on your own machine by default.

This is a usability goal, not a claim of superior biological accuracy to Primer-BLAST.

## Features

- DNA sequence normalization and validation.
- GC percentage from Biopython.
- Thermodynamic calculations through primer3-py.
- Length, Tm, GC, homopolymer, hairpin, homodimer, and heterodimer checks.
- Optional exact-match amplicon check against a supplied template.
- CLI and local Streamlit interface.
- JSON and HTML reports.
- Scientific methods and limitations documentation.
- Automated tests and GitHub Actions workflow.

## Installation

Python 3.10 or later is recommended.

```bash
git clone https://github.com/YOUR-USERNAME/primerchecklite.git
cd primerchecklite
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[ui,dev]"
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Quick start: web UI

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. Analysis runs locally. The app does not need an account or upload sequences to a remote service.

## Quick start: CLI

```bash
primerchecklite check \
  --forward ATGACCTACTTCGACGACGA \
  --reverse TCAGGATCTTGTCGATGTCG \
  --json-out report.json \
  --html-out report.html
```

The example sequences are software demonstration inputs only. They are not claimed to be validated for a biological target.

To check an optional template:

```bash
primerchecklite check \
  --forward ATGACCTACTTCGACGACGA \
  --reverse TCAGGATCTTGTCGATGTCG \
  --template examples/synthetic_template.fasta \
  --json-out report.json \
  --html-out report.html
```

See all options:

```bash
primerchecklite check --help
```

## What the results mean

| Metric | Meaning |
|---|---|
| Length | Number of nucleotides in the primer |
| GC percentage | Fraction of bases that are G or C |
| Estimated Tm | Primer3 predicted melting temperature under the shown settings |
| Hairpin Tm | Predicted melting temperature associated with a hairpin structure |
| Homodimer Tm | Predicted self-dimer metric |
| Heterodimer Tm | Predicted interaction metric between forward and reverse primers |
| Homopolymer | Longest run of a repeated nucleotide |
| Tm difference | Absolute difference between forward and reverse estimated Tm values |
| Amplicon length | Exact-match product length only if one inward-facing pair is found on the supplied template |

Warnings are heuristics and prompts for review. They are not proof of failure. Read [the scientific methods](docs/scientific-methods.md) and [limitations](docs/limitations.md).

## Specificity matters

A primer pair can have acceptable GC content and Tm yet amplify unintended genomic regions. PrimerCheck Lite does not search genome databases, evaluate off-target alignments, or account for variants. For target specificity, use [NCBI Primer-BLAST](https://www.ncbi.nlm.nih.gov/tools/primer-blast/) or another validated in silico PCR workflow against the correct organism and reference assembly.

## Development and tests

```bash
pip install -e ".[dev,ui]"
pytest
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and [prompt.md](prompt.md) for the detailed AI coding agent brief.

## Scientific references

- Untergasser A, et al. Primer3: new capabilities and interfaces. *Nucleic Acids Research*. 2012;40(15):e115. https://doi.org/10.1093/nar/gks596
- Biopython: https://biopython.org/
- primer3-py: https://libnano.github.io/primer3-py/
- NCBI Primer-BLAST: https://www.ncbi.nlm.nih.gov/tools/primer-blast/

Verify the references, software versions, and parameters before citing this software in a publication.

## Status

Early development. Review scientific assumptions, run the test suite in a clean environment, and validate results against the installed Primer3 version before using it for a research decision.

## License

MIT. See [LICENSE](LICENSE).
