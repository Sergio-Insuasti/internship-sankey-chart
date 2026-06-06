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
 
print("  Status breakdown:")
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
 
# Sankey Diagram
# Derive funnel counts from status data
n_no_resp  = app_statuses.get('No Response', 0)
n_rejected = app_statuses.get('Rejected', 0)
n_oa_stop  = app_statuses.get('OA', 0)
n_1st_stop = app_statuses.get('1st Round', 0)
n_2nd_stop = app_statuses.get('2nd Round', 0)
n_fin_stop = app_statuses.get('Final Round', 0)
n_accepted = app_statuses.get('Offer Sent', 0) or app_statuses.get('Accepted', 0)
 
n_reached_final = n_fin_stop + n_accepted
n_reached_2nd   = n_2nd_stop + n_reached_final
n_reached_1st   = n_1st_stop + n_reached_2nd
n_reached_oa    = n_oa_stop  + n_reached_1st
 
# (id, label, y_pos, count, color)
NODES = [
    ('submitted', f'Submitted\n{total}',              0.08, total,           '#378ADD'),
    ('no_resp',   f'No response\n{n_no_resp}',         0.35, n_no_resp,       '#B4B2A9'),
    ('rejected',  f'Rejected\n{n_rejected}',           0.35, n_rejected,      '#E24B4A'),
    ('oa',        f'OA\n{n_reached_oa}',               0.35, n_reached_oa,    '#EF9F27'),
    ('oa_stop',   f'Rejected\n{n_oa_stop}',             0.58, n_oa_stop,       '#B4B2A9'),
    ('r1',        f'1st round\n{n_reached_1st}',       0.58, n_reached_1st,   '#BA7517'),
    ('r1_stop',   f'Failed\n{n_1st_stop}',            0.72, n_1st_stop,      '#B4B2A9'),
    ('r2',        f'2nd round\n{n_reached_2nd}',       0.72, n_reached_2nd,   '#854F0B'),
    ('r2_stop',   f'Failed\n{n_2nd_stop}',            0.86, n_2nd_stop,      '#B4B2A9'),
    ('final',     f'Final round\n{n_reached_final}',   0.86, n_reached_final, '#534AB7'),
    ('fin_stop',  f'Rejected\n{n_fin_stop}',            1.00, n_fin_stop,      '#B4B2A9'),
    ('accepted',  f'Accepted\n{n_accepted}',           1.00, n_accepted,      '#1D9E75'),
]
 
LINKS = [
    ('submitted', 'no_resp',  n_no_resp),
    ('submitted', 'rejected', n_rejected),
    ('submitted', 'oa',       n_reached_oa),
    ('oa',        'oa_stop',  n_oa_stop),
    ('oa',        'r1',       n_reached_1st),
    ('r1',        'r1_stop',  n_1st_stop),
    ('r1',        'r2',       n_reached_2nd),
    ('r2',        'r2_stop',  n_2nd_stop),
    ('r2',        'final',    n_reached_final),
    ('final',     'fin_stop', n_fin_stop),
    ('final',     'accepted', n_accepted),
]
 
node_map  = {n[0]: n for n in NODES}
node_geom = {}
BAR_W  = 0.022
H_TOTAL = 0.85
MIN_H  = 0.012
GAP    = 0.025
 
col_nodes = defaultdict(list)
for node in NODES:
    col_nodes[node[2]].append(node)

for stage_x, nodes_in_stage in col_nodes.items():
    stage_total = sum(node[3] for node in nodes_in_stage)
    available_height = H_TOTAL - GAP * (len(nodes_in_stage) - 1)
    cursor_y = 0.08
    for node in nodes_in_stage:
        bar_height = max((node[3] / total) * H_TOTAL, MIN_H)
        node_geom[node[0]] = (stage_x, cursor_y + bar_height / 2, bar_height)
        cursor_y += bar_height + GAP
 
