#!/usr/bin/env python3
"""
Build individual student results CSV from scraped UIL JSON data.

Usage:
    python build_student_csv.py uil_5a_district14.json --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"
    python build_student_csv.py uil_5a_district14.json --schools "Mesquite Poteet" -o student_results.csv
    python build_student_csv.py uil_5a_district14.json  # all schools

Output: CSV with columns Name, School, Total Points, [event1], [event2], ...
        Blank cells where a student scored 0 in an event.
        Rows sorted by total points descending.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict


def normalize_school(name: str) -> str:
    """Normalize school name for matching (lowercase, stripped)."""
    return name.strip().lower()


def main():
    parser = argparse.ArgumentParser(
        description="Build student results CSV from scraped UIL JSON"
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
        help="Output CSV file (default: uil_student_results.csv)"
    )
    args = parser.parse_args()

    output_file = args.output or "uil_student_results.csv"

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build school filter set (lowercase for case-insensitive matching)
    school_filter = None
    if args.schools:
        school_filter = {normalize_school(s) for s in args.schools}

    def school_matches(school_name: str) -> bool:
        if school_filter is None:
            return True
        return normalize_school(school_name) in school_filter

    # Collect event names in order they appear
    event_names = [e["name"] for e in data["events"]]

    # Build student -> {school, event -> points}
    students = defaultdict(lambda: {"school": "", "events": defaultdict(float)})

    for event in data["events"]:
        event_name = event["name"]
        for entry in event.get("individual_results", []):
            school = entry["school"]
            if not school_matches(school):
                continue
            name = entry["name"]
            points = entry.get("points", 0)
            if points > 0:
                students[name]["school"] = school
                students[name]["events"][event_name] += points

    if not students:
        print("No matching students found.", file=sys.stderr)
        if school_filter:
            print(f"School filter: {args.schools}", file=sys.stderr)
            # Show available schools to help the user
            all_schools = set()
            for event in data["events"]:
                for entry in event.get("individual_results", []):
                    all_schools.add(entry["school"])
            print(f"Available schools: {sorted(all_schools)}", file=sys.stderr)
        sys.exit(1)

    # Build rows
    rows = []
    for name, info in students.items():
        total = sum(info["events"].values())
        row = [name, info["school"]]
        # Format total
        if total == int(total):
            row.append(str(int(total)))
        else:
            row.append(f"{total:.2f}")
        for event_name in event_names:
            pts = info["events"].get(event_name, 0)
            if pts == 0:
                row.append("")
            elif pts == int(pts):
                row.append(str(int(pts)))
            else:
                row.append(f"{pts:.3f}")
        rows.append(row)

    # Sort by total points descending
    rows.sort(key=lambda r: float(r[2]), reverse=True)

    # Write CSV
    header = ["Name", "School", "Total Points"] + event_names
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

    school_label = f" for {', '.join(args.schools)}" if args.schools else ""
    print(f"Wrote {len(rows)} students{school_label} to {output_file}")


if __name__ == "__main__":
    main()
