"""
Export shift assignments to CSV format for Outlook mail merge

This script:
1. Reads assignments.json (shift assignments)
2. Reads reporter_credentials.csv (email addresses)
3. Creates a CSV file with: Name, Email, Shift1Details, Shift2Details
4. Ready for Outlook mail merge
"""

import json
import csv
from datetime import datetime
from pathlib import Path

# Shift definitions (match your app.py)
SHIFTS = [
    {'id': 0, 'date': '2025-11-01', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 1, 'date': '2025-11-02', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 2, 'date': '2025-11-02', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 3, 'date': '2025-11-08', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 4, 'date': '2025-11-09', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 5, 'date': '2025-11-09', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 6, 'date': '2025-11-15', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 7, 'date': '2025-11-16', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 8, 'date': '2025-11-16', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 9, 'date': '2025-11-22', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 10, 'date': '2025-11-23', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 11, 'date': '2025-11-23', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 12, 'date': '2025-11-29', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 13, 'date': '2025-11-30', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 14, 'date': '2025-11-30', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 15, 'date': '2025-12-06', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 16, 'date': '2025-12-07', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 17, 'date': '2025-12-07', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 18, 'date': '2025-12-13', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 19, 'date': '2025-12-14', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 20, 'date': '2025-12-14', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 21, 'date': '2025-12-20', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 22, 'date': '2025-12-21', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 23, 'date': '2025-12-21', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 24, 'date': '2025-12-27', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 25, 'date': '2025-12-28', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 26, 'date': '2025-12-28', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 27, 'date': '2026-01-03', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 28, 'date': '2026-01-04', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 29, 'date': '2026-01-04', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 30, 'date': '2026-01-10', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 31, 'date': '2026-01-11', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 32, 'date': '2026-01-11', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 33, 'date': '2026-01-17', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 34, 'date': '2026-01-18', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 35, 'date': '2026-01-18', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 36, 'date': '2026-01-24', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 37, 'date': '2026-01-25', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 38, 'date': '2026-01-25', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 39, 'date': '2026-01-31', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 40, 'date': '2026-02-01', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 41, 'date': '2026-02-01', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 42, 'date': '2026-02-07', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 43, 'date': '2026-02-08', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 44, 'date': '2026-02-08', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 45, 'date': '2026-02-14', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 46, 'date': '2026-02-15', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 47, 'date': '2026-02-15', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 48, 'date': '2026-02-21', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 49, 'date': '2026-02-22', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 50, 'date': '2026-02-22', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 51, 'date': '2026-02-28', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 52, 'date': '2026-03-01', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 53, 'date': '2026-03-01', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 54, 'date': '2026-03-07', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 55, 'date': '2026-03-08', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 56, 'date': '2026-03-08', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 57, 'date': '2026-03-14', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 58, 'date': '2026-03-15', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 59, 'date': '2026-03-15', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
    {'id': 60, 'date': '2026-03-21', 'day': 'Saturday', 'time': '11:00 AM - 7:00 PM'},
    {'id': 61, 'date': '2026-03-22', 'day': 'Sunday', 'time': '8:00 AM - 4:00 PM'},
    {'id': 62, 'date': '2026-03-22', 'day': 'Sunday', 'time': '3:00 PM - 10:00 PM'},
]

def format_shift(shift_id):
    """Convert shift ID to human-readable format"""
    shift = next((s for s in SHIFTS if s['id'] == shift_id), None)
    if not shift:
        return f"Unknown Shift (ID: {shift_id})"
    
    # Format: Saturday, November 1, 2025 - 11:00 AM to 7:00 PM
    date_obj = datetime.strptime(shift['date'], '%Y-%m-%d')
    formatted_date = date_obj.strftime('%A, %B %d, %Y')
    return f"{formatted_date} - {shift['time']}"

def main():
    # Load assignments
    with open('data/assignments.json', 'r') as f:
        assignments = json.load(f)
    
    # Load reporter credentials for email addresses
    reporters = {}
    with open('reporter_credentials.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['Username']
            reporters[username] = {
                'name': row['Name'],
                'email': row['Email']
            }
    
    # Build mail merge data
    mail_merge_data = []
    
    for username, shift_ids in assignments.items():
        if username == 'admin':
            continue
        
        if username not in reporters:
            print(f"Warning: {username} not found in reporter_credentials.csv")
            continue
        
        reporter = reporters[username]
        
        # Sort shifts by date
        shift_ids_sorted = sorted(shift_ids, key=lambda sid: SHIFTS[sid]['date'])
        
        # Format shift details
        if len(shift_ids_sorted) >= 1:
            shift1 = format_shift(shift_ids_sorted[0])
        else:
            shift1 = "No shift assigned"
        
        if len(shift_ids_sorted) >= 2:
            shift2 = format_shift(shift_ids_sorted[1])
        else:
            shift2 = "No second shift assigned"
        
        mail_merge_data.append({
            'Name': reporter['name'],
            'Email': reporter['email'],
            'Shift1': shift1,
            'Shift2': shift2,
            'TotalShifts': len(shift_ids_sorted)
        })
    
    # Sort by name
    mail_merge_data.sort(key=lambda x: x['Name'])
    
    # Write to CSV
    output_file = f'mailmerge_assignments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Name', 'Email', 'Shift1', 'Shift2', 'TotalShifts']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(mail_merge_data)
    
    print(f"✓ Created mail merge file: {output_file}")
    print(f"✓ Total reporters: {len(mail_merge_data)}")
    print(f"\nPreview of first 3 entries:")
    for i, row in enumerate(mail_merge_data[:3]):
        print(f"\n{i+1}. {row['Name']}")
        print(f"   Email: {row['Email']}")
        print(f"   Shift 1: {row['Shift1']}")
        print(f"   Shift 2: {row['Shift2']}")
    
    print(f"\n\n=== NEXT STEPS ===")
    print(f"1. Open Microsoft Outlook")
    print(f"2. Create a new email message")
    print(f"3. Go to Mailings tab > Start Mail Merge > Email Messages")
    print(f"4. Select Recipients > Use an Existing List > Choose {output_file}")
    print(f"5. Compose your email using Insert Merge Field for personalization")
    print(f"6. Finish & Merge > Send Email Messages")

if __name__ == '__main__':
    main()
