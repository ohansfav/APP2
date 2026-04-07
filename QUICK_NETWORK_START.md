# 🚀 APP Network Hosting - Quick Start

## Start the App for Network Access

### Step 1: Run the Server
```bash
cd "path/to/final year project 2"
python run.py
```

### Step 2: Share the URL
Look for this in the console output:
```
🌐 Network Access: http://192.168.1.100:8000
```

Copy this URL and send to your friends! ✅

## What Your Friends Can Do

1. **Login or Sign Up**
   - Demo login: `admin` / `admin123`
   - Or create account with email & password

2. **Manage Athletes**
   - View all athletes with performance scores
   - Add new athletes
   - Delete athletes
   - Search athletes

3. **Analytics Dashboard**
   - Performance distribution charts
   - Athletes by sport breakdown
   - Injury risk assessments
   - Key statistics

4. **Manage Events**
   - Create events
   - Assign athletes to events
   - View event details

5. **Dark Mode**
   - Toggle anytime with moon/sun icon

## Mobile-Ready
✅ Fully responsive on phones & tablets
✅ Bottom navigation on mobile screens
✅ Touch-friendly interface
✅ No content overlap with nav bar

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Friends can't access | Check URL is correct IP (not localhost) |
| Port in use | `set PORT=3000` then `python run.py` |
| Firewall blocks | Add python.exe to Windows Firewall exceptions |
| Styling looks broken | Refresh browser (Ctrl+F5) |

## Important Notes

- Keep server computer awake while hosting
- All devices must be on same network/WiFi
- SQLite database is local (created automatically)
- Perfect for testing with small groups!

📖 Full guide: See NETWORK_HOSTING.md
