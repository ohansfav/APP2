# 🧪 TESTING GUIDE - Verify All New Features

This guide helps you test all the new features added to the Intelligent Sports Management System.

---

## Prerequisites

Make sure the system is running:

```bash
python run.py
```

You should see:
```
====================================================
🎯 INTELLIGENT SPORTS MANAGEMENT SYSTEM
====================================================
📊 Dashboard: http://localhost:5000
🚀 Server running in offline-first mode...
```

Then open: **http://localhost:5000** in your browser

---

## Test 1: Data Validation ✅

### A. Try Creating Athlete with Invalid Age

**How to Test:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Run this JavaScript:

```javascript
fetch('/api/athletes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'John Doe',
        registration_number: 'TEST001',
        age: 60,  // ❌ Invalid: > 50
        sport: 'Football',
        training_hours_pw: 15,
        sleep_hours: 7
    })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Expected Result:**
```json
{
    "error": "Age must be between 12 and 50 years."
}
```

✅ **If you see this message, validation is working!**

---

### B. Try Invalid Training Hours

**JavaScript:**
```javascript
fetch('/api/athletes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'Jane Smith',
        registration_number: 'TEST002',
        age: 22,
        sport: 'Basketball',
        training_hours_pw: 30,  // ❌ Invalid: > 24
        sleep_hours: 7
    })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Expected Result:**
```
"Training hours per week must be between 0 and 24."
```

✅ **Validation working!**

---

### C. Try Invalid Sleep Hours

```javascript
fetch('/api/athletes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'Mike Johnson',
        registration_number: 'TEST003',
        age: 25,
        sport: 'Soccer',
        training_hours_pw: 15,
        sleep_hours: 30  // ❌ Invalid: > 24
    })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Expected Result:**
```
"Sleep hours per day must be between 0 and 24."
```

---

### D. Try Duplicate Registration Number

**First, create one athlete:**
```javascript
fetch('/api/athletes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'First Athlete',
        registration_number: 'UNIQUE001',
        age: 22,
        sport: 'Football',
        training_hours_pw: 15,
        sleep_hours: 8
    })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Then try creating another with SAME registration number:**
```javascript
fetch('/api/athletes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'Second Athlete',
        registration_number: 'UNIQUE001',  // ❌ Duplicate!
        age: 23,
        sport: 'Basketball',
        training_hours_pw: 12,
        sleep_hours: 7
    })
})
.then(r => r.json())
.then(data => console.log(data))
```

**Expected Result:**
```
"Registration number already exists. Must be unique."
```

✅ **Uniqueness validation working!**

---

## Test 2: Enhanced Recommendations ✅

### Test HIGH INJURY RISK Recommendations

**Run this:**
```javascript
fetch('/api/predict/injury-risk', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        athlete_id: 1,
        training_hours_pw: 22,     // Very high training
        prev_injuries: 3,          // Multiple previous injuries
        sleep_hours: 4             // Very low sleep
    })
})
.then(r => r.json())
.then(data => {
    console.log('Risk Category:', data.risk_category);
    console.log('Risk Score:', data.injury_risk_score);
    console.log('Recommendation:');
    console.log(data.recommendation);
})
```

**Expected Output:**
```
Risk Category: high

Recommendation:
  Summary: "🚨 High Injury Risk - Immediate Intervention Required"
  Tips:
    1. Reduce training intensity by 40% immediately; focus on technique...
    2. Implement mandatory 10+ hours of sleep per night for 1 week...
    3. Conduct full physical assessment; consider temporary training suspension...
```

✅ **Enhanced recommendations with 3 specific tips!**

---

### Test MEDIUM INJURY RISK Recommendations

```javascript
fetch('/api/predict/injury-risk', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        athlete_id: 2,
        training_hours_pw: 15,     // Moderate training
        prev_injuries: 1,          // One previous injury
        sleep_hours: 6             // Low sleep
    })
})
.then(r => r.json())
.then(data => console.log(data.recommendation))
```

**Expected Output Shows:**
```
Summary: "⚠️ Moderate Injury Risk - Increase Preventive Measures"
Tips:
  1. Reduce high-intensity drills by 20% for the next 2 weeks...
  2. Focus on mobility and stretching routines: 15-20 minutes daily...
  3. Ensure 8+ hours of sleep for the next 3 consecutive days...
```

