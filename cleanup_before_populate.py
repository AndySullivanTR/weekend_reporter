"""
Fix Reporter App - Clean up old data and prepare for real names

This script will:
1. Backup existing data
2. Clear assignments and preferences (which reference old placeholder names)
3. Keep settings (deadline, lock status)
4. Allow you to start fresh with real reporter names

Run this BEFORE running populate_real_reporters.py
"""

import json
import os
from datetime import datetime
import shutil

print("=" * 80)
print("REPORTER APP CLEANUP SCRIPT")
print("=" * 80)

data_dir = r"C:\Users\8010317\projects\scheduler\weekend_reporter\data"

# Check if data directory exists
if not os.path.exists(data_dir):
    print(f"\n✗ Data directory not found: {data_dir}")
    print("  Creating directory...")
    os.makedirs(data_dir, exist_ok=True)
    print("✓ Directory created")

# Create backup directory
backup_dir = os.path.join(os.path.dirname(data_dir), f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
os.makedirs(backup_dir, exist_ok=True)
print(f"\n📁 Backup directory: {backup_dir}")

# Files to handle
files = {
    'reporters.json': 'delete',  # Will be recreated by populate script
    'preferences.json': 'clear',   # Clear but keep file
    'assignments.json': 'clear',   # Clear but keep file
    'settings.json': 'keep'        # Keep as-is
}

print("\n--- Processing Files ---")

for filename, action in files.items():
    filepath = os.path.join(data_dir, filename)
    
    if os.path.exists(filepath):
        # Backup file
        backup_path = os.path.join(backup_dir, filename)
        shutil.copy2(filepath, backup_path)
        print(f"✓ Backed up: {filename}")
        
        if action == 'delete':
            os.remove(filepath)
            print(f"  → Deleted (will be recreated with real names)")
        elif action == 'clear':
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=2)
            print(f"  → Cleared (ready for new data)")
        elif action == 'keep':
            print(f"  → Kept unchanged")
    else:
        print(f"⚠ Not found: {filename}")
        if action == 'clear':
            # Create empty file
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=2)
            print(f"  → Created empty file")

print("\n--- Summary ---")
print("✓ Old data backed up to:", backup_dir)
print("✓ reporters.json deleted (will be recreated)")
print("✓ preferences.json cleared (employees will re-submit)")
print("✓ assignments.json cleared (will be generated after preferences)")
print("✓ settings.json preserved (deadline and lock status kept)")

print("\n--- Next Steps ---")
print("1. Run: python populate_real_reporters.py")
print("2. Start app: python app.py")
print("3. Login as manager (admin/admin123)")
print("4. Verify all 121 reporters are listed")
print("5. Set new deadline for preference submission")
print("6. Employees submit preferences with real accounts")
print("7. Run allocation when ready")

print("\n" + "=" * 80)
