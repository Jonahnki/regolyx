#!/usr/bin/env python3
"""
Step 2: Codon Optimization

Optimizes protein sequences for expression in Bacillus subtilis using
most-frequent-synonymous-codon substitution. For each amino acid, the codon
with the highest frequency in the B. subtilis reference table is selected.

Method: Sharp & Li (1987) Codon Adaptation Index (CAI)
  - CAI = (∏ w_ij)^(1/N), where w_ij is relative synonymous adaptiveness
  - Maximum CAI for optimized sequences = 1.0 (by method design)

Reference:
  Sharp, P.M., Li, W.H. (1987) Nucleic Acids Res 15(3):1281-1295

Output:
  - results/codon_optimization/*_optimized.fasta: optimized DNA sequences
  - results/codon_optimization/summary.csv: metrics per gene

Usage:
  python3 step2_codon_optimize.py
"""

import csv
import math
from pathlib import Path
from datetime import datetime

DATA_SEQ_DIR = Path("data") / "sequences"
DATA_CODON_FILE = Path("data") / "bsubtilis_codon_usage.csv"
RESULTS_CODON_OPT_DIR = Path("results") / "codon_optimization"
SUMMARY_FILE = RESULTS_CODON_OPT_DIR / "summary.csv"

GENETIC_CODE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

def load_codon_usage_table(filepath):
    codon_usage = {}

    with open(filepath, 'r') as f:
        rows = [line for line in f if not line.startswith('#')]
        reader = csv.DictReader(rows)

        for row in reader:
            codon = row['codon'].strip().upper()
            aa = row['amino_acid'].strip()
            freq = float(row['frequency'])

            if aa not in codon_usage:
                codon_usage[aa] = {}

            codon_usage[aa][codon] = freq

    return codon_usage

def get_max_frequency_codon(aa, codon_usage):
    if aa not in codon_usage:
        return None

    codons = codon_usage[aa]

    if not codons:
        return None

    return max(codons.keys(), key=lambda c: codons[c])

def read_protein_fasta(filepath):
    with open(filepath, 'r') as f:
        header = None
        lines = []

        for line in f:
            line = line.rstrip('\n')

            if line.startswith('>'):
                if header is not None:
                    break

                header = line[1:]
            else:
                lines.append(line)

        return header, ''.join(lines)

def write_dna_fasta(filepath, gene_id, header_info, dna_seq):
    with open(filepath, 'w') as f:
        f.write(f">{gene_id} {header_info}\n")

        for i in range(0, len(dna_seq), 80):
            f.write(dna_seq[i:i+80] + '\n')

def optimize_protein_sequence(protein_seq, codon_usage):
    dna_codons = []
    unmapped = 0

    for aa in protein_seq:
        codon = get_max_frequency_codon(aa, codon_usage)

        if codon:
            dna_codons.append(codon)
        else:
            unmapped += 1
            dna_codons.append("NNN")

    dna_seq = ''.join(dna_codons)

    return dna_seq, unmapped

def compute_gc_content(dna_seq):
    gc_count = dna_seq.count('G') + dna_seq.count('C')

    return (gc_count / len(dna_seq)) * 100 if len(dna_seq) > 0 else 0

def compute_cai(dna_seq, codon_usage):
    n_codons = len(dna_seq) // 3

    if n_codons == 0:
        return 1.0

    weights = []

    for i in range(0, len(dna_seq), 3):
        codon = dna_seq[i:i+3]
        aa = GENETIC_CODE.get(codon)

        if aa and aa in codon_usage:
            codon_freq = codon_usage[aa].get(codon, 0)
            max_freq = max(codon_usage[aa].values())

            if max_freq > 0:
                w = codon_freq / max_freq
                weights.append(w)

    if not weights:
        return 0

    product = 1.0

    for w in weights:
        product *= w

    cai = product ** (1.0 / len(weights))

    return cai

def run_step2():
    print("\n" + "="*80)
    print("STEP 2: Codon Optimization")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    RESULTS_CODON_OPT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading codon usage table...")

    if not DATA_CODON_FILE.exists():
        print(f"✗ File not found: {DATA_CODON_FILE}")
        print("  Run step1_codon_usage.py first")
        return

    codon_usage = load_codon_usage_table(DATA_CODON_FILE)

    print(f"✓ Loaded {len(codon_usage)} amino acid families")

    fasta_files = sorted(DATA_SEQ_DIR.glob("*.fasta"))

    if not fasta_files:
        print(f"✗ No FASTA files found in {DATA_SEQ_DIR}")
        print("  Run step0_verify_accessions.py first")
        return

    print(f"Found {len(fasta_files)} sequence(s)\n")

    summary_rows = []

    for fasta_path in fasta_files:
        gene_id = fasta_path.stem

        print(f"Processing: {gene_id}")

        header, protein_seq = read_protein_fasta(fasta_path)

        protein_len = len(protein_seq)

        print(f"  Protein: {protein_len} aa")

        dna_seq, unmapped = optimize_protein_sequence(
            protein_seq,
            codon_usage
        )

        dna_len = len(dna_seq)

        print(f"  DNA: {dna_len} bp")

        gc_pct = compute_gc_content(dna_seq)
        cai = compute_cai(dna_seq, codon_usage)

        print(f"  GC%: {gc_pct:.2f}%")
        print(f"  CAI: {cai:.4f}")

        out_fasta = (
            RESULTS_CODON_OPT_DIR /
            f"{gene_id}_optimized.fasta"
        )

        write_dna_fasta(
            out_fasta,
            gene_id,
            "B. subtilis optimized",
            dna_seq
        )

        print(f"  ✓ {out_fasta}\n")

        summary_rows.append({
            "gene_id": gene_id,
            "protein_length_aa": protein_len,
            "dna_length_bp": dna_len,
            "gc_percent": f"{gc_pct:.2f}",
            "cai": f"{cai:.4f}",
            "unmapped_residues": unmapped
        })

    print(f"Writing summary to {SUMMARY_FILE}...")

    with open(SUMMARY_FILE, 'w', newline='') as f:
        fieldnames = [
            "gene_id",
            "protein_length_aa",
            "dna_length_bp",
            "gc_percent",
            "cai",
            "unmapped_residues"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"✓ {len(summary_rows)} genes processed")

    print(f"\n{'='*80}")
    print("Step 2 complete")
    print(f"  Output: {SUMMARY_FILE}")
    print(f"End time: {datetime.now().isoformat()}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_step2()
