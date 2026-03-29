# UIL 5A District 14 Academic Competition — 2025-2026 Season

## Data Source
Results are posted on Speechwire. The URL pattern is:
```
https://postings.speechwire.com/r-uil-academics.php?groupingid=N&Submit=View+postings&region=&district=14&state=&conference=5&seasonid=18
```
- Valid event groupingids: 1, 3–22 (groupingid 2 and 23+ return no data)
- Sweepstakes (overall totals): groupingid=-1
- Do NOT include results from groupingids -1, -2, -3 in per-event analysis (those are aggregate sweepstakes pages)

## Schools of Interest
Only track these three schools: **Mesquite Poteet**, **North Mesquite**, **Mesquite Vanguard**

## Region Analysis
Region 1: Districts 1-8
Region 2: Districts 9-16
Region 3: Districts 17-24
Region 4: Districts 25-32

**When doing region analysis, we care about *ANY* school with region qualifiers.

Header names for scores:
| ID | Event | Individual Score | Team Score

| 1  | Accounting | Total | Total
| 3  | Current Issues and Events | Scores Totaled | Total
| 4  | Literary Criticism | Objective Score | Total
| 5  | Ready Writing | [none] |
| 6  | Social Studies | Scores Totaled | Total
| 7  | Spelling | Total | Total
| 8  | Calculator Applications | Total Score | Total
| 9  | Computer Science | Written | Total
| 10 | Mathematics | Total | Total
| 11 | Number Sense | Total | Total
| 12 | Science | Science Total | Total
| 13 | Copy Editing | [none] 
| 14 | Editorial | [none] 
| 15 | Feature Writing | [none]
| 16 | Headline Writing | [none]
| 17 | News Writing | [none]] |
| 18 | Informative Speaking | [none] |
| 19 | Persuasive Speaking | [none] |
| 20 | Lincoln Douglas Debate | [none] |
| 21 | Poetry Interpretation | [none] |
| 22 | Prose Interpretation | [none] |

## Data to Extract
- **Individual results table**: "School" and "Points" columns (sum all individual point entries per school)
- **Team results table**: "School" and "Points" columns
- Combined points per event = individual points + team points

## Events (groupingid mapping)
| ID | Event | Day |
|----|-------|-----|
| 1  | Accounting | 2 |
| 3  | Current Issues and Events | 2 |
| 4  | Literary Criticism | 2 |
| 5  | Ready Writing | 1 |
| 6  | Social Studies | 2 |
| 7  | Spelling | 2 |
| 8  | Calculator Applications | 2 |
| 9  | Computer Science | 2 |
| 10 | Mathematics | 2 |
| 11 | Number Sense | 2 |
| 12 | Science | 2 |
| 13 | Copy Editing | 1 |
| 14 | Editorial | 1 |
| 15 | Feature Writing | 1 |
| 16 | Headline Writing | 1 |
| 17 | News Writing | 1 |
| 18 | Informative Speaking | 1 |
| 19 | Persuasive Speaking | 1 |
| 20 | Lincoln Douglas Debate | 1 |
| 21 | Poetry Interpretation | 1 |
| 22 | Prose Interpretation | 1 |

## Competition Schedule

### Day 1 — Journalism & Speech
- 9:00 AM: Ready Writing, LD Debate (Round 1)
- 9:30 AM: Prose (prelim), Poetry (prelim)
- 10:00 AM: LD Debate (Round 2)
- 11:00 AM: LD Debate (Round 3)
- 11:30 AM: Copy Editing
- 12:00 PM: Informative Speaking (prelim), Persuasive Speaking (prelim), News Writing
- 1:00 PM: Feature Writing
- 2:30 PM: Prose Finals, Poetry Finals, Editorial Writing, LD Semi-Finals
- 3:30 PM: LD Finals, Headline Writing
- 4:30 PM: Informative Speaking Finals, Persuasive Speaking Finals

### Day 2 — Academics
- 9:00 AM: Number Sense, Current Issues and Events
- 10:00 AM: Calculator Applications
- 12:00 PM: Accounting, Spelling, Science
- 2:30 PM: Social Studies, Computer Science (Written Test)
- 3:30 PM: Math
- 4:30 PM: Literary Criticism, Computer Science (Programming)

## Starting Scores (before Day 1)
These are pre-existing points from prior events (not part of this district meet):
- Mesquite Poteet: 76
- North Mesquite: 121
- Mesquite Vanguard: 5

## Final Sweepstakes Results
- **Mesquite Poteet: 607** (1st place)
- **North Mesquite: 573** (2nd place)
- **Mesquite Vanguard: 256.67** (3rd place)

## Scripts
- `scrape_uil.py` — Scrapes Speechwire for all 21 events, outputs JSON
  - Usage: `python scrape_uil.py --conference 5A --district 14`
  - Output: `uil_<conf>_district<dist>.json`
- `build_event_csv.py` — Builds event-by-school CSV from scraped JSON
  - Usage: `python build_event_csv.py uil_5a_district14.json --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"`
- `build_student_csv.py` — Builds individual student grid CSV from scraped JSON
  - Usage: `python build_student_csv.py uil_5a_district14.json --schools "Mesquite Poteet" "North Mesquite" "Mesquite Vanguard"`
- `chart.py` — Generates two-day score progression chart (hardcoded for this meet)
- `scrape_region_qualifiers.py` — Scrapes all districts in a region, outputs region qualifiers CSV
  - Usage: `python scrape_region_qualifiers.py --conference 5A --region 2`
  - Output: `Region_<N>_qualifiers.csv`
  - Columns: Event, Name, School, District, Score
  - Only includes rows where Advance? = "Region" (alternates excluded)
  - Only scrapes the 10 academic events that have a score column (IDs 1,3,4,6,7,8,9,10,11,12)
  - Optional: `--districts 9 10 11 12` to override auto-computed district list

## Generated Files
- `uil_5a_district14.json` — Raw scraped data from Speechwire
- `uil_results.csv` — Points by event by school (events as rows, schools as columns)
- `uil_student_results.csv` — Individual student points grid (students as rows, events as columns)
- `uil_score_progression.png` — Two-day time-series line chart of score progression
- `Region_<N>_qualifiers.csv` — All region qualifiers across all districts in a region

## Pipeline
```
scrape_uil.py → .json → build_event_csv.py → uil_results.csv
                       → build_student_csv.py → uil_student_results.csv

scrape_region_qualifiers.py → Region_<N>_qualifiers.csv
```
