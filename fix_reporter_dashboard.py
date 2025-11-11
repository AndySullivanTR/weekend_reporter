"""
Comprehensive fix for reporter_dashboard.html
Changes ALL instances of 12/6 to 10/5 including JavaScript validation
"""

def fix_reporter_dashboard():
    """Fix reporter_dashboard.html completely"""
    filepath = 'templates/reporter_dashboard.html'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Text replacements
    replacements = [
        # Instruction text
        ('First 12 clicks', 'First 10 clicks'),
        ('Next 6 clicks', 'Next 5 clicks'),
        ('top 12', 'top 10'),
        ('Top 12', 'Top 10'),
        ('bottom 6', 'bottom 5'),
        ('Bottom 6', 'Bottom 5'),
        ('12 preferred', '10 preferred'),
        ('6 least', '5 least'),
        
        # JavaScript array lengths
        ("top_12", "top_10"),
        ("bottom_6", "bottom_5"),
        ("'top_12'", "'top_10'"),
        ("'bottom_6'", "'bottom_5'"),
        ('"top_12"', '"top_10"'),
        ('"bottom_6"', '"bottom_5"'),
        
        # JavaScript validation numbers
        ('.length < 12', '.length < 10'),
        ('.length !== 12', '.length !== 10'),
        ('!== 12', '!== 10'),
        ('== 12', '== 10'),
        ('< 12', '< 10'),
        
        ('.length < 6', '.length < 5'),
        ('.length !== 6', '.length !== 5'),
        ('!== 6', '!== 5'),
        ('== 6', '== 5'),
        ('< 6', '< 5'),
        
        # Display text
        ('need 12', 'need 10'),
        ('need 6', 'need 5'),
        ('(need 12)', '(need 10)'),
        ('(need 6)', '(need 5)'),
        
        # Error messages
        ('exactly 12 top', 'exactly 10 top'),
        ('exactly 6 least', 'exactly 5 least'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed reporter_dashboard.html - all 12/6 changed to 10/5")

print("="*70)
print("FIXING REPORTER DASHBOARD")
print("="*70)

fix_reporter_dashboard()

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
print("\nRestart Flask and test:")
print("- Should show 'First 10 clicks' and 'Next 5 clicks'")
print("- Validation should require exactly 10 and 5")
print("- Counter should show '0 / 10' and '0 / 5'")
print("="*70)
