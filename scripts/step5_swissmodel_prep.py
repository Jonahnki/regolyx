#!/usr/bin/env python3
"""
Step 5: SWISS-MODEL Submission Package Preparation

Purpose
-------
Prepare all verified protein sequences for homology modeling using
SWISS-MODEL.

This step DOES NOT perform modeling.

Instead it:

1. Collects verified protein FASTA files
2. Creates a SWISS-MODEL submission package
3. Generates a manifest file
4. Records sequence statistics

Input
-----
data/sequences/*.fasta

Output
------
results/structural_modeling/
    submission_manifest.csv
    swissmodel_submission/
        *.fasta

Reference
---------
Waterhouse et al. (2018)
SWISS-MODEL: Homology modelling of protein structures and complexes.
Nucleic Acids Research 46(W1):W296-W303
"""

import csv
from pathlib import Path
from datetime import datetime

DATA_SEQ_DIR = Path("data") / "sequences"

RESULTS_DIR = Path("results") / "structural_modeling"
SUBMISSION_DIR = RESULTS_DIR / "swissmodel_submission"

MANIFEST_FILE = RESULTS_DIR / "submission_manifest.csv"


def read_fasta(filepath):
    with open(filepath) as f:
        header = None
        seq = []

        for line in f:
            line = line.strip()

            if line.startswith(">"):
                header = line[1:]
            else:
                seq.append(line)

    return header, "".join(seq)


def run_step5():
    print("\n" + "=" * 80)
    print("STEP 5: SWISS-MODEL Preparation")
    print("=" * 80)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    fasta_files = sorted(DATA_SEQ_DIR.glob("*.fasta"))

    if not fasta_files:
        print("No FASTA files found")
        return

    rows = []

    for fasta in fasta_files:
        gene_id = fasta.stem

        header, seq = read_fasta(fasta)

        out_file = SUBMISSION_DIR / fasta.name

        with open(out_file, "w") as f:
            f.write(f">{gene_id}\n")
            f.write(seq + "\n")

        rows.append({
            "gene_id": gene_id,
            "length_aa": len(seq),
            "submission_fasta": str(out_file)
        })

        print(f"✓ {gene_id}")

    with open(MANIFEST_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gene_id",
                "length_aa",
                "submission_fasta"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Prepared {len(rows)} proteins")
    print(f"Manifest: {MANIFEST_FILE}")
    print(f"Finished: {datetime.now().isoformat()}")


if __name__ == "__main__":
    run_step5()
