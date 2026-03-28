#!/usr/bin/env python3
"""
Scrape UIL Academic results from Speechwire for a given conference and district.

Usage:
    python scrape_uil.py --conference 5A --district 14
    python scrape_uil.py --conference 5A --district 14 --season 18 --output results.json

Output: JSON file with all individual and team results for every event.
"""

import argparse
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://postings.speechwire.com/r-uil-academics.php"

# All known UIL academic event groupingids
EVENTS = {
    1: "Accounting",
    3: "Current Issues and Events",
    4: "Literary Criticism",
    5: "Ready Writing",
    6: "Social Studies",
    7: "Spelling",
    8: "Calculator Applications",
    9: "Computer Science",
    10: "Mathematics",
    11: "Number Sense",
    12: "Science",
    13: "Copy Editing",
    14: "Editorial",
    15: "Feature Writing",
    16: "Headline Writing",
    17: "News Writing",
    18: "Informative Speaking",
    19: "Persuasive Speaking",
    20: "Lincoln Douglas Debate",
    21: "Poetry Interpretation",
    22: "Prose Interpretation",
}


def parse_conference(conf_str: str) -> int:
    """Convert '5A' -> 5, '6A' -> 6, etc."""
    match = re.match(r"(\d+)\s*[Aa]?", conf_str.strip())
    if not match:
        print(f"Error: invalid conference '{conf_str}'. Expected format like '5A'.", file=sys.stderr)
        sys.exit(1)
    return int(match.group(1))


def fetch_event(session: requests.Session, conference: int, district: int,
                season_id: int, grouping_id: int) -> dict | None:
    """Fetch and parse a single event page. Returns parsed data or None if no results."""
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

    # Check if the page has actual results (look for "Individual results" heading)
    headings = soup.find_all("p", style=re.compile(r"font-size:\s*20px"))
    heading_texts = [h.get_text(strip=True) for h in headings]

    if not any("individual" in t.lower() or "results" in t.lower() for t in heading_texts):
        return None

    # Find all tables with class 'ddprint'
    tables = soup.find_all("table", class_="ddprint")
    if not tables:
        return None

    individual_results = []
    team_results = []

    for i, table in enumerate(tables):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        # Get headers from first row
        header_cells = rows[0].find_all("td")
        headers = [c.get_text(separator=" ", strip=True).lower() for c in header_cells]

        # Determine if this is individual or team table based on headers
        has_entry = any("entry" in h for h in headers)

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < len(headers):
                continue

            cell_texts = []
            for c in cells:
                txt = c.get_text(separator="|", strip=True)
                # Clean non-breaking spaces
                txt = txt.replace("\xa0", "").strip()
                cell_texts.append(txt)

            if has_entry:
                # Individual results table
                entry = _parse_individual_row(headers, cell_texts)
                if entry:
                    individual_results.append(entry)
            else:
                # Team results table
                entry = _parse_team_row(headers, cell_texts)
                if entry:
                    team_results.append(entry)

    if not individual_results and not team_results:
        return None

    return {
        "individual_results": individual_results,
        "team_results": team_results,
    }


def _parse_individual_row(headers: list[str], cells: list[str]) -> dict | None:
    """Parse a single row from the individual results table."""
    data = dict(zip(headers, cells))

    school = data.get("school", "").strip()
    if not school:
        return None

    # Entry field contains the student name
    entry_raw = data.get("entry", "")
    # Clean up any pipe separators from get_text(separator="|")
    name = entry_raw.replace("|", " ").strip()

    # Parse points
    points_str = data.get("points", "").strip()
    points = _parse_points(points_str)

    place_str = data.get("place", "").strip()
    try:
        place = int(place_str)
    except (ValueError, TypeError):
        place = None

    return {
        "place": place,
        "name": name,
        "school": school,
        "points": points,
    }


def _parse_team_row(headers: list[str], cells: list[str]) -> dict | None:
    """Parse a single row from the team results table."""
    data = dict(zip(headers, cells))

    school_raw = data.get("school", "").strip()
    if not school_raw:
        return None

    # School cell may contain team member names separated by |
    parts = school_raw.split("|")
    school = parts[0].strip()
    members = [p.strip() for p in parts[1:] if p.strip()]

    points_str = data.get("points", "").strip()
    points = _parse_points(points_str)

    place_str = data.get("place", "").strip()
    try:
        place = int(place_str)
    except (ValueError, TypeError):
        place = None

    return {
        "place": place,
        "school": school,
        "points": points,
        "members": members,
    }


def _parse_points(s: str) -> float:
    """Parse a points string, returning 0 for blanks/dashes."""
    s = s.strip()
    if not s or s == "-" or s == "&nbsp;":
        return 0
    try:
        val = float(s)
        return int(val) if val == int(val) else val
    except ValueError:
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Scrape UIL Academic results from Speechwire"
    )
    parser.add_argument(
        "--conference", required=True,
        help="UIL conference (e.g., '5A', '6A', '4A')"
    )
    parser.add_argument(
        "--district", required=True, type=int,
        help="District number (e.g., 14)"
    )
    parser.add_argument(
        "--season", type=int, default=18,
        help="Speechwire season ID (default: 18 for 2025-2026)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output JSON file (default: uil_<conf>_district<dist>.json)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )
    args = parser.parse_args()

    conference = parse_conference(args.conference)
    district = args.district
    season_id = args.season
    output_file = args.output or f"uil_{args.conference.lower()}_district{district}.json"

    print(f"Scraping UIL {args.conference} District {district} (season {season_id})...")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "UIL-Results-Scraper/1.0"
    })

    all_events = []
    for gid, event_name in sorted(EVENTS.items()):
        print(f"  Fetching {event_name} (id={gid})...", end=" ", flush=True)
        try:
            data = fetch_event(session, conference, district, season_id, gid)
            if data:
                ind_count = len(data["individual_results"])
                team_count = len(data["team_results"])
                print(f"{ind_count} individual, {team_count} team entries")
                all_events.append({
                    "id": gid,
                    "name": event_name,
                    **data,
                })
            else:
                print("no results")
        except requests.RequestException as e:
            print(f"ERROR: {e}")

        time.sleep(args.delay)

    output = {
        "conference": args.conference.upper(),
        "district": district,
        "season_id": season_id,
        "events": all_events,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(all_events)} events to {output_file}")


if __name__ == "__main__":
    main()
