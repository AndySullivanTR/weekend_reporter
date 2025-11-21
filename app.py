from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import random

# Determine the base directory (where this script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

template_folder = os.path.join(BASE_DIR, 'templates')
app = Flask(__name__, template_folder=template_folder)

# Fixed secret key for session persistence across restarts
app.secret_key = 'reporter-weekend-shifts-secret-key-2025'

# Data storage (in production, use a proper database or persistent volume)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

REPORTERS_FILE = os.path.join(DATA_DIR, 'reporters.json')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'preferences.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'assignments.json')

# ---- SHIFT GENERATION ----
# You can tweak this however you like; currently:
# - Starts from "next Saturday" relative to now
# - 6 weekends
# - 4 shifts per weekend (Sat day/eve, Sun day/eve)
def generate_shifts():
    shifts = []
    today = datetime.today()
    # next Saturday
    start_saturday = today + timedelta((5 - today.weekday()) % 7)
    shift_id = 0

    for week in range(6):  # 6 weekends
        saturday = start_saturday + timedelta(weeks=week)
        sunday = saturday + timedelta(days=1)

        # Saturday daytime shift
        shifts.append({
            'id': shift_id,
            'date': saturday.strftime('%Y-%m-%d'),
            'day': 'Saturday',
            'time': '9:00 AM - 5:00 PM',
            'slots': 2,
            'week': week + 1
        })
        shift_id += 1

        # Saturday evening shift
        shifts.append({
            'id': shift_id,
            'date': saturday.strftime('%Y-%m-%d'),
            'day': 'Saturday',
            'time': '5:00 PM - 11:00 PM',
            'slots': 1,
            'week': week + 1
        })
        shift_id += 1

        # Sunday daytime shift
        shifts.append({
            'id': shift_id,
            'date': sunday.strftime('%Y-%m-%d'),
            'day': 'Sunday',
            'time': '9:00 AM - 5:00 PM',
            'slots': 2,
            'week': week + 1
        })
        shift_id += 1

        # Sunday evening shift
        shifts.append({
            'id': shift_id,
            'date': sunday.strftime('%Y-%m-%d'),
            'day': 'Sunday',
            'time': '5:00 PM - 11:00 PM',
            'slots': 1,
            'week': week + 1
        })
        shift_id += 1

    return shifts

SHIFTS = generate_shifts()

# ---- INITIAL DATA ----

def init_data_files():
    # Create 121 reporters + admin if reporters.json doesn't exist
    if not os.path.exists(REPORTERS_FILE):
        reporters = {}

        # Manager account
        reporters['admin'] = {
            'name': 'Admin',
            'is_manager': True,
            'password': generate_password_hash('admin123')
        }

        # 121 reporter accounts
        for i in range(1, 122):
            username = f'reporter{i}'
            reporters[username] = {
                'name': f'Reporter{i}',
                'is_manager': False,
                'password': generate_password_hash('password')
            }

        with open(REPORTERS_FILE, 'w') as f:
            json.dump(reporters, f, indent=2)

    if not os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump({}, f)

    if not os.path.exists(SETTINGS_FILE):
        # Default deadline: 7 days from now
        deadline = (datetime.now() + timedelta(days=7)).isoformat()
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({'deadline': deadline, 'is_locked': False}, f)

    if not os.path.exists(ASSIGNMENTS_FILE):
        with open(ASSIGNMENTS_FILE, 'w') as f:
            json.dump({}, f)

init_data_files()

# ---- HELPERS ----

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_reporters():
    return load_json(REPORTERS_FILE)

def get_preferences():
    return load_json(PREFERENCES_FILE)

def get_settings():
    return load_json(SETTINGS_FILE)

def get_assignments():
    return load_json(ASSIGNMENTS_FILE)

def get_naive_deadline(settings):
    """
    Parse settings['deadline'] and return a timezone-naive datetime suitable
    for comparison with datetime.now(). If parsing fails, default to a week
    from now and log a warning.
    """
    try:
        deadline_str = settings['deadline']
        deadline = datetime.fromisoformat(deadline_str)
        if deadline.tzinfo is not None:
            deadline = deadline.replace(tzinfo=None)
        return deadline
    except Exception as e:
        print(f"Warning: Could not parse deadline: {e}")
        return datetime.now() + timedelta(days=7)

