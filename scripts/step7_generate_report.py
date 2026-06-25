#!/usr/bin/env python3
"""
Step 7: Final Results Report

Combines outputs from:

Step 2
Step 3
Step 6

into a single publication-ready CSV.

Output
------
results/final_report.csv
"""

import csv
from pathlib import Path

CODON_SUMMARY = (
    Path("results")
    / "codon_optimization"
    / "summary.csv"
)

STRUCTURE_SUMMARY = (
    Path("results")
    / "secondary_structure"
    / "summary.csv"
)

MODEL_SUMMARY = (
    Path("results")
    / "structural_modeling"
    / "model_quality_summary.csv"
)

FINAL_REPORT = Path("results") / "final_report.csv"


def load_csv(path, key):

    if not path.exists():
        return {}

    with open(path) as f:
        rows = list(csv.DictReader(f))

    return {
        row[key]: row
        for row in rows
    }


def run_step7():

    codon = load_csv(CODON_SUMMARY, "gene_id")
    structure = load_csv(STRUCTURE_SUMMARY, "gene_id")
    models = load_csv(MODEL_SUMMARY, "model")

    genes = sorted(codon.keys())

    rows = []

    for gene in genes:

        c = codon.get(gene, {})
        s = structure.get(gene, {})
        m = models.get(gene, {})

        rows.append({
            "gene_id": gene,
            "protein_length_aa":
                c.get("protein_length_aa", ""),
            "dna_length_bp":
                c.get("dna_length_bp", ""),
            "gc_percent":
                c.get("gc_percent", ""),
            "cai":
                c.get("cai", ""),
            "mfe_kcal_mol":
                s.get("mfe_kcal_mol", ""),
            "gmqe":
                m.get("gmqe", ""),
            "qmean":
                m.get("qmean", "")
        })

    with open(FINAL_REPORT, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "gene_id",
                "protein_length_aa",
                "dna_length_bp",
                "gc_percent",
                "cai",
                "mfe_kcal_mol",
                "gmqe",
                "qmean"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ {FINAL_REPORT}")


if __name__ == "__main__":
    run_step7()
