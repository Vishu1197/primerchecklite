"""Core screening functions.

These are screening heuristics, not a replacement for empirical validation or
genome-wide specificity analysis. Primer3 calculations use default thermodynamic
settings unless callers explicitly configure them in a future release.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from Bio.SeqUtils import gc_fraction

try:
    import primer3
except ImportError as exc:  # pragma: no cover
    primer3 = None
    _PRIMER3_IMPORT_ERROR = exc
else:
    _PRIMER3_IMPORT_ERROR = None


DNA_ALPHABET = set("ACGT")
IUPAC_ALPHABET = set("ACGTRYSWKMBDHVN")


@dataclass
class PrimerMetrics:
    sequence: str
    length: int
    gc_percent: float
    tm_celsius: float
    longest_homopolymer: int
    homopolymer_base: str
    hairpin_tm_celsius: float | None
    homodimer_tm_celsius: float | None
    three_prime_end: str
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PairReport:
    forward: PrimerMetrics
    reverse: PrimerMetrics
    heterodimer_tm_celsius: float | None
    tm_difference_celsius: float
    amplicon_length: int | None
    pair_warnings: list[str]
    settings: dict[str, Any]
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "forward": self.forward.to_dict(),
            "reverse": self.reverse.to_dict(),
            "heterodimer_tm_celsius": self.heterodimer_tm_celsius,
            "tm_difference_celsius": self.tm_difference_celsius,
            "amplicon_length": self.amplicon_length,
            "pair_warnings": self.pair_warnings,
            "settings": self.settings,
            "limitations": self.limitations,
        }


def normalize_sequence(sequence: str, *, allow_ambiguous: bool = False) -> str:
    """Normalize a primer sequence and reject non-IUPAC characters."""
    normalized = "".join(sequence.split()).upper()
    allowed = IUPAC_ALPHABET if allow_ambiguous else DNA_ALPHABET
    if not normalized:
        raise ValueError("Sequence is empty.")
    invalid = sorted(set(normalized) - allowed)
    if invalid:
        raise ValueError(
            "Sequence contains unsupported characters: "
            + ", ".join(invalid)
            + (". Use only A, C, G, and T for standard primer screening." if not allow_ambiguous else ".")
        )
    return normalized


def longest_homopolymer(sequence: str) -> tuple[int, str]:
    best_length = 0
    best_base = ""
    current_base = ""
    current_length = 0
    for base in sequence:
        if base == current_base:
            current_length += 1
        else:
            current_base = base
            current_length = 1
        if current_length > best_length:
            best_length, best_base = current_length, base
    return best_length, best_base


def _require_primer3() -> None:
    if primer3 is None:
        raise RuntimeError(
            "primer3-py is required for thermodynamic checks. Install with: "
            "pip install 'primerchecklite[ui]' or pip install primer3-py"
        ) from _PRIMER3_IMPORT_ERROR


def analyze_primer(
    sequence: str,
    *,
    min_length: int = 18,
    max_length: int = 30,
    target_tm_min: float = 57.0,
    target_tm_max: float = 63.0,
    target_gc_min: float = 40.0,
    target_gc_max: float = 60.0,
    max_homopolymer: int = 4,
    monovalent_salt_mM: float = 50.0,
    divalent_salt_mM: float = 1.5,
    dntp_mM: float = 0.6,
    primer_nM: float = 250.0,
) -> PrimerMetrics:
    """Calculate primer metrics using Biopython and Primer3."""
    _require_primer3()
    seq = normalize_sequence(sequence)
    gc = float(gc_fraction(seq) * 100.0)
    tm = float(primer3.calc_tm(
        seq,
        mv_conc=monovalent_salt_mM,
        dv_conc=divalent_salt_mM,
        dntp_conc=dntp_mM,
        dna_conc=primer_nM,
    ))
    hairpin = float(primer3.calc_hairpin(
        seq, mv_conc=monovalent_salt_mM, dv_conc=divalent_salt_mM,
        dntp_conc=dntp_mM, dna_conc=primer_nM
    ).tm)
    homodimer = float(primer3.calc_homodimer(
        seq, mv_conc=monovalent_salt_mM, dv_conc=divalent_salt_mM,
        dntp_conc=dntp_mM, dna_conc=primer_nM
    ).tm)
    run_length, run_base = longest_homopolymer(seq)

    warnings: list[str] = []
    if not min_length <= len(seq) <= max_length:
        warnings.append(f"Length {len(seq)} nt is outside the configured range ({min_length} to {max_length} nt).")
    if not target_tm_min <= tm <= target_tm_max:
        warnings.append(f"Estimated Tm {tm:.1f} °C is outside the configured range ({target_tm_min:.1f} to {target_tm_max:.1f} °C).")
    if not target_gc_min <= gc <= target_gc_max:
        warnings.append(f"GC content {gc:.1f}% is outside the configured range ({target_gc_min:.1f}% to {target_gc_max:.1f}%).")
    if run_length > max_homopolymer:
        warnings.append(f"Longest homopolymer is {run_base * run_length} ({run_length} bases), above the configured limit of {max_homopolymer}.")
    if hairpin >= 45.0:
        warnings.append(f"Potential hairpin structure has a predicted Tm of {hairpin:.1f} °C. Review under assay conditions.")
    if homodimer >= 45.0:
        warnings.append(f"Potential self-dimer has a predicted Tm of {homodimer:.1f} °C. Review under assay conditions.")
    if seq.endswith(("A", "T", "C", "G")):
        # A terminal G/C count is descriptive, not a standalone pass/fail criterion.
        gc_clamp = len(seq) - len(seq.rstrip("GC"))
        if gc_clamp == 0:
            warnings.append("Primer has no terminal G/C base. This is a descriptive flag, not an automatic rejection.")

    return PrimerMetrics(
        sequence=seq,
        length=len(seq),
        gc_percent=round(gc, 2),
        tm_celsius=round(tm, 2),
        longest_homopolymer=run_length,
        homopolymer_base=run_base,
        hairpin_tm_celsius=round(hairpin, 2),
        homodimer_tm_celsius=round(homodimer, 2),
        three_prime_end=seq[-5:],
        warnings=warnings,
    )


def find_amplicon_length(template: str, forward: str, reverse: str) -> int | None:
    """Find a single exact inward-facing amplicon in a supplied DNA template.

    This simple exact-match helper is intentionally not a genome-wide primer
    specificity search. It returns a length only when exactly one inward-facing
    pair of binding sites can be identified on the supplied sequence.
    """
    from Bio.Seq import Seq

    tmpl = normalize_sequence(template, allow_ambiguous=True)
    fwd = normalize_sequence(forward)
    rev_binding = str(Seq(normalize_sequence(reverse)).reverse_complement())
    forward_starts = [i for i in range(len(tmpl)) if tmpl.startswith(fwd, i)]
    reverse_starts = [i for i in range(len(tmpl)) if tmpl.startswith(rev_binding, i)]
    candidates = []
    for f_start in forward_starts:
        for r_start in reverse_starts:
            if r_start >= f_start + len(fwd):
                candidates.append((f_start, r_start + len(rev_binding)))
    if len(candidates) != 1:
        return None
    start, end = candidates[0]
    return end - start


def analyze_pair(
    forward: str,
    reverse: str,
    *,
    template: str | None = None,
    min_amplicon_length: int = 100,
    max_amplicon_length: int = 1000,
    **primer_settings: Any,
) -> PairReport:
    """Analyze two primers and produce a transparent pair-level report."""
    _require_primer3()
    fwd = analyze_primer(forward, **primer_settings)
    rev = analyze_primer(reverse, **primer_settings)
    settings = {
        "tm_model": "Primer3 default nearest-neighbor thermodynamic model",
        "monovalent_salt_mM": primer_settings.get("monovalent_salt_mM", 50.0),
        "divalent_salt_mM": primer_settings.get("divalent_salt_mM", 1.5),
        "dntp_mM": primer_settings.get("dntp_mM", 0.6),
        "primer_nM": primer_settings.get("primer_nM", 250.0),
        "tm_range_celsius": [
            primer_settings.get("target_tm_min", 57.0),
            primer_settings.get("target_tm_max", 63.0),
        ],
        "gc_range_percent": [
            primer_settings.get("target_gc_min", 40.0),
            primer_settings.get("target_gc_max", 60.0),
        ],
    }
    heterodimer = float(primer3.calc_heterodimer(
        fwd.sequence, rev.sequence,
        mv_conc=settings["monovalent_salt_mM"],
        dv_conc=settings["divalent_salt_mM"],
        dntp_conc=settings["dntp_mM"],
        dna_conc=settings["primer_nM"],
    ).tm)
    tm_difference = abs(fwd.tm_celsius - rev.tm_celsius)
    pair_warnings: list[str] = []
    if tm_difference > 5.0:
        pair_warnings.append(f"Primer Tm values differ by {tm_difference:.1f} °C. Review annealing conditions and design.")
    if heterodimer >= 45.0:
        pair_warnings.append(f"Potential cross-dimer has a predicted Tm of {heterodimer:.1f} °C. Review under assay conditions.")

    amplicon_length = None
    if template:
        amplicon_length = find_amplicon_length(template, fwd.sequence, rev.sequence)
        if amplicon_length is None:
            pair_warnings.append("Could not identify exactly one inward-facing, exact-match amplicon in the supplied template. Mismatches and genome-wide off-targets are not evaluated.")
        elif not min_amplicon_length <= amplicon_length <= max_amplicon_length:
            pair_warnings.append(
                f"Amplicon length {amplicon_length} bp is outside the configured range "
                f"({min_amplicon_length} to {max_amplicon_length} bp)."
            )

    limitations = [
        "Predictions depend on the configured concentrations, salt conditions, thermodynamic model, and assay conditions.",
        "Hairpin and dimer melting temperatures are screening signals, not definitive evidence of PCR failure.",
        "Exact amplicon matching checks only the supplied template and does not evaluate mismatches, variants, or genome-wide off-targets.",
        "This tool does not replace NCBI Primer-BLAST, in silico PCR against an appropriate reference, or wet-lab validation.",
    ]
    return PairReport(
        forward=fwd,
        reverse=rev,
        heterodimer_tm_celsius=round(heterodimer, 2),
        tm_difference_celsius=round(tm_difference, 2),
        amplicon_length=amplicon_length,
        pair_warnings=pair_warnings,
        settings=settings,
        limitations=limitations,
    )