---

### Test LOW INJURY RISK Recommendations

```javascript
fetch('/api/predict/injury-risk', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        athlete_id: 3,
        training_hours_pw: 10,     // Healthy training
        prev_injuries: 0,          // No injuries
        sleep_hours: 8             // Good sleep
    })
})
.then(r => r.json())
.then(data => console.log(data.recommendation))
```

**Expected Output Shows:**
```
Summary: "✅ Low Injury Risk - Maintain Current Status"
Tips:
  1. Continue current training regimen with 2-3 rest days per week...
  2. Maintain 7-9 hours of sleep nightly and 2-3 stretching sessions weekly...
  3. Schedule monthly performance assessments...
```

✅ **Different recommendations based on risk level!**

---

## Test 3: CSV Export Feature ✅

### Export Athlete Registry

**Method 1: Click Button on Dashboard**
1. Go to http://localhost:5000
2. Look for blue "Export Data" card
3. Click "Export Athlete Registry" button
4. Check Downloads folder → `athlete_registry_[TIMESTAMP].csv`

**Method 2: Direct URL**
```
Visit: http://localhost:5000/export/athletes
```

**Expected File Contents:**
```csv
ID,Name,Registration Number,Age,Sport,Height (cm),Weight (kg),Performance Score,Training Hours/Week,Sleep Hours/Day,Date Joined
1,Adebayo Oluwaseun,UOD_2024_001,22,Football,180,75,85.5,12,8,2024-03-30
2,Chioma Nwankwo,UOD_2024_002,21,Basketball,175,68,78.3,15,7,2024-03-30
...
```

✅ **CSV export working!**

---

### Export Risk Predictions

1. Go to http://localhost:5000
2. Click "Export Risk Predictions" button
3. Check Downloads → `injury_predictions_[TIMESTAMP].csv`

**Expected File Contents:**
```csv
Athlete ID,Athlete Name,Sport,Training Hours/Week,Previous Injuries,Sleep Hours/Day,Risk Score,Risk Category,Confidence,Assessment Date
1,Adebayo Oluwaseun,Football,12,1,8,0.342,low,0.756,2024-03-30 14:25
2,Chioma Nwankwo,Basketball,15,0,7,0.421,low,0.801,2024-03-30 14:26
...
```

✅ **Export working with actual data!**

---

## Test 4: Mobile Responsiveness ✅

### Test on Different Screen Sizes

**Using Browser DevTools:**

1. Open http://localhost:5000
2. Press `Ctrl+Shift+M` (or right-click → Inspect → Toggle Device Toolbar)
3. Test these resolutions:

**Small Phone (320px):**
- ✓ No horizontal scrolling
- ✓ Navigation menu collapses
- ✓ Buttons stack vertically
- ✓ Cards are single column
- ✓ Font is readable

**Tablet (768px):**
- ✓ Two-column layout for metrics
- ✓ Charts display nicely
- ✓ Tables readable
- ✓ Export buttons in one row

**Desktop (1920px):**
- ✓ Full four-column metrics display
- ✓ Side-by-side charts
- ✓ Full table display

**Try Rotating Phone:**
- Device toolbar → Rotate to landscape
- ✓ Layout adapts to horizontal view
- ✓ Still readable and usable

✅ **Mobile responsiveness working across all screen sizes!**

---

## Test 5: .env Configuration ✅

### Verify .env File Exists

**Check that `.env` file exists:**
```bash
# On Windows (PowerShell):
ls .env

# On Mac/Linux:
ls .env
```

**Should show:**
```
.env
```

### Verify Configuration is Loaded

**Method 1: Check in Python**
```python
from app import create_app
app = create_app()
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Secret Key is set:", bool(app.config['SECRET_KEY']))
```

**Expected Output:**
```
Database URI: sqlite:///sports_management.db
Secret Key is set: True
```

✅ **.env configuration loaded successfully!**

---

## Test 6: Dashboard Export Buttons ✅

### Verify Buttons are Visible

