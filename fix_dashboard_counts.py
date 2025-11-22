"""
Fix Reporter Dashboard - Correct the preference count display

The dashboard currently shows:
- "0/12" for top preferences (should be "0/10")
- "0/6" for bottom preferences (should be "0/5")

This script fixes those display values.
"""

import os

template_file = r"C:\Users\8010317\projects\scheduler\weekend_reporter\templates\manager_dashboard.html"

print("=" * 80)
print("FIXING REPORTER DASHBOARD PREFERENCE COUNTS")
print("=" * 80)

if not os.path.exists(template_file):
    print(f"✗ Template file not found: {template_file}")
    exit(1)

# Read the file
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Make the replacements
original_content = content

# Fix 1: Change "0/12" to "0/10" for top preferences
content = content.replace(
    "0/12",
    "0/10"
)

# Fix 2: Change "0/6" to "0/5" for bottom preferences  
content = content.replace(
    "0/6",
    "0/5"
)

# Check if changes were made
if content == original_content:
    print("⚠ No changes needed - values already correct")
else:
    # Write back to file
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed preference count display:")
    print("  - Top 10 Preferences: now shows '0/10' (was '0/12')")
    print("  - Bottom 5 Preferences: now shows '0/5' (was '0/6')")
    print("\n✓ File updated successfully!")
    print("\nNext steps:")
    print("1. Restart the Flask app: python app.py")
    print("2. Refresh the manager dashboard")
    print("3. Verify the counts now show correctly")

print("=" * 80)
