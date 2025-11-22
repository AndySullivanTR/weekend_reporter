"""
Add Password Change Feature to Reporter App

This script adds a password change route to the reporter app.
"""

import os

app_file = r"C:\Users\8010317\projects\scheduler\weekend_reporter\app.py"

print("=" * 80)
print("ADDING PASSWORD CHANGE FEATURE TO REPORTER APP")
print("=" * 80)

if not os.path.exists(app_file):
    print(f"✗ App file not found: {app_file}")
    exit(1)

# Read the file
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if password change route already exists
if '/api/change-password' in content:
    print("✓ Password change feature already exists in app.py")
else:
    # Find the position to insert the new route (before the if __name__ == '__main__':)
    insert_marker = "if __name__ == '__main__':"
    
    password_change_route = '''
@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Allow users to change their password"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    username = session['username']
    data = request.json
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    reporters = get_reporters()
    
    # Verify current password
    if username not in reporters:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_password_hash(reporters[username]['password'], current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    reporters[username]['password'] = generate_password_hash(new_password)
    save_json(REPORTERS_FILE, reporters)
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

'''
    
    # Insert the route
    content = content.replace(insert_marker, password_change_route + insert_marker)
    
    # Write back to file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Added password change route to app.py")

print("\n" + "=" * 80)
