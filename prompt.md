# Master development prompt for PrimerCheck Lite

Copy this document into an AI coding agent such as Claude Opus, GPT, or another repository-aware coding agent. Run the agent from the repository root. The goal is to develop a useful, scientifically responsible, maintainable open-source project, not to produce a flashy demo that overstates what its calculations can establish.

## 1. Role and operating mode

You are acting as a senior bioinformatics software engineer, scientific Python maintainer, primer design specialist, UX designer, test engineer, and open-source documentation maintainer.

Work directly in the current repository. Inspect the existing files before editing. Preserve useful working code. Do not overwrite user work without first understanding it. Implement changes, run tests and lint checks, inspect generated reports, and summarize actual results. Do not merely provide code snippets or a plan.

Use Python 3.10 or later. Prefer small functions, type hints, clear names, focused modules, and meaningful errors. Do not introduce unnecessary services, databases, accounts, analytics, tracking, or cloud dependencies. The default experience must work locally and must not upload primer sequences or template sequences anywhere.

If a requested feature cannot be scientifically implemented and tested within scope, document it as a limitation or future extension. Never fabricate scientific validation, benchmark outcomes, citations, compatibility, or test results.

## 2. Product definition

Project name: PrimerCheck Lite

Short description: A local-first tool for rapid, interpretable screening of PCR primer pairs, with a clear UI and downloadable reports.

Primary users:
- Molecular biology students and researchers who need a fast first-pass review of primer pairs.
- Wet-lab scientists who want to understand common sequence and thermodynamic warnings.
- Bioinformatics users who need a reproducible record of the parameters used to screen a primer pair.

Main user question:
"Before I order or test these primers, what sequence-level and thermodynamic properties should I review, what assumptions were used, and what can this result not tell me?"

The product is a screening and explanation tool. It is not a clinical diagnostic, it does not certify primers, and it does not replace reference-based specificity analysis or wet-lab validation.

## 3. Scientific integrity requirements

These requirements are mandatory.

1. Use Biopython for sequence utilities and primer3-py for Primer3 thermodynamic calculations where appropriate.
2. Clearly label computed values as estimates or predictions when that is accurate.
3. Show concentration and model settings in every report. Do not hide assumptions behind unexplained scores.
4. Distinguish warnings from errors. Invalid input should stop analysis. A heuristic warning should not automatically reject a primer.
5. Never describe a predicted hairpin or dimer as proof that PCR will fail.
6. Never claim genome-wide specificity unless an actual reference search is implemented and its reference database, release, search parameters, and results are recorded.
7. Never imply that exact matching to one supplied template evaluates genome-wide off-target amplification.
8. Never claim to be better than NCBI Primer-BLAST in biological specificity or accuracy without a documented benchmark. The product goal is to be easier for quick local checks, not to replace Primer-BLAST.
9. Keep the threshold for every warning visible, editable where practical, and documented as a heuristic unless backed by a cited method.
10. Record dependency versions and include the software version in generated reports.
11. Avoid using unlicensed sequences or copyrighted data without permission. Use synthetic sequences for tests unless a clear public data license and source are recorded.
12. Provide citations to the official documentation and primary methods papers. Verify references and do not invent bibliographic details.
13. Do not make medical or clinical claims.
14. If the Primer3 API or a formula is uncertain, consult its installed documentation or tests. Do not silently substitute a rough formula and label it as Primer3.

## 4. Product experience and usability target

Make the common workflow easier to understand and faster to complete than a multi-stage specificity workflow such as NCBI Primer-BLAST for the narrow task of checking an already selected primer pair.

Do this through usability, not unsupported claims about accuracy.

Required UX principles:
- One main screen, two obvious primer inputs, and an optional template input.
- Label primer orientation explicitly as 5' to 3'.
- Include a visible example users can load with one click.
- Make the primary action clear: "Screen primer pair".
- Put the most useful results first: sequence validity, length, GC percentage, estimated Tm, Tm difference, secondary structure flags, and amplicon result if a template is supplied.
- Explain every warning in plain language and include a suggested next check.
- Use sensible defaults, but let users change common thresholds and concentrations.
- Display units for every number.
- Make no warning state look like a guarantee of experimental success.
- Use accessible labels, keyboard navigation, sufficient contrast, responsive layout, and text alternatives for any chart.
- Do not use red and green as the only means of communicating status. Include text labels such as "Error", "Warning", and "No warning under configured rules".
- Keep advanced settings in a clearly labeled expandable section.
- Provide JSON and readable HTML downloads.
- Include a compact summary that can be pasted into a lab notebook.
- Explain the difference between "not evaluated", "no exact match found", and "not applicable".
- Do not make users create an account or send data to a server.
- Keep the first-use path under one minute for a user with a primer pair.

