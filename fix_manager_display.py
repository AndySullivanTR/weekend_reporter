"""
Fix manager_dashboard.html to show correct 10/5 counts in table
"""

def fix_manager_dashboard_display():
    """Fix manager_dashboard.html display counts"""
    filepath = 'templates/manager_dashboard.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the Jinja template logic that checks length
    replacements = [
        # Table header text
        ('Top 12 Preferences', 'Top 10 Preferences'),
        ('Bottom 6 Preferences', 'Bottom 5 Preferences'),
        
        # Jinja length checks
        ("preferences[username].get('top_12')", "preferences[username].get('top_10')"),
        ("preferences[username].get('bottom_6')", "preferences[username].get('bottom_5')"),
        ("preferences[username]['top_12']", "preferences[username]['top_10']"),
        ("preferences[username]['bottom_6']", "preferences[username]['bottom_5']"),
        
        # Display counts
        ('|length }}/12', '|length }}/10'),
        ('|length }}/6', '|length }}/5'),
        (' == 12 and ', ' == 10 and '),
        (' == 6 %}', ' == 5 %}'),
        
        # Any remaining references
        ('top_12', 'top_10'),
        ('bottom_6', 'bottom_5'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed manager_dashboard.html - display now shows 10/5")

print("="*70)
print("FIXING MANAGER DASHBOARD DISPLAY")
print("="*70)

fix_manager_dashboard_display()

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
print("\nRestart Flask and you should see:")
print("- Top 10 Preferences: 10/10")
print("- Bottom 5 Preferences: 5/5")
print("="*70)
