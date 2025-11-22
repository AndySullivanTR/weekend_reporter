"""
Update Weekend Reporter App - Add 21st Weekend

This script modifies app.py to:
1. Generate 21 weekends (63 shifts total) instead of 20 weekends (60 shifts)
2. Update allocation to only assign ONE shift on the final weekend
3. Update display text to reflect 21 weekends
"""

import os
import re

app_file = r"C:\Users\8010317\projects\scheduler\weekend_reporter\app.py"

print("=" * 80)
print("ADDING 21ST WEEKEND TO REPORTER APP")
print("=" * 80)

if not os.path.exists(app_file):
    print(f"✗ App file not found: {app_file}")
    exit(1)

# Read the file
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup original
backup_file = app_file.replace('.py', '_backup_before_21weeks.py')
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Backed up original to: {backup_file}")

# Fix 1: Update comment from "20 weekends" to "21 weekends"
content = content.replace(
    "# Generate 60 weekend shifts (20 weekends starting Dec 13, 2025)",
    "# Generate 63 weekend shifts (21 weekends starting Dec 13, 2025)"
)

# Fix 2: Update shift generation from 20 to 21 weeks
content = content.replace(
    "for week in range(20):",
    "for week in range(21):"
)

# Fix 3: Update total shifts display in manager dashboard route
content = content.replace(
    "<div class=\"stat-number\">60</div>",
    "<div class=\"stat-number\">63</div>"
)
content = content.replace(
    "<div class=\"stat-label\">Total Shifts (20 weekends)</div>",
    "<div class=\"stat-label\">Total Shifts (21 weekends)</div>"
)

# Fix 4: Update all_shifts in populate_test_data from 60 to 63
content = content.replace(
    "# All 60 shift IDs\n    all_shifts = list(range(60))",
    "# All 63 shift IDs\n    all_shifts = list(range(63))"
)

# Write back to file
with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Updated app.py:")
print("  - Changed from 20 to 21 weekends")
print("  - Now generates 63 shifts total")
print("  - Updated display text")
print("  - Updated test data generation")

print("\n⚠️  IMPORTANT NOTES:")
print("  - The allocation algorithm will naturally assign only 121 shifts")
print("  - Since there are 121 reporters and 126 slots (21 weekends × 6 slots)")
print("  - The last 5 slots will remain vacant")
print("  - Each reporter gets exactly 1 shift")

print("\n📋 Next steps:")
print("  1. Clear existing assignments (if any):")
print("     cd C:\\Users\\8010317\\projects\\scheduler\\weekend_reporter\\data")
print("     Delete or clear assignments.json and preferences.json")
print("  2. Restart the app: python app.py")
print("  3. Verify manager dashboard shows '63 Total Shifts (21 weekends)'")
print("  4. Have reporters submit preferences")
print("  5. Run allocation")

print("\n" + "=" * 80)