1. Go to http://localhost:5000
2. Look at the top of the dashboard
3. You should see a blue card with:
   - Title: "🔽 Export Data"
   - Description: "Download athlete registry and prediction results..."
   - Two buttons:
     - "👥 Export Athlete Registry"
     - "❤️ Export Risk Predictions"

### Verify Buttons Work

1. Click "Export Athlete Registry"
2. File should download to your Downloads folder
3. Filename format: `athlete_registry_20240330_143025.csv`
4. Open in Excel/Google Sheets → Should have athlete data

✅ **Export buttons working and visible!**

---

## Test 7: Production Security ✅

### Verify .env is NOT in Git

**Check .gitignore:**
```bash
cat .gitignore | grep env
```

**Should show:**
```
.env
```

This prevents accidental commit of secrets.

### Verify SECRET_KEY is Not Hardcoded

**Check app/__init__.py:**
```bash
grep -n "SECRET_KEY" app/__init__.py
```

**Should show something like:**
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
```

✓ **NOT hardcoded in code!**

---

## Test 8: Error Handling ✅

### Test Invalid JSON

```javascript
fetch('/api/athletes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: 'invalid json'
})
.then(r => r.json())
.then(data => console.log(data))
```

**Expected:** Error message returned (not a crash)

### Test Non-existent Athlete

```javascript
fetch('/api/athletes/99999')
.then(r => {
    console.log('Status:', r.status);
    return r.json();
})
.then(data => console.log(data))
```

**Expected:** 404 error gracefully handled

✅ **Error handling working!**

---

## Test 9: Comments & Documentation ✅

### Verify Code is Well-Commented

**Check routes.py:**
```bash
grep -c "# " app/routes.py
```

Should show many comment lines (100+)

**Check specific functions have docstrings:**
```bash
grep -A 5 "def get_injury_recommendation" app/routes.py
```

Should show:
```python
def get_injury_recommendation(risk_category):
    """
    Generate 3 specific, actionable recommendation tips...
    """
```

✅ **Code is well-documented!**

---

## Test 10: Defense Guide Readability ✅

### Verify PROJECT_DEFENSE_GUIDE.txt

1. Open: `PROJECT_DEFENSE_GUIDE.txt`
2. Verify contents include:
   - ✓ Elevator Pitch
   - ✓ Random Forest explanation with "Council of Experts" analogy
   - ✓ Logistic Regression with "Probability Slider" analogy
   - ✓ 10 Anticipated Viva Questions & Answers
   - ✓ System Requirements
   - ✓ Quick Start Instructions
   - ✓ Key Innovation section

**Try reading the Q&A sections** - they should be clear and easy to understand

✅ **Defense guide is comprehensive and readable!**

---

## 🎉 All Tests Passed?

If you've gone through all 10 tests and they all passed, then:

✅ Data validation is working
✅ Enhanced recommendations are providing 3 specific tips
✅ CSV export is working
✅ Mobile responsiveness is perfect
✅ .env configuration is secure
✅ Export buttons are visible and functional
✅ Error handling prevents crashes
✅ Code is well-commented
✅ Security is production-grade
✅ Defense guide is comprehensive

**Your system is production-ready for your final year presentation! 🎓**

---

## 📞 Troubleshooting

### Export button not showing?
- Clear browser cache (Ctrl+Shift+Delete)
- Restart Python server
- Check dashboard.html was updated

### Validation not working?
- Restart server: `python run.py`
- Check routes.py was updated correctly
- Try validation in console (see Test 1)

### Mobile view not responsive?
- Clear CSS cache
- Check style.css has mobile media queries
- Try different browser

### .env not loading?
- Install python-dotenv: `pip install python-dotenv`
- Verify .env file exists in project root
- Check app/__init__.py loads it first

---

## 🎯 For Your Presentation

When demonstrating to examiners:

1. **Show Data Validation:** Try creating athlete with invalid age
2. **Show Enhanced Recommendations:** Run injury risk prediction
3. **Show Export:** Download CSV and open in Excel
4. **Show Mobile:** Flip to phone view in DevTools
5. **Show Code Quality:** Reference specific functions in PROJECT_DEFENSE_GUIDE.txt
6. **Show Your Understanding:** Explain why each feature matters

**Good luck! 🎓**