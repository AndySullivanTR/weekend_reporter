"""
Generate Random Passwords and Email Templates

This script will:
1. Generate unique random passwords for all reporters
2. Update the reporters.json file with hashed passwords
3. Create an email template file with username/password for each reporter
4. Export to CSV for easy bulk emailing
"""

import json
import os
import random
import string
from werkzeug.security import generate_password_hash

def generate_password(length=6):
    """Generate a random password with letters and numbers"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Paths
data_dir = r"C:\Users\8010317\projects\scheduler\weekend_reporter\data"
reporters_file = os.path.join(data_dir, 'reporters.json')
output_dir = r"C:\Users\8010317\projects\scheduler\weekend_reporter"

print("=" * 80)
print("GENERATING RANDOM PASSWORDS FOR REPORTERS")
print("=" * 80)

if not os.path.exists(reporters_file):
    print(f"✗ Reporters file not found: {reporters_file}")
    exit(1)

# Read reporters
with open(reporters_file, 'r') as f:
    reporters = json.load(f)

# Generate passwords
password_list = []

print("\nGenerating passwords...")
for username, data in reporters.items():
    if data.get('is_manager'):
        # Keep admin password as is
        password_list.append({
            'username': username,
            'name': data['name'],
            'password': 'admin123',
            'is_manager': True
        })
    else:
        # Generate random password
        random_password = generate_password(6)
        
        # Update the reporters dict with hashed password
        reporters[username]['password'] = generate_password_hash(random_password)
        
        password_list.append({
            'username': username,
            'name': data['name'],
            'password': random_password,
            'is_manager': False
        })

# Save updated reporters.json
with open(reporters_file, 'w') as f:
    json.dump(reporters, f, indent=2)

print(f"✓ Updated {reporters_file} with new hashed passwords")

# Create email template file
email_template_file = os.path.join(output_dir, 'reporter_login_emails.txt')
with open(email_template_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("WEEKEND REPORTER SHIFT SYSTEM - LOGIN CREDENTIALS\n")
    f.write("=" * 80 + "\n\n")
    
    non_managers = [p for p in password_list if not p['is_manager']]
    
    for person in non_managers:
        f.write("-" * 80 + "\n")
        f.write(f"TO: {person['name']}\n")
        f.write(f"SUBJECT: Weekend Reporter Shift System - Login Credentials\n\n")
        f.write("Dear Colleague,\n\n")
        f.write("You can now access the Weekend Reporter Shift System to submit your shift preferences.\n\n")
        f.write("Your login credentials are:\n\n")
        f.write(f"  Username: {person['username']}\n")
        f.write(f"  Initial Password: {person['password']}\n\n")
        f.write("Please log in at: [INSERT URL HERE]\n\n")
        f.write("IMPORTANT: After logging in for the first time, please change your password\n")
        f.write("by clicking the 'Change Password' button in your dashboard.\n\n")
        f.write("Once logged in, you will need to:\n")
        f.write("1. Select your TOP 10 preferred shifts\n")
        f.write("2. Select your 5 LEAST wanted shifts\n")
        f.write("3. Rank your preference for shift types (Saturday, Sunday morning, Sunday evening)\n\n")
        f.write("Please submit your preferences by the deadline shown in the system.\n\n")
        f.write("If you have any questions, please contact [INSERT CONTACT].\n\n")
        f.write("Best regards,\n")
        f.write("Scheduling Team\n")
        f.write("-" * 80 + "\n\n")

print(f"✓ Created email templates: {email_template_file}")

# Create CSV file for bulk emailing
csv_file = os.path.join(output_dir, 'reporter_credentials.csv')
with open(csv_file, 'w') as f:
    f.write("Name,Username,Password,Email\n")
    non_managers = [p for p in password_list if not p['is_manager']]
    for person in non_managers:
        # Extract email from username (add @thomsonreuters.com)
        email = f"{person['username']}@thomsonreuters.com"
        f.write(f'"{person["name"]}",{person["username"]},{person["password"]},{email}\n')

print(f"✓ Created CSV file: {csv_file}")

# Create a summary file
summary_file = os.path.join(output_dir, 'password_summary.txt')
with open(summary_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("PASSWORD GENERATION SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Total reporters: {len([p for p in password_list if not p['is_manager']])}\n")
    f.write(f"Manager account: admin / admin123\n\n")
    f.write("Sample credentials (first 5):\n\n")
    
    non_managers = [p for p in password_list if not p['is_manager']]
    for person in non_managers[:5]:
        f.write(f"  {person['name']}\n")
        f.write(f"    Username: {person['username']}\n")
        f.write(f"    Password: {person['password']}\n\n")
    
    f.write("...\n\n")
    f.write("Full list available in:\n")
    f.write(f"  - {email_template_file}\n")
    f.write(f"  - {csv_file}\n")

print(f"✓ Created summary: {summary_file}")

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
print("\nFiles created:")
print(f"  1. {email_template_file}")
print(f"     - Individual email templates for each reporter")
print(f"  2. {csv_file}")
print(f"     - CSV file for bulk emailing (can import to email client)")
print(f"  3. {summary_file}")
print(f"     - Summary of password generation")

print("\n📧 Next steps:")
print("  1. Review the email templates")
print("  2. Update [INSERT URL HERE] with your actual app URL")
print("  3. Update [INSERT CONTACT] with your contact info")
print("  4. Send emails to reporters using your email client")
print("  5. Reporters login and change their passwords")

print("\n⚠️  SECURITY NOTE:")
print("  - Delete these files after sending emails!")
print("  - They contain plain-text passwords")
print("  - Store securely if you need to keep them")

print("\n" + "=" * 80)
