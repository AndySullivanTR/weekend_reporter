"""
Analyze reporter allocation results
Shows which reporters got their top choices vs. who got less preferred shifts
"""

import json
from collections import defaultdict

# Load data
with open('data/reporters.json', 'r') as f:
    reporters = json.load(f)

with open('data/preferences.json', 'r') as f:
    preferences = json.load(f)

with open('data/assignments.json', 'r') as f:
    assignments = json.load(f)

print("="*80)
print("REPORTER ALLOCATION RESULTS ANALYSIS")
print("="*80)

# Analyze each reporter
reporter_results = []

for rep in sorted(assignments.keys()):
    if rep not in reporters or reporters[rep].get('is_manager'):
        continue
    
    rep_name = reporters[rep]['name']
    rep_prefs = preferences.get(rep, {})
    rep_shifts = assignments.get(rep, [])
    
    top_10 = rep_prefs.get('top_10', [])
    bottom_5 = rep_prefs.get('bottom_5', [])
    
    # Calculate rank for assigned shift
    shift_rank = None
    got_top_10 = False
    got_bottom_5 = False
    
    if len(rep_shifts) > 0:
        shift_id = rep_shifts[0]
        if shift_id in top_10:
            shift_rank = top_10.index(shift_id) + 1
            got_top_10 = True
        elif shift_id in bottom_5:
            shift_rank = 'BOTTOM-5'
            got_bottom_5 = True
        else:
            shift_rank = 'NOT-RANKED'
    
    reporter_results.append({
        'name': rep_name,
        'has_shift': len(rep_shifts) > 0,
        'rank': shift_rank,
        'got_top_10': got_top_10,
        'got_bottom_5': got_bottom_5,
        'got_screwed': got_bottom_5
    })

# Sort by rank (best first)
def sort_key(x):
    if x['rank'] == 'BOTTOM-5':
        return 999
    elif x['rank'] == 'NOT-RANKED':
        return 100
    elif isinstance(x['rank'], int):
        return x['rank']
    else:
        return 1000

reporter_results.sort(key=sort_key)

print("\n" + "="*80)
print("REPORTER RESULTS (Best to Worst)")
print("="*80)
print(f"{'Reporter':<15} {'Shift Assigned':<15} {'Rank':<15} {'Status'}")
print("-"*80)

for result in reporter_results:
    assigned = "Yes" if result['has_shift'] else "No"
    
    if result['rank'] is None:
        rank_str = "N/A"
    elif isinstance(result['rank'], int):
        rank_str = f"#{result['rank']}"
    else:
        rank_str = result['rank']
    
    # Status
    if result['got_bottom_5']:
        status = "😢 GOT BOTTOM-5"
    elif result['got_top_10']:
        if result['rank'] <= 3:
            status = "😊 GREAT"
        elif result['rank'] <= 6:
            status = "🙂 GOOD"
        else:
            status = "😐 OK"
    elif result['has_shift']:
        status = "⚠️  UNRANKED"
    else:
        status = "✗ NO SHIFT"
    
    print(f"{result['name']:<15} {assigned:<15} {rank_str:<15} {status}")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

total_reporters = len(reporter_results)
fully_assigned = sum(1 for r in reporter_results if r['has_shift'])
got_top_10 = sum(1 for r in reporter_results if r['got_top_10'])
got_bottom_5 = sum(1 for r in reporter_results if r['got_bottom_5'])
got_unranked = sum(1 for r in reporter_results if r['has_shift'] and not r['got_top_10'] and not r['got_bottom_5'])

print(f"Total Reporters:           {total_reporters}")
print(f"Assigned (1 shift):        {fully_assigned} ({fully_assigned/total_reporters*100:.1f}%)")
print(f"Got Top 10 Choice:         {got_top_10} ({got_top_10/total_reporters*100:.1f}%)")
print(f"Got Unranked Shift:        {got_unranked} ({got_unranked/total_reporters*100:.1f}%)")
print(f"Got Bottom-5 Shift:        {got_bottom_5} ({got_bottom_5/total_reporters*100:.1f}%)")

# Rank distribution
rank_counts = defaultdict(int)
for result in reporter_results:
    if isinstance(result['rank'], int):
        if result['rank'] <= 3:
            rank_counts['Top 3'] += 1
        elif result['rank'] <= 5:
            rank_counts['4-5'] += 1
        elif result['rank'] <= 7:
            rank_counts['6-7'] += 1
        else:
            rank_counts['8-10'] += 1
    elif result['rank'] == 'BOTTOM-5':
        rank_counts['Bottom 5'] += 1
    elif result['rank'] == 'NOT-RANKED':
        rank_counts['Not Ranked'] += 1

print(f"\nRank Distribution ({fully_assigned} shifts assigned):")
for rank_range, count in sorted(rank_counts.items()):
    print(f"  {rank_range}: {count} reporters")

# Average satisfaction
numeric_ranks = [r['rank'] for r in reporter_results if isinstance(r['rank'], int)]
overall_avg = sum(numeric_ranks) / len(numeric_ranks) if numeric_ranks else 0

print(f"\nOverall Average Rank: {overall_avg:.2f} (lower is better, out of top 10)")

print("\n" + "="*80)
print("WHO GOT SCREWED?")
print("="*80)

screwed_reporters = [r for r in reporter_results if r['got_screwed']]
if screwed_reporters:
    for result in screwed_reporters:
        print(f"😢 {result['name']:<15} got: BOTTOM-5 shift")
else:
    print("✅ Nobody got screwed! Everyone got shifts from their top 10 or unranked (not bottom 5).")

print("\n" + "="*80)
print("TOP PERFORMERS (Best ranks)")
print("="*80)

top_reporters = [r for r in reporter_results if isinstance(r['rank'], int)][:10]
for i, result in enumerate(top_reporters, 1):
    print(f"{i}. {result['name']:<15} Rank: #{result['rank']}")

print("\n" + "="*80)
print("\nNote: Each reporter gets exactly 1 shift (vs. 2 for trunk writers)")
print("="*80)
