# ⚡ Quick Start Guide - Intelligent Sports Management System

## 🚀 Get Up & Running in 3 Steps

### Step 1️⃣: Install Dependencies (1 minute)
```bash
cd c:\Users\ohanu\OneDrive\Desktop\final year project 2
pip install -r requirements.txt
```

**What it does:** Installs Flask, SQLAlchemy, scikit-learn, pandas, and other libraries

---

### Step 2️⃣: Initialize System (2-3 minutes)
```bash
python setup.py
```

**What the setup script does:**
- ✅ Creates SQLite database (`sports_management.db`)
- ✅ Generates 200 mock athletes (Nigerian university context)
- ✅ Creates 60+ injury records
- ✅ Creates 30+ event records
- ✅ Trains Random Forest model (Injury Prediction)
- ✅ Trains Logistic Regression model (Talent Identification)
- ✅ Saves trained models as .pkl files

**Expected output:**
```
============================================================
🚀 INITIALIZING SPORTS MANAGEMENT SYSTEM
============================================================

✅ Database tables created

📊 Generating mock athlete data...
📋 Generating injury records...
📅 Generating event records...

💾 Loading athletes into database...
   ✅ 200 athletes loaded
💾 Loading injury records into database...
   ✅ 60 injury records loaded
💾 Loading events into database...
   ✅ 30 events loaded

✨ Database initialization complete!

============================================================
🤖 TRAINING MACHINE LEARNING MODELS
============================================================
...training output...
============================================================
✅ SETUP COMPLETE!
```

---

### Step 3️⃣: Start the Application
```bash
python run.py
```

**Expected output:**
```
============================================================
🎯 INTELLIGENT SPORTS MANAGEMENT SYSTEM
============================================================

📊 Dashboard: http://localhost:5000
🏃 Athletes: http://localhost:5000/athletes
📈 Analytics: http://localhost:5000/analytics

🚀 Server running in offline-first mode...
```

---

## 📱 Open in Browser

Open any browser and navigate to:
```
http://localhost:5000
```

You should see the main dashboard with:
- 📊 Key metrics (Athletes, Events, Injuries)
- 📈 Charts and visualizations
- 🏃 Navigation to Athletes, Analytics, Events sections

---

## 🎯 Try These Features

### 1. View Athlete Registry
- Click **Athletes** in navigation
- See list of 200 generated athletes
- Click any athlete to view profile
- **Search by name** to find specific athletes

### 2. Assess Injury Risk
- Go to any athlete's detail page
- Click **"Assess Injury Risk"** button
- Enter training hours, previous injuries, sleep hours
- See real-time ML prediction with:
  - Risk score (0-100%)
  - Risk category (Low/Medium/High)
  - Model confidence
  - Coach recommendations

### 3. Predict Talent Potential
- In athlete detail page
- Click **"Assess Talent Potential"**
- Enter performance metrics (speed, strength, endurance, agility, technique)
- Get talent score and category:
  - **Developing** (0-33%)
  - **Promising** (33-67%)
  - **Elite** (67-100%)

### 4. Explore Analytics
- Click **Analytics** in navigation  
- View talent potential distribution
- See injury risk distribution
- Analyze 4-year performance trends
- Study injury and recovery patterns

### 5. Manage Events
- Click **Events** in navigation
- View all sports events and competitions
- Create new events (training, competition, tournaments)
- Track athlete participation

---

## 🔧 Common Tasks

### Add a New Athlete via API
```bash
curl -X POST http://localhost:5000/api/athletes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ngozi Okafor",
    "registration_number": "UOD-2024-1001",
    "age": 21,
    "sport": "Basketball",
    "height_cm": 178,
    "weight_kg": 72,
    "performance_score": 75
  }'
```

### Get All Athletes
```bash
curl http://localhost:5000/api/athletes
```

### Predict Injury Risk
```bash
curl -X POST http://localhost:5000/api/predict/injury-risk \
  -H "Content-Type: application/json" \
  -d '{
    "athlete_id": 1,
    "training_hours_pw": 18,
    "prev_injuries": 1,
    "sleep_hours": 7
  }'
```

---

## 📊 Accessing Data

### View Database (SQLite)
The database is stored in: `sports_management.db`

To inspect:
```bash
# Using SQLite CLI
sqlite3 sports_management.db

# Then in SQLite:
SELECT * FROM athletes LIMIT 5;
SELECT COUNT(*) FROM athletes;
SELECT * FROM injuries LIMIT 5;
```

### View ML Models
Models are saved in the `ml/` folder:
- `injury_model.pkl` - Trained Random Forest
- `injury_scaler.pkl` - Feature scaler
- `talent_model.pkl` - Trained Logistic Regression
- `talent_scaler.pkl` - Feature scaler

---

## 🆘 Troubleshooting

### Issue: "ModuleNotFoundError"
```bash
# Make sure you're in the right directory
cd c:\Users\ohanu\OneDrive\Desktop\final year project 2

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: "Port 5000 already in use"
```bash
# Kill the process using port 5000
# Windows PowerShell:
Get-Process | Where-Object {$_.Port -eq 5000} | Stop-Process

# Or run on different port:
python -c "import run; run.app.run(port=5001)"
```

### Issue: Database errors
```bash
# Delete and recreate database
del sports_management.db
python setup.py
```

### Issue: ML models not found
```bash
# Retrain models
python ml_engine.py

# Or use setup (comprehensive):
python setup.py
```

---

## 💡 Tips & Best Practices

1. **First Time Setup**: Always run `python setup.py` first
2. **Regular Backups**: Copy `sports_management.db` regularly
3. **Data Export**: Use the UI to export data to CSV
4. **Offline Mode**: System works completely offline - no internet needed!
5. **Performance**: Don't add more than 50,000 athletes for optimal performance

---

## 📚 Documentation

For comprehensive documentation, see **README.md** in the project root folder.

Includes:
- 📋 Complete feature list
- 🔌 API endpoint reference
- 📊 ML model documentation
- 💾 Database schema
- 🎯 Usage examples

---

## 🎉 You're All Set!

The system is now ready to use. Here's what you have:

✅ **200 Athletes** with realistic Nigerian university data  
✅ **60 Injury Records** for historical analysis  
✅ **30 Events** scheduled  
✅ **Trained ML Models** ready for predictions  
✅ **Modern Dashboard** with real-time visualizations  
✅ **REST API** for programmatic access  
✅ **Offline-First Architecture** - works without internet  

---

## 🚀 Next Steps

1. **Explore the Dashboard**: Get familiar with the UI
2. **Try ML Predictions**: Assess injury risk & talent potential
3. **View Analytics**: Analyze performance trends
4. **Create Events**: Add your own college events
5. **Add Athletes**: Build your complete roster
6. **Integrate**: Use the REST API in other systems

---

## 📞 Support

Check **README.md** for:
- Detailed API documentation
- Database schema information
- Troubleshooting guide
- Development guidelines

---

*🎯 Intelligent Sports Management System v1.0*  
*📍 University of Delta - Offline-First Platform*  
*🚀 Production-Ready & Fully Functional*
