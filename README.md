# Weekend Reporter Shifts Scheduler

A Flask web application for managing weekend shift scheduling with preference-based allocation.

## Features

- **Reporter Interface**: Reporters can rank their top 10 preferred shifts and bottom 5 least wanted shifts
- **General Shift Preferences**: Rank shift types (Saturday 11-7, Sunday 8-4, Sunday 3-10)
- **Fair Allocation Algorithm**: Two-phase allocation ensuring equity
  - Phase 1: Random order, get everyone their first shift
  - Phase 2: Compensatory order based on Phase 1 satisfaction
- **Manager Dashboard**: View submissions, run allocation, export to Excel
- **60 Shifts**: 20 weekends × 3 shifts per weekend (Dec 13, 2025 - Apr 26, 2026)
- **30 Reporters**: Pre-configured with reporter1 through reporter30

## Quick Start

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access at `http://localhost:5000`

### Login Credentials

**Manager:**
- Username: `admin`
- Password: `admin123`

**Reporters:**
- Username: `reporter1` through `reporter30`
- Password: `password`

## Deployment to Render.com

### Prerequisites
- GitHub account
- Render.com account (free)

### Steps

1. **Create a GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment

3. **Access your application**
   - Render will provide a URL like: `https://weekend-reporter-shifts.onrender.com`
   - Share this URL with reporters

## File Structure

```
.
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment configuration
├── templates/
│   ├── login.html             # Login page
│   ├── reporter_dashboard.html # Reporter shift selection interface
│   └── manager_dashboard.html  # Manager control panel
└── data/                       # Auto-created directory for JSON storage
    ├── reporters.json         # Reporter accounts
    ├── preferences.json       # Reporter preferences
    ├── settings.json          # Deadline and lock status
    └── assignments.json       # Final shift assignments
```

## Usage Workflow

### For Reporters

1. **Login** with your credentials
2. **Rank general shift preferences** (1-3)
3. **Select shifts**:
   - Click shifts to add to "Top 10" (first 12 clicks)
   - Continue clicking to add to "Bottom 5" (next 6 clicks)
   - Click again to remove a selection
4. **Submit preferences** before the deadline
5. **View assigned shifts** after manager runs allocation

### For Manager

1. **Login** with admin credentials
2. **Monitor submissions** - See who has submitted preferences
3. **Set/update deadline** for submissions
4. **Run allocation algorithm** once all reporters have submitted
5. **Export to Excel** for distribution
6. **Download backup** (JSON) for data persistence

## Allocation Algorithm

The system uses a two-phase balanced allocation approach:

### Phase 1: First Shift
- Process reporters in random order (seed=42 for reproducibility)
- Try to assign from reporter's top 10 preferences
- Skip if: shift full, would create same-weekend conflict
- Fallback: Use shift type preference for non-bottom-6 shifts

### Phase 2: Second Shift
- Sort reporters by Phase 1 satisfaction (worst assignments first)
- Randomize within same satisfaction level
- Same logic as Phase 1
- Ensures reporters who got poor first shifts get priority for second

### Constraints
- Each reporter gets exactly 1 shift over 20 weeks
- No reporter gets their shift on the same weekend
- Bottom 5 preferences avoided unless no other option
- All 60 shifts must be filled (60 slots ÷ 30 reporters × 2 = perfect match)

## Data Persistence

⚠️ **Important**: Render's free tier uses ephemeral storage, meaning data resets on app restart.

### Backup Strategy

1. **Regular backups**: Use "Download Backup" button to save JSON data
2. **Before shutdown**: Export Excel and download backup
3. **After restart**: You'll need to re-import data or restart preference collection

### For Production Use

Consider upgrading to:
- Render PostgreSQL database (free tier available)
- Persistent disk storage
- Or export data before each shutdown

## Customization

### Change Reporter List

Edit `init_data_files()` in `app.py`:

```python
# Replace reporter names
reporter_names = ['Alice', 'Bob', 'Charlie', ...]
for name in reporter_names:
    reporters[name.lower()] = {
        'name': name,
        'is_manager': False,
        'password': generate_password_hash('password')
    }
```

### Change Schedule Dates

Edit `generate_shifts()` in `app.py`:

```python
start_date = datetime(2026, 1, 3)  # Change start date
for week in range(20):              # Change number of weekends
    ...
```

### Modify Shift Times

Edit the shift generation in `generate_shifts()`:

```python
# Saturday
shifts.append({
    'time': '11:00 AM - 7:00 PM',  # Change times here
    ...
})
```

## Troubleshooting

### App won't start on Render
- Check build logs for Python version compatibility
- Verify all dependencies are in `requirements.txt`
- Ensure `gunicorn` is installed

### Data disappears after restart
- Expected behavior on free tier
- Download regular backups
- Consider adding PostgreSQL database

### Allocation fails
- Verify all reporters submitted complete preferences (10 top + 5 bottom)
- Check console logs for specific error messages
- Ensure no conflicts in shift availability

## API Endpoints

### Authentication Required Endpoints

All endpoints require an active session (login required). Manager endpoints require `is_manager: true`.

#### Public Endpoints

**GET `/`**
- Redirects to appropriate dashboard based on login status
- No authentication required initially, redirects to `/login` if not authenticated