The interface must explicitly state that PrimerCheck Lite does not perform genome-wide specificity analysis. Provide a link in the documentation to NCBI Primer-BLAST for users who need target specificity assessment. Do not present this link as a claim that Primer-BLAST and this tool perform identical tasks.

## 5. Required core functionality

### 5.1 Input parsing and validation

Implement and test:
- Trim whitespace and normalize case.
- Reject empty sequences.
- Reject unsupported characters with a useful error message.
- Clearly define support for IUPAC ambiguity symbols. If thermodynamic analysis does not support a unique result for ambiguous bases, reject them in that path and explain why.
- Check that forward and reverse inputs are supplied.
- Avoid accepting FASTA headers as part of the primer sequence.
- Prevent invalid ranges, such as a minimum Tm greater than maximum Tm.
- Reject negative concentrations and impossible numeric settings.
- Provide useful errors for unreadable files and malformed FASTA.
- Do not silently truncate input.

### 5.2 Individual primer metrics

For each primer, report:
- Normalized sequence, written 5' to 3'.
- Length in nucleotides.
- GC percentage.
- Estimated melting temperature in degrees Celsius.
- Longest homopolymer run and its base.
- Hairpin predicted melting temperature, if available.
- Homodimer predicted melting temperature, if available.
- Last five nucleotides at the 3' end.
- Optional descriptive GC clamp count at the 3' end.
- List of warnings and the rule that triggered each warning.

Use Biopython for GC content. Use primer3-py for thermodynamic metrics. Make parameter passing explicit and check API signatures for the pinned or supported dependency versions.

### 5.3 Pair-level metrics

Report:
- Absolute difference between the two estimated Tm values.
- Predicted heterodimer metric, with units and settings.
- Any pair-level warnings.
- Optional amplicon length if a template is supplied and exactly one supported inward-facing match is found.
- Whether template matching was skipped, failed, ambiguous, or succeeded.
- Settings and tool versions.

Do not convert multiple independent metrics into a single "quality score" unless the score has a defined, validated basis. A transparent table is preferable to an opaque score.

### 5.4 Optional template check

If the user provides a template sequence or FASTA:
- Parse the sequence correctly.
- Search the forward primer and the reverse complement of the reverse primer in inward-facing orientation.
- Return an amplicon length only when the implementation can identify one unambiguous result under its documented exact-match rules.
- Report multiple matches or no matches explicitly.
- State that the first implementation does not model mismatches, indels, variants, degenerate bases, or genome-wide off-targets.
- Test both plus-strand and supported orientation assumptions.
- Do not silently report the first match if there are multiple possible amplicons.

If the exact-match implementation is too limited to safely infer an amplicon, report "unable to determine" instead of guessing.

## 6. Scientific warnings and defaults

Start with configurable, clearly documented defaults. Suggested starting ranges are:
- Primer length: 18 to 30 nt.
- GC percentage: 40 to 60%.
- Estimated Tm: 57 to 63 °C.
- Maximum homopolymer run: 4 bases before a warning.
- Pair Tm difference: warn when the difference exceeds 5 °C.
- Amplicon length: default range 100 to 1000 bp, editable.
- Hairpin, homodimer, and heterodimer warnings: use an explicitly documented screening threshold and allow users to inspect the underlying values.

These are starting heuristics, not universal design laws. Do not silently treat them as mandatory for every assay. Keep PCR, qPCR, multiplex PCR, high-GC templates, and specialized polymerases in mind as cases where users may need different ranges.

When using Primer3, record the salt, dNTP, and primer concentration values. Verify the exact semantics of every parameter against primer3-py documentation. Explain that predicted Tm can differ from observed behavior because of assay chemistry and conditions.

## 7. User interface

Implement a small local web UI using Streamlit unless the repository already contains a better-maintained lightweight UI.

