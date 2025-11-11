"""
Fix manager dashboard button text:
- "Run Allocation Algorithm" → "Assign Shifts"
- "Export to Excel" → "Download Schedule"
"""

def fix_manager_buttons():
    """Fix manager_dashboard.html button text"""
    filepath = 'templates/manager_dashboard.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace button text
    replacements = [
        ('Run Allocation Algorithm', 'Assign Shifts'),
        ('Export to Excel', 'Download Schedule'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed manager_dashboard.html button text")

print("="*70)
print("UPDATING MANAGER DASHBOARD BUTTONS")
print("="*70)

fix_manager_buttons()

print("\n✓ Complete! Restart Flask to see changes.")
print("="*70)