def create_auto_backup():
    """Create an automatic backup of all data files"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_data = {
            'reporters': get_reporters(),
            'preferences': get_preferences(),
            'settings': get_settings(),
            'assignments': get_assignments(),
            'timestamp': datetime.now().isoformat()
        }

        backup_file = os.path.join(BACKUP_DIR, f'auto_backup_{timestamp}.json')
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        # Keep only last 30 backups
        backup_files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith('auto_backup_')]
        )
        if len(backup_files) > 30:
            for old_backup in backup_files[:-30]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))

        return True
    except Exception as e:
        print(f"Auto-backup failed: {e}")
        return False

def format_deadline(iso_datetime_str):
    """Format ISO datetime to readable format: 'Nov. 27, 2025 3:24 a.m. ET'"""
    dt = datetime.fromisoformat(iso_datetime_str)
    month = dt.strftime('%b')
    day = dt.day
    year = dt.year
    hour = dt.hour
    minute = dt.minute

    # Convert to 12-hour format with am/pm
    if hour == 0:
        hour_12 = 12
        am_pm = 'a.m.'
    elif hour < 12:
        hour_12 = hour
        am_pm = 'a.m.'
    elif hour == 12:
        hour_12 = 12
        am_pm = 'p.m.'
    else:
        hour_12 = hour - 12
        am_pm = 'p.m.'

    return f"{month}. {day}, {year} {hour_12}:{minute:02d} {am_pm} ET"

def calculate_satisfaction_score(preferences, assigned_shift_id):
    """
    Calculate satisfaction score for a single assigned shift.
    Lower score = better (based on preference rank)
    """
    top_prefs = preferences.get('top_12', [])

    if assigned_shift_id in top_prefs:
        rank = top_prefs.index(assigned_shift_id) + 1
        return rank
    else:
        # Not in top preferences - assign high penalty score
        return 999

def has_same_weekend_conflict(reporter_shifts, new_shift_id):
    """
    Check if assigning new_shift_id would create two shifts on same weekend.
    Returns True if there's a conflict.
    """
    new_shift = next(s for s in SHIFTS if s['id'] == new_shift_id)
    new_week = new_shift['week']

    for shift_id in reporter_shifts:
        existing_shift = next(s for s in SHIFTS if s['id'] == shift_id)
        if existing_shift['week'] == new_week:
            return True

    return False

def has_consecutive_shift_conflict(reporter_shifts, new_shift_id):
    """
    Check if assigning new_shift_id would create back-to-back/overlapping shifts.
    For the current schedule this mostly matters if you add overlapping shifts
    on the same day; kept for safety / future changes.
    """
    new_shift = next(s for s in SHIFTS if s['id'] == new_shift_id)
    new_date = new_shift['date']
    new_day = new_shift['day']

    for shift_id in reporter_shifts:
        existing_shift = next(s for s in SHIFTS if s['id'] == shift_id)
        if existing_shift['date'] == new_date and existing_shift['day'] == new_day:
            return True

    return False

# ---- ROUTES ----

@app.route('/')
def index():
    if 'username' in session:
        if session.get('is_manager'):
            return redirect(url_for('manager_dashboard'))
        else:
            return redirect(url_for('reporter_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        reporters = get_reporters()

        if username in reporters:
            if check_password_hash(reporters[username]['password'], password):
                session['username'] = username
                session['is_manager'] = reporters[username].get('is_manager', False)
                return jsonify({'success': True, 'is_manager': session['is_manager']})

        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/manager/dashboard')
def manager_dashboard():
    if not session.get('is_manager'):
        return redirect(url_for('login'))

    reporters = get_reporters()
    settings = get_settings()
    preferences = get_preferences()
    assignments = get_assignments()

    # Count reporters who have submitted complete preferences
    submitted_count = sum(
        1 for user, prefs in preferences.items()
        if prefs and len(prefs.get('top_12', [])) == 12 and len(prefs.get('bottom_6', [])) == 6
    )

    return render_template(
        'manager_dashboard.html',
        reporters=reporters,
        settings=settings,
        submitted_count=submitted_count,
        total_reporters=len([u for u in reporters.values() if not u.get('is_manager')]),
        assignments=assignments,
        preferences=preferences,
        shifts=SHIFTS
    )

@app.route('/reporter/dashboard')
def reporter_dashboard():
    if 'username' not in session or session.get('is_manager'):
        return redirect(url_for('login'))

    settings = get_settings()
    preferences = get_preferences()
    assignments = get_assignments()
    username = session['username']

    user_prefs = preferences.get(username, {})
    user_assignments = assignments.get(username, [])

    # Deadline / lock state
    deadline = get_naive_deadline(settings)
    is_locked = settings.get('is_locked', False) or datetime.now() > deadline

    try:
        formatted_deadline = format_deadline(settings['deadline'])
    except Exception:
        formatted_deadline = settings.get('deadline', 'Not set')

    return render_template(
        'reporter_dashboard.html',
        username=username,
        shifts=SHIFTS,
        preferences=user_prefs,
        assignments=user_assignments,
        deadline=formatted_deadline,
        is_locked=is_locked
    )

@app.route('/api/reporters', methods=['GET', 'POST', 'DELETE'])
def manage_reporters():
    if not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    reporters = get_reporters()

    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')

        if username in reporters:
            return jsonify({'error': 'Reporter already exists'}), 400

        reporters[username] = {
            'name': name,
            'password': generate_password_hash(password),
            'is_manager': False
        }
        save_json(REPORTERS_FILE, reporters)
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        data = request.json
        username = data.get('username')

        if username in reporters:
            del reporters[username]
            save_json(REPORTERS_FILE, reporters)

            # Also remove their preferences
            preferences = get_preferences()
            if username in preferences:
                del preferences[username]
                save_json(PREFERENCES_FILE, preferences)

            return jsonify({'success': True})

        return jsonify({'error': 'Reporter not found'}), 404

    # GET
    return jsonify(reporters)

@app.route('/api/preferences', methods=['GET', 'POST'])
def manage_preferences():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    username = session['username']
    preferences = get_preferences()
    settings = get_settings()

    # Lock check using timezone-safe helper
    deadline = get_naive_deadline(settings)
    is_locked = settings.get('is_locked', False) or datetime.now() > deadline

    if request.method == 'POST':
        if is_locked and not session.get('is_manager'):
            return jsonify({'error': 'Preferences are locked'}), 403

        data = request.json

        # Validate structure
        if 'top_12' not in data or 'bottom_6' not in data or 'shift_type_pref' not in data:
            return jsonify({'error': 'Invalid preference format'}), 400

        if len(data['top_12']) != 12:
            return jsonify({'error': 'Must select exactly 12 top preferences'}), 400

        if len(data['bottom_6']) != 6:
            return jsonify({'error': 'Must select exactly 6 least wanted shifts'}), 400

        preferences[username] = {
            'top_12': data['top_12'],
            'bottom_6': data['bottom_6'],
            'shift_type_pref': data['shift_type_pref']
        }
        save_json(PREFERENCES_FILE, preferences)

        # Auto-backup after a successful submission
        create_auto_backup()

        return jsonify({'success': True})

    # GET
    if session.get('is_manager'):
        return jsonify(preferences)
    else:
        return jsonify({username: preferences.get(username, {})})

@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    if not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    settings = get_settings()

    if request.method == 'POST':
        data = request.json

        if 'deadline' in data:
            settings['deadline'] = data['deadline']

        if 'is_locked' in data:
            settings['is_locked'] = data['is_locked']

        save_json(SETTINGS_FILE, settings)
        return jsonify({'success': True})

    return jsonify(settings)

@app.route('/api/allocate', methods=['POST'])
def allocate_shifts():
    if not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    # Backup before allocation
    create_auto_backup()

    preferences = get_preferences()
    reporters_data = get_reporters()

    # All non-manager reporters
    reporter_list = [user for user, info in reporters_data.items() if not info.get('is_manager')]

    reporters_with_prefs = []
    reporters_without_prefs = []

    for rep in reporter_list:
        if rep in preferences:
            prefs = preferences[rep]
            if len(prefs.get('top_12', [])) == 12 and len(prefs.get('bottom_6', [])) == 6:
                reporters_with_prefs.append(rep)
            else:
                reporters_without_prefs.append(rep)
        else:
            reporters_without_prefs.append(rep)

    assignments = {rep: [] for rep in reporter_list}
    shift_assignments = {shift['id']: [] for shift in SHIFTS}
    warnings = []

    random.seed(42)

    # PHASE 1: First shift, preference-based
    shuffled_reporters = reporters_with_prefs.copy()
    random.shuffle(shuffled_reporters)

    for rep in shuffled_reporters:
        prefs = preferences[rep]
        top_12 = prefs['top_12']
        bottom_6 = prefs['bottom_6']

        assigned = False

        for shift_id in top_12:
            shift = next(s for s in SHIFTS if s['id'] == shift_id)
            if len(shift_assignments[shift_id]) >= shift['slots']:
                continue

            if has_same_weekend_conflict(assignments[rep], shift_id):
                continue

            if has_consecutive_shift_conflict(assignments[rep], shift_id):
                continue

            assignments[rep].append(shift_id)
            shift_assignments[shift_id].append(rep)
            assigned = True
            break

        if not assigned:
            shift_type_pref = prefs.get('shift_type_pref', {})
            sorted_types = sorted(shift_type_pref.items(), key=lambda x: x[1])

            for shift_type, _ in sorted_types:
                for shift in SHIFTS:
                    sid = shift['id']

                    if sid in bottom_6:
                        continue
                    if sid in top_12:
                        continue

                    # Simple type matching demo
                    shift_matches = False
                    if shift_type == 'saturday' and shift['day'] == 'Saturday':
                        shift_matches = True
                    elif shift_type == 'sunday_day' and shift['day'] == 'Sunday' and '9:00 AM' in shift['time']:
                        shift_matches = True
                    elif shift_type == 'sunday_evening' and shift['day'] == 'Sunday' and '5:00 PM' in shift['time']:
                        shift_matches = True

                    if not shift_matches:
                        continue

                    if len(shift_assignments[sid]) >= shift['slots']:
                        continue

                    if has_same_weekend_conflict(assignments[rep], sid):
                        continue

                    if has_consecutive_shift_conflict(assignments[rep], sid):
                        continue

                    assignments[rep].append(sid)
                    shift_assignments[sid].append(rep)
                    assigned = True
                    break

                if assigned:
                    break

        if not assigned:
            warnings.append(f"{rep} could not be assigned a first shift via preferences")

    # PHASE 2: Second shift, sorted by satisfaction
    reporter_satisfaction = []
    for rep in reporters_with_prefs:
        if len(assignments[rep]) > 0:
            score = calculate_satisfaction_score(preferences[rep], assignments[rep][0])
            reporter_satisfaction.append((rep, score))
        else:
            reporter_satisfaction.append((rep, 9999))

    reporter_satisfaction.sort(key=lambda x: (x[1], random.random()))

    for rep, score in reporter_satisfaction:
        if len(assignments[rep]) >= 2:
            continue

        prefs = preferences[rep]
        top_12 = prefs['top_12']
        bottom_6 = prefs['bottom_6']

        assigned = False

        for shift_id in top_12:
            if shift_id in assignments[rep]:
                continue

            shift = next(s for s in SHIFTS if s['id'] == shift_id)
            if len(shift_assignments[shift_id]) >= shift['slots']:
                continue

            if has_same_weekend_conflict(assignments[rep], shift_id):
                continue

            if has_consecutive_shift_conflict(assignments[rep], shift_id):
                continue

            assignments[rep].append(shift_id)
            shift_assignments[shift_id].append(rep)
            assigned = True
            break

        if not assigned:
            shift_type_pref = prefs.get('shift_type_pref', {})
            sorted_types = sorted(shift_type_pref.items(), key=lambda x: x[1])

            for shift_type, _ in sorted_types:
                for shift in SHIFTS:
                    sid = shift['id']

                    if sid in assignments[rep]:
                        continue
                    if sid in bottom_6:
                        continue

                    shift_matches = False
                    if shift_type == 'saturday' and shift['day'] == 'Saturday':
                        shift_matches = True
                    elif shift_type == 'sunday_day' and shift['day'] == 'Sunday' and '9:00 AM' in shift['time']:
                        shift_matches = True
                    elif shift_type == 'sunday_evening' and shift['day'] == 'Sunday' and '5:00 PM' in shift['time']:
                        shift_matches = True

                    if not shift_matches:
                        continue

                    if len(shift_assignments[sid]) >= shift['slots']:
                        continue

                    if has_same_weekend_conflict(assignments[rep], sid):
                        continue

                    if has_consecutive_shift_conflict(assignments[rep], sid):
                        continue

                    assignments[rep].append(sid)
                    shift_assignments[sid].append(rep)
                    assigned = True
                    break

                if assigned:
                    break

        if not assigned:
            warnings.append(f"{rep} could not be assigned a second shift via preferences")

    # PHASE 3: Random for reporters without complete prefs
    if reporters_without_prefs:
        for rep in reporters_without_prefs:
            warnings.append(f"{rep} was randomly assigned (no or incomplete preferences)")

            available_shifts = []
            for shift in SHIFTS:
                sid = shift['id']

                if len(shift_assignments[sid]) >= shift['slots']:
                    continue

                if has_same_weekend_conflict(assignments[rep], sid):
                    continue

                if has_consecutive_shift_conflict(assignments[rep], sid):
                    continue

                available_shifts.append(sid)

            needed = max(0, 2 - len(assignments[rep]))
            if len(available_shifts) >= needed and needed > 0:
                selected = random.sample(available_shifts, needed)
                for sid in selected:
                    assignments[rep].append(sid)
                    shift_assignments[sid].append(rep)
            else:
                warnings.append(f"{rep} could not be fully assigned - insufficient available shifts")

    # Save assignments + lock
    save_json(ASSIGNMENTS_FILE, assignments)
    settings = get_settings()
    settings['is_locked'] = True
    save_json(SETTINGS_FILE, settings)

    return jsonify({
        'success': True,
        'assignments': assignments,
        'shift_assignments': shift_assignments,
        'warnings': warnings
    })

@app.route('/api/backup')
def backup_data():
    """Download all data files as JSON for backup (manager only)"""
    if not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    backup_data = {
        'reporters': get_reporters(),
        'preferences': get_preferences(),
        'settings': get_settings(),
        'assignments': get_assignments(),
        'timestamp': datetime.now().isoformat()
    }

    from io import BytesIO
    output = BytesIO()
    output.write(json.dumps(backup_data, indent=2).encode('utf-8'))
    output.seek(0)

    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

@app.route('/api/create-backup', methods=['POST'])
def trigger_backup():
    """Manually trigger an auto-backup (manager only)"""
    if not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    success = create_auto_backup()
    if success:
        return jsonify({'success': True, 'message': 'Backup created successfully'})
    else:
        return jsonify({'error': 'Backup failed'}), 500

@app.route('/api/list-backups')
def list_backups():
    """List available backup files (manager only)"""
    if not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        backup_files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith('auto_backup_')],
            reverse=True
        )
        backups = []

        for filename in backup_files[:30]:
            filepath = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(filepath)
            backups.append({
                'filename': filename,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return jsonify({
            'success': True,
            'backups': backups,
            'total': len(backup_files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Allow reporters (or admin) to change their password"""
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

    if username not in reporters:
        return jsonify({'error': 'User not found'}), 404

    if not check_password_hash(reporters[username]['password'], current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    reporters[username]['password'] = generate_password_hash(new_password)
    save_json(REPORTERS_FILE, reporters)

    return jsonify({'success': True, 'message': 'Password changed successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