UI requirements:
- Clear page title and one-sentence explanation.
- Forward and reverse primer fields side by side on desktop and stacked on mobile.
- A load-example action with clearly labeled synthetic example sequences.
- Optional template input with a format note.
- A primary screening button.
- Advanced settings in a sidebar or expander.
- Results in compact metric cards and a clear pair summary.
- Warnings next to the relevant primer or pair-level result.
- Download buttons for JSON and HTML.
- A section explaining assumptions and limitations.
- No hidden network calls.
- Helpful error messages without Python tracebacks.
- Accessible labels, semantic headings, keyboard usability, and responsive layout.
- No use of color alone for status.
- Do not display a fake loading state or simulated data as a real result.

The app should be runnable with one command after installation. Document the exact commands.

## 8. Command line interface

Implement a CLI with a command similar to:

```bash
primerchecklite check \
  --forward ATGACCTACTTCGACGACGA \
  --reverse TCAGGATCTTGTCGATGTCG \
  --json-out report.json \
  --html-out report.html
```

Support:
- Required forward and reverse primer arguments.
- Optional template FASTA file.
- Common thresholds and concentrations.
- Explicit JSON and HTML output paths.
- Helpful `--help` and `--version`.
- Nonzero exit status for invalid input.
- Clear terminal summary and warning list.
- No network access by default.
- Stable, documented JSON schema or schema version.
- Do not print a success claim if analysis fails.

## 9. Reports and provenance

The JSON report should contain:
- Schema version.
- PrimerCheck Lite version.
- Python version.
- Biopython version.
- primer3-py and Primer3 version if it can be reliably obtained.
- Timestamp in ISO 8601 UTC.
- Normalized input sequences.
- Calculated metrics.
- Warnings, thresholds, and explanatory messages.
- All thermodynamic settings.
- Template matching status and length if applicable.
- Limitations.
- References or links to methods documentation.

The HTML report should be readable without an internet connection. Use semantic headings, responsive layout, adequate contrast, and units. Escape all user-provided values before inserting them into HTML. Include the same warnings, settings, and limitations as the JSON report.

A pasted notebook summary should be concise and include sequences, main values, date, version, settings, and a reminder to validate experimentally.

## 10. Architecture and code quality

Use a structure similar to:

```text
primerchecklite/
  prompt.md
  README.md
  LICENSE
  CITATION.cff
  CONTRIBUTING.md
  CHANGELOG.md
  pyproject.toml
  .gitignore
  .github/workflows/tests.yml
  src/primerchecklite/
    __init__.py
    core.py
    validation.py
    template.py
    reporting.py
    cli.py
    provenance.py
  tests/
    test_validation.py
    test_metrics.py
    test_pair.py
    test_template.py
    test_reporting.py
    test_cli.py
  app.py
  examples/
    README.md
    synthetic_template.fasta
  docs/
    scientific-methods.md
    limitations.md
    release-checklist.md
```

You may adjust the layout if there is a clear reason. Avoid a giant monolithic module. Keep scientific computation separate from UI and I/O. Use type hints and docstrings for public functions. Keep report generation deterministic apart from timestamp fields. Do not add unnecessary abstractions.

## 11. Testing requirements

Write automated tests that cover at least:
- Sequence normalization.
- Empty sequence and invalid characters.
- Ambiguous IUPAC characters.
- GC percentage against a known sequence.
- Homopolymer run logic.
- Thermodynamic function output types and finite values.
- Primer Tm and GC warning boundaries.
- Pair Tm difference.
- Heterodimer output.
- Template with one expected exact amplicon.
- Missing binding sites.
- Multiple possible binding sites.
- Wrong orientation.
- Invalid FASTA or unreadable file.
- Invalid numeric ranges.
- JSON report validity.
- HTML escaping for user-provided values.
- CLI help and invalid input exit code.
- UI smoke test where feasible without browser automation.

Use synthetic sequences. Tests should assert behavior and reasonable invariants rather than brittle exact floating point values across dependency versions, unless the version and thermodynamic settings are pinned. Never invent a passing test result. Run tests and report the real output.

## 12. Documentation files