**GET `/login`**
- Returns login page
- POST: Authenticate user with username/password
  ```json
  {
    "username": "reporter1",
    "password": "password"
  }
  ```

**GET `/logout`**
- Clears session and redirects to login

**GET `/initialize-system`**
- Public endpoint (no auth required)
- Initializes reporters.json from embedded REPORTER_CREDENTIALS
- Useful for first-time setup or emergency recovery
- Response: `{ "success": true, "total_accounts": 124, "message": "..." }`

#### Reporter Endpoints

**GET `/reporter/dashboard`**
- Returns reporter dashboard HTML
- Authentication: Reporter account required

**GET `/api/preferences`**
- Returns preferences for the logged-in reporter
- Response: `{ "username": { "top_10": [...], "bottom_5": [...], "shift_type_pref": {...} } }`

**POST `/api/preferences`**
- Submit or update reporter preferences
- Body:
  ```json
  {
    "top_10": [0, 5, 12, 18, 24, 30, 36, 42, 48, 54],
    "bottom_5": [3, 9, 15, 21, 27],
    "shift_type_pref": {
      "saturday": "1",
      "sunday_morning": "2",
      "sunday_evening": "3"
    }
  }
  ```
- Creates automatic backup after submission
- Returns: `{ "success": true }`

**POST `/api/change-password`**
- Change password for logged-in user (reporter or manager)
- Body:
  ```json
  {
    "current_password": "oldpass",
    "new_password": "newpass"
  }
  ```
- Min password length: 6 characters
- Returns: `{ "success": true, "message": "Password changed successfully" }`

#### Manager Endpoints

**GET `/manager/dashboard`**
- Returns manager dashboard HTML
- Authentication: Manager account required

**GET `/api/preferences`** (Manager view)
- Returns ALL reporter preferences
- Response: `{ "reporter1": {...}, "reporter2": {...}, ... }`

**GET `/api/settings`**
- Returns current settings
- Response: `{ "deadline": "2025-12-01T00:00:00Z", "is_locked": false }`

**POST `/api/settings`**
- Update deadline or lock status
- Body (optional fields):
  ```json
  {
    "deadline": "2025-12-15T23:59:59Z",
    "is_locked": true
  }
  ```

**POST `/api/allocate`**
- Run shift allocation algorithm
- Creates backup before allocation
- Automatically locks preferences
- Returns:
  ```json
  {
    "success": true,
    "assignments": { "reporter1": [5, 42], ... },
    "shift_assignments": { "0": ["reporter3"], ... },
    "warnings": ["Reporter X has incomplete preferences"],
    "reporters_with_prefs": 120,
    "reporters_without_prefs": 3
  }
  ```

**GET `/api/export-excel`**
- Download schedule as Excel file (.xlsx)
- Includes:
  - Full shift schedule with assigned reporters
  - Preference rankings for each assignment
  - Status (filled/vacant)
  - Reporter summary table
- Returns: Excel file download

**GET `/api/backup`**
- Download complete system backup as JSON
- Includes all data files: reporters, preferences, settings, assignments
- Filename: `backup_YYYYMMDD_HHMMSS.json`
- Returns: JSON file download

**POST `/api/populate-test-data`**
- Generate random preferences for all reporters (TESTING ONLY)
- Useful for development/testing
- Returns: `{ "success": true, "message": "Populated random preferences for N reporters" }`

**POST `/api/create-backup`**
- Manually trigger an automatic backup
- Saves to `data/backups/auto_backup_{timestamp}.json`
- Returns: `{ "success": true, "message": "Backup created successfully" }`

**GET `/api/list-backups`**
- List last 30 automatic backups
- Returns:
  ```json
  {
    "success": true,
    "backups": [
      {
        "filename": "auto_backup_20251201_143022.json",
        "size": 45678,
        "created": "2025-12-01T14:30:22"
      }
    ],
    "total": 30
  }
  ```

#### Emergency/Administrative Endpoints

**POST `/api/reload-reporters-from-csv`** ⚠️
- **DANGER**: Resets ALL reporter accounts to embedded credentials
- Overwrites reporters.json completely
- **Wipes all password changes**
- Preserves preferences.json (but orphans may exist)
- Use only for: Initial setup, corrupted data recovery
- Not accessible from UI (removed for safety)
- Returns: `{ "success": true, "message": "Successfully reloaded N reporter accounts", "total_accounts": 124 }`

**POST `/api/reset-data`** ⚠️
- **DANGER**: Clears ALL preferences and assignments
- Creates backup before reset
- Unlocks preferences
- Use only for: Starting fresh, testing
- Returns: `{ "success": true, "message": "All preferences and assignments cleared..." }`

### Response Status Codes

- `200`: Success
- `401`: Unauthorized (invalid credentials)
- `403`: Forbidden (insufficient permissions, or preferences locked)
- `404`: Not found
- `500`: Server error

### Notes on Data Persistence

- All data stored in `data/*.json` files
- On Render.com with persistent disk at `/opt/render/project/src/data`, data survives deployments
- Automatic backups created:
  - After each preference submission
  - Before allocation
  - Manual trigger via `/api/create-backup`
- Last 30 backups retained automatically

## Support

For issues or questions:
1. Check Render deployment logs
2. Review browser console for JavaScript errors
3. Verify JSON data files are properly formatted

## License

Internal use only - Reuters News
