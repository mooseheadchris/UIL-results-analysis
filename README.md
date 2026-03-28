# UIL Academic Results Scraper & Analyzer

Tools for scraping, analyzing, and visualizing UIL Academic district competition results from [Speechwire](https://postings.speechwire.com).

## Requirements

```bash
pip install requests beautifulsoup4 matplotlib numpy
```

## Pipeline Overview

```
scrape_uil.py → uil_5a_district14.json → build_event_csv.py   → uil_results.csv
                                        → build_student_csv.py → uil_student_results.csv
```

---

## Scripts

### 1. `scrape_uil.py` — Scrape results from Speechwire

Fetches all 21 UIL academic events for a given conference and district and saves the raw results to a JSON file.

```bash
python scrape_uil.py --conference 5A --district 14
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `--conference` | Yes | UIL conference (e.g. `5A`, `6A`, `4A`) |
| `--district` | Yes | District number (e.g. `14`) |
| `--season` | No | Speechwire season ID (default: `18` = 2025-2026) |
| `--output`, `-o` | No | Output JSON filename (default: `uil_<conf>_district<dist>.json`) |
| `--delay` | No | Seconds between requests (default: `0.5`) |

**Examples:**

```bash
# Scrape 5A District 14 (default season)
python scrape_uil.py --conference 5A --district 14

# Scrape 6A District 8, save to custom file
python scrape_uil.py --conference 6A --district 8 -o sixA_dist8.json

# Be more polite to the server
python scrape_uil.py --conference 5A --district 14 --delay 1.0
```

**Output JSON structure:**
```json
{
  "conference": "5A",
  "district": 14,
  "season_id": 18,
  "events": [
    {
      "id": 1,
      "name": "Accounting",
      "individual_results": [
        { "place": 1, "name": "Jane Smith", "school": "Some High", "points": 15 }
      ],
      "team_results": [
        { "place": 1, "school": "Some High", "points": 10, "members": ["Jane Smith", ...] }
      ]
    }
  ]
}
```

---

### 2. `build_event_csv.py` — Event-by-school points table

Builds a CSV with events as rows and schools as columns. Each cell is the combined individual + team points for that school in that event. Includes a TOTAL row at the bottom.

```bash
python build_event_csv.py uil_5a_district14.json --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `input` | Yes | JSON file from `scrape_uil.py` |
| `--schools` | No | Schools to include (default: all schools in the data) |
| `--output`, `-o` | No | Output CSV filename (default: `uil_results.csv`) |

**Examples:**

```bash
# Three specific schools
python build_event_csv.py uil_5a_district14.json \
    --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"

# All schools in the district
python build_event_csv.py uil_5a_district14.json

# Custom output filename
python build_event_csv.py uil_5a_district14.json \
    --schools "Mesquite Poteet" "North Mesquite" \
    -o comparison.csv
```

**Output format:**

| Event | School A | School B |
|---|---|---|
| Accounting | 0 | 18 |
| Calculator Applications | 23 | 37 |
| ... | ... | ... |
| TOTAL | 531 | 452 |

---

### 3. `build_student_csv.py` — Individual student points grid

Builds a CSV with one row per student and one column per event, showing points each student scored. Students with zero points in all events for their school are excluded. Rows are sorted by total points descending.

```bash
python build_student_csv.py uil_5a_district14.json --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"
```

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `input` | Yes | JSON file from `scrape_uil.py` |
| `--schools` | No | Schools to include (default: all schools in the data) |
| `--output`, `-o` | No | Output CSV filename (default: `uil_student_results.csv`) |

**Examples:**

```bash
# Three specific schools
python build_student_csv.py uil_5a_district14.json \
    --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"

# All schools
python build_student_csv.py uil_5a_district14.json

# Single school, custom output
python build_student_csv.py uil_5a_district14.json \
    --schools "Mesquite Poteet" \
    -o poteet_students.csv
```

**Output format:**

| Name | School | Total Points | Accounting | Calculator Applications | ... |
|---|---|---|---|---|---|
| Jane Smith | Some High | 92 | | 8 | ... |
| John Doe | Other High | 73 | 15 | | ... |

Blank cells indicate zero points in that event.

---

### 4. `chart.py` — Score progression chart

Generates a two-day time-series line chart showing cumulative score progression across both competition days. This script is hardcoded for the 2025-2026 UIL 5A District 14 meet (Mesquite Poteet, North Mesquite, Mesquite Vanguard).

```bash
python chart.py
```

Outputs `uil_score_progression.png` in the current directory.

---

## Full Workflow Example

```bash
# 1. Scrape all event results
python scrape_uil.py --conference 5A --district 14

# 2. Build the event-by-school summary
python build_event_csv.py uil_5a_district14.json \
    --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"

# 3. Build the individual student grid
python build_student_csv.py uil_5a_district14.json \
    --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"

# 4. Generate the score progression chart
python chart.py
```

## Generated Files

| File | Description |
|---|---|
| `uil_5a_district14.json` | Raw scraped data — source of truth for all analysis |
| `uil_results.csv` | Points by event by school |
| `uil_student_results.csv` | Points by student by event |
| `uil_score_progression.png` | Two-day score progression chart |
