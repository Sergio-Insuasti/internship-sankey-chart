import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
            
        
        
        
        
        




