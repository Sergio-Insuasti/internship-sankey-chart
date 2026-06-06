import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from collections import defaultdict

# holds all applications for analysis
applications = []
# stores applications by company name
companies = defaultdict(list)
# frequency map of industries
industries = defaultdict(int)
# frequency map of statuses
app_statuses = defaultdict(int)

PIPELINE = ['Submitted', 'No Response', 'Rejected', 'OA', '1st Round', '2nd Round', 'Offer Sent', 'Accepted']

# DATA INGESTER
# replace path name with your version of template.csv!
with open('./data.csv', newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company  = row['Company Name'].strip()
        industry = row['Industry'].strip()
        position = row['Position'].strip()
        salary   = row['Max Salary'].strip()
        status   = row['Status'].strip()
 
        applications.append({
            'company':  company,
            'industry': industry,
            'position': position,
            'salary':   int(salary) if salary.isdigit() else None,
            'status':   status,
        })
 
        companies[company].append(position)
        industries[industry] += 1
 
        if status not in PIPELINE:
            PIPELINE.append(status)
        app_statuses[status] += 1
app_statuses['Submitted'] = len(applications)


total = len(applications)
salaries = [a['salary'] for a in applications if a['salary']]
avg_salary = int(np.mean(salaries)) if salaries else 0
max_salary = max(salaries) if salaries else 0


# TERMINAL SUMMARY
print("=" * 50)
print("  INTERNSHIP APPLICATION ANALYSER")
print("=" * 50)
print(f"\n  Total applications : {total}")
print(f"  Avg listed salary  : ${avg_salary:,}")
print(f"  Max listed salary  : ${max_salary:,}")
print(f"  Unique companies   : {len(companies)}")
print(f"  Unique industries  : {len(industries)}\n")
 
print("  Status Breakdown:")
for s in PIPELINE:
    if s == 'Submitted':
        continue
    count = app_statuses.get(s, 0)
    pct   = count / total * 100
    bar   = '=' * int(pct / 2)
    print(f"    {s:<14} {count:>3}  {bar} {pct:.0f}%")
 
print("\n  Industry breakdown:")
for ind, count in sorted(industries.items(), key=lambda x: -x[1]):
    pct = count / total * 100
    bar   = '=' * int(pct / 2)
    print(f"    {ind:<18} {count:>3} {bar} {pct:.0f}%")
 
print("\n  Companies with multiple applications:")
for co, positions in sorted(companies.items()):
    if len(positions) > 1:
        print(f"    {co} ({len(positions)})")


# PRESENTING THE DATA
 
STATUS_COLORS = {
    'No Response': '#B4B2A9',
    'Rejected':    '#E24B4A',
    'OA':          '#EF9F27',
    '1st Round':   '#BA7517',
    '2nd Round':   '#854F0B',
    'Final Round': '#534AB7',
    'Offer Sent':  '#1D9E75',
    'Accepted':    '#1D9E75',
}
IND_COLORS = ['#378ADD','#EF9F27','#1D9E75','#E24B4A','#534AB7','#B4B2A9','#854F0B']
 
# Sankey Diagram — cleaner application funnel layout

BLUE = '#5B9BD5'
GREEN = '#1D9E75'
GREY = '#B4B2A9'
TEXT = '#2C2C2A'
BG = '#FAFAF8'
LINK = '#B8B8B8'

# Current/final status counts
n_no_resp = app_statuses.get('No Response', 0)
n_rejected = app_statuses.get('Rejected', 0)
n_oa_stop = app_statuses.get('OA', 0)
n_r1_stop = app_statuses.get('1st Round', 0)
n_r2_stop = app_statuses.get('2nd Round', 0)
n_final_stop = app_statuses.get('Final Round', 0)
n_accepted = app_statuses.get('Offer Sent', 0) + app_statuses.get('Accepted', 0)

# Cumulative reached-stage counts
n_final = n_final_stop + n_accepted
n_r2 = n_r2_stop + n_final
n_r1 = n_r1_stop + n_r2
n_oa = n_oa_stop + n_r1

BAR_W = 0.006
SCALE = 0.68
MIN_H = 0.012

def scaled_height(value):
    if value <= 0:
        return 0
    return max((value / total) * SCALE, MIN_H)

# id: x, y_center, count, label, colour, label_side
nodes = {
    'submitted':  (0.07, 0.52, total, 'Applications', BLUE, 'left'),
    'oa':         (0.27, 0.62, n_oa, 'OA', BLUE, 'right'),
    'r1':         (0.45, 0.66, n_r1, '1st Round', BLUE, 'right'),
    'r2':         (0.63, 0.70, n_r2, '2nd Round', BLUE, 'right'),
    'final':      (0.78, 0.73, n_final, 'Final Round', BLUE, 'right'),
    'accepted':   (0.92, 0.73, n_accepted, 'Accepted', GREEN, 'right'),

    'no_resp':    (0.27, 0.33, n_no_resp, 'No response', GREY, 'right'),
    'rejected':   (0.27, 0.17, n_rejected, 'Rejected', GREY, 'right'),
    'oa_stop':    (0.45, 0.48, n_oa_stop, 'Rejected', GREY, 'right'),
    'r1_stop':    (0.63, 0.55, n_r1_stop, 'Failed', GREY, 'right'),
    'r2_stop':    (0.78, 0.62, n_r2_stop, 'Failed', GREY, 'right'),
    'final_stop': (0.92, 0.64, n_final_stop, 'No offer', GREY, 'right'),
}

links = [
    ('submitted', 'rejected', n_rejected),
    ('submitted', 'no_resp', n_no_resp),
    ('submitted', 'oa', n_oa),

    ('oa', 'oa_stop', n_oa_stop),
    ('oa', 'r1', n_r1),

    ('r1', 'r1_stop', n_r1_stop),
    ('r1', 'r2', n_r2),

    ('r2', 'r2_stop', n_r2_stop),
    ('r2', 'final', n_final),

    ('final', 'final_stop', n_final_stop),
    ('final', 'accepted', n_accepted),
]

geom = {
    node_id: (x, y, scaled_height(count), count, label, color, label_side)
    for node_id, (x, y, count, label, color, label_side) in nodes.items()
    if count > 0
}

fig_sankey, ax = plt.subplots(figsize=(10, 5.2))
fig_sankey.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

out_offset = {node_id: 0 for node_id in geom}
in_offset = {node_id: 0 for node_id in geom}

def draw_link(source_id, target_id, value):
    if value <= 0 or source_id not in geom or target_id not in geom:
        return

    sx, sy, sh, *_ = geom[source_id]
    tx, ty, th, *_ = geom[target_id]

    link_height = scaled_height(value)

    sy_bottom = sy - sh / 2 + out_offset[source_id]
    ty_bottom = ty - th / 2 + in_offset[target_id]

    out_offset[source_id] += link_height
    in_offset[target_id] += link_height

    x0 = sx + BAR_W
    x1 = tx - BAR_W
    mid_x = x0 + (x1 - x0) * 0.55

    verts = [
        (x0, sy_bottom),
        (mid_x, sy_bottom),
        (mid_x, ty_bottom),
        (x1, ty_bottom),

        (x1, ty_bottom + link_height),
        (mid_x, ty_bottom + link_height),
        (mid_x, sy_bottom + link_height),
        (x0, sy_bottom + link_height),

        (x0, sy_bottom),
    ]

    codes = [
        Path.MOVETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.LINETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CLOSEPOLY,
    ]

    patch = mpatches.PathPatch(
        Path(verts, codes),
        facecolor=LINK,
        edgecolor='none',
        alpha=0.55,
        zorder=1,
    )
    ax.add_patch(patch)

for source_id, target_id, value in links:
    draw_link(source_id, target_id, value)

for node_id, (x, y, node_height, count, label, color, label_side) in geom.items():
    ax.add_patch(mpatches.FancyBboxPatch(
        (x - BAR_W, y - node_height / 2),
        BAR_W * 2,
        node_height,
        boxstyle='round,pad=0.001,rounding_size=0.002',
        facecolor=color,
        edgecolor='none',
        zorder=5,
    ))

    if label_side == 'left':
        label_x = x - 0.018
        align = 'right'
    else:
        label_x = x + 0.018
        align = 'left'

    ax.text(
        label_x,
        y,
        f'{label}: {count}',
        ha=align,
        va='center',
        fontsize=9,
        fontweight='bold',
        color=TEXT,
        zorder=6,
    )

ax.set_title(
    'Application Pipeline',
    fontsize=15,
    fontweight='bold',
    color=TEXT,
    loc='left',
    pad=10,
)

plt.tight_layout()
plt.savefig('./outputs/sankey.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  Saved → sankey.png")
 
# Status Bar Chart 
fig_bar, ax = plt.subplots(figsize=(8, 5))
fig_bar.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')
statuses_to_plot = [s for s in PIPELINE if s != 'Submitted' and app_statuses.get(s, 0) > 0]
counts = [app_statuses[s] for s in statuses_to_plot]
colors = [STATUS_COLORS.get(s, '#888780') for s in statuses_to_plot]
bars = ax.barh(statuses_to_plot, counts, color=colors, height=0.6)
ax.set_xlabel('Applications', fontsize=10, color='#5F5E5A')
ax.set_title('Status Breakdown', fontsize=12, fontweight='bold', color='#2C2C2A', pad=10)
ax.tick_params(colors='#5F5E5A')
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.spines['bottom'].set_color('#D3D1C7')
ax.xaxis.grid(True, color='#D3D1C7', linewidth=0.5)
ax.set_axisbelow(True)
for bar, count in zip(bars, counts):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
            str(count), va='center', fontsize=9, color='#5F5E5A')
plt.tight_layout()
plt.savefig('./outputs/status_bar.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("  Saved → status_bar.png")
 
# Industry Donut Chart 
fig_donut, ax = plt.subplots(figsize=(7, 6))
fig_donut.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')
ind_labels = list(industries.keys())
ind_counts = [industries[i] for i in ind_labels]
wedges, _, autotexts = ax.pie(
    ind_counts, labels=None, autopct='%1.0f%%',
    colors=IND_COLORS[:len(ind_labels)],
    pctdistance=1.1, startangle=90,
    wedgeprops=dict(width=0.5, edgecolor='#FAFAF8', linewidth=2))
for at in autotexts:
    at.set_fontsize(9)
    at.set_color('#2C2C2A')
ax.set_title('Applications by Industry', fontsize=12, fontweight='bold', color='#2C2C2A', pad=10)
ax.legend(wedges, ind_labels, loc='lower center', bbox_to_anchor=(0.5, -0.12),
          ncol=2, fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig('./outputs/industry_donut.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("  Saved → industry_donut.png")
 
# Salary Boxplot 
fig_box, ax = plt.subplots(figsize=(8, 5))
fig_box.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')
ind_salary = defaultdict(list)
for a in applications:
    if a['salary']:
        ind_salary[a['industry']].append(a['salary'] / 1000)
inds_with_sal = sorted(ind_salary.keys(), key=lambda i: -np.median(ind_salary[i]))
ind_keys = list(industries.keys())
bp = ax.boxplot([ind_salary[i] for i in inds_with_sal], vert=False, patch_artist=True,
                medianprops=dict(color='#2C2C2A', linewidth=2),
                boxprops=dict(linewidth=0.8),
                whiskerprops=dict(color='#888780', linewidth=0.8),
                capprops=dict(color='#888780'),
                flierprops=dict(marker='o', markersize=4, color='#888780'))
for patch, ind in zip(bp['boxes'], inds_with_sal):
    patch.set_facecolor(IND_COLORS[ind_keys.index(ind) % len(IND_COLORS)])
    patch.set_alpha(0.7)
ax.set_yticks(range(1, len(inds_with_sal) + 1))
ax.set_yticklabels(inds_with_sal, fontsize=9, color='#5F5E5A')
ax.set_xlabel('Max Salary ($k)', fontsize=10, color='#5F5E5A')
ax.set_title('Salary by industry', fontsize=12, fontweight='bold', color='#2C2C2A', pad=10)
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.spines['bottom'].set_color('#D3D1C7')
ax.xaxis.grid(True, color='#D3D1C7', linewidth=0.5)
ax.tick_params(colors='#5F5E5A')
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig('./outputs/salary_boxplot.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("  Saved → salary_boxplot.png")
