#!/usr/bin/env python3
"""
Build event-by-school results CSV from scraped UIL JSON data.

Usage:
    python build_event_csv.py uil_5a_district14.json --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"
    python build_event_csv.py uil_5a_district14.json  # all schools
    python build_event_csv.py uil_5a_district14.json -o results.csv

Output: CSV with events as rows, schools as columns.
        Each cell = sum of individual points + team points for that school in that event.
        Includes a TOTAL row at the bottom.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict


def normalize_school(name: str) -> str:
    return name.strip().lower()


def main():
    parser = argparse.ArgumentParser(
        description="Build event-by-school results CSV from scraped UIL JSON"
    )
    parser.add_argument(
        "input", help="Input JSON file from scrape_uil.py"
    )
    parser.add_argument(
        "--schools", nargs="+", default=None,
        help="Schools to include (default: all). Use quotes for multi-word names."
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output CSV file (default: uil_results.csv)"
    )
    args = parser.parse_args()

    output_file = args.output or "uil_results.csv"

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    school_filter = None
    if args.schools:
        school_filter = {normalize_school(s) for s in args.schools}

    def school_matches(name: str) -> bool:
        if school_filter is None:
            return True
        return normalize_school(name) in school_filter

    # First pass: discover all matching schools (preserving original casing)
    school_names_seen = {}  # lowercase -> original
    for event in data["events"]:
        for entry in event.get("individual_results", []):
            if school_matches(entry["school"]):
                school_names_seen[normalize_school(entry["school"])] = entry["school"]
        for entry in event.get("team_results", []):
            if school_matches(entry["school"]):
                school_names_seen[normalize_school(entry["school"])] = entry["school"]

    if not school_names_seen:
        print("No matching schools found.", file=sys.stderr)
        sys.exit(1)

    # Use the order from --schools if provided, otherwise alphabetical
    if args.schools:
        schools = []
        for s in args.schools:
            key = normalize_school(s)
            if key in school_names_seen:
                schools.append(school_names_seen[key])
        # Add any discovered schools not in the filter (shouldn't happen, but safe)
        for s in sorted(school_names_seen.values()):
            if s not in schools:
                schools.append(s)
    else:
        schools = sorted(school_names_seen.values())

    # Second pass: compute points per event per school
    rows = []
    totals = defaultdict(float)

    for event in data["events"]:
        event_name = event["name"]
        school_points = defaultdict(float)

        for entry in event.get("individual_results", []):
            s = entry["school"]
            if school_matches(s):
                school_points[s] += entry.get("points", 0)

        for entry in event.get("team_results", []):
            s = entry["school"]
            if school_matches(s):
                school_points[s] += entry.get("points", 0)

        row = [event_name]
        for school in schools:
            pts = school_points.get(school, 0)
            totals[school] += pts
            if pts == 0:
                row.append("0")
            elif pts == int(pts):
                row.append(str(int(pts)))
            else:
                row.append(f"{pts:.2f}")
        rows.append(row)

    # Total row
    total_row = ["TOTAL"]
    for school in schools:
        t = totals[school]
        if t == int(t):
            total_row.append(str(int(t)))
        else:
            total_row.append(f"{t:.2f}")
    rows.append(total_row)

    # Write CSV
    header = ["Event"] + schools
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

    school_label = f" for {', '.join(schools)}" if args.schools else ""
    print(f"Wrote {len(rows) - 1} events + totals{school_label} to {output_file}")


if __name__ == "__main__":
    main()
