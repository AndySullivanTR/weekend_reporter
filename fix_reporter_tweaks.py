"""
Fix reporter system tweaks:
1. Change login title to "Reuters weekend reporter shifts"
2. Remove credential hints from login page
3. Fix any remaining 12/6 references to 10/5
"""

import re

def fix_login_page():
    """Fix login.html"""
    filepath = 'templates/login.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Change title
    content = content.replace(
        'Weekend Reporter Shifts - Login',
        'Reuters Weekend Reporter Shifts - Login'
    )
    content = content.replace(
        '<h1>Weekend Reporter Shifts</h1>',
        '<h1>Reuters Weekend Reporter Shifts</h1>'
    )
    
    # Remove credentials hint section
    # Find and remove the entire div with class "credentials-hint"
    content = re.sub(
        r'<div class="credentials-hint">.*?</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed login.html")

def fix_dashboard_preferences():
    """Fix reporter_dashboard.html - ensure 10 and 5"""
    filepath = 'templates/reporter_dashboard.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace any remaining 12/6 references
    replacements = [
        ('12 preferred', '10 preferred'),
        ('12 top', '10 top'),
        ('top 12', 'top 10'),
        ('Top 12', 'Top 10'),
        ('6 least', '5 least'),
        ('bottom 6', 'bottom 5'),
        ('Bottom 6', 'Bottom 5'),
        ('exactly 12', 'exactly 10'),
        ('exactly 6', 'exactly 5'),
        ('need 12', 'need 10'),
        ('need 6', 'need 5'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed reporter_dashboard.html")

def fix_manager_dashboard():
    """Fix manager_dashboard.html"""
    filepath = 'templates/manager_dashboard.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace any remaining 12/6 references
    replacements = [
        ('12 preferred', '10 preferred'),
        ('top 12', 'top 10'),
        ('Top 12', 'Top 10'),
        ('bottom 6', 'bottom 5'),
        ('Bottom 6', 'Bottom 5'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed manager_dashboard.html")

print("="*70)
print("APPLYING REPORTER TWEAKS")
print("="*70)

fix_login_page()
fix_dashboard_preferences()
fix_manager_dashboard()

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
print("\nNext steps:")
print("1. Restart Flask (Ctrl+C then python app.py)")
print("2. Test locally")
print("3. git add .")
print("4. git commit -m 'Fix login title and preference counts'")
print("5. git push")
print("="*70)
