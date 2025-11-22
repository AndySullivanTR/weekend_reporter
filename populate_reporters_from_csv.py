#!/usr/bin/env python3
"""
Script to populate reporters.json from reporter_credentials.csv
This should be run in the weekend_reporter directory
"""

import csv
import json
from werkzeug.security import generate_password_hash

def populate_reporters():
    reporters = {}
    
    # Add admin account
    reporters['admin'] = {
        'name': 'Admin',
        'is_manager': True,
        'password': generate_password_hash('admin123')
    }
    
    # Read CSV and add reporters
    with open('reporter_credentials.csv', 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['Username'].strip()
            name = row['Name'].strip()
            password = row['Password'].strip()
            
            reporters[username] = {
                'name': name,
                'is_manager': False,
                'password': generate_password_hash(password)
            }
    
    # Write to data/reporters.json
    with open('data/reporters.json', 'w') as f:
        json.dump(reporters, f, indent=2)
    
    print(f"✅ Created data/reporters.json with {len(reporters)} users:")
    print(f"   - 1 admin (username: admin, password: admin123)")
    print(f"   - {len(reporters)-1} reporters (usernames/passwords from CSV)")

if __name__ == '__main__':
    populate_reporters()
