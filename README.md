![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.13-blue)

# Regolyx

Codon Optimization and Structural Modeling of (Per)chlorate-Reducing Enzymes from Three Bacterial Donors for Bacillus subtilis–Based Martian Regolith Bioremediation

## Overview

Regolyx is a reproducible computational pipeline for:

1. Verification of target (per)chlorate-reduction enzymes
2. Codon optimization for Bacillus subtilis
3. CAI and GC-content analysis
4. Translation-initiation-region mRNA folding
5. Homology structural modeling using SWISS-MODEL
6. Automated result reporting

## Target Enzymes

| Organism | Enzyme |
|-----------|---------|
| Azospira suillum PS | PcrA |
| Azospira suillum PS | PcrB |
| Azospira suillum PS | Cld |
| Dechloromonas aromatica RCB | PcrA |
| Dechloromonas aromatica RCB | PcrB |
| Dechloromonas aromatica RCB | Cld |
| Ideonella dechloratans | ClrA |
| Ideonella dechloratans | ClrB |
| Ideonella dechloratans | Cld |

## Pipeline

Step 0 – accession verification

Step 1 – codon usage table construction

Step 2 – codon optimization

Step 3 – CAI and GC analysis

Step 4 – RNA secondary structure prediction

Step 5 – SWISS-MODEL structural modeling

Step 6 – model quality extraction

Step 7 – final report generation

## Repository Structure

data/
docs/
results/
scripts/

## Running

python scripts/step0_verify_accessions.py

python scripts/step1_codon_usage.py

python scripts/step2_codon_optimize.py

python scripts/step3_secondary_structure.py

python scripts/step5_swissmodel_prep.py

python scripts/step6_model_quality_parser.py

python scripts/step7_generate_report.py

## Structural Models

Publication-selected models are located in:

results/structural_modeling/selected_models/

## Citation

See CITATION.cff

## License

MIT License
