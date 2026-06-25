#!/usr/bin/env python3
"""
Step 1: Codon Usage Reference Table

Retrieves Bacillus subtilis genus-level codon usage frequencies from the
Kazusa Codon Usage Database (CUTG, species ID 1423; 2,529 CDS / 815,445 codons).

Reference:
  Kazusa CUTG: https://www.kazusa.or.jp/codon/
  Nakamura, Y., Gojobori, T., Ikemura, T. (2000) Nucleic Acids Research 28(1):292-294

Output:
  - data/bsubtilis_codon_usage.csv: codon frequency table with metadata

Usage:
  python3 step1_codon_usage.py
"""

import sys
import ssl
import re
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

KAZUSA_BASE = "https://www.kazusa.jp/codon/cgi-bin"
BSUBTILIS_GENUS_ID = 1423

DATA_DIR = Path("data")
CODON_USAGE_FILE = DATA_DIR / "bsubtilis_codon_usage.csv"


def fetch_kazusa_html(species_id, timeout=15):
    """
    Download codon usage table from Kazusa CUTG HTML page.
    """

    url = f"{KAZUSA_BASE}/showcodon.cgi?species={species_id}"

    context = ssl._create_unverified_context()

    try:
        with urlopen(url, timeout=timeout, context=context) as response:
            content = response.read().decode("iso-8859-1")

            if not content:
                return False, None, {"error": "Empty response"}

            return True, content, {"url": url}

    except (URLError, HTTPError, Exception) as e:
        return False, None, {"error": str(e)[:200]}


def parse_kazusa_html(content):
    """
    Parse Kazusa HTML codon usage table.
    """

    pre_match = re.search(
        r"<PRE>(.*?)</PRE>",
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not pre_match:
        return False, {}, {"error": "PRE block not found"}

    pre_text = pre_match.group(1)

    codon_dict = {}

    pattern = r"([AUCG]{3})\s+([0-9]+\.[0-9]+)"

    for codon, freq in re.findall(pattern, pre_text):
        codon_dict[codon.replace("U", "T")] = float(freq)

    metadata = {
        "parsed_codons": len(codon_dict)
    }

    return len(codon_dict) > 0, codon_dict, metadata


def organize_by_amino_acid(codon_dict):
    """
    Group codons according to the standard genetic code.
    """
    genetic_code = {
        "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
        "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
        "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
        "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
        "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
        "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
        "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
        "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
        "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
        "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
        "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
        "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
        "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
        "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
        "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
        "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
    }

    by_aa = {}

    for codon, freq in codon_dict.items():
        codon_upper = codon.replace("U", "T")
        aa = genetic_code.get(codon_upper)

        if aa:
            by_aa.setdefault(aa, []).append((codon, freq))

    return by_aa


def save_codon_usage_csv(codon_dict, by_aa, filepath):
    """
    Save codon usage table with metadata header.
    """
    with open(filepath, "w", newline="") as f:
        f.write("# Codon Usage: Bacillus subtilis (genus level)\n")
        f.write("# Source: Kazusa Codon Usage Database (CUTG)\n")
        f.write("# Species ID: 1423\n")
        f.write("# CDS count: 2,529\n")
        f.write("# Codon count: 815,445\n")
        f.write(
            f"# Retrieval date: {datetime.now().strftime('%Y-%m-%d')}\n"
        )
        f.write(
            "# URL: https://www.kazusa.jp/codon/cgi-bin/showcodon.cgi?species=1423\n"
        )
        f.write(
            "# Reference: Nakamura et al. (2000) Nucleic Acids Res 28(1):292-294\n"
        )
        f.write("#\n")
        f.write("codon,frequency,amino_acid\n")

        for aa in sorted(by_aa.keys()):
            for codon, freq in sorted(by_aa[aa], key=lambda x: -x[1]):
                f.write(f"{codon},{freq:.4f},{aa}\n")


def run_step1():
    print("\n" + "=" * 80)
    print("STEP 1: Codon Usage Reference Table")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    print()

    DATA_DIR.mkdir(exist_ok=True)

    print(
        f"Fetching B. subtilis codon usage (species ID {BSUBTILIS_GENUS_ID})..."
    )

    success, content, fetch_info = fetch_kazusa_html(
        BSUBTILIS_GENUS_ID
    )

    if not success:
        print(f"✗ Failed: {fetch_info.get('error')}")
        sys.exit(1)

    print(f"✓ Fetched ({len(content)} bytes)")

    print("Parsing codon frequencies...")
    parse_success, codon_dict, parse_info = parse_kazusa_html(content)

    if not parse_success:
        print(f"✗ Parse failed: {parse_info}")
        sys.exit(1)

    print(f"✓ Parsed {parse_info['parsed_codons']} codons")

    print("Organizing by amino acid...")
    by_aa = organize_by_amino_acid(codon_dict)
    print(f"✓ {len(by_aa)} amino acid families")

    print(f"\nSaving to {CODON_USAGE_FILE}...")
    save_codon_usage_csv(codon_dict, by_aa, CODON_USAGE_FILE)

    if CODON_USAGE_FILE.exists():
        size = CODON_USAGE_FILE.stat().st_size

        with open(CODON_USAGE_FILE) as f:
            lines = len(f.readlines())

        print(f"✓ {size} bytes, {lines} lines")

    print("\n" + "=" * 80)
    print("Step 1 complete")
    print(f"  Output: {CODON_USAGE_FILE}")
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_step1()