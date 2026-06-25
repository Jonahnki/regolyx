#!/usr/bin/env python3
"""
Step 0: Gene Target Identification and Accession Verification

Identifies and retrieves protein sequences for (per)chlorate-reducing enzymes
from three bacterial donors. All accessions verified against UniProt.

Donor organisms and genes:
  - Azospira suillum PS:
      PcrA (G8QM55 / Dsui_0149), PcrB (G8QM54 / Dsui_0148),
      Cld  (E2DI02 / strain GR-1; no PS-specific Cld record available)
  - Dechloromonas aromatica RCB:
      PcrA (Q47CW6 / Daro_2584), PcrB (Q47CW7 / Daro_2583),
      Cld  (Q47CX0 / Daro_2580)
  - Ideonella dechloratans:
      ClrA (P60068), ClrB (P60069), Cld (Q9F437)

Note on Cld_Asui: UniProt E2DI02 derives from Azospira oryzae strain GR-1,
the closest sequenced relative of A. suillum PS. No strain-PS-specific Cld
protein record exists in UniProt or NCBI as of the verification date. This
substitution is documented here and in the verification log.

Output:
  - data/sequences/*.fasta: 9 verified protein sequences
  - docs/verification_log.md: detailed verification trail

Usage:
  python3 step0_verify_accessions.py
"""

import sys
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

TARGETS = {
    "Azospira suillum PS": {
        "organism_name": "Azospira",
        "genes": {
            "PcrA": {
                "accession": "G8QM55",
                "source": "UniProt",
                "note": "Dsui_0149; strain-PS-specific",
            },
            "PcrB": {
                "accession": "G8QM54",
                "source": "UniProt",
                "note": "Dsui_0148; strain-PS-specific",
            },
            "Cld": {
                "accession": "E2DI02",
                "source": "UniProt",
                "note": "A. oryzae GR-1 ortholog; no PS-specific record available",
            },
        },
    },
    "Dechloromonas aromatica RCB": {
        "organism_name": "Dechloromonas",
        "genes": {
            "PcrA": {
                "accession": "Q47CW6",
                "source": "UniProt",
                "note": "Daro_2584; strain-RCB-specific",
            },
            "PcrB": {
                "accession": "Q47CW7",
                "source": "UniProt",
                "note": "Daro_2583; strain-RCB-specific",
            },
            "Cld": {
                "accession": "Q47CX0",
                "source": "UniProt",
                "note": "Daro_2580; strain-RCB-specific",
            },
        },
    },
    "Ideonella dechloratans": {
        "organism_name": "Ideonella",
        "genes": {
            "ClrA": {
                "accession": "P60068",
                "source": "UniProt",
                "note": "",
            },
            "ClrB": {
                "accession": "P60069",
                "source": "UniProt",
                "note": "",
            },
            "Cld": {
                "accession": "Q9F437",
                "source": "UniProt",
                "note": "",
            },
        },
    },
}

DOCS_DIR = Path("docs")
DATA_SEQ_DIR = Path("data") / "sequences"
UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"

DOCS_DIR.mkdir(exist_ok=True)
DATA_SEQ_DIR.mkdir(parents=True, exist_ok=True)


def fetch_uniprot_fasta(accession, timeout=15):
    url = f"{UNIPROT_BASE}/{accession}.fasta"
    try:
        with urlopen(url, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            if not text or "Error" in text[:50]:
                return False, None, text[:200]
            lines = text.strip().splitlines()
            header = lines[0]
            seq = "".join(lines[1:])
            return True, seq, header
    except (URLError, HTTPError, Exception) as e:
        return False, None, str(e)[:200]


def run_step0():
    print("\n" + "=" * 80)
    print("STEP 0: Gene Target Identification and Accession Verification")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    verifications = []
    fasta_created = []
    passed = 0
    failed = 0

    for donor_label, donor_data in TARGETS.items():
        org_name = donor_data["organism_name"]
        print(f"\nDonor organism: {donor_label}")

        for gene_name, acc_data in donor_data["genes"].items():
            accession = acc_data["accession"]
            note = acc_data["note"]

            gene_id = f"{gene_name}_{org_name[:4]}"

            print(f"\n  Gene: {gene_name}")
            print(f"    Accession: {accession}")
            if note:
                print(f"    Note: {note}")

            success, seq, info = fetch_uniprot_fasta(accession)

            entry = {
                "donor": donor_label,
                "gene": gene_name,
                "gene_id": gene_id,
                "accession": accession,
                "note": note,
                "status": "PASS" if success else "FAIL",
                "sequence_length": len(seq) if success else 0,
                "detail": info if not success else "",
            }
            verifications.append(entry)

            if success:
                print(f"    ✓ Status: PASS")
                print(f"    ✓ Length: {len(seq)} aa")
                passed += 1

                fasta_path = DATA_SEQ_DIR / f"{gene_id}.fasta"
                with open(fasta_path, "w") as f:
                    f.write(f">{gene_id} {donor_label} {gene_name} {accession}\n")
                    for i in range(0, len(seq), 80):
                        f.write(seq[i : i + 80] + "\n")

                print(f"    ✓ Output: {fasta_path}")
                fasta_created.append(gene_id)
            else:
                print(f"    ✗ Status: FAIL — {info}")
                failed += 1

    log_path = DOCS_DIR / "verification_log.md"
    with open(log_path, "w") as f:
        f.write("# Step 0: Gene Target Verification\n\n")
        f.write(f"**Verification date:** {datetime.now().isoformat()}\n\n")
        f.write("## Summary\n")
        f.write(f"- Total genes: {len(verifications)}\n")
        f.write(f"- Passed: {passed}\n")
        f.write(f"- Failed: {failed}\n")
        f.write(f"- FASTA files created: {len(fasta_created)}\n\n")
        f.write("## Gene Verifications\n\n")
        for entry in verifications:
            f.write(
                f"### {entry['donor']} — {entry['gene']} ({entry['accession']})\n"
            )
            f.write(f"- Status: **{entry['status']}**\n")
            f.write(f"- Sequence length: {entry['sequence_length']} aa\n")
            if entry["note"]:
                f.write(f"- Note: {entry['note']}\n")
            if entry["detail"]:
                f.write(f"- Error: {entry['detail']}\n")
            f.write("\n")

    print(f"\n{'=' * 80}")
    print("Step 0 complete")
    print(f"  Log: {log_path}")
    print(f"  FASTA files: {len(fasta_created)}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_step0()
