"""Core sequence validation, primer metrics, and threshold evaluation."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

try:
    import primer3
except ImportError:  # pragma: no cover
    primer3 = None

DNA_ALPHABET = set("ACGT")


@dataclass
class Threshold:
    minimum: float | None = None
    maximum: float | None = None
    unit: str = ""
    description: str = ""


DEFAULT_THRESHOLDS: dict[str, Threshold] = {
    "length": Threshold(18, 30, "nt", "Primer length. Very short or long primers may behave unpredictably."),
    "gc_percent": Threshold(40, 60, "%", "GC fraction affects duplex stability and primer binding."),
    "tm_c": Threshold(57, 63, "°C", "Estimated melting temperature under the selected chemical conditions."),
    "hairpin_tm_c": Threshold(None, 45, "°C", "Higher predicted hairpin Tm can indicate a stable folded primer."),
    "homodimer_tm_c": Threshold(None, 45, "°C", "Predicted interaction between two copies of the same primer."),
    "heterodimer_tm_c": Threshold(None, 45, "°C", "Predicted interaction between the forward and reverse primers."),
    "homopolymer": Threshold(None, 4, "bases", "Longest run of one repeated nucleotide."),
    "tm_difference_c": Threshold(None, 5, "°C", "Absolute difference between forward and reverse primer Tm."),
    "three_prime_gc_count": Threshold(1, 5, "bases", "Count of G/C bases in the final five nucleotides. Interpret with assay context."),
}


def normalize_sequence(sequence: str) -> str:
    """Normalize DNA input, allowing whitespace and FASTA header lines."""
    if not isinstance(sequence, str):
        raise ValueError("Sequence must be text.")
    lines = [line.strip() for line in sequence.splitlines() if line.strip()]
    sequence = "".join(line for line in lines if not line.startswith(">"))
    sequence = "".join(sequence.split()).upper().replace("U", "T")
    if not sequence:
        raise ValueError("Enter a DNA sequence.")
    invalid = sorted(set(sequence) - DNA_ALPHABET)
    if invalid:
        raise ValueError(f"Only A, C, G, and T are supported. Invalid characters: {', '.join(invalid)}")
    return sequence


def longest_homopolymer(sequence: str) -> int:
    best = current = 0
    previous = None
    for base in sequence:
        current = current + 1 if base == previous else 1
        best = max(best, current)
        previous = base
    return best


def _tm(sequence: str, settings: dict[str, float]) -> float:
    if primer3 is None:
        raise RuntimeError("Primer3 is required for Tm and structure calculations. Install primer3-py.")
    return float(primer3.calc_tm(
        sequence,
        mv_conc=settings["mv_conc"],
        dv_conc=settings["dv_conc"],
        dntp_conc=settings["dntp_conc"],
        dna_conc=settings["dna_conc"],
    ))


def analyze_primer(sequence: str, settings: dict[str, float] | None = None) -> dict[str, Any]:
    sequence = normalize_sequence(sequence)
    settings = settings or default_settings()
    tm = _tm(sequence, settings)
    if primer3 is None:
        raise RuntimeError("Primer3 is required for thermodynamic calculations.")
    hp = primer3.calc_hairpin(
        sequence, mv_conc=settings["mv_conc"], dv_conc=settings["dv_conc"],
        dntp_conc=settings["dntp_conc"]
    )
    hd = primer3.calc_homodimer(
        sequence, mv_conc=settings["mv_conc"], dv_conc=settings["dv_conc"],
        dntp_conc=settings["dntp_conc"]
    )
    return {
        "sequence": sequence,
        "length": len(sequence),
        "gc_percent": round(float(gc_fraction(sequence) * 100), 2),
        "tm_c": round(tm, 2),
        "hairpin_tm_c": round(float(hp.tm), 2),
        "homodimer_tm_c": round(float(hd.tm), 2),
        "homopolymer": longest_homopolymer(sequence),
        "three_prime_end": sequence[-5:],
        "three_prime_gc_count": sum(base in "GC" for base in sequence[-5:]),
    }


def default_settings() -> dict[str, float]:
    return {"mv_conc": 50.0, "dv_conc": 1.5, "dntp_conc": 0.2, "dna_conc": 50.0}


def default_threshold_values() -> dict[str, dict[str, Any]]:
    return {name: asdict(value) for name, value in DEFAULT_THRESHOLDS.items()}


def evaluate_value(value: float, threshold: dict[str, Any]) -> str:
    minimum, maximum = threshold.get("minimum"), threshold.get("maximum")
    if minimum is not None and value < minimum:
        return "review"
    if maximum is not None and value > maximum:
        return "review"
    return "within_range"


def _add_status(metrics: dict[str, Any], thresholds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = dict(metrics)
    statuses = {}
    for key, threshold in thresholds.items():
        if key in metrics and isinstance(metrics[key], (int, float)):
            statuses[key] = evaluate_value(float(metrics[key]), threshold)
    result["statuses"] = statuses
    return result


def find_amplicon(template: str, forward: str, reverse: str,
                  min_length: int = 1, max_length: int = 10000) -> dict[str, Any]:
    """Find one exact inward-facing product on a supplied template."""
    template = normalize_sequence(template)
    forward = normalize_sequence(forward)
    reverse_binding = str(Seq(normalize_sequence(reverse)).reverse_complement())
    candidates = []
    start = 0
    while True:
        fpos = template.find(forward, start)
        if fpos < 0:
            break
        rpos = template.find(reverse_binding, fpos + len(forward))
        while rpos >= 0:
            length = rpos + len(reverse_binding) - fpos
            if min_length <= length <= max_length:
                candidates.append({"start_0_based": fpos, "end_0_based_exclusive": rpos + len(reverse_binding),
                                   "length_bp": length})
            rpos = template.find(reverse_binding, rpos + 1)
        start = fpos + 1
    if len(candidates) == 1:
        return {"status": "unique_exact_product", **candidates[0]}
    if len(candidates) == 0:
        return {"status": "no_unique_exact_product", "message": "No exact inward-facing product was found within the selected length range."}
    return {"status": "ambiguous", "candidate_count": len(candidates),
            "message": "Multiple exact products were found. Review specificity separately."}


def analyze_pair(
    forward: str,
    reverse: str,
    template: str | None = None,
    settings: dict[str, float] | None = None,
    thresholds: dict[str, dict[str, Any]] | None = None,
    amplicon_min: int = 1,
    amplicon_max: int = 10000,
) -> dict[str, Any]:
    settings = settings or default_settings()
    thresholds = thresholds or default_threshold_values()
    f = analyze_primer(forward, settings)
    r = analyze_primer(reverse, settings)
    hetero = primer3.calc_heterodimer(
        f["sequence"], r["sequence"], mv_conc=settings["mv_conc"],
        dv_conc=settings["dv_conc"], dntp_conc=settings["dntp_conc"]
    )
    pair_metrics = {
        "tm_difference_c": round(abs(f["tm_c"] - r["tm_c"]), 2),
        "heterodimer_tm_c": round(float(hetero.tm), 2),
    }
    f = _add_status(f, thresholds)
    r = _add_status(r, thresholds)
    pair_metrics = _add_status(pair_metrics, thresholds)
    warnings = []
    for label, primer in (("Forward", f), ("Reverse", r)):
        for metric, status in primer["statuses"].items():
            if status == "review":
                t = thresholds[metric]
                warnings.append(f"{label} primer: {metric.replace('_', ' ')} is {primer[metric]}, outside the configured range ({t.get('minimum')} to {t.get('maximum')} {t.get('unit', '')}).")
    for metric, status in pair_metrics["statuses"].items():
        if status == "review":
            t = thresholds[metric]
            warnings.append(f"Primer pair: {metric.replace('_', ' ')} is {pair_metrics[metric]}, outside the configured range ({t.get('minimum')} to {t.get('maximum')} {t.get('unit', '')}).")
    amplicon = find_amplicon(template, f["sequence"], r["sequence"], amplicon_min, amplicon_max) if template else None
    return {
        "forward": f,
        "reverse": r,
        "pair": pair_metrics,
        "warnings": warnings,
        "settings": settings,
        "thresholds": thresholds,
        "amplicon": amplicon,
        "limitations": [
            "Thresholds are configurable screening guides, not universal PCR rules.",
            "Exact template matching is not genome-wide specificity analysis.",
            "In silico metrics do not establish amplification efficiency or experimental success.",
        ],
    }
