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

### Structural Modeling Summary

| Gene      | GMQE | Status    |
| --------- | ---: | --------- |
| Cld_Azos  | 0.89 | COMPLETED |
| Cld_Dech  | 0.89 | COMPLETED |
| Cld_Ideo  | 0.89 | COMPLETED |
| ClrA_Ideo | 0.94 | COMPLETED |
| ClrB_Ideo | 0.96 | COMPLETED |
| PcrA_Azos | 0.97 | COMPLETED |
| PcrA_Dech | 0.97 | COMPLETED |
| PcrB_Azos | 0.99 | COMPLETED |
| PcrB_Dech | 0.98 | COMPLETED |

### Verification Summary

All optimized constructs:

* Passed accession verification
* Retained full-length coding sequences
* Produced zero unmapped residues
* Achieved CAI = 1.000
* Successfully completed SWISS-MODEL processing

---

## Highlights

- Verification of experimentally characterized perchlorate-reduction genes
- Codon optimization for *Bacillus subtilis*
- Secondary-structure analysis of optimized transcripts
- Automated SWISS-MODEL structural modeling
- Model quality assessment and reporting
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

| Donor Organism | Gene | Function |
|---------------|------|----------|
| Azospira suillum PS | PcrA | Catalytic perchlorate reductase subunit |
| Azospira suillum PS | PcrB | Electron-transfer subunit |
| Azospira suillum PS | Cld | Chlorite dismutase |
| Dechloromonas aromatica RCB | PcrA | Catalytic perchlorate reductase subunit |
| Dechloromonas aromatica RCB | PcrB | Electron-transfer subunit |
| Dechloromonas aromatica RCB | Cld | Chlorite dismutase |
| Ideonella dechloratans | ClrA | Chlorate reductase catalytic subunit |
| Ideonella dechloratans | ClrB | Electron-transfer subunit |
| Ideonella dechloratans | Cld | Chlorite dismutase |

---

## Workflow

```text
Sequence Verification
        │
        ▼
Codon Usage Analysis
        │
        ▼
Codon Optimization
        │
        ▼
Secondary Structure Prediction
        │
        ▼
SWISS-MODEL Homology Modeling
        │
        ▼
Model Quality Assessment
        │
        ▼
Automated Reporting
```

---

## Repository Structure

```text
regolyx/
├── CITATION.cff
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
python scripts/step4_swissmodel_api.py
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

- SWISS-MODEL predictions
- Model quality metrics
- Structural summaries

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
5. SWISS-MODEL structural modeling
6. Automated reporting

All analyses can be reproduced from raw sequence files using the scripts contained in the `scripts/` directory.

---

## Data Availability

All input sequences, optimized constructs, structural models, intermediate files, and analysis outputs are available in this repository.

Archived release:

https://zenodo.org/records/20838989

DOI:

10.5281/zenodo.20838989


## Citation

If you use Regolyx in academic work, please cite the metadata contained in:

```text
CITATION.cff
```

---

## License

Released under the MIT License.

See `LICENSE` for details.
