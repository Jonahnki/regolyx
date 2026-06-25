# Changelog

All notable changes to Regolyx are documented in this file.

## [1.1.0] — 2026-06-25

### Fixed

- **Accession verification.** Five of the nine original gene accessions were found, on independent re-verification against live NCBI/UniProt/PDB records, to resolve to the wrong gene and the wrong organism (e.g. a claimed *Azospira suillum* PcrA accession that in fact corresponded to a thioredoxin-disulfide reductase from *Neomoorella thermoacetica*; three retired NP_ accessions whose current merged identities are unrelated *Bradyrhizobium diazoefficiens* proteins). All nine accessions have been re-sourced from primary structural (PDB) and curated (UniProt/Swiss-Prot) records and independently re-verified by direct inspection of each record. See `docs/verification_log.md` for the full corrected accession table and provenance notes.

- **`step0_verify_accessions.py` verification logic.** The organism-match check previously defaulted to a pass when it could not parse an organism string from a FASTA header, and the script performed no check of gene/product identity at all. This allowed the accession errors above through undetected. The verification logic has been hardened: organism mismatches and unparseable headers now fail closed rather than open, and a gene-identity check against the DEFINITION/product line has been added.

- **Model quality extraction (`step4_swissmodel_api.py`).** The script previously selected `models[0]` from the SWISS-MODEL API response and looked for `qmean_norm`/`qmean` as flat fields. Against the actual response schema, the first list entry is not guaranteed to be the most complete result, and QMEAN is returned nested under `qmean_global.avg_local_score`. The extraction logic now selects the model entry that actually carries `qmean_global` data and reads the correct nested field. `identity`, `coverage`, and `template` are not present in this API endpoint's response and are left as `None` rather than guessed; a previous version of this pipeline scraped these from HTML reports using a label-proximity regex, which silently returned wrong values (e.g. matching a digit from an image file path rather than the actual score) and has been fully removed in favor of the structured API response.

### Changed

- Replaced the manual SWISS-MODEL submission workflow (file packaging for browser upload, followed by HTML report scraping) with direct REST API submission, polling, and structured JSON result retrieval (`step4_swissmodel_api.py`, formerly two separate scripts).
- Renumbered pipeline steps so script filenames match the README's conceptual step list exactly (previously off by one due to an analysis step folded into another script's output rather than given its own file).

### Verified, no change needed

- Codon usage reference table (`data/bsubtilis_codon_usage.csv`): cross-checked against the live Kazusa CUTG source for species ID 1423; all checked codon frequency values matched exactly.
- RNA secondary structure outputs: spot-checked `Cld_Azos` (MFE 0.00, fully unstructured 30nt window) and `ClrA_Ideo` (MFE -0.20, small stem-loop) directly against ViennaRNA's dot-bracket output; both are genuine results, not parsing artifacts.
- *D. aromatica* and *A. suillum* PcrA/PcrB sequences sharing identical lengths (927aa/333aa) are confirmed to be distinct, non-identical sequences at 88.0% and 94.6% pairwise identity respectively — consistent with orthologous genes between related Rhodocyclaceae species, not a duplication error.

### Known limitations carried forward

- `identity`, `coverage`, and `template` fields remain unpopulated in `model_quality_summary.csv`; the current SWISS-MODEL API endpoint used does not return these values. A future revision may query a separate endpoint if this data is required.
- Chlorite dismutase for *Azospira suillum* PS (E2DI02) is sourced from *Azospira oryzae* strain GR-1, not strain PS; no PS-strain-specific Cld record was found in UniProt or NCBI as of this verification. See `docs/verification_log.md` for details. Any manuscript text using this sequence should cite strain GR-1 explicitly.
- Native (non-codon-optimized) CAI/GC baseline comparison remains pending, as noted in `docs/methodology.md`: the verified gene targets are protein sequences without an available native nucleotide CDS for direct comparison.

## [1.0.0] — 2026-06-25

- Initial Regolyx publication release. Superseded the withdrawn "RedDust Reclaimer" project following an internal audit that identified poor project recordkeeping and feasibility alongside several fabricated placeholder results.
