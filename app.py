from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import random

def get_naive_deadline(settings):
    """Return a timezone-naive deadline datetime parsed from settings['deadline'].

    If the stored deadline is timezone-aware, its tzinfo is stripped so it can be
    safely compared with datetime.now(), which is also naive by default.
    On parse errors, defaults to one week from now and logs a warning.
    """
    try:
        deadline = datetime.fromisoformat(settings['deadline'])
        if deadline.tzinfo is not None:
            deadline = deadline.replace(tzinfo=None)
        return deadline
    except Exception as e:
        print(f"Warning: Could not parse deadline: {e}")
        return datetime.now() + timedelta(days=7)

# Determine the base directory (where this script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

template_folder = os.path.join(BASE_DIR, 'templates')
app = Flask(__name__, template_folder=template_folder)
# Fixed secret key for session persistence across restarts
app.secret_key = 'super_secret_key_for_dev_only'

# File paths for data storage
SETTINGS_FILE = os.path.join(PARENT_DIR, 'reporter_settings.json')
PREFERENCES_FILE = os.path.join(PARENT_DIR, 'reporter_preferences.json')
ASSIGNMENTS_FILE = os.path.join(PARENT_DIR, 'weekend_assignments.json')
USERS_FILE = os.path.join(PARENT_DIR, 'users.json')

# Define the user shift pedigree file path here
PEDIGREE_FILE = os.path.join(PARENT_DIR, 'user_shift_pedigree.json')

# Default settings structure
default_settings = {
    'period_label': 'Weekend Coverage: Saturday, Jan 4 - Sunday, Jan 5',
    'deadline': '',
    'is_locked': False,
    'require_rating': True,
    'collect_availability': False
}

# Default users with hashed passwords
default_users = {
    "manager": {
        "password": generate_password_hash("managerpass"),
        "is_manager": True,
        "is_reporter": False
    },
    "reporter1": {
        "password": generate_password_hash("reporterpass"),
        "is_manager": False,
        "is_reporter": True
    }
}

# Updated shifts to have more slots and include identifying info
def generate_weekend_shifts():
    """
    Generates weekend shifts for the next six weekends (Saturday and Sunday) with multiple slots per shift.
    """
    shifts = []
    today = datetime.today()
    start_saturday = today + timedelta((5 - today.weekday()) % 7)  # Next Saturday
    
    shift_id = 1
    for week in range(6):  # Next 6 weekends
        saturday = start_saturday + timedelta(weeks=week)
        sunday = saturday + timedelta(days=1)
        
        # Saturday daytime shift - 2 reporters
        shifts.append({
            'id': shift_id,
            'date': saturday.strftime('%Y-%m-%d'),
            'day': 'Saturday',
            'time': '9:00 AM - 5:00 PM',
            'slots': 2,
            'week': week + 1
        })
        shift_id += 1
        
        # Saturday evening shift - 1 reporter
        shifts.append({
            'id': shift_id,
            'date': saturday.strftime('%Y-%m-%d'),
            'day': 'Saturday',
            'time': '5:00 PM - 11:00 PM',
            'slots': 1,
            'week': week + 1
        })
        shift_id += 1
        
        # Sunday daytime shift - 2 reporters
        shifts.append({
            'id': shift_id,
            'date': sunday.strftime('%Y-%m-%d'),
            'day': 'Sunday',
            'time': '9:00 AM - 5:00 PM',
            'slots': 2,
            'week': week + 1
        })
        shift_id += 1
        
        # Sunday evening shift - 1 reporter
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

SHIFTS = generate_weekend_shifts()

def load_users():
    """Load users from file or initialize default users."""
    if not os.path.exists(USERS_FILE):
        save_users(default_users)
        return default_users
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        save_users(default_users)
        return default_users

def save_users(users):
    """Save users to file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except IOError as e:
        print(f"Error saving users: {e}")

def get_settings():
    """Load settings from JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        for key, value in default_settings.items():
            settings.setdefault(key, value)
        return settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading settings: {e}")
        save_settings(default_settings)
        return default_settings

