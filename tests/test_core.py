import pytest

from primerchecklite.core import (
    analyze_pair,
    analyze_primer,
    find_amplicon_length,
    longest_homopolymer,
    normalize_sequence,
)


def test_normalize_sequence():
    assert normalize_sequence("  atgc\n") == "ATGC"


@pytest.mark.parametrize("sequence", ["", "ATGX", "ATG-N"])
def test_invalid_sequence_rejected(sequence):
    with pytest.raises(ValueError):
        normalize_sequence(sequence)


def test_homopolymer():
    assert longest_homopolymer("AACCCGT") == (3, "C")
    assert longest_homopolymer("ATGC") == (1, "A")


def test_exact_amplicon_length():
    # Forward site at 0, reverse primer binds as reverse complement at positions 12 to 20.
    template = "ATGCGTACGTAA" + "CC" + "CGACATCGAC"
    forward = "ATGCGTACGTAA"
    reverse = "GTCGATGTCG"
    assert find_amplicon_length(template, forward, reverse) == 24


def test_no_amplicon_when_sites_missing():
    assert find_amplicon_length("ACGTACGT", "AAAA", "CCCC") is None


def test_analyze_primer_has_metrics():
    pytest.importorskip("primer3")
    result = analyze_primer("ATGACCTACTTCGACGACGA")
    assert result.length == 20
    assert 0 <= result.gc_percent <= 100
    assert isinstance(result.tm_celsius, float)


def test_pair_report_contains_limitations():
    pytest.importorskip("primer3")
    result = analyze_pair("ATGACCTACTTCGACGACGA", "TCAGGATCTTGTCGATGTCG")
    data = result.to_dict()
    assert "limitations" in data
    assert "heterodimer_tm_celsius" in data
    assert len(data["limitations"]) >= 3
