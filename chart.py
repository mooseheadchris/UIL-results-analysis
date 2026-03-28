import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ── Two-day score progression ──
# Starting scores (before Day 1): Poteet=76, NM=121, Vanguard=5
# Day 1 = journalism/speech events
# Day 2 = academic events
# Final totals match sweepstakes: 607 / 573 / 256.67

# X positions: evenly spaced with a gap between days
x = np.array([0, 1, 2, 3, 4, 5, 6, 7,     9, 10, 11, 12, 13, 14])
#             Day 1 --->                     Day 2 --->

time_labels = [
    # Day 1
    "Start",
    "9:00 AM",
    "11:30 AM",
    "12:00 PM",
    "1:00 PM",
    "2:30 PM",
    "3:30 PM",
    "4:30 PM",
    # Day 2
    "9:00 AM",
    "10:00 AM",
    "12:00 PM",
    "2:30 PM",
    "3:30 PM",
    "4:30 PM",
]

# Events at each time slot
events_at = [
    # Day 1
    "",
    "Ready Writing",
    "Copy Editing",
    "News Writing",
    "Feature Writing",
    "Editorial, Prose\nPoetry",
    "Headline Writing\nLD Debate",
    "Informative Spk\nPersuasive Spk",
    # Day 2
    "Number Sense\nCurrent Issues",
    "Calculator Apps",
    "Accounting, Spelling\nScience",
    "Social Studies",
    "Math",
    "Lit Criticism\nComputer Science",
]

# Cumulative scores
# Day 1:
#   Start:    76 / 121 / 5
#   9:00 AM:  +ReadyWr(33/18/0)
#   11:30 AM: +CopyEdit(12/22/21)
#   12:00 PM: +NewsWr(18/19/18)
#   1:00 PM:  +Feature(14/35/6)
#   2:30 PM:  +Editorial(0/35/20) +Prose(37/18/0) +Poetry(33/22/0)
#   3:30 PM:  +Headline(20/23/12) +LD(24/31/0)
#   4:30 PM:  +InfoSpk(33/22/0) +PersSpk(26/29/0)
# Day 2:
#   9:00 AM:  +NumSense(41/21/8) +CurrIss(35/0/0)
#   10:00 AM: +CalcApps(23/37/10)
#   12:00 PM: +Acct(0/18/0) +Spell(37/0/18) +Sci(0/9/70)
#   2:30 PM:  +SocStud(38/10/22)
#   3:30 PM:  +Math(26/32/10.67)
#   4:30 PM:  +LitCrit(49/16/0) +CompSci(32/35/36)

poteet = [76, 109, 121, 139, 153, 223, 267, 326,     402, 425, 462, 500, 526, 607]
nm     = [121, 139, 161, 180, 215, 290, 344, 395,    416, 453, 480, 490, 522, 573]
van    = [5,    5,  26,  44,  50,  70,  82,  82,      90, 100, 188, 210, 220.67, 256.67]

# ── Plot ──
fig, ax = plt.subplots(figsize=(18, 8))

c_poteet = '#228B22'   # green
c_nm     = '#1f77b4'   # blue
c_van    = '#e68a00'   # orange

ax.plot(x, poteet, marker='o', linewidth=2.5, markersize=7,
        color=c_poteet, label='Mesquite Poteet', zorder=3)
ax.plot(x, nm,     marker='s', linewidth=2.5, markersize=7,
        color=c_nm,     label='North Mesquite', zorder=3)
ax.plot(x, van,    marker='^', linewidth=2.5, markersize=7,
        color=c_van,    label='Mesquite Vanguard', zorder=3)

# Day separator
ax.axvline(x=8, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)
ax.text(3.5, 635, 'DAY 1 — Journalism & Speech', ha='center', fontsize=11,
        fontweight='bold', color='#555')
ax.text(11.5, 635, 'DAY 2 — Academics', ha='center', fontsize=11,
        fontweight='bold', color='#555')

# Annotate scores at each point
for i in range(len(x)):
    p, n, v = poteet[i], nm[i], van[i]

    # Sort the three values to figure out best placement
    pts = sorted([(p, 'p'), (n, 'n'), (v, 'v')])

    offsets = {}
    # Place labels: bottom gets -18, top gets +10, middle decides based on proximity
    offsets[pts[0][1]] = -17
    offsets[pts[2][1]] = 10

    mid_key = pts[1][1]
    gap_above = pts[2][0] - pts[1][0]
    gap_below = pts[1][0] - pts[0][0]
    if gap_above >= gap_below and gap_above >= 20:
        offsets[mid_key] = 10
    elif gap_below >= 20:
        offsets[mid_key] = -17
    elif gap_above > gap_below:
        offsets[mid_key] = 10
    else:
        offsets[mid_key] = -17

    colors = {'p': c_poteet, 'n': c_nm, 'v': c_van}
    vals   = {'p': p, 'n': n, 'v': v}

    for key in ['p', 'n', 'v']:
        val = vals[key]
        label = str(int(val)) if val == int(val) else f"{val:.1f}"
        ax.annotate(label, (x[i], val),
                    textcoords="offset points", xytext=(0, offsets[key]),
                    ha='center', fontsize=7.5, color=colors[key], fontweight='bold')

# Event annotations below x-axis
for i in range(len(x)):
    if events_at[i]:
        ax.annotate(events_at[i], (x[i], 0),
                    textcoords="offset points", xytext=(0, -55),
                    ha='center', fontsize=6.5, color='#666',
                    fontstyle='italic', va='top')

ax.set_xticks(x)
ax.set_xticklabels(time_labels, fontsize=8, rotation=30, ha='right')
ax.set_ylabel('Cumulative Points', fontsize=12)
ax.set_title('UIL 5A District 14 — Score Progression\n(2025-2026 Season)',
             fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.yaxis.set_minor_locator(ticker.MultipleLocator(25))
ax.grid(True, which='major', linestyle='--', alpha=0.4)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)
ax.set_ylim(0, 660)
ax.set_xlim(-0.5, 14.8)

plt.subplots_adjust(bottom=0.22)
plt.savefig('uil_score_progression.png', dpi=150, bbox_inches='tight')
print("Chart saved to uil_score_progression.png")