def save_settings(settings):
    """Save settings to JSON file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except IOError as e:
        print(f"Error saving settings: {e}")

def get_preferences():
    """Load preferences from JSON file."""
    if not os.path.exists(PREFERENCES_FILE):
        return {}
    try:
        with open(PREFERENCES_FILE, 'r') as f:
            data = json.load(f)
            return data.get('preferences', {})
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading preferences: {e}")
        return {}

def save_preferences_to_file(preferences):
    """Save preferences to JSON file."""
    data = {
        "last_updated": datetime.now().isoformat(),
        "preferences": preferences
    }
    try:
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving preferences: {e}")

def get_assignments():
    """Load assignments from JSON file."""
    if not os.path.exists(ASSIGNMENTS_FILE):
        return {}
    try:
        with open(ASSIGNMENTS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('assignments', {})
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading assignments: {e}")
        return {}

def save_assignments(assignments, assigned_shift_counts=None, coverage_gaps=None, future_assignments=None):
    """Save assignments to JSON file."""
    data = {
        "last_updated": datetime.now().isoformat(),
        "assignments": assignments
    }

    if assigned_shift_counts is not None:
        data["metadata"] = data.get("metadata", {})
        data["metadata"]["assigned_shift_counts"] = assigned_shift_counts

    if coverage_gaps is not None:
        data["metadata"] = data.get("metadata", {})
        data["metadata"]["coverage_gaps"] = coverage_gaps

    if future_assignments is not None:
        data["metadata"] = data.get("metadata", {})
        data["metadata"]["future_assignments"] = future_assignments
        
    try:
        with open(ASSIGNMENTS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving assignments: {e}")

def save_user_shift_pedigree(user_shift_pedigree):
    """Save user shift pedigree to JSON file."""
    data = {
        "last_updated": datetime.now().isoformat(),
        "user_shift_pedigree": user_shift_pedigree
    }
    try:
        with open(PEDIGREE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving user shift pedigree: {e}")

def load_user_shift_pedigree():
    """Load user shift pedigree from JSON file or return empty dict."""
    if not os.path.exists(PEDIGREE_FILE):
        return {}
    try:
        with open(PEDIGREE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("user_shift_pedigree", {})
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading user shift pedigree: {e}")
        return {}

def get_eligible_users_for_shift(user_shift_pedigree, cutoff_months=6):
    """
    Returns a set of users who have taken shifts in the last given number of months (default 6).
    """
    eligible_users = set()
    cutoff_date = datetime.now() - timedelta(days=30 * cutoff_months)  # Rough 6 months period
    
    for user, shifts in user_shift_pedigree.items():
        for shift in shifts:
            try:
                shift_date = datetime.strptime(shift['date'], '%Y-%m-%d')
                if shift_date >= cutoff_date:
                    eligible_users.add(user)
                    break  # Only need to know if they worked at least once
            except ValueError as e:
                print(f"Error parsing shift date for user {user}: {e}")
                continue
    
    return eligible_users

def compute_shift_pedigree(assignments, existing_pedigree=None):
    """
    Computes and returns user shift pedigree from the assignments.
    """
    user_shift_pedigree = existing_pedigree or {}

    # Use SHIFTS data to map shift IDs to details (day, time, date)
    shift_map = {shift['id']: shift for shift in SHIFTS}

    for user, user_assignments in assignments.items():
        for shift_data in user_assignments:
            shift_id = shift_data if isinstance(shift_data, int) else shift_data.get('id')
            shift_details = shift_map.get(shift_id)

            if not shift_details:
                continue

            entry = {
                'date': shift_details['date'],
                'day': shift_details['day'],
                'time': shift_details['time'],
                'week': shift_details['week']
            }

            if user not in user_shift_pedigree:
                user_shift_pedigree[user] = []

            if entry not in user_shift_pedigree[user]:
                user_shift_pedigree[user].append(entry)

    return user_shift_pedigree

def format_deadline(deadline_str):
    """Format deadline string in a more readable way."""
    try:
        if deadline_str.endswith('Z'):
            # Convert to local time
            deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        else:
            deadline_dt = datetime.fromisoformat(deadline_str)
        return deadline_dt.strftime('%A, %B %d at %I:%M %p')
    except Exception as e:
        print(f"Error formatting deadline: {e}")
        return deadline_str

@app.route('/')
def home():
    if 'username' in session:
        if session.get('is_manager'):
            return redirect(url_for('manager_dashboard'))
        elif session.get('is_reporter'):
            return redirect(url_for('reporter_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Debug print: show available users and their types
        print(f"Login attempt for username: {username}")
        print(f"Available users in system: {list(users.keys())}")

        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['is_manager'] = user.get('is_manager', False)
            session['is_reporter'] = user.get('is_reporter', False)

            if user.get('is_manager'):
                print(f"User '{username}' identified as manager. Redirecting to manager dashboard.")
                return redirect(url_for('manager_dashboard'))
            elif user.get('is_reporter'):
                print(f"User '{username}' identified as reporter. Redirecting to reporter dashboard.")
                return redirect(url_for('reporter_dashboard'))
        else:
            error = 'Invalid username or password'
            print(f"Invalid login attempt for username: {username}")
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/manager/dashboard')
def manager_dashboard():
    if 'username' not in session or not session.get('is_manager'):
        return redirect(url_for('login'))
    
    settings = get_settings()
    preferences = get_preferences()
    assignments = get_assignments()
    
    # Format deadline for display
    formatted_deadline = format_deadline(settings['deadline']) if settings.get('deadline') else 'Not set'
        
    # Calculate preference statistics
    shift_stats = {shift['id']: {
        'total_rating': 0,
        'rating_count': 0,
        'avg_rating': 0.0,
        'full_name': f"{shift['day']} ({shift['date']}) {shift['time']}",
        'slots': shift['slots']
    } for shift in SHIFTS}
    
    for user_prefs in preferences.values():
        for shift_id, rating in user_prefs.items():
            if isinstance(rating, int) and shift_id in shift_stats:
                shift_stats[shift_id]['total_rating'] += rating
                shift_stats[shift_id]['rating_count'] += 1
    
    for stats in shift_stats.values():
        if stats['rating_count'] > 0:
            stats['avg_rating'] = round(stats['total_rating'] / stats['rating_count'], 2)
    
    # Compute shift pedigree
    user_shift_pedigree = load_user_shift_pedigree()
    
    # Update the pedigree with current assignments (if any new)
    current_assignments = get_assignments()
    user_shift_pedigree = compute_shift_pedigree(current_assignments, existing_pedigree=user_shift_pedigree)
    
    # Save pedigree and pass it to the template
    save_user_shift_pedigree(user_shift_pedigree)
    
    return render_template(
        'manager_dashboard.html',
        shifts=SHIFTS,
        settings=settings,
        preferences=preferences,
        assignments=assignments,
        shift_stats=shift_stats,
        user_shift_pedigree=user_shift_pedigree,
        formatted_deadline=formatted_deadline
    )

@app.route('/manager/settings', methods=['GET', 'POST'])
def manage_settings():
    if 'username' not in session or not session.get('is_manager'):
        return redirect(url_for('login'))
    
    settings = get_settings()
    error = None
    success = None
    
    if request.method == 'POST':
        try:
            settings['period_label'] = request.form.get('period_label', '').strip() or default_settings['period_label']
            settings['deadline'] = request.form.get('deadline', '').strip()
            settings['is_locked'] = 'is_locked' in request.form
            settings['require_rating'] = 'require_rating' in request.form
            settings['collect_availability'] = 'collect_availability' in request.form
            
            save_settings(settings)
            success = "Settings updated successfully."
        except Exception as e:
            error = f"Error updating settings: {e}"
    
    formatted_deadline = format_deadline(settings['deadline']) if settings.get('deadline') else ''
    
    return render_template(
        'manage_settings.html',
        settings=settings,
        error=error,
        success=success,
        formatted_deadline=formatted_deadline
    )

@app.route('/manager/users', methods=['GET', 'POST'])
def manage_users():
    if 'username' not in session or not session.get('is_manager'):
        return redirect(url_for('login'))
    
    users = load_users()
    error = None
    success = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            new_username = request.form.get('new_username', '').strip()
            new_password = request.form.get('new_password', '').strip()
            is_manager = 'is_manager' in request.form
            is_reporter = 'is_reporter' in request.form
            
            if not new_username or not new_password:
                error = "Username and password are required."
            elif new_username in users:
                error = "User already exists."
            else:
                # Add salt to password
                salt = secrets.token_hex(16)
                salted_password = f"{new_password}{salt}"
                
                users[new_username] = {
                    'password': generate_password_hash(salted_password),
                    'is_manager': is_manager,
                    'is_reporter': is_reporter,
                    'salt': salt  # Store salt in user data
                }
                save_users(users)
                success = "User added successfully."

        elif action == 'delete':
            delete_username = request.form.get('delete_username', '').strip()
            if delete_username == 'manager':
                error = "Cannot delete the default manager account."
            elif delete_username in users:
                users.pop(delete_username)
                save_users(users)
                success = "User deleted successfully."
            else:
                error = "User not found."
        
        elif action == 'reset_password':
            reset_username = request.form.get('reset_username', '').strip()
            new_password = request.form.get('new_password', '').strip()
            
            if not new_password:
                error = "New password is required."
            elif reset_username in users:
                # Generate new salt and update password
                salt = secrets.token_hex(16)
                salted_password = f"{new_password}{salt}"
                
                users[reset_username]['password'] = generate_password_hash(salted_password)
                users[reset_username]['salt'] = salt
                save_users(users)
                success = f"Password for {reset_username} has been reset."
            else:
                error = "User not found."
    
    return render_template('manage_users.html', users=users, error=error, success=success)

@app.route('/employee/dashboard')
def employee_dashboard():
    if 'username' not in session or session.get('is_manager'):
        return redirect(url_for('login'))
    
    settings = get_settings()
    preferences = get_preferences()
    assignments = get_assignments()
    username = session['username']
    
    user_prefs = preferences.get(username, {})
    user_assignments = assignments.get(username, [])
    
    # Check if deadline has passed
    deadline = get_naive_deadline(settings)
    is_locked = settings.get('is_locked', False) or datetime.now() > deadline
    
    # Format deadline for display
    formatted_deadline = format_deadline(settings['deadline']) if settings.get('deadline') else 'Not set'
    
    return render_template('employee_dashboard.html',
                         username=username,
                         shifts=SHIFTS,
                         preferences=user_prefs,
                         assignments=user_assignments,
                         deadline=formatted_deadline,
                         is_locked=is_locked)

@app.route('/reporter/dashboard')
def reporter_dashboard():
    if 'username' not in session or not session.get('is_reporter'):
        return redirect(url_for('login'))

    settings = get_settings()
    preferences = get_preferences()
    assignments = get_assignments()
    username = session['username']

    user_prefs = preferences.get(username, {})
    user_assignments = assignments.get(username, [])

    # Format deadline for display
    formatted_deadline = format_deadline(settings['deadline']) if settings.get('deadline') else 'Not set'

    # Fetch the full user shift pedigree
    user_shift_pedigree = load_user_shift_pedigree()

    # If current user doesn't have a history yet, initialize it
    if username not in user_shift_pedigree:
        user_shift_pedigree[username] = []

    # Get assigned shift counts from assignments metadata
    assigned_shift_counts = {}
    if os.path.exists(ASSIGNMENTS_FILE):
        try:
            with open(ASSIGNMENTS_FILE, 'r') as f:
                data = json.load(f)
                if 'metadata' in data and 'assigned_shift_counts' in data['metadata']:
                    assigned_shift_counts = data['metadata']['assigned_shift_counts']
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading assignments metadata: {e}")

    user_assigned_shifts = assigned_shift_counts.get(username, [])

    # Generate and display status message for the user
    status_messages = []
    today = datetime.today().date()
    future_additional_shifts = []

    for shift in user_assigned_shifts:
        try:
            shift_date = datetime.strptime(shift['date'], '%Y-%m-%d').date()
            if shift_date >= today:
                # Future or today's shift
                future_additional_shifts.append(shift)
        except ValueError as e:
            print(f"Error parsing date in user_assigned_shifts: {e}")
            continue

    if future_additional_shifts:
        status_messages.append("You have the following shift(s) assigned in the upcoming weekends beyond the current period:")
        for shift in future_additional_shifts:
            status_messages.append(f"- {shift['day']} ({shift['date']}) {shift['time']}")

    # Calculate overall assignment count for reporter
    total_assigned_shifts = len(user_assigned_shifts)
    if total_assigned_shifts == 0:
        status_messages.append("You have no additional shift assignments beyond the current period.")
    else:
        status_messages.append(f"You have a total of {total_assigned_shifts} shift(s) assigned in the next six months.")

    # If user has history (shift pedigree), add summary
    if user_shift_pedigree.get(username):
        total_past_shifts = len(user_shift_pedigree[username])
        status_messages.append(f"You have previously worked {total_past_shifts} weekend shift(s) in the last six months.")

    return render_template(
        'reporter_dashboard.html',
        username=username,
        shifts=SHIFTS,
        preferences=user_prefs,
        assignments=user_assignments,
        deadline=formatted_deadline,
        status_messages=status_messages,
        user_shift_pedigree=user_shift_pedigree
    )

@app.route('/employee/preferences', methods=['GET', 'POST'])
def manage_preferences():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    username = session['username']
    preferences = get_preferences()
    settings = get_settings()
    
    # Check if locked
    deadline = get_naive_deadline(settings)
    is_locked = settings.get('is_locked', False) or datetime.now() > deadline
    
    if request.method == 'POST':
        if is_locked and not session.get('is_manager'):
            return jsonify({'error': 'Preferences are locked'}), 403
        
        try:
            ratings = request.json.get('ratings', {})
            print(f"Received ratings for {username}: {ratings}")
            
            # Ensure user has a preferences entry
            if username not in preferences:
                preferences[username] = {}
            
            for shift_id_str, rating in ratings.items():
                try:
                    shift_id = int(shift_id_str)
                    if rating is None:
                        # Remove rating if None
                        preferences[username].pop(str(shift_id), None)
                    elif isinstance(rating, int) and -1 <= rating <= 3:
                        preferences[username][str(shift_id)] = rating
                except ValueError:
                    print(f"Invalid shift_id: {shift_id_str}")
                    continue
            
            save_preferences_to_file(preferences)
            return jsonify({'success': True})
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return jsonify({'error': f"Error saving preferences: {e}"}), 400
    
    # GET request - return current preferences and settings
    user_prefs = preferences.get(username, {})
    
    # Prepare shift data with user ratings
    shift_data = []
    for shift in SHIFTS:
        shift_id = str(shift['id'])
        shift_info = shift.copy()
        shift_info['rating'] = user_prefs.get(shift_id, None)
        shift_data.append(shift_info)
    
    return jsonify({
        'shifts': shift_data,
        'settings': settings,
        'is_locked': is_locked
    })

@app.route('/manager/assign', methods=['POST'])
def assign_shifts():
    if 'username' not in session or not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    preferences = get_preferences()
    assignments = {}
    shift_slots = {shift['id']: shift['slots'] for shift in SHIFTS}
    unfilled_shifts = []
    
    # Prepare user shift pedigree for adding new assignments
    user_shift_pedigree = load_user_shift_pedigree()
    
    # Initialize a dictionary to track assigned shift counts per user
    assigned_shift_counts = {user: [] for user in preferences.keys()}
    
    # Compute available users (who have worked shifts in last 6 months)
    eligible_users = get_eligible_users_for_shift(user_shift_pedigree)
    
    # Check if any eligible users exist for assignment
    if not eligible_users:
        return jsonify({'error': 'No eligible users available for shift assignments based on the last 6 months.'}), 400
    
    for shift in SHIFTS:
        shift_id = shift['id']
        available_users = []
        
        # First pass: filter only users who prefer this shift (rating 2 or 3) and are eligible
        for user, prefs in preferences.items():
            rating = prefs.get(str(shift_id), 0)
            if rating >= 2 and shift_id not in assignments.get(user, []) and user in eligible_users:
                available_users.append((user, rating))
        
        # Sort users by rating (descending) and a random tie-breaker
        random.shuffle(available_users)
        sorted_users = sorted(available_users, key=lambda x: x[1], reverse=True)
        
        # Assign shift based on availability and rating
        assigned_count = 0
        for user, rating in sorted_users:
            if assigned_count >= shift_slots[shift_id]:
                break
            
            assignments.setdefault(user, []).append({
                'id': shift_id,
                'date': shift['date'],
                'day': shift['day'],
                'time': shift['time'],
                'week': shift['week'],
                'rating': rating
            })
            assigned_shift_counts[user].append({
                'id': shift['id'],
                'date': shift['date'],
                'day': shift['day'],
                'time': shift['time'],
                'week': shift['week'],
                'rating': rating
            })
            
            # Update user shift pedigree
            user_shift_pedigree.setdefault(user, []).append({
                'date': shift['date'],
                'day': shift['day'],
                'time': shift['time'],
                'week': shift['week']
            })
            assigned_count += 1
        
        # Track unfilled shifts
        if assigned_count < shift_slots[shift_id]:
            unfilled_shifts.append({
                'id': shift['id'],
                'date': shift['date'],
                'day': shift['day'],
                'time': shift['time'],
                'required_slots': shift_slots[shift_id],
                'filled_slots': assigned_count
            })
    
    # Store assignments, user shift pedigree, and metadata (including assigned_shift_counts) in file
    save_assignments(assignments, assigned_shift_counts=assigned_shift_counts, coverage_gaps=unfilled_shifts)
    save_user_shift_pedigree(user_shift_pedigree)
    
    return jsonify({'assignments': assignments, 'unfilled_shifts': unfilled_shifts})

@app.route('/manager/assignments')
def view_assignments():
    if 'username' not in session or not session.get('is_manager'):
        return redirect(url_for('login'))
    
    assignments = get_assignments()
    return render_template('view_assignments.html', assignments=assignments, shifts=SHIFTS)

@app.route('/manager/export', methods=['GET'])
def export_assignments():
    if 'username' not in session or not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        assignments = get_assignments()
        export_file_path = os.path.join(PARENT_DIR, 'weekend_assignments_export.json')
        
        with open(export_file_path, 'w') as f:
            json.dump(assignments, f, indent=4)
        
        return send_file(export_file_path, as_attachment=True)
    except Exception as e:
        print(f"Error exporting assignments: {e}")
        return jsonify({'error': f"Error exporting assignments: {e}"}), 500

@app.route('/manager/import', methods=['POST'])
def import_assignments():
    if 'username' not in session or not session.get('is_manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    
    try:
        data = json.load(file)
        if 'assignments' in data:
            save_assignments(data['assignments'])
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid file format'}), 400
    except Exception as e:
        print(f"Error importing assignments: {e}")
        return jsonify({'error': f"Error importing assignments: {e}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
