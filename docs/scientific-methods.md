# Scientific methods

PrimerCheck Lite uses Biopython for sequence normalization and GC fraction, and Primer3 through `primer3-py` for melting temperature and secondary structure estimates.

## Metrics

- Length: number of bases in the normalized primer.
- GC percentage: 100 multiplied by the fraction of G and C bases.
- Tm: Primer3's estimate using the configured monovalent salt, divalent salt, dNTP, and primer concentrations.
- Hairpin Tm: Primer3 estimate for an intramolecular hairpin.
- Homodimer Tm: Primer3 estimate for interaction between two copies of the same primer.
- Heterodimer Tm: Primer3 estimate for interaction between forward and reverse primers.
- Tm difference: absolute difference between the two individual primer Tm estimates.
- Homopolymer: longest consecutive run of one base.
- Three prime GC count: number of G/C bases among the last five bases.
- Template amplicon: exact forward-primer match plus exact reverse-complement match in inward-facing orientation, within the selected length range.

## Threshold interpretation

The initial ranges are editable teaching defaults. They are not universal acceptance limits. Real primer suitability depends on target sequence, assay chemistry, polymerase, instrument, reaction setup, and validation data. A metric within range is not proof that the primer is suitable.
