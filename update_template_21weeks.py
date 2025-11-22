"""
Update Reporter Dashboard Template - Show 21 Weekends

This updates the manager_dashboard.html template to reflect the new 21-weekend schedule.
"""

import os

template_file = r"C:\Users\8010317\projects\scheduler\weekend_reporter\templates\manager_dashboard.html"

print("=" * 80)
print("UPDATING REPORTER DASHBOARD TEMPLATE FOR 21 WEEKENDS")
print("=" * 80)

if not os.path.exists(template_file):
    print(f"✗ Template file not found: {template_file}")
    exit(1)

# Read the file
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup original
backup_file = template_file.replace('.html', '_backup_before_21weeks.html')
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Backed up original to: {backup_file}")

# Update title in Excel export section
content = content.replace(
    "Weekend Reporter Shift Schedule - Dec 2025 - Apr 2026",
    "Weekend Reporter Shift Schedule - Dec 2025 - May 2026"
)

# Update the stat card for total shifts
content = content.replace(
    "<div class=\"stat-number\">60</div>",
    "<div class=\"stat-number\">63</div>"
)
content = content.replace(
    "<div class=\"stat-label\">Total Shifts (20 weekends)</div>",
    "<div class=\"stat-label\">Total Shifts (21 weekends)</div>"
)

# Update test data button text
content = content.replace(
    "This will populate random preferences for all 30 reporters",
    "This will populate random preferences for all 121 reporters"
)

# Write back to file
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Updated manager_dashboard.html:")
print("  - Changed to 63 total shifts (21 weekends)")
print("  - Updated schedule title to show through May 2026")
print("  - Fixed test data button text to say 121 reporters")

print("\n" + "=" * 80)
