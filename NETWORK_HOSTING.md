# Network Hosting Guide - Athlete Performance Predictor

This guide explains how to host the APP on your local network so your friends can access it from their devices.

## Quick Start (Windows)

### Step 1: Start the Application
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   ```
   cd "path\to\final year project 2"
   ```
3. Run the Flask server:
   ```
   python run.py
   ```

### Step 2: Get Your Network IP Address

When the server starts, you'll see output like:
```
==============================================
🎯 ATHLETE PERFORMANCE PREDICTOR
==============================================

📱 Local Access: http://localhost:8000
🌐 Network Access: http://192.168.1.100:8000
...
```

The **Network Access** URL is what you share with your friends. Example: `http://192.168.1.100:8000`

## How to Share with Friends

### Option 1: Direct URL (Easiest)
1. Share the network URL shown when you start the server
2. Friends open this URL in their browser
3. They can login with demo credentials:
   - Username: `admin`
   - Password: `admin123`
4. Or create their own account using the **Sign Up** tab

### Option 2: Find Your IP Address Manually

**Windows:**
1. Open Command Prompt
2. Type: `ipconfig`
3. Look for "IPv4 Address" under your network adapter (usually looks like `192.168.x.x`)
4. Share: `http://YOUR_IP:8000`

**Mac/Linux:**
1. Open Terminal
2. Type: `ifconfig` or `hostname -I`
3. Find your local IP address
4. Share: `http://YOUR_IP:8000`

## Accessing from Different Devices

### From Another Computer on Same Network
- Enter the network URL in any browser: `http://192.168.1.100:8000`

### From a Mobile Phone on Same Network
- Connect phone to the same WiFi network
- Open browser and enter: `http://192.168.1.100:8000`
- The app automatically adapts to mobile screens!

### From a Tablet on Same Network
- Same as mobile phone - will show optimized tablet layout

## Port Configuration

By default, the app runs on port **8000**. You can change it:

**Windows Command Prompt:**
```
set PORT=3000
python run.py
```

**Windows PowerShell:**
```
$env:PORT=3000
python run.py
```

**Mac/Linux Terminal:**
```
PORT=3000 python run.py
```

## Firewall Settings

If friends can't access the app even with the correct URL, your firewall might be blocking it:

**Windows Firewall:**
1. Go to Settings → Privacy & Security → Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings"
4. Click "Allow another app"
5. Browse and select `python.exe` from your Python installation
6. Click "Add"
7. Click "OK"

## Available Features

Once connected, users can:

### 🔐 Authentication
- **Login** with demo credentials (admin/admin123)
- **Sign Up** to create their own account
- Secure password storage with encryption

### 🏃 Athletes Management
- View all athletes and their performance scores
- Add new athletes
- View detailed athlete information
- Delete athletes (demo only)
- Search athletes

### 📊 Analytics
- View performance distributions
- Analyze performance by sport
- Check injury risk assessments
- View key statistics (total athletes, high-risk injuries, etc.)

### 📅 Events
- Create and manage events
- View event details and locations
- Add athletes to events
- Filter events by type

### 🌙 Dark Mode
- Toggle between light and dark themes
- Settings automatically saved

### 📱 Responsive Design
- Desktop optimized interface
- Tablet-friendly layout
- Mobile-first navigation with bottom nav bar
- Touch-friendly buttons and controls

## Troubleshooting

### "Connection refused" or "Can't reach server"
- Make sure the Flask server is still running
- Check the IP address is correct
- Ensure both devices are on the same network/WiFi

### "Connection timed out"
- Try `http://localhost:8000` if on the same computer
- Check Windows Firewall settings (see Firewall Settings above)
- Try disabling antivirus temporarily to test

### App shows but styling is broken
- Refresh the page (F5 or Cmd+R)
- Clear browser cache (Ctrl+Shift+Delete)
- Try a different browser

### "Port already in use" error
- Another app is using port 8000
- Change the PORT as shown above
- Or stop the other app using the port

## Database

- The app uses SQLite (local file database)
- Located at: `instance/database.db`
- No setup required - created automatically
- Supports concurrent access from multiple users

## Performance Tips

- Keep the server computer connected to the network
- Don't put the server computer to sleep while hosting
- Keep browser tabs < 10 for smooth performance
- Refresh if experiencing slowdowns (server might need memory)

## Security Notes

⚠️ **This setup is for LOCAL NETWORK TESTING ONLY**

For public deployment, you should:
- Use HTTPS instead of HTTP
- Set strong passwords
- Use a production WSGI server (Gunicorn, Waitress)
- Host on a dedicated server
- Add proper authentication/authorization
- Enable CORS properly
- Set up rate limiting

## Need Help?

Check the main README.md for:
- Detailed feature descriptions
- Installation instructions
- API documentation
- Development guidelines

---

**Happy Testing! 🚀**
