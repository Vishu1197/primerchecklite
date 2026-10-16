# Scientific methods and interpretation

## Sequence validation

The first release accepts standard DNA primer sequences containing only A, C, G, and T. Whitespace is removed and letters are converted to uppercase. Ambiguous IUPAC symbols are rejected for primer thermodynamic analysis because the package does not calculate a unique thermodynamic value for a mixed base at that position.

## GC content

GC percentage is calculated with Biopython `Bio.SeqUtils.gc_fraction`, multiplied by 100. The default suggested range is 40 to 60 percent. Users can change the range. This range is a screening convention, not a universal rule.

## Melting temperature

Primer melting temperature and predicted secondary structure metrics are computed with `primer3-py`. The selected concentrations are included in the report. The result depends on salt concentrations, primer concentration, dNTP concentration, model settings, and the laboratory protocol. It should not be treated as an exact experimental annealing temperature.

## Hairpins and dimers

Hairpin, homodimer, and heterodimer melting temperatures are reported as screening signals. The default warning threshold of 45 °C is a configurable heuristic in the code and is not a universal scientific cutoff. Review predicted structures and thermodynamic parameters in the context of the intended assay.

## Homopolymer runs

The longest consecutive run of the same nucleotide is reported. The default warning limit is greater than four bases. This is a heuristic, and the effect depends on sequence context and assay design.

## Amplicon matching

If a template is supplied, the current implementation searches for exact matches to the forward primer and reverse complement of the reverse primer, with inward-facing orientation. It reports an amplicon length only if exactly one matching pair is found. It does not allow mismatches, indels, variants, degenerate primer sites, or multiple possible products. It is not a substitute for NCBI Primer-BLAST or an in silico PCR tool against the appropriate reference genome.

## Reproducibility

Reports include the principal concentration settings and target ranges. For publication, also record the Primer3 version, Python version, package version, template accession/version, reference database release, and any wet-lab conditions used to validate a primer pair.

## References

- Untergasser A, et al. Primer3: new capabilities and interfaces. Nucleic Acids Research. 2012;40(15):e115. https://doi.org/10.1093/nar/gks596
- Biopython documentation: https://biopython.org/
- primer3-py documentation: https://libnano.github.io/primer3-py/
- NCBI Primer-BLAST: https://www.ncbi.nlm.nih.gov/tools/primer-blast/

Check each reference and software version before citing in a manuscript.
