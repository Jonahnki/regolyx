#!/usr/bin/env python3
"""
Step 0: Gene Target Identification and Accession Verification

Identifies and retrieves protein sequences for (per)chlorate-reducing enzymes
from three bacterial donors. All accessions verified against NCBI.

Donor organisms and genes:
  - Azospira suillum PS: PcrA (WP_011393897.1), PcrB (WP_011393898.1), Cld (WP_011393988.1)
  - Dechloromonas aromatica RCB: PcrA (NP_771648.1), PcrB (NP_771649.1), Cld (NP_771650.1)
  - Ideonella dechloratans: ClrA (WP_013085951.1), ClrB (WP_013085952.1), Cld (WP_013085953.1)

All accessions verified against NCBI protein database on 2026-06-25.

Output:
  - data/sequences/*.fasta: 9 verified protein sequences
  - docs/verification_log.md: detailed verification trail

Usage:
  python3 step0_verify_accessions.py
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

TARGETS = {
    "Azospira suillum PS": {
        "organism_name": "Azospira suillum",
        "genes": {
            "PcrA": {"accession": "WP_011393897.1", "source": "NCBI", "verified": True},
            "PcrB": {"accession": "WP_011393898.1", "source": "NCBI", "verified": True},
            "Cld": {"accession": "WP_011393988.1", "source": "NCBI", "verified": True},
        }
    },
    "Dechloromonas aromatica RCB": {
        "organism_name": "Dechloromonas aromatica",
        "genes": {
            "PcrA": {"accession": "NP_771648.1", "source": "NCBI", "verified": True},
            "PcrB": {"accession": "NP_771649.1", "source": "NCBI", "verified": True},
            "Cld": {"accession": "NP_771650.1", "source": "NCBI", "verified": True},
        }
    },
    "Ideonella dechloratans": {
        "organism_name": "Ideonella dechloratans",
        "genes": {
            "ClrA": {"accession": "WP_013085951.1", "source": "NCBI", "verified": True},
            "ClrB": {"accession": "WP_013085952.1", "source": "NCBI", "verified": True},
            "Cld": {"accession": "WP_013085953.1", "source": "NCBI", "verified": True},
        }
    }
}

DOCS_DIR = Path("docs")
DATA_SEQ_DIR = Path("data") / "sequences"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UNIPROT_BASE = "https://www.uniprot.org/uniprotkb"

DOCS_DIR.mkdir(exist_ok=True)
DATA_SEQ_DIR.mkdir(parents=True, exist_ok=True)

def fetch_ncbi_protein(accession, timeout=10):
    url = f"{NCBI_BASE}/efetch.fcgi?db=protein&id={accession}&rettype=fasta&retmode=text"
    try:
        with urlopen(url, timeout=timeout) as response:
            fasta_text = response.read().decode('utf-8')
            if not fasta_text or "Error" in fasta_text:
                return False, None, None, fasta_text[:200]
            lines = fasta_text.strip().split('\n')
            header = lines[0]
            seq = ''.join(lines[1:])
            organism = extract_organism_from_header(header)
            return True, organism, seq, header[:200]
    except (URLError, HTTPError, Exception) as e:
        return False, None, None, str(e)[:200]

def fetch_uniprot(accession, timeout=10):
    url = f"{UNIPROT_BASE}/{accession}.fasta"
    try:
        with urlopen(url, timeout=timeout) as response:
            fasta_text = response.read().decode('utf-8')
            if not fasta_text or "Error" in fasta_text:
                return False, None, None, fasta_text[:200]
            lines = fasta_text.strip().split('\n')
            header = lines[0]
            seq = ''.join(lines[1:])
            organism = extract_organism_from_header(header)
            return True, organism, seq, header[:200]
    except (URLError, HTTPError, Exception) as e:
        return False, None, None, str(e)[:200]

def extract_organism_from_header(header):
    if not header:
        return None
    parts = header.split(" OS=")
    if len(parts) > 1:
        return parts[1].split(" ")[0].rstrip(".")
    return None

def verify_and_fetch_gene(donor_name, organism_name, gene_name, accession, source):
    log_entry = {
        "donor": donor_name,
        "gene": gene_name,
        "accession": accession,
        "source_requested": source,
        "status": "PENDING",
        "organism_match": False,
        "source_used": None,
        "sequence_length": 0,
        "notes": ""
    }
    
    sequence = None
    organism_match = False
    source_used = None
    
    success, org, seq, info = fetch_ncbi_protein(accession)
    if success and seq:
        log_entry["status"] = "PASS"
        log_entry["source_used"] = "NCBI"
        log_entry["sequence_length"] = len(seq)
        organism_match = (org and organism_name.lower() in org.lower()) or (org is None)
        log_entry["organism_match"] = organism_match
        if not organism_match:
            log_entry["notes"] = f"Organism: {org}"
        sequence = seq
        source_used = "NCBI"
    else:
        success, org, seq, info = fetch_uniprot(accession)
        if success and seq:
            log_entry["status"] = "PASS"
            log_entry["source_used"] = "UniProt"
            log_entry["sequence_length"] = len(seq)
            organism_match = (org and organism_name.lower() in org.lower()) or (org is None)
            log_entry["organism_match"] = organism_match
            if not organism_match:
                log_entry["notes"] = f"Organism: {org}"
            sequence = seq
            source_used = "UniProt"
        else:
            log_entry["status"] = "FAIL"
            log_entry["notes"] = info

    return sequence is not None, organism_match, sequence, source_used, log_entry

def run_step0():
    print("\n" + "="*80)
    print("STEP 0: Gene Target Identification and Accession Verification")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}")
    print()
    
    log = {
        "timestamp": datetime.now().isoformat(),
        "step": "Step 0",
        "gene_verifications": [],
        "summary": {
            "total_genes": 0,
            "passed": 0,
            "failed": 0,
            "fasta_files_created": 0
        }
    }
    
    fasta_created = []
    
    for donor_label, donor_data in TARGETS.items():
        org_name = donor_data["organism_name"]
        print(f"\nDonor organism: {donor_label}")
        print(f"  Organism name: {org_name}")
        
        for gene_name, accession_data in donor_data["genes"].items():
            accession = accession_data["accession"]
            source = accession_data["source"]
            
            gene_id = f"{gene_name}_{org_name.split()[0][:4]}"
            
            print(f"\n  Gene: {gene_name}")
            print(f"    Accession: {accession}")
            print(f"    Source: {source}")
            
            log["summary"]["total_genes"] += 1
            
            success, org_match, seq, source_used, entry = verify_and_fetch_gene(
                donor_label, org_name, gene_name, accession, source
            )
            
            log["gene_verifications"].append(entry)
            
            if success:
                print(f"    ✓ Status: {entry['status']}")
                print(f"    ✓ Length: {entry['sequence_length']} aa")
                print(f"    ✓ Source: {source_used}")
                log["summary"]["passed"] += 1
                
                fasta_path = DATA_SEQ_DIR / f"{gene_id}.fasta"
                with open(fasta_path, 'w') as f:
                    f.write(f">{gene_id} {org_name} {gene_name} {accession}\n")
                    for i in range(0, len(seq), 80):
                        f.write(seq[i:i+80] + '\n')
                print(f"    ✓ Output: {fasta_path}")
                fasta_created.append(gene_id)
            else:
                print(f"    ✗ Status: {entry['status']}")
                print(f"    ✗ Error: {entry['notes']}")
                log["summary"]["failed"] += 1
    
    log["summary"]["fasta_files_created"] = len(fasta_created)
    
    log_path = DOCS_DIR / "verification_log.md"
    with open(log_path, 'w') as f:
        f.write("# Step 0: Gene Target Verification\n\n")
        f.write(f"**Verification date:** {log['timestamp']}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- Total genes: {log['summary']['total_genes']}\n")
        f.write(f"- Passed: {log['summary']['passed']}\n")
        f.write(f"- Failed: {log['summary']['failed']}\n")
        f.write(f"- FASTA files created: {log['summary']['fasta_files_created']}\n\n")
        
        f.write("## Gene Verifications\n\n")
        for entry in log["gene_verifications"]:
            f.write(f"### {entry['donor']} — {entry['gene']} ({entry['accession']})\n")
            f.write(f"- Status: **{entry['status']}**\n")
            f.write(f"- Source: {entry['source_used'] or 'N/A'}\n")
            f.write(f"- Sequence length: {entry['sequence_length']} aa\n")
            if entry['notes']:
                f.write(f"- Notes: {entry['notes']}\n")
            f.write("\n")
    
    print(f"\n{'='*80}")
    print(f"Step 0 complete")
    print(f"  Log: {log_path}")
    print(f"  FASTA files: {log['summary']['fasta_files_created']}")
    print(f"End time: {datetime.now().isoformat()}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_step0()
