"""
Convert Weekend Trunk system to Weekend Reporter system
Run this in the weekend_reporter directory after copying files from weekend_trunk
"""

import re
import os

def replace_in_file(filepath, replacements):
    """Apply multiple find/replace operations to a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {filepath}")

# Color scheme replacements (Purple/Blue → Orange/Red)
color_replacements = [
    # Primary gradient
    ('linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)', 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)'),
    # Solid colors
    ('#FF6B35', '#FF6B35'),
    ('#F7931E', '#F7931E'),
    ('#E85A2B', '#E85A2B'),
    # Header colors
    ('#FF6B35', '#FF6B35'),
    # Link colors  
    ('#FF6B35', '#FF6B35'),
    ('#E85A2B', '#E85A2B'),
]

# Text replacements (Trunk → Reporter)
text_replacements = [
    ('Weekend Reporter Shifts', 'Weekend Reporter Shifts'),
    ('Weekend Reporter Shift', 'Weekend Reporter Shift'),
    ('weekend-reporter-shifts', 'weekend-reporter-shifts'),
    ('Reporter Shift', 'Reporter Shift'),
    ('reporter shift', 'reporter shift'),
    ('REPORTER SHIFT', 'REPORTER SHIFT'),
    ('employee', 'reporter'),
    ('Employee', 'Reporter'),
    ('EMPLOYEE', 'REPORTER'),
    ('reporters', 'reporters'),
    ('Reporters', 'Reporters'),
    ('EMPLOYEES', 'REPORTERS'),
    # Preference counts
    ('top 10', 'top 10'),
    ('Top 10', 'Top 10'),
    ('top_10', 'top_10'),
    ('bottom 5', 'bottom 5'),
    ('Bottom 5', 'Bottom 5'),
    ('bottom_5', 'bottom_5'),
    ('10 top', '10 top'),
    ('5 least', '5 least'),
    ('5 bottom', '5 bottom'),
    # Assignment counts
    ('1 shift', '1 shift'),
    ('one shift', 'one shift'),
    ('their shift', 'their shift'),
    ('/1)', '/1)'),
    ('== 2', '== 1'),
    ('>= 2', '>= 1'),
    ('< 2', '< 1'),
]

# Files to update
files_to_update = [
    'app.py',
    'templates/login.html',
    'templates/reporter_dashboard.html',  # Will be renamed from reporter_dashboard.html
    'templates/manager_dashboard.html',
    'README.md',
    'DEPLOYMENT_GUIDE.md',
]

print("="*70)
print("CONVERTING WEEKEND TRUNK TO WEEKEND REPORTER SYSTEM")
print("="*70)

# Rename reporter_dashboard.html to reporter_dashboard.html
if os.path.exists('templates/reporter_dashboard.html'):
    os.rename('templates/reporter_dashboard.html', 'templates/reporter_dashboard.html')
    print("✓ Renamed reporter_dashboard.html → reporter_dashboard.html")

# Apply replacements to each file
for filepath in files_to_update:
    if not os.path.exists(filepath):
        print(f"⚠ Skipping {filepath} (not found)")
        continue
    
    all_replacements = color_replacements + text_replacements
    replace_in_file(filepath, all_replacements)

print("\n" + "="*70)
print("CONVERSION COMPLETE!")
print("="*70)
print("\nNext steps:")
print("1. Delete the data/ folder (if it exists)")
print("2. Run: python app.py")
print("3. Login as admin/admin123")
print("4. You should see 119 reporters instead of 30 reporters")
print("5. Test the 'Populate Test Data' button")
print("="*70)
