# Deploy to Replit - Cloud Hosting Guide

Your app is now ready to deploy to **Replit** - a free cloud platform that makes your app accessible to friends from anywhere on the internet!

## Step-by-Step Deployment

### 1. Create a Replit Account
- Go to https://replit.com
- Sign up (free account)
- Click "Create" or "New Replit"

### 2. Import Your Project

#### Option A: Upload Files (Easiest)
1. On Replit, click **"Import from GitHub"** or **"Create Replit" → "Python"**
2. Choose **"Upload files"** if available
3. Zip your project folder:
   - Right-click on your project folder → "Send to" → "Compressed folder"
   - Name it `athlete-app.zip`
4. Upload the ZIP to Replit
5. Replit will extract and set up automatically

#### Option B: Connect GitHub (Alternative)
1. Push your code to GitHub
2. Go to https://replit.com
3. Click "Import from GitHub"
4. Paste your GitHub repository URL
5. Click "Import"

### 3. Configure Environment Variables
1. In Replit, go to **"Secrets"** (lock icon on the left sidebar)
2. Add the environment variables from your `.env` file:
   ```
   SECRET_KEY=kiara
   FLASK_ENV=production
   DATABASE_URI=sqlite:///sports_management.db
   ```
3. Save each one

### 4. Install Dependencies
- Replit will automatically detect `requirements.txt` and install packages
- If it doesn't auto-install, click "Run" and it will prompt you to install

### 5. Run the App
- Click the **"Run"** button (green play button)
- Watch for the output message with your cloud URL
- You'll see something like: `https://athlete-app-username.replit.dev`

### 6. Share with Friends
- Copy the URL shown in the output
- Send it to your friends
- They can access your app from any device, anywhere!

### Example Output
```
🎯 ATHLETE PERFORMANCE PREDICTOR - REPLIT
======================================================================
🌐 Cloud Access: https://athlete-app-username.replit.dev
📊 Dashboard: https://athlete-app-username.replit.dev/
🏃 Athletes: https://athlete-app-username.replit.dev/athletes
📈 Analytics: https://athlete-app-username.replit.dev/analytics
📅 Events: https://athlete-app-username.replit.dev/events

✅ Share the URL above with your friends!
🚀 Server running on Replit...
```

## Features Available to Your Friends

Your friends can:
- ✅ Create accounts (Signup)
- ✅ Log in with credentials
- ✅ View all athletes
- ✅ See analytics and performance metrics
- ✅ View events
- ✅ Toggle dark/light theme
- ✅ Use on mobile devices (fully responsive)

## Important Notes

### Database
- SQLite database is stored on Replit's filesystem
- Data persists between restarts
- **Backup your data regularly** if you want to keep it

### Always Free
- Replit free tier includes:
  - Unlimited projects
  - Unlimited storage
  - Always-on hosting (app doesn't sleep)
  - Perfect for testing with friends

### Stopping the App
- Click "Stop" button in Replit to stop the server
- Click "Run" to restart

### Common Issues

**Issue: "Port already in use"**
- Replit automatically assigns a PORT environment variable
- The updated `run.py` handles this automatically

**Issue: "Database not found"**
- This is normal on first run if using SQLite
- The app creates the database automatically
- Demo data is initialized on first run

**Issue: Imports fail after running**
- Click "Run" again - dependencies are still installing
- Wait a few seconds and refresh the page

## Next Steps

1. **Test locally first** (optional):
   ```
   python run.py
   ```

2. **Deploy to Replit** using the steps above

3. **Share the Replit URL** with your friends

4. **Monitor the app** - Replit shows live logs and errors

## Your App is Now Global!

Your friends can test your Athlete Performance Predictor app from anywhere in the world, on any device. No network configuration needed - just a simple URL!

---

**Need help?** Check Replit's documentation: https://docs.replit.com
