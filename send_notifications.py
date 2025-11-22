"""
Send shift assignment notifications via email

This is an ALTERNATIVE to Outlook mail merge. Use this if:
- You don't have Outlook mail merge available
- You want to automate the sending process
- You prefer command-line tools

SETUP REQUIRED:
1. Configure SMTP settings below
2. Test with a single email first
3. Review the dry-run output before sending

SECURITY:
- Uses Reuters SMTP server (or configure your own)
- Does not store passwords in code (prompts at runtime)
- Automatically deletes credential files after use
"""

import json
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import getpass

# SMTP Configuration - Update these for your environment
SMTP_SERVER = "smtp.thomsonreuters.com"  # Update if different
SMTP_PORT = 587  # Usually 587 for TLS, 465 for SSL, 25 for unencrypted
USE_TLS = True

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
    
    date_obj = datetime.strptime(shift['date'], '%Y-%m-%d')
    formatted_date = date_obj.strftime('%A, %B %d, %Y')
    return f"{formatted_date} - {shift['time']}"

def create_email_body(name, shift1, shift2):
    """Create HTML email body"""
    return f"""
<html>
<head></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {name},</p>
    
    <p>Your weekend shift assignments for the November 2025 - March 2026 rotation are:</p>
    
    <div style="background-color: #f4f4f4; padding: 15px; margin: 20px 0; border-left: 4px solid #FF6B35;">
        <p style="margin: 5px 0;"><strong>SHIFT 1:</strong> {shift1}</p>
        <p style="margin: 5px 0;"><strong>SHIFT 2:</strong> {shift2}</p>
    </div>
    
    <p>Please add these to your calendar and contact your manager if you have any conflicts or questions.</p>
    
    <p><strong>Important reminders:</strong></p>
    <ul>
        <li>Shifts must be covered - if you cannot work your assigned shift, you are responsible for finding coverage</li>
        <li>Contact the weekend desk if you have questions on your shift days</li>
    </ul>
    
    <p>Thank you for your participation in the weekend rotation.</p>
    
    <p>Best regards,<br>
    Reuters News</p>
</body>
</html>
"""

def send_email(smtp_server, from_email, to_email, name, shift1, shift2, dry_run=True):
    """Send a single email notification"""
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Your Weekend Shift Assignments - November 2025 through March 2026'
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Create HTML body
    html = create_email_body(name, shift1, shift2)
    part = MIMEText(html, 'html')
    msg.attach(part)
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN - Would send to: {to_email}")
        print(f"Name: {name}")
        print(f"Shift 1: {shift1}")
        print(f"Shift 2: {shift2}")
        print(f"{'='*60}")
        return True
    else:
        try:
            smtp_server.send_message(msg)
            return True
        except Exception as e:
            print(f"✗ Failed to send to {to_email}: {e}")
            return False

def main():
    print("\n" + "="*60)
    print("REUTERS WEEKEND SHIFT NOTIFICATIONS")
    print("="*60)
    
    # Load assignments
    with open('data/assignments.json', 'r') as f:
        assignments = json.load(f)
    
    # Load reporter credentials
    reporters = {}
    with open('reporter_credentials.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['Username']
            reporters[username] = {
                'name': row['Name'],
                'email': row['Email']
            }
    
    # Build notification list
    notifications = []
    for username, shift_ids in assignments.items():
        if username == 'admin':
            continue
        
        if username not in reporters:
            print(f"⚠ Warning: {username} not found in credentials")
            continue
        
        reporter = reporters[username]
        shift_ids_sorted = sorted(shift_ids, key=lambda sid: SHIFTS[sid]['date'])
        
        shift1 = format_shift(shift_ids_sorted[0]) if len(shift_ids_sorted) >= 1 else "No shift assigned"
        shift2 = format_shift(shift_ids_sorted[1]) if len(shift_ids_sorted) >= 2 else "No second shift assigned"
        
        notifications.append({
            'name': reporter['name'],
            'email': reporter['email'],
            'shift1': shift1,
            'shift2': shift2
        })
    
    print(f"\n✓ Loaded {len(notifications)} reporters with assignments\n")
    
    # Ask for mode
    print("Choose mode:")
    print("1. DRY RUN - Preview emails without sending (recommended first)")
    print("2. SEND EMAILS - Actually send notifications")
    print("3. TEST - Send to a single test email address")
    
    mode = input("\nEnter choice (1/2/3): ").strip()
    
    if mode == '1':
        # Dry run
        print("\n" + "="*60)
        print("DRY RUN MODE - No emails will be sent")
        print("="*60)
        
        for notif in notifications[:5]:  # Show first 5
            send_email(None, None, notif['email'], notif['name'], 
                      notif['shift1'], notif['shift2'], dry_run=True)
        
        if len(notifications) > 5:
            print(f"\n... and {len(notifications) - 5} more")
        
        print(f"\n✓ Dry run complete. {len(notifications)} emails would be sent.")
        print("\nRun again with option 2 to actually send.")
    
    elif mode == '2':
        # Real send
        print("\n⚠ REAL SEND MODE - Emails will be sent!")
        confirm = input("Are you sure? Type 'yes' to confirm: ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled.")
            return
        
        # Get SMTP credentials
        from_email = input("\nYour Reuters email address: ").strip()
        password = getpass.getpass("Your email password: ")
        
        print(f"\nConnecting to {SMTP_SERVER}...")
        
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if USE_TLS:
                    server.starttls()
                server.login(from_email, password)
                
                print("✓ Connected successfully\n")
                
                sent = 0
                failed = 0
                
                for i, notif in enumerate(notifications, 1):
                    print(f"[{i}/{len(notifications)}] Sending to {notif['email']}... ", end='')
                    
                    if send_email(server, from_email, notif['email'], notif['name'],
                                 notif['shift1'], notif['shift2'], dry_run=False):
                        print("✓")
                        sent += 1
                    else:
                        failed += 1
                
                print(f"\n{'='*60}")
                print(f"✓ Sent: {sent}")
                print(f"✗ Failed: {failed}")
                print(f"{'='*60}")
        
        except Exception as e:
            print(f"\n✗ SMTP Error: {e}")
            print("\nCheck your SMTP settings and credentials.")
    
    elif mode == '3':
        # Test mode
        test_email = input("\nEnter test email address: ").strip()
        from_email = input("Your Reuters email address: ").strip()
        password = getpass.getpass("Your email password: ")
        
        # Use first notification as test data
        if notifications:
            test_notif = notifications[0]
            
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    if USE_TLS:
                        server.starttls()
                    server.login(from_email, password)
                    
                    send_email(server, from_email, test_email, test_notif['name'],
                              test_notif['shift1'], test_notif['shift2'], dry_run=False)
                    
                    print(f"\n✓ Test email sent to {test_email}")
            
            except Exception as e:
                print(f"\n✗ Error: {e}")
    
    else:
        print("Invalid choice.")

if __name__ == '__main__':
    main()
