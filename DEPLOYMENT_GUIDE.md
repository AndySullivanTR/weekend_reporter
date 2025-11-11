# Deployment Guide for Render.com

## Step-by-Step Instructions

### 1. Prepare Your GitHub Repository

First, you need to upload these files to GitHub.

**Option A: Using GitHub Desktop (Easiest)**
1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Open GitHub Desktop
3. Click "File" → "New Repository"
   - Name: `weekend-reporter-shifts`
   - Local Path: Choose the folder containing these files
4. Click "Create Repository"
5. Click "Publish repository" (top right)
6. Uncheck "Keep this code private" or leave checked (your choice)
7. Click "Publish Repository"

**Option B: Using Command Line**
```bash
# Navigate to your project folder
cd /path/to/weekend-reporter-shifts

# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: Weekend reporter shifts scheduler"

# Create GitHub repo at github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/weekend-reporter-shifts.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Render

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Click "Get Started" or "Sign Up"
   - Sign up with your GitHub account (recommended)

2. **Create New Web Service**
   - Click "New +" button (top right)
   - Select "Web Service"

3. **Connect Your Repository**
   - If first time: Click "Connect GitHub" and authorize Render
   - Find and select your `weekend-reporter-shifts` repository
   - Click "Connect"

4. **Configure Service**
   
   Render should auto-detect settings from `render.yaml`, but verify:
   
   - **Name**: `weekend-reporter-shifts` (or your preference)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

5. **Deploy**
   - Click "Create Web Service"
   - Wait 2-4 minutes for deployment
   - You'll see build logs in real-time

6. **Access Your App**
   - Once deployed, you'll get a URL like: `https://weekend-reporter-shifts.onrender.com`
   - Click the URL to test your application
   - Login with: `admin` / `admin123`

### 3. Share With Your Team

Send an email to reporters with:

```
Subject: Weekend Reporter Shift Preferences - Action Required

Hi team,

Please submit your weekend shift preferences by [DEADLINE] using this link:
https://YOUR-APP-NAME.onrender.com

Login Instructions:
- Username: [your assigned username, e.g., reporter1]
- Password: password

What to do:
1. Rank your general shift type preferences (Saturday, Sunday morning, Sunday evening)
2. Select your top 10 preferred specific shifts
3. Select your bottom 5 least wanted shifts
4. Click Submit

You'll be assigned 1 shift over the 20-week period. Shifts on the same weekend won't be assigned together.

Questions? Contact [YOUR NAME]
```

### 4. Managing the Schedule

**As Manager:**

1. **Monitor Submissions**
   - Log in regularly to see who has submitted
   - URL: `https://YOUR-APP.onrender.com`
   - Credentials: `admin` / `admin123`

2. **Set Deadline**
   - Use the deadline picker on manager dashboard
   - Click "Update Deadline"

3. **Run Allocation**
   - Once all 30 reporters have submitted
   - Click "Run Allocation Algorithm"
   - Check browser console (F12) for detailed logs

4. **Export Results**
   - Click "Export to Excel" for distribution
   - Click "Download Backup" to save JSON data

5. **Important: Download Backup Before App Sleeps**
   - Free tier apps sleep after 15 minutes of inactivity
   - Data persists during sleep
   - BUT: Data is ephemeral and could be lost on restart
   - Always download backup after allocation!

### 5. Troubleshooting

**Problem: App shows "Not Found" or error page**
- Solution: Check Render dashboard for build errors
- Look at "Logs" tab for error messages

**Problem: App is slow to load**
- Cause: Free tier apps "sleep" after 15 min inactivity
- Solution: First request takes ~30 seconds to wake up
- This is normal on free tier

**Problem: Data disappeared**
- Cause: Render free tier uses ephemeral storage
- Solution: Use "Download Backup" button regularly
- Consider upgrading to paid tier with persistent disk

**Problem: Can't connect GitHub repository**
- Solution: Make sure repository is not private, or grant Render access to private repos

**Problem: Build fails**
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Look at build logs in Render dashboard

### 6. Updating the App

When you need to make changes:

1. **Edit files locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. **Render auto-deploys** - Your app will automatically redeploy with changes

### 7. Cost Considerations

**Free Tier Limits:**
- 750 hours/month runtime (plenty for this use)
- Apps sleep after 15 min inactivity
- Ephemeral storage (data resets on restart)
- HTTP/2 and HTTPS included

**When to Upgrade:**
- Need persistent storage: $7/month (includes PostgreSQL)
- Need always-on service: $7/month
- High traffic: May need more resources

For a 1-2 week preference collection period, **free tier is perfect**.

### 8. Best Practices

**Before Collection Period:**
- Test the app thoroughly
- Set the deadline date
- Send clear instructions to reporters

**During Collection Period:**
- Check dashboard daily for submissions
- Download backup every few days
- Keep the app active (visit URL daily to prevent sleep)

**After Allocation:**
- Export Excel immediately
- Download JSON backup
- Distribute schedule to team
- Can delete Render service or let it sleep

### 9. Security Notes

**Current Setup:**
- Simple username/password authentication
- Fixed passwords for reporters (`password`)
- Admin password (`admin123`)
- HTTPS encryption by default

**For Production:**
- Change passwords in `app.py` before deploying
- Consider more secure password generation
- Or keep current setup if your team is comfortable

### 10. Getting Help

**Render Support:**
- Documentation: [docs.render.com](https://docs.render.com)
- Community: [community.render.com](https://community.render.com)
- Status: [status.render.com](https://status.render.com)

**App Issues:**
- Check Render logs first
- Review browser console (F12 → Console tab)
- Check data files are being created in `/data` directory

---

## Quick Reference

**URLs:**
- Your app: `https://YOUR-APP-NAME.onrender.com`
- Render dashboard: `https://dashboard.render.com`
- Your GitHub repo: `https://github.com/YOUR-USERNAME/weekend-reporter-shifts`

**Credentials:**
- Manager: `admin` / `admin123`
- Reporters: `reporter1-30` / `password`

**Key Actions:**
- Download backup: Manager Dashboard → "Download Backup"
- Export Excel: Manager Dashboard → "Export to Excel"
- Update code: Push to GitHub, auto-deploys
- View logs: Render Dashboard → Your Service → "Logs"

**Support Contact:**
- Render support: support@render.com
- Your IT department for internal hosting questions
