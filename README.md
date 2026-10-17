# PrimerCheck Lite

A beginner friendly local tool for screening existing PCR and qRT-PCR primer pairs. It calculates sequence metrics, estimates thermodynamic properties with Primer3, applies editable thresholds, and exports JSON and HTML reports.

This project keeps a small, familiar architecture:

```text
primerchecklite/
├── app.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CITATION.cff
├── prompt.md
├── src/primerchecklite/
│   ├── __init__.py
│   ├── core.py
│   ├── cli.py
│   └── reporting.py
├── docs/
│   ├── scientific-methods.md
│   └── limitations.md
├── examples/
│   └── synthetic_template.fasta
└── tests/
    └── test_core.py
```

## Quick start

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[ui,dev]"
streamlit run app.py
```

The interface has a guided input page, editable minimum and maximum thresholds, explanations for each metric, clear status colors, and JSON/HTML downloads.

## Command line

```bash
primerchecklite check \
  --forward ATGACCTACTTCGACGACGA \
  --reverse TCAGGATCTTGTCGATGTCG \
  --json-out report.json \
  --html-out report.html
```

Optional template:

```bash
primerchecklite check \
  --forward ATGACCTACTTCGACGACGA \
  --reverse TCAGGATCTTGTCGATGTCG \
  --template examples/synthetic_template.fasta
```

## Thresholds

Each quantitative screening metric can be reviewed against configurable limits in the interface. The initial values are educational starting points, not universal standards. Choose thresholds based on the assay, polymerase, buffer, instrument, target, and validated laboratory protocol. Some metrics, such as homopolymer length, are naturally expressed as a maximum; the interface still provides explicit limits where that makes sense.

## Important scientific limitation

This is a preliminary screening tool. Good scores do not prove target specificity, amplification efficiency, or successful qPCR. The template check uses exact sequence matches and is not a genome-wide specificity search. Use Primer BLAST or an appropriate in silico PCR workflow for specificity, and validate primers experimentally.

PrimerCheck Lite is not a substitute for a validated assay or laboratory protocol.
