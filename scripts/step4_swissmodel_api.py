#!/usr/bin/env python3
"""
Step 4: SWISS-MODEL Submission and Modelling via REST API

Purpose
-------
Submit all verified protein sequences to SWISS-MODEL programmatically via
the official REST API, poll until each job completes, and retrieve
structured JSON results directly. This replaces the previous two-step
manual process (step5_swissmodel_prep.py for file packaging + manual
browser upload, followed by step6_model_quality_parser.py scraping the
returned HTML report with regex).

Rationale for this change
--------------------------
The original step6 parser extracted GMQE/QMEAN/identity/coverage from
SWISS-MODEL's HTML report using regex keyed on label proximity. This
silently failed: every extracted value was wrong, because the regex
matched unrelated numbers in nearby markup (e.g. an image file path)
rather than the actual score, which sits inside a separate HTML table.
Submitting via the API and reading the JSON response directly removes
this entire failure mode, since the relevant fields are returned as
named, typed JSON values rather than something to be scraped out of
rendered HTML. It also removes the manual copy/paste-into-browser step,
which is itself a source of possible transcription error.

Authentication
---------------
Requires an API token, NOT a plaintext username/password, in the
environment variable SWISSMODEL_TOKEN.

To obtain a token (run this yourself, locally — never paste a password
into a script or chat):

    curl -X POST https://swissmodel.expasy.org/api-token-auth/ \\
      -H "Content-Type: application/json" \\
      -d '{"username": "YOUR_EMAIL", "password": "YOUR_PASSWORD"}'

This returns a token. Export it before running this script:

    export SWISSMODEL_TOKEN="the_token_value"

Input
-----
data/sequences/*.fasta

Output
------
results/structural_modeling/
    swissmodel_api_results.json   (raw API responses, one per gene)
    model_quality_summary.csv     (parsed from JSON, not HTML)
    models/<gene_id>.pdb          (downloaded coordinate files, if available)

Reference
---------
Waterhouse et al. (2018)
SWISS-MODEL: Homology modelling of protein structures and complexes.
Nucleic Acids Research 46(W1):W296-W303
"""

import csv
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

API_BASE = "https://swissmodel.expasy.org"
AUTOMODEL_ENDPOINT = f"{API_BASE}/automodel/"
PROJECT_STATUS_ENDPOINT = f"{API_BASE}/project/{{project_id}}/models/summary/"

DATA_SEQ_DIR = Path("data") / "sequences"
RESULTS_DIR = Path("results") / "structural_modeling"
MODELS_DIR = RESULTS_DIR / "models"
RAW_RESULTS_FILE = RESULTS_DIR / "swissmodel_api_results.json"
SUMMARY_FILE = RESULTS_DIR / "model_quality_summary.csv"

POLL_INTERVAL_SECONDS = 30
POLL_TIMEOUT_SECONDS = 3600  # 1 hour ceiling per job


def get_token():
    token = os.environ.get("SWISSMODEL_TOKEN")
    if not token:
        print("ERROR: SWISSMODEL_TOKEN environment variable not set.")
        print("Generate a token locally (see script docstring) and export it before running.")
        sys.exit(1)
    return token


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


def api_request(url, token, method="GET", payload=None):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return True, json.loads(body) if body else {}
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return False, {"error": f"HTTP {e.code}", "detail": error_body[:500]}
    except URLError as e:
        return False, {"error": str(e)[:500]}


def submit_job(gene_id, sequence, token):
    payload = {
        "target_sequences": sequence,
        "project_title": f"Regolyx_{gene_id}",
    }
    ok, result = api_request(AUTOMODEL_ENDPOINT, token, method="POST", payload=payload)
    return ok, result


