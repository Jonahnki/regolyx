# Regolyx
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20838989.svg)](https://doi.org/10.5281/zenodo.20838989)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Status](https://img.shields.io/badge/status-research-orange)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey)

## Codon Optimization and Structural Modeling of (Per)chlorate-Reducing Enzymes from Three Bacterial Donors for *Bacillus subtilis*-Based Martian Regolith Bioremediation

### Overview

Regolyx is a reproducible bioinformatics workflow for the computational engineering of perchlorate-reducing enzymes intended for expression in *Bacillus subtilis* as a potential chassis organism for Martian regolith bioremediation.

Perchlorates are widespread contaminants in Martian regolith and represent a major challenge for future human habitation and in-situ resource utilization (ISRU). This project investigates whether key enzymes from naturally occurring perchlorate-reducing bacteria can be optimized for heterologous expression in *B. subtilis* while retaining favorable structural characteristics.

The workflow integrates sequence verification, codon optimization, secondary-structure analysis, and homology modeling into a single reproducible pipeline.

See `CHANGELOG.md` for a full record of corrections made since the initial release, including a gene/accession verification failure that was identified and resolved (summary below).

## Key Results

A total of nine perchlorate- and chlorate-reduction pathway enzymes from three bacterial donors were optimized for expression in *Bacillus subtilis* and structurally assessed using SWISS-MODEL.

### Codon Optimization Summary

| Gene      | Protein Length (aa) | DNA Length (bp) | GC (%) |   CAI |
| --------- | ------------------: | --------------: | -----: | ----: |
| Cld_Azos  |                 282 |             846 |  37.59 | 1.000 |
| Cld_Dech  |                 282 |             846 |  37.71 | 1.000 |
| Cld_Ideo  |                 285 |             855 |  40.47 | 1.000 |
| ClrA_Ideo |                 914 |            2742 |  40.15 | 1.000 |
| ClrB_Ideo |                 328 |             984 |  42.58 | 1.000 |
| PcrA_Azos |                 927 |            2781 |  40.27 | 1.000 |
| PcrA_Dech |                 927 |            2781 |  40.52 | 1.000 |
| PcrB_Azos |                 333 |             999 |  43.64 | 1.000 |
| PcrB_Dech |                 333 |             999 |  43.54 | 1.000 |

CAI is mathematically fixed at 1.000 for every sequence by construction: the optimization method always substitutes the single highest-frequency synonymous codon, so CAI against the same reference table cannot vary. This is reported as a stated property of the optimization method, not as a measure of result quality. *D. aromatica* and *A. suillum* PcrA/PcrB pairs share identical lengths but are non-identical sequences (88.0% and 94.6% pairwise identity respectively), consistent with orthologous genes between related species.

### RNA Folding Analysis

| Gene      | MFE (kcal/mol) |
| --------- | -------------: |
| Cld_Azos  |           0.00 |
| Cld_Dech  |          -4.00 |
| Cld_Ideo  |          -2.40 |
| ClrA_Ideo |          -0.20 |
| ClrB_Ideo |          -2.80 |
| PcrA_Azos |          -1.50 |
| PcrA_Dech |          -1.50 |
| PcrB_Azos |          -1.20 |
| PcrB_Dech |          -1.20 |

Values are minimum free energy for the first 30nt of each optimized coding sequence (translation-initiation region), predicted with ViennaRNA at 37°C. An MFE of 0.00 (Cld_Azos) reflects a genuinely unstructured window in that prediction, not a missing value.

### Structural Modeling Summary

| Gene      | GMQE | QMEAN | Status    |
| --------- | ---: | ----: | --------- |
| Cld_Azos  | 0.82 |  0.91 | COMPLETED |
| Cld_Dech  | 0.83 |  0.91 | COMPLETED |
| Cld_Ideo  | 0.75 |  0.85 | COMPLETED |
| ClrA_Ideo | 0.70 |  0.74 | COMPLETED |
| ClrB_Ideo | 0.84 |  0.78 | COMPLETED |
| PcrA_Azos | 0.93 |  0.95 | COMPLETED |
| PcrA_Dech | 0.91 |  0.93 | COMPLETED |
| PcrB_Azos | 0.99 |  0.95 | COMPLETED |
| PcrB_Dech | 0.98 |  0.94 | COMPLETED |

GMQE and QMEAN (average local score) are retrieved directly from the SWISS-MODEL REST API's structured JSON response. Template identity and coverage are not returned by this API endpoint and are not reported here; see Known Limitations.

### Verification Summary

All nine constructs:

* Passed accession verification against primary structural (PDB) and curated (UniProt/Swiss-Prot) database records, independently re-verified by direct inspection
* Retained full-length coding sequences
* Produced zero unmapped residues during codon optimization
* Achieved CAI = 1.000 (see note above on why this is expected, not a quality signal)
* Successfully completed SWISS-MODEL processing via the REST API

**Note on accession provenance:** an earlier accession set used in this pipeline was found, on independent re-verification, to be incorrect for five of the nine genes (each resolving to a real but unrelated protein from an unrelated organism). All nine accessions were re-sourced and re-verified before this release; see `docs/verification_log.md` for the corrected accession table and `CHANGELOG.md` for the full incident record.

---

## Highlights

- Verification of experimentally characterized perchlorate-reduction genes, independently re-confirmed against primary database records
- Codon optimization for *Bacillus subtilis*
- Secondary-structure analysis of optimized transcripts
- Automated SWISS-MODEL structural modeling via direct REST API integration (no manual upload or HTML scraping)
- Model quality assessment and reporting from structured API data
- Fully reproducible computational workflow

---

## Research Objectives

- Verify target enzyme sequences from perchlorate-reducing bacteria
- Optimize coding sequences for expression in *Bacillus subtilis*
- Evaluate codon adaptation and sequence composition
- Assess RNA secondary-structure characteristics
- Generate homology models using SWISS-MODEL
- Compare model quality metrics across donor organisms
- Produce publication-ready summary reports

---

## Target Enzymes

| Donor Organism | Gene | Function | Accession | Notes |
|---|---|---|---|---|
| Azospira suillum PS | PcrA | Catalytic perchlorate reductase subunit | UniProt G8QM55 | Strain-specific (PDB 5E7O, locus Dsui_0149) |
| Azospira suillum PS | PcrB | Electron-transfer subunit | UniProt G8QM54 | Strain-specific (PDB 5E7O, locus Dsui_0148) |
| Azospira suillum PS | Cld | Chlorite dismutase | UniProt E2DI02 | From strain GR-1, not PS — no PS-specific record available |
| Dechloromonas aromatica RCB | PcrA | Catalytic perchlorate reductase subunit | UniProt Q47CW6 | Strain-specific (Daro_2584) |
| Dechloromonas aromatica RCB | PcrB | Electron-transfer subunit | UniProt Q47CW7 | Strain-specific (Daro_2583) |
| Dechloromonas aromatica RCB | Cld | Chlorite dismutase | UniProt Q47CX0 | Strain-specific (Daro_2580) |
| Ideonella dechloratans | ClrA | Chlorate reductase catalytic subunit | UniProt P60068 | Species-specific |
| Ideonella dechloratans | ClrB | Electron-transfer subunit | UniProt P60069 | Species-specific |
| Ideonella dechloratans | Cld | Chlorite dismutase | UniProt Q9F437 | Species-specific |

Full provenance and verification method for each accession are documented in `docs/verification_log.md`.

---

## Workflow

```text
Sequence Verification
        |
        v
Codon Usage Analysis
        |
        v
Codon Optimization
        |
        v
Secondary Structure Prediction
        |
        v
SWISS-MODEL Homology Modeling (REST API)
        |
        v
Model Quality Assessment
        |
        v
Automated Reporting
```

---

## Repository Structure

```text
regolyx/
├── CITATION.cff
├── CHANGELOG.md
├── LICENSE
├── README.md
├── environment.yml
├── requirements.txt
├── data/
│   ├── bsubtilis_codon_usage.csv
│   └── sequences/
├── docs/
│   └── verification_log.md
├── scripts/
│   ├── step0_verify_accessions.py
│   ├── step1_codon_usage.py
│   ├── step2_codon_optimize.py
│   ├── step3_secondary_structure.py
│   ├── step4_swissmodel_api.py
│   └── step5_generate_report.py
└── results/
    ├── codon_optimization/
    ├── secondary_structure/
    └── structural_modeling/
```

---

## Installation

### Conda

```bash
conda env create -f environment.yml
conda activate regolyx
```

### Pip

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

```bash
python scripts/step0_verify_accessions.py
python scripts/step1_codon_usage.py
python scripts/step2_codon_optimize.py
python scripts/step3_secondary_structure.py
python scripts/step4_swissmodel_api.py   # requires SWISSMODEL_TOKEN env var; see script docstring
python scripts/step5_generate_report.py
```

---

## Outputs

### Codon Optimization

Location:

```text
results/codon_optimization/
```

Includes:

- Optimized coding sequences
- Codon usage statistics
- Summary tables

### Secondary Structure

Location:

```text
results/secondary_structure/
```

Includes:

- RNA folding predictions
- Structure summaries

### Structural Modeling

Location:

```text
results/structural_modeling/
```

Includes:

- SWISS-MODEL predictions (retrieved via REST API as structured JSON, `swissmodel_api_results.json`)
- Model quality metrics (`model_quality_summary.csv`)
- Structural summaries

---

## Known Limitations

- **Template identity and coverage are not reported.** The SWISS-MODEL REST API endpoint used by this pipeline returns GMQE and QMEAN (average local score) but does not return template sequence identity, coverage, or template ID in its response. These fields are present as empty columns in `model_quality_summary.csv` rather than omitted, so the gap is visible. A future revision may query a separate SWISS-MODEL endpoint if this data is required for downstream analysis.
- **Native-sequence CAI/GC baseline comparison is pending.** The verified gene targets are protein sequences; no native nucleotide CDS is available for direct before/after comparison of codon optimization. Reverse-translation was deliberately not used as a substitute, since it would not reflect the donor organism's actual codon usage.
- **Cld for *Azospira suillum* PS is a cross-strain substitution.** No strain-PS-specific chlorite dismutase accession was found in UniProt or NCBI. The sequence used (UniProt E2DI02) is from *Azospira oryzae* strain GR-1, the strain in which Cld was originally biochemically characterized for this genus. Any manuscript text or figure using this sequence should cite strain GR-1 explicitly, not strain PS.

---

## Scientific Context

Keywords:

- Perchlorate Reduction
- Chlorite Dismutase
- Perchlorate Reductase
- Synthetic Biology
- Bacillus subtilis
- Codon Optimization
- Structural Bioinformatics
- SWISS-MODEL
- Astrobiotechnology
- Martian Regolith
- ISRU
- Bioremediation

---

## Reproducibility

Environment:

- Python 3.13
- Conda environment specification included
- Requirements file included

Pipeline stages:

1. Sequence verification
2. Codon usage analysis
3. Codon optimization
4. RNA secondary structure prediction
5. SWISS-MODEL structural modeling (REST API)
6. Automated reporting

All analyses can be reproduced from raw sequence files using the scripts contained in the `scripts/` directory. `scripts/step4_swissmodel_api.py` requires a SWISS-MODEL account API token, set via the `SWISSMODEL_TOKEN` environment variable — see the script's docstring for how to obtain one. No password or token should ever be passed as a command-line argument or committed to this repository.

---

## Data Availability

All input sequences, optimized constructs, structural models, intermediate files, and analysis outputs are available in this repository.

Archived release:

https://zenodo.org/records/20838989

DOI:

10.5281/zenodo.20838989

**Note:** the archived Zenodo release should be checked against the version of `data/sequences/` it captured. If the archived snapshot predates the accession corrections described in `CHANGELOG.md`, a new Zenodo version should be minted against the corrected data before this DOI is cited as authoritative.

## Citation

If you use Regolyx in academic work, please cite the metadata contained in:

```text
CITATION.cff
```

`CITATION.cff` should be updated to reflect the current version (see `CHANGELOG.md`) before this repository is cited externally.

---

## License

Released under the MIT License.

See `LICENSE` for details.
