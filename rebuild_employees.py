import json
import csv
from werkzeug.security import generate_password_hash

# Read the CSV file
employees = {}

# Add admin account
employees['admin'] = {
    'name': 'Admin',
    'is_manager': True,
    'password': generate_password_hash('admin123')
}

# Read reporter credentials
with open('reporter_credentials.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        username = row['Username']
        name = row['Name']
        password = row['Password']
        
        employees[username] = {
            'name': name,
            'is_manager': False,
            'password': generate_password_hash(password)
        }

# Save to employees.json
with open('data/employees.json', 'w') as f:
    json.dump(employees, f, indent=2)

print(f"✓ Created employees.json with {len(employees)} accounts")
print(f"  - 1 admin account")
print(f"  - {len(employees) - 1} reporter accounts")
print("\nAdmin login:")
print("  Username: admin")
print("  Password: admin123")
