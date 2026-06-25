#!/usr/bin/env python3
"""
Step 6: Structural Model Quality Assessment

Parses SWISS-MODEL quality reports.

Extracts:
    GMQE
    QMEANDisCo
    Template identity
    Coverage

Input
-----
results/structural_modeling/swissmodel_reports/

Output
------
results/structural_modeling/model_quality_summary.csv
"""

import csv
import re
from pathlib import Path

REPORT_DIR = (
    Path("results")
    / "structural_modeling"
    / "swissmodel_reports"
)

SUMMARY_FILE = (
    Path("results")
    / "structural_modeling"
    / "model_quality_summary.csv"
)


def extract_value(pattern, text):
    match = re.search(pattern, text)

    if match:
        return match.group(1)

    return ""


def run_step6():

    reports = sorted(REPORT_DIR.glob("*"))

    if not reports:
        print("No SWISS-MODEL reports found")
        return

    rows = []

    for report in reports:

        text = report.read_text(errors="ignore")

        rows.append({
            "model": report.stem,
            "gmqe": extract_value(
                r"GMQE[^0-9]*([0-9.]+)",
                text
            ),
            "qmean": extract_value(
                r"QMEAN[^0-9-]*([-0-9.]+)",
                text
            ),
            "identity": extract_value(
                r"Identity[^0-9]*([0-9.]+)",
                text
            ),
            "coverage": extract_value(
                r"Coverage[^0-9]*([0-9.]+)",
                text
            )
        })

    with open(SUMMARY_FILE, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "gmqe",
                "qmean",
                "identity",
                "coverage"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Parsed {len(rows)} models")
    print(f"✓ {SUMMARY_FILE}")


if __name__ == "__main__":
    run_step6()
