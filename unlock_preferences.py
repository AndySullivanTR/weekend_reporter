"""
Fix Reporter App - Unlock Preferences and Set New Deadline

This script will:
1. Unlock preferences
2. Set a new deadline (7 days from now)
3. Show current settings
"""

import json
import os
from datetime import datetime, timedelta

data_dir = r"C:\Users\8010317\projects\scheduler\weekend_reporter\data"
settings_file = os.path.join(data_dir, 'settings.json')

print("=" * 80)
print("UNLOCKING PREFERENCES AND SETTING NEW DEADLINE")
print("=" * 80)

if not os.path.exists(settings_file):
    print(f"✗ Settings file not found: {settings_file}")
    print("  Creating new settings file...")
    os.makedirs(data_dir, exist_ok=True)
    settings = {
        'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
        'is_locked': False
    }
else:
    # Read current settings
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    
    print("\n📋 Current Settings:")
    print(f"  Deadline: {settings.get('deadline', 'Not set')}")
    print(f"  Locked: {settings.get('is_locked', False)}")
    
    # Check if deadline has passed
    if 'deadline' in settings:
        deadline = datetime.fromisoformat(settings['deadline'].replace('Z', '+00:00'))
        now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
        if deadline < now:
            print(f"  ⚠️  Deadline has PASSED (was {deadline.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"  ✓ Deadline is in the FUTURE ({deadline.strftime('%Y-%m-%d %H:%M')})")

# Update settings
new_deadline = datetime.now() + timedelta(days=7)
settings['deadline'] = new_deadline.isoformat()
settings['is_locked'] = False

# Save settings
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print("\n✅ Updated Settings:")
print(f"  New Deadline: {new_deadline.strftime('%Y-%m-%d %H:%M')} (7 days from now)")
print(f"  Locked: False (unlocked)")

print("\n📋 Next Steps:")
print("  1. Restart the Flask app if it's running")
print("  2. Reporters can now login and submit preferences")
print("  3. They have 7 days to submit")
print("\n💡 To change the deadline:")
print("  - Login as manager (admin/admin123)")
print("  - Use the 'Update Deadline' button on the dashboard")
print("  - Or run this script again")

print("\n" + "=" * 80)
