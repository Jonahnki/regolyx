#!/usr/bin/env python3
"""
Step 3: mRNA Secondary Structure Prediction

Predicts secondary structure of the translation initiation region (first 30 nt
post-start-codon) using the ViennaRNA package (RNAfold, RNA.fold algorithm).
Temperature: 37°C, default parameters, no folding constraints.

Reference:
  Lorenz, R., Bernhart, S.H., Höner zu Siederdissen, C., Tafer, H., et al. (2011)
  Algorithms Mol Biol 6(1):26
  ViennaRNA Package: https://www.tbi.univie.ac.at/RNA/

Output:
  - results/secondary_structure/*_structure.txt: detailed folding predictions
  - results/secondary_structure/summary.csv: MFE values per gene

Usage:
  python3 step3_secondary_structure.py

Requirements:
  - ViennaRNA 2.7.2+
"""

import csv
import re
import subprocess
from pathlib import Path
from datetime import datetime

RESULTS_SS_DIR = Path("results") / "secondary_structure"
RESULTS_CODON_OPT_DIR = Path("results") / "codon_optimization"
SUMMARY_FILE = RESULTS_SS_DIR / "summary.csv"

WINDOW_SIZE = 30
TEMPERATURE = 37


def check_viennarna_installed():
    try:
        result = subprocess.run(
            ["RNAfold", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version_line = (
                result.stdout.strip()
                or result.stderr.strip()
            )
            return True, version_line

    except FileNotFoundError:
        pass

    except Exception as e:
        return False, str(e)

    return False, "RNAfold not found"


def fold_rna_sequence(rna_seq, temperature=37):
    try:
        rna_input = rna_seq.upper().replace("T", "U")

        result = subprocess.run(
            ["RNAfold", "-T", str(temperature), "--noconv"],
            input=rna_input + "\n",
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return False, None, None, result.stderr[:200]

        lines = [
            line.strip()
            for line in result.stdout.strip().splitlines()
            if line.strip()
        ]

        if len(lines) < 2:
            return (
                False,
                None,
                None,
                f"Unexpected RNAfold output:\n{result.stdout}"
            )

        # RNAfold output:
        # line 0 = RNA sequence
        # line 1 = structure + MFE

        structure_line = lines[1]

        match = re.match(
            r"^([().]+)\s+\(\s*([-\d.]+)\s*\)",
            structure_line
        )

        if not match:
            return (
                False,
                None,
                None,
                f"Could not parse structure/MFE from:\n{structure_line}"
            )

        structure = match.group(1)
        mfe = float(match.group(2))

        return True, structure, mfe, result.stdout

    except subprocess.TimeoutExpired:
        return False, None, None, "Timeout"

    except Exception as e:
        return False, None, None, str(e)[:200]


def read_dna_fasta(filepath):
    with open(filepath, "r") as f:
        header = None
        lines = []

        for line in f:
            line = line.rstrip("\n")

            if line.startswith(">"):
                if header is not None:
                    break

                header = line[1:]

            else:
                lines.append(line)

        return header, "".join(lines)


def run_step3():
    print("\n" + "=" * 80)
    print("STEP 3: mRNA Secondary Structure Prediction")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    RESULTS_SS_DIR.mkdir(parents=True, exist_ok=True)

    print("Checking ViennaRNA...")

    vr_installed, vr_version = check_viennarna_installed()

    if not vr_installed:
        print(f"✗ ViennaRNA not found: {vr_version}")
        return

    print(f"✓ ViennaRNA: {vr_version}")

    dna_fasta_files = sorted(
        RESULTS_CODON_OPT_DIR.glob("*_optimized.fasta")
    )

    if not dna_fasta_files:
        print(f"✗ No sequences found in {RESULTS_CODON_OPT_DIR}")
        print("  Run step2_codon_optimize.py first")
        return

    print(f"Found {len(dna_fasta_files)} sequence(s)")
    print(f"Window: {WINDOW_SIZE} nt (post-start-codon)")
    print(f"Temperature: {TEMPERATURE}°C\n")

    summary_rows = []

    for fasta_path in dna_fasta_files:
        gene_id = fasta_path.stem.replace("_optimized", "")

        print(f"Processing: {gene_id}")

        header, dna_seq = read_dna_fasta(fasta_path)

        print(f"  DNA: {len(dna_seq)} bp")

        window_seq = dna_seq[:WINDOW_SIZE]

        if len(window_seq) < WINDOW_SIZE:
            print(
                f"  Warning: sequence shorter than "
                f"{WINDOW_SIZE} nt window"
            )

        rna_seq = window_seq.replace("T", "U")

        print(
            f"  Window: {window_seq[:30]}... "
            f"({len(window_seq)} nt)"
        )

        success, structure, mfe, output = fold_rna_sequence(
            rna_seq,
            TEMPERATURE
        )

        if not success:
            print(f"  ✗ Folding failed: {output}")

            summary_rows.append({
                "gene_id": gene_id,
                "window_length": len(window_seq),
                "structure": "FAILED",
                "mfe_kcal_mol": "N/A"
            })

            continue

        print(f"  Structure: {structure}")
        print(f"  MFE: {mfe:.2f} kcal/mol")

        out_txt = RESULTS_SS_DIR / f"{gene_id}_structure.txt"

        with open(out_txt, "w") as f:
            f.write(f"Gene: {gene_id}\n")
            f.write(f"DNA (full): {dna_seq}\n")
            f.write(f"DNA (window): {window_seq}\n")
            f.write(f"RNA (window): {rna_seq}\n")
            f.write(f"Window size: {len(window_seq)} nt\n")
            f.write(f"Temperature: {TEMPERATURE}°C\n\n")
            f.write(
                f"Structure (dot-bracket):\n"
                f"{structure}\n\n"
            )
            f.write(f"MFE: {mfe:.2f} kcal/mol\n")

        print(f"  ✓ {out_txt}\n")

        summary_rows.append({
            "gene_id": gene_id,
            "window_length": len(window_seq),
            "structure": structure,
            "mfe_kcal_mol": f"{mfe:.2f}"
        })

    print(f"Writing summary to {SUMMARY_FILE}...")

    with open(SUMMARY_FILE, "w", newline="") as f:
        fieldnames = [
            "gene_id",
            "window_length",
            "structure",
            "mfe_kcal_mol"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    successful = sum(
        1
        for row in summary_rows
        if row["mfe_kcal_mol"] != "N/A"
    )

    print(
        f"✓ {successful}/{len(summary_rows)} "
        f"sequences folded"
    )

    print("\n" + "=" * 80)
    print("Step 3 complete")
    print(f"  Output: {SUMMARY_FILE}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_step3()
