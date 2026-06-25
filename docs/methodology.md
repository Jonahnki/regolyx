# Regolyx Methodology Pipeline

## CODON OPTIMIZATION AND STRUCTURAL MODELING OF (PER)CHLORATE-REDUCING ENZYMES FROM THREE BACTERIAL DONORS FOR B. SUBTILIS-BASED MARTIAN REGOLITH BIOREMEDIATION

---

## Step 0 — Gene Target Identification and Accession Verification

- Identified three donor organisms based on documented perchlorate/chlorate reduction biology:
  - Azospira suillum PS
  - Dechloromonas aromatica RCB
  - Ideonella dechloratans

- Selected enzyme targets:
  - PcrA/PcrB + Cld for Azospira suillum
  - PcrA/PcrB + Cld for Dechloromonas aromatica
  - ClrA/ClrB + Cld for Ideonella dechloratans

- Verified every accession individually using:
  - NCBI EFetch/Esearch
  - UniProt REST API

- PcrA_Asui and PcrB_Asui were obtained from PDB 5E7O and cross-validated against:
  - 5CH7
  - 5CHC
  - 4YDD

Output:
- 9 verified protein FASTA files

---

## Step 1 — Codon Usage Reference Table

Source:
- Kazusa Codon Usage Database (CUTG)

Host:
- Bacillus subtilis

Database Entry:
- Species ID 1423

Statistics:
- 2,529 CDS
- 815,445 codons

Rejected:
- Species ID 224308
- 1 CDS
- 256 codons

Output:
- CSV codon usage table

---

## Step 2 — Codon Optimization

Method:
- Most-frequent synonymous codon substitution

Implementation:
- Standalone Python script

Procedure:
- Each amino acid replaced with highest-frequency synonymous codon from Step 1 table

Output:
- Optimized DNA FASTA
- Summary statistics

Recorded:
- Protein length
- DNA length
- GC%
- CAI
- Unmapped residues

---

## Step 3 — CAI and GC Analysis

CAI:
- Calculated using Sharp & Li methodology

GC%:
- Direct nucleotide counting

Limitation:
- CAI becomes mathematically fixed at 1.0 because optimization always selects maximum-weight codons.

Native sequence comparison:
- Not performed because native CDS sequences were unavailable.

---

## Step 4 — mRNA Secondary Structure Prediction

Tool:
- ViennaRNA 2.7.2

Program:
- RNAfold

Parameters:
- Default settings
- 37°C
- No folding constraints

Window:
- First 30 nucleotides of optimized CDS

Output:
- Dot-bracket structure
- Minimum Free Energy (MFE)

---

## Step 5 — Homology Structural Modeling

Tool:
- SWISS-MODEL

Procedure:
- Submit all nine protein sequences
- Select highest-quality model based on SWISS-MODEL metrics

Metrics recorded:
- GMQE
- QMEAN
- QMEANDisCo
- Template identity
- Coverage
- Oligomeric state

Output:
- PDB coordinates
- Model quality summary

---

## Step 6 — Reporting Rules

All numerical values reported in manuscripts must originate from:

- results/*/summary.csv
- SWISS-MODEL output reports
- Raw computational outputs committed in repository

Policy:
- Uncomputed values are reported as "not computed"
- No estimates
- No inferred values
- Full reproducibility maintained
