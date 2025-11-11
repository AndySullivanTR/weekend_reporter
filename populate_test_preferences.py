"""
Generate random preferences for all 119 reporters
This populates the preferences.json file for testing the allocation algorithm
"""

import json
import random

# Path to preferences file
PREFS_FILE = 'data/preferences.json'

# All 60 shift IDs (0-59)
all_shifts = list(range(60))

# Generate random preferences for each reporter
preferences = {}

for i in range(1, 120):
    username = f'reporter{i}'
    
    # Shuffle all shifts
    shuffled = all_shifts.copy()
    random.shuffle(shuffled)
    
    # Top 10 are first 10 from shuffled list
    top_10 = shuffled[:10]
    
    # Bottom 5 are next 5 from shuffled list (ensuring no overlap)
    bottom_5 = shuffled[10:15]
    
    # Random shift type preferences (1, 2, 3)
    shift_types = [1, 2, 3]
    random.shuffle(shift_types)
    
    preferences[username] = {
        'top_10': top_10,
        'bottom_5': bottom_5,
        'shift_type_pref': {
            'saturday': str(shift_types[0]),
            'sunday_morning': str(shift_types[1]),
            'sunday_evening': str(shift_types[2])
        }
    }

# Save to file
with open(PREFS_FILE, 'w') as f:
    json.dump(preferences, f, indent=2)

print(f"✅ Generated random preferences for 119 reporters")
print(f"✅ Saved to {PREFS_FILE}")
print(f"\nYou can now:")
print(f"1. Login as admin/admin123")
print(f"2. Click 'Run Allocation Algorithm'")
print(f"3. Check the results and export to Excel")
print(f"\nNote: Each reporter will be assigned exactly 1 shift")
print(f"      2 reporters per shift = 119 reporters + 1 empty slot")