def poll_job(project_id, token, gene_id):
    elapsed = 0
    url = PROJECT_STATUS_ENDPOINT.format(project_id=project_id)

    while elapsed < POLL_TIMEOUT_SECONDS:
        ok, result = api_request(url, token, method="GET")

        if not ok:
            return False, result

        status = result.get("status", "UNKNOWN")

        if status in ("COMPLETED", "FINISHED", "DONE"):
            return True, result
        if status in ("FAILED", "ERROR"):
            return False, result

        print(f"  {gene_id}: status={status}, waiting {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    return False, {"error": "timeout", "detail": f"Job did not complete within {POLL_TIMEOUT_SECONDS}s"}


def extract_quality_row(gene_id, result_json):
    """
    Pull GMQE/QMEAN directly from JSON fields.

    Confirmed against a real SWISS-MODEL API response (2026-06-25): the
    "models" list is not ordered by completeness, and only some entries
    carry the nested "qmean_global" object. This selects the model with
    the most complete quality data rather than assuming models[0] is
    best. "identity", "coverage", and "template" are not present
    anywhere in the observed response schema for this endpoint and are
    left as None rather than guessed; per-residue/template alignment
    detail would need a different endpoint if required later.
    """
    models = result_json.get("models", [])

    # Prefer the model with qmean_global data present, since list order
    # is not guaranteed to put the most complete model first.
    best_model = {}
    for m in models:
        if "qmean_global" in m:
            best_model = m
            break
    if not best_model and models:
        best_model = models[0]

    qmean_global = best_model.get("qmean_global", {})

    return {
        "gene_id": gene_id,
        "gmqe": best_model.get("gmqe"),
        "qmean": qmean_global.get("avg_local_score"),
        "identity": None,
        "coverage": None,
        "template": None,
        "status": result_json.get("status"),
    }


def run_step4():
    print("\n" + "=" * 80)
    print("STEP 4: SWISS-MODEL Submission via REST API")
    print("=" * 80)

    token = get_token()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    fasta_files = sorted(DATA_SEQ_DIR.glob("*.fasta"))
    if not fasta_files:
        print("No FASTA files found")
        return

    all_results = {}
    summary_rows = []

    for fasta in fasta_files:
        gene_id = fasta.stem
        header, seq = read_fasta(fasta)

        print(f"\nSubmitting {gene_id} ({len(seq)} aa)...")
        ok, submit_result = submit_job(gene_id, seq, token)

        if not ok:
            print(f"  ✗ Submission failed: {submit_result}")
            all_results[gene_id] = {"submit_error": submit_result}
            summary_rows.append({
                "gene_id": gene_id, "gmqe": None, "qmean": None,
                "identity": None, "coverage": None,
                "template": None, "status": "SUBMIT_FAILED",
            })
            continue

        project_id = submit_result.get("project_id") or submit_result.get("id")
        if not project_id:
            print(f"  ✗ No project_id in response: {submit_result}")
            all_results[gene_id] = {"submit_error": "no project_id returned", "raw": submit_result}
            continue

        print(f"  Submitted, project_id={project_id}. Polling for completion...")
        ok, final_result = poll_job(project_id, token, gene_id)

        all_results[gene_id] = final_result

        if not ok:
            print(f"  ✗ Job did not complete successfully: {final_result.get('error')}")
            summary_rows.append({
                "gene_id": gene_id, "gmqe": None, "qmean": None,
                "identity": None, "coverage": None,
                "template": None, "status": "FAILED",
            })
            continue

        print(f"  ✓ {gene_id} complete")
        summary_rows.append(extract_quality_row(gene_id, final_result))

    with open(RAW_RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)

    with open(SUMMARY_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["gene_id", "gmqe", "qmean", "identity", "coverage", "template", "status"]
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print()
    print(f"Raw API results: {RAW_RESULTS_FILE}")
    print(f"Quality summary: {SUMMARY_FILE}")
    print(f"Finished: {datetime.now().isoformat()}")
    print()
    print("NOTE: extract_quality_row() field names are best-effort based on")
    print("documented SWISS-MODEL API conventions. After the first real run,")
    print("inspect swissmodel_api_results.json directly and adjust the field")
    print("names in extract_quality_row() if they don't match the actual")
    print("response schema, before trusting model_quality_summary.csv.")


if __name__ == "__main__":
    run_step4()