fig_sankey, ax = plt.subplots(figsize=(14, 7))
fig_sankey.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')
ax.set_xlim(-0.05, 1.18)
ax.set_ylim(-0.05, 1.05)
ax.axis('off')
 
out_offset = {n[0]: 0.0 for n in NODES}
in_offset  = {n[0]: 0.0 for n in NODES}
 
for s_id, t_id, val in LINKS:
    if val == 0:
        continue
    sx, sy_c, sh = node_geom[s_id]
    tx, ty_c, th = node_geom[t_id]
    s_total = node_map[s_id][3]
    t_total = node_map[t_id][3]
    bh_s = (val / s_total) * sh if s_total else 0
    bh_t = (val / t_total) * th if t_total else 0
    sy_bot = (sy_c - sh / 2) + out_offset[s_id]
    ty_bot = (ty_c - th / 2) + in_offset[t_id]
    out_offset[s_id] += bh_s
    in_offset[t_id]  += bh_t
 
    mx = ((sx + BAR_W) + (tx - BAR_W)) / 2
    verts = [
        (sx + BAR_W, sy_bot),
        (mx,         sy_bot),
        (mx,         ty_bot),
        (tx - BAR_W, ty_bot),
        (tx - BAR_W, ty_bot + bh_t),
        (mx,         ty_bot + bh_t),
        (mx,         sy_bot + bh_s),
        (sx + BAR_W, sy_bot + bh_s),
        (sx + BAR_W, sy_bot),
    ]
    codes = [Path.MOVETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CLOSEPOLY]
    patch = mpatches.PathPatch(Path(verts, codes),
                               facecolor='#AAAAAA', edgecolor='none', alpha=0.4)
    ax.add_patch(patch)
 
for node_id, (node_x, node_y_center, node_height) in node_geom.items():
    node_color = node_map[node_id][4]
    ax.add_patch(mpatches.FancyBboxPatch(
        (node_x - BAR_W, node_y_center - node_height / 2), BAR_W * 2, node_height,
        boxstyle='round,pad=0.002',
        facecolor=node_color, edgecolor='none', zorder=5))
    label_lines = node_map[node_id][1].split('\n')
    label_x, label_align = (node_x - BAR_W - 0.01, 'right') if node_x <= 0.35 else (node_x + BAR_W + 0.01, 'left')
    ax.text(label_x, node_y_center + 0.012, label_lines[0], ha=label_align, va='center',
            fontsize=8.5, fontweight='bold', color='#2C2C2A', zorder=6)
    ax.text(label_x, node_y_center - 0.022, label_lines[1], ha=label_align, va='center',
            fontsize=8, color='#5F5E5A', zorder=6)
 
ax.set_title('Application funnel', fontsize=13, fontweight='bold',
             color='#2C2C2A', pad=12, loc='left', x=0.02)
plt.tight_layout()
plt.savefig('sankey.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
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
ax.set_title('Status breakdown', fontsize=12, fontweight='bold', color='#2C2C2A', pad=10)
ax.tick_params(colors='#5F5E5A')
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.spines['bottom'].set_color('#D3D1C7')
ax.xaxis.grid(True, color='#D3D1C7', linewidth=0.5)
ax.set_axisbelow(True)
for bar, count in zip(bars, counts):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
            str(count), va='center', fontsize=9, color='#5F5E5A')
plt.tight_layout()
plt.savefig('status_bar.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
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
    pctdistance=0.75, startangle=90,
    wedgeprops=dict(width=0.5, edgecolor='#FAFAF8', linewidth=2))
for at in autotexts:
    at.set_fontsize(9)
    at.set_color('#2C2C2A')
ax.set_title('Applications by industry', fontsize=12, fontweight='bold', color='#2C2C2A', pad=10)
ax.legend(wedges, ind_labels, loc='lower center', bbox_to_anchor=(0.5, -0.12),
          ncol=2, fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig('industry_donut.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
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
plt.savefig('salary_boxplot.png', dpi=150, bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("  Saved → salary_boxplot.png")

        

        




