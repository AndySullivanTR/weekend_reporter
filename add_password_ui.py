"""
Add Password Change Button to Reporter Dashboard Template

This adds a password change modal and button to the reporter dashboard.
"""

import os

template_file = r"C:\Users\8010317\projects\scheduler\weekend_reporter\templates\reporter_dashboard.html"

print("=" * 80)
print("ADDING PASSWORD CHANGE UI TO REPORTER DASHBOARD")
print("=" * 80)

if not os.path.exists(template_file):
    print(f"✗ Template file not found: {template_file}")
    exit(1)

# Read the file
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if password change modal already exists
if 'change-password-modal' in content:
    print("✓ Password change UI already exists")
    exit(0)

# Add the password change modal HTML before </body>
modal_html = '''
    <!-- Password Change Modal -->
    <div id="change-password-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center;">
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 400px; width: 90%;">
            <h2 style="margin-bottom: 20px; color: #333;">Change Password</h2>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; color: #666;">Current Password:</label>
                <input type="password" id="current-password" style="width: 100%; padding: 8px; border: 2px solid #e1e4e8; border-radius: 5px; font-size: 14px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; color: #666;">New Password (min 6 characters):</label>
                <input type="password" id="new-password" style="width: 100%; padding: 8px; border: 2px solid #e1e4e8; border-radius: 5px; font-size: 14px;">
            </div>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 5px; color: #666;">Confirm New Password:</label>
                <input type="password" id="confirm-password" style="width: 100%; padding: 8px; border: 2px solid #e1e4e8; border-radius: 5px; font-size: 14px;">
            </div>
            <div style="display: flex; gap: 10px;">
                <button onclick="submitPasswordChange()" style="flex: 1; padding: 12px; background: #FF6B35; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600;">Change Password</button>
                <button onclick="closePasswordModal()" style="flex: 1; padding: 12px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600;">Cancel</button>
            </div>
        </div>
    </div>
'''

# Add password change button to header (find the logout button and add before it)
password_button = '''<button onclick="openPasswordModal()" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">Change Password</button>
            '''

# Insert modal before </body>
content = content.replace('</body>', modal_html + '\n</body>')

# Insert button before logout link in header
content = content.replace('<a href="/logout" class="logout-btn">Logout</a>', 
                         password_button + '<a href="/logout" class="logout-btn">Logout</a>')

# Add JavaScript functions before </script>
js_functions = '''
        function openPasswordModal() {
            document.getElementById('change-password-modal').style.display = 'flex';
            document.getElementById('current-password').value = '';
            document.getElementById('new-password').value = '';
            document.getElementById('confirm-password').value = '';
        }
        
        function closePasswordModal() {
            document.getElementById('change-password-modal').style.display = 'none';
        }
        
        async function submitPasswordChange() {
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            if (!currentPassword || !newPassword || !confirmPassword) {
                showAlert('Please fill in all fields.', 'danger');
                return;
            }
            
            if (newPassword.length < 6) {
                showAlert('New password must be at least 6 characters.', 'danger');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                showAlert('New passwords do not match.', 'danger');
                return;
            }
            
            try {
                const response = await fetch('/api/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        current_password: currentPassword,
                        new_password: newPassword
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ Password changed successfully!', 'success');
                    closePasswordModal();
                } else {
                    showAlert(data.error || 'Failed to change password.', 'danger');
                }
            } catch (error) {
                showAlert('An error occurred.', 'danger');
            }
        }
        
'''

# Insert JS functions before the closing </script> tag
content = content.replace('    </script>', js_functions + '    </script>')

# Write back to file
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added password change UI to reporter_dashboard.html")
print("  - Added 'Change Password' button in header")
print("  - Added password change modal")
print("  - Added JavaScript functions")

print("\n" + "=" * 80)