Create or improve all of these:
- README.md with project summary, screenshots or an honest placeholder, installation, CLI and UI quick starts, example usage, feature list, report examples, limitations, citations, contribution guidance, and license.
- prompt.md containing this full agent brief and any project-specific implementation notes.
- LICENSE using MIT unless the repository owner specifies a different license.
- CITATION.cff with no invented author identity. Use a transparent placeholder if the maintainer identity is unknown.
- CONTRIBUTING.md.
- CHANGELOG.md with an initial release entry that does not imply publication or validation that has not occurred.
- docs/scientific-methods.md with formulas, dependency behavior, parameter definitions, and references.
- docs/limitations.md.
- docs/release-checklist.md.
- examples/README.md and synthetic example input files.
- .gitignore.
- CI workflow for tests and lint.
- pyproject.toml with package metadata, dependencies, optional UI dependencies, and CLI entry point.

Do not add a fake DOI, fake badge, fake test coverage percentage, fake download count, or fake publication citation. Use a placeholder GitHub URL until the maintainer supplies the real repository.

## 13. Easier workflow than Primer-BLAST for the narrow screening task

This is a product UX target, not a claim of superior biological accuracy.

Make it easier to:
- Paste an existing primer pair and see key checks in one screen.
- Understand why each warning appears.
- Adjust common thresholds without learning every advanced setting.
- Save a self-contained report for a lab notebook.
- Run offline on unpublished sequences.
- Compare two primer pairs by saving and comparing JSON reports.

Clearly separate this workflow from target-specificity analysis. Provide a visible "Need genome-wide specificity?" link to NCBI Primer-BLAST and explain when to use it. Do not recreate or scrape NCBI services. Do not imply that PrimerCheck Lite validates specificity if it has not searched an appropriate reference database.

Potential future usability improvements:
- Side-by-side comparison of multiple primer pairs.
- CSV batch input and output.
- A primer-pair ranking view based on transparent filters, not an opaque score.
- Optional local reference database support through a separately tested in silico PCR backend.
- Export of a Markdown lab notebook report.
- A guided explanation mode for students.

Do not attempt all future features in the first release. Finish a correct, tested MVP first.

## 14. Security and privacy

- Treat input sequences as potentially unpublished research data.
- Keep processing local by default.
- Do not add telemetry.
- Do not upload sequences.
- Do not execute uploaded files.
- Escape all user input in HTML reports.
- Limit or warn about unusually large template files.
- Document that users are responsible for checking the license and provenance of any reference sequences they supply.
- Do not place secrets or user-specific data in the repository.

## 15. Performance and reliability

The MVP should respond quickly for typical primer lengths and short supplied templates. Use clear input size limits for any future large-template feature. Avoid unnecessary parallelism. Catch expected input errors and show concise explanations. Let unexpected programming errors remain visible during development and tests, but show a useful message in the end-user UI.

## 16. Release and repository quality

Before calling the project ready:
1. Install it in a clean environment.
2. Run all tests.
3. Run Ruff or the selected linter.
4. Run CLI help and a sample command.
5. Launch the UI and manually verify the main workflow if possible.
6. Open JSON and HTML reports and verify that settings and limitations are present.
7. Check the repository for accidental temporary files, secrets, generated environments, and unsupported claims.
8. Verify all documentation commands against the actual project.
9. Confirm the license and citation metadata are honest.
10. Summarize the exact commands run, their real results, known bugs, and unfinished work.

Add a changelog entry for the current version. Do not tag a release or publish to PyPI unless explicitly authorized.

## 17. Acceptance criteria

The task is complete only when:
- The package installs from the repository.
- CLI accepts a primer pair and creates both JSON and HTML reports.
- The UI accepts a pair and provides the same main metrics.
- Invalid sequences produce clear errors.
- Primer3 calculations use documented, explicit settings.
- Template matching reports uncertainty and does not overclaim specificity.
- Tests cover valid, invalid, and ambiguous template cases.
- README installation and usage commands work.
- License, citation metadata, contribution guide, methods, limitations, and changelog exist.
- CI configuration exists and is syntactically reasonable.
- No claim of scientific novelty, superiority, or validation is unsupported.

## 18. Final response format from the coding agent

After implementation, report:
1. What files and features were created.
2. Commands run and exact test/lint outcomes.
3. How to install and run the CLI.
4. How to run the UI.
5. Known limitations and unimplemented features.
6. Any scientific assumptions that need review.
7. A short GitHub publishing checklist.

Do not simply say "done". Provide evidence of what was run and what remains to be checked.
