#!/usr/bin/env python3
"""
Scrape UIL Academic region qualifiers across all districts in a region.

Produces a CSV with columns: Event, Name, School, District, Score

Usage:
    python scrape_region_qualifiers.py --conference 5A --region 4
    python scrape_region_qualifiers.py --conference 5A --region 4 --districts 13 14 15 16
    python scrape_region_qualifiers.py --conference 5A --region 4 --output "Region 4 qualifiers.csv"

Default district range: (region-1)*8+1 through region*8  (e.g. region 2 → 9-16)
Only scrapes events with a score column (10 academic events, excludes journalism/speech/ready writing).
"""

import argparse
import csv
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://postings.speechwire.com/r-uil-academics.php"

# Events with score columns.  Value = (event name, individual score header, team score header)
# Events without a score column (Ready Writing, Journalism, Speech) are omitted.
EVENTS = {
    1:  ("Accounting",                  "total",          "total"),
    3:  ("Current Issues and Events",   "scores totaled", "total"),
    4:  ("Literary Criticism",          "objective score", "total"),
    6:  ("Social Studies",              "scores totaled", "total"),
    7:  ("Spelling",                    "total",          "total"),
    8:  ("Calculator Applications",     "total score",    "total"),
    9:  ("Computer Science",            "written",        "total"),
    10: ("Mathematics",                 "total",          "total"),
    11: ("Number Sense",                "total",          "total"),
    12: ("Science",                     "science total",  "total"),
}


def parse_conference(conf_str: str) -> int:
    """Convert '5A' -> 5, '6A' -> 6, etc."""
    match = re.match(r"(\d+)\s*[Aa]?", conf_str.strip())
    if not match:
        print(f"Error: invalid conference '{conf_str}'. Expected format like '5A'.", file=sys.stderr)
        sys.exit(1)
    return int(match.group(1))


def fetch_qualifiers(
    session: requests.Session,
    conference: int,
    district: int,
    season_id: int,
    grouping_id: int,
    individual_score_col: str = "total",
    team_score_col: str = "total",
) -> list[dict]:
    """
    Fetch a single event page for a district and return region qualifiers.
    Each returned dict has: name, school, score.
    """
    params = {
        "groupingid": grouping_id,
        "Submit": "View postings",
        "region": "",
        "district": district,
        "state": "",
        "conference": conference,
        "seasonid": season_id,
    }
    resp = session.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Quick check: page must have recognizable results headings
    headings = soup.find_all("p", style=re.compile(r"font-size:\s*20px"))
    heading_texts = [h.get_text(strip=True) for h in headings]
    if not any("individual" in t.lower() or "results" in t.lower() for t in heading_texts):
        return []

    tables = soup.find_all("table", class_="ddprint")
    if not tables:
        return []

    qualifiers = []

    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        header_cells = rows[0].find_all("td")
        headers = [c.get_text(separator=" ", strip=True).lower() for c in header_cells]

        # Identify advance column index
        advance_col = next((i for i, h in enumerate(headers) if "advance" in h), None)
        if advance_col is None:
            continue  # skip tables without an Advance? column

        has_entry = any("entry" in h for h in headers)

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) <= advance_col:
                continue

            advance_val = cells[advance_col].get_text(strip=True).replace("\xa0", "").strip()
            if advance_val.lower() != "region":
                continue  # only include region qualifiers, not alternates or blanks

            cell_texts = [
                c.get_text(separator="|", strip=True).replace("\xa0", "").strip()
                for c in cells
            ]
            data = dict(zip(headers, cell_texts))

            if has_entry:
                # Individual results table
                name = data.get("entry", "").replace("|", " ").strip()
                school = data.get("school", "").strip()
                score_str = data.get(individual_score_col, "").strip()
            else:
                # Team results table — school cell may embed member names via |
                school_raw = data.get("school", "")
                parts = school_raw.split("|")
                school = parts[0].strip()
                members = [p.strip() for p in parts[1:] if p.strip()]
                name = ", ".join(members) if members else school
                score_str = data.get(team_score_col, "").strip()
            score = _parse_score(score_str)

            if not school:
                continue

            qualifiers.append({
                "name": name,
                "school": school,
                "score": score,
                "advance": advance_val,
            })

    return qualifiers


def _parse_score(s: str) -> str:
    """Return the score as a clean string (int if whole number, else float, else raw)."""
    s = s.strip()
    if not s or s in ("-", "&nbsp;"):
        return ""
    try:
        val = float(s)
        return str(int(val)) if val == int(val) else str(val)
    except ValueError:
        return s


def districts_for_region(region: int) -> list[int]:
    """Return the 8 district numbers for a given region (1-indexed).
    Region 1: 1-8, Region 2: 9-16, Region 3: 17-24, Region 4: 25-32
    """
    base = (region - 1) * 8 + 1
    return list(range(base, base + 8))


def main():
    parser = argparse.ArgumentParser(
        description="Scrape UIL Academic region qualifiers from Speechwire"
    )
    parser.add_argument("--conference", required=True, help="UIL conference (e.g. '5A', '6A')")
    parser.add_argument("--region", required=True, type=int, help="Region number (e.g. 4)")
    parser.add_argument(
        "--districts", nargs="+", type=int, default=None,
        help="Override district list (e.g. --districts 13 14 15 16)"
    )
    parser.add_argument("--season", type=int, default=18, help="Speechwire season ID (default: 18)")
    parser.add_argument("--output", "-o", default=None, help="Output CSV filename")
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )
    args = parser.parse_args()

    conference = parse_conference(args.conference)
    districts = args.districts or districts_for_region(args.region)
    output_file = args.output or f"Region_{args.region}_qualifiers.csv"

    print(
        f"Scraping UIL {args.conference} Region {args.region} qualifiers "
        f"(districts: {districts}, season {args.season})..."
    )

    session = requests.Session()
    session.headers.update({"User-Agent": "UIL-Results-Scraper/1.0"})

    all_rows = []

    for district in districts:
        print(f"\n--- District {district} ---")
        for gid, (event_name, ind_col, team_col) in sorted(EVENTS.items()):
            print(f"  {event_name}...", end=" ", flush=True)
            try:
                qualifiers = fetch_qualifiers(
                    session, conference, district, args.season, gid,
                    individual_score_col=ind_col, team_score_col=team_col,
                )
                if qualifiers:
                    print(f"{len(qualifiers)} qualifier(s)")
                    for q in qualifiers:
                        all_rows.append({
                            "Event": event_name,
                            "Name": q["name"],
                            "School": q["school"],
                            "District": district,
                            "Score": q["score"],
                        })
                else:
                    print("none")
            except requests.RequestException as e:
                print(f"ERROR: {e}")

            time.sleep(args.delay)

    # Write CSV
    fieldnames = ["Event", "Name", "School", "District", "Score"]
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} qualifier rows to '{output_file}'")


if __name__ == "__main__":
    main()
