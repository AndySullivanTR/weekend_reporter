"""
More thorough conversion script - updates ALL instances
Run this to fix any remaining "trunk" or "employee" references
"""

import os
import glob

def replace_in_file(filepath, replacements):
    """Apply replacements to a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {filepath}")
            return True
        else:
            print(f"  No changes needed in {filepath}")
            return False
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

# Comprehensive replacements
replacements = [
    # Trunk → Reporter
    ('Weekend Reporter Shifts', 'Weekend Reporter Shifts'),
    ('Weekend Reporter Shift', 'Weekend Reporter Shift'),  
    ('weekend reporter shift', 'weekend reporter shift'),
    ('weekend-reporter-shifts', 'weekend-reporter-shifts'),
    ('Reporter Shifts', 'Reporter Shifts'),
    ('Reporter Shift', 'Reporter Shift'),
    ('reporter shift', 'reporter shift'),
    ('reporter shifts', 'reporter shifts'),
    ('REPORTER SHIFT', 'REPORTER SHIFT'),
    
    # Reporter → Reporter (various cases)
    ('reporters.json', 'reporters.json'),
    ('REPORTERS_FILE', 'REPORTERS_FILE'),
    ("'reporters':", "'reporters':"),
    ('get_reporters()', 'get_reporters()'),
    ('def get_reporters', 'def get_reporters'),
    ('reporter_dashboard', 'reporter_dashboard'),
    ('Reporter Dashboard', 'Reporter Dashboard'),
    ('reporter accounts', 'reporter accounts'),
    ('Reporter accounts', 'Reporter accounts'),
    ('reporter1', 'reporter1'),
    ('Reporter1', 'Reporter1'),
    ('reporter{i}', 'reporter{i}'),
    ('Reporter{i}', 'Reporter{i}'),
    (' reporter', ' reporter'),
    (' Reporter', ' Reporter'),
    (' reporters', ' reporters'),
    (' Reporters', ' Reporters'),
    ('reporters', 'reporters'),
    ('Reporters', 'Reporters'),
    
    # Preferences
    ('top_10', 'top_10'),
    ('top 10', 'top 10'),
    ('Top 10', 'Top 10'),
    ("'top_10'", "'top_10'"),
    ('"top_10"', '"top_10"'),
    ('bottom_5', 'bottom_5'),
    ('bottom 5', 'bottom 5'),
    ('Bottom 5', 'Bottom 5'),
    ("'bottom_5'", "'bottom_5'"),
    ('"bottom_5"', '"bottom_5"'),
    ('10 top', '10 top'),
    ('5 bottom', '5 bottom'),
    ('5 least', '5 least'),
    (' == 10', ' == 10'),
    (' != 10', ' != 10'),
    ('exactly 10', 'exactly 10'),
    (' == 5', ' == 5'),
    (' != 5', ' != 5'),
    ('exactly 5', 'exactly 5'),
    
    # Shift counts
    ('1 shift', '1 shift'),
    ('one shift', 'one shift'),
    ('their shift', 'their shift'),
    ('/1)', '/1)'),
    (' == 1:', ' == 1:'),
    (' >= 1:', ' >= 1:'),
    (' < 1:', ' < 1:'),
    ('Shifts Assigned: 1', 'Shifts Assigned: 1'),
    
    # Colors - Purple/Blue → Orange/Red
    ('linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)', 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)'),
    ('#FF6B35', '#FF6B35'),
    ('#F7931E', '#F7931E'),
    ('#E85A2B', '#E85A2B'),
    ('#FF6B35', '#FF6B35'),
    ('#FF6B35', '#FF6B35'),
    ('#E85A2B', '#E85A2B'),
]

print("="*70)
print("COMPREHENSIVE CONVERSION TO REPORTER SYSTEM")
print("="*70)

# Files to update
file_patterns = [
    '*.py',
    '*.md',
    '*.yaml',
    'templates/*.html'
]

files_updated = 0
files_checked = 0

for pattern in file_patterns:
    for filepath in glob.glob(pattern, recursive=True):
        files_checked += 1
        if replace_in_file(filepath, replacements):
            files_updated += 1

print("\n" + "="*70)
print(f"COMPLETE: Checked {files_checked} files, updated {files_updated} files")
print("="*70)
print("\nNext steps:")
print("1. Restart your Flask app (Ctrl+C then python app.py)")
print("2. Refresh browser (Ctrl+Shift+R)")
print("3. Should now see 'Weekend Reporter Shifts' everywhere")
print("="*70)
