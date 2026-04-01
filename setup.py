"""
Setup Script - Initialize Database and Train ML Models
Run: python setup.py
"""
import os
import sys
from app import create_app
from models.database import db, Athlete, Injury, Event, TalentMetric, InjuryRiskAssessment
from generate_mock_data import generate_athlete_data, generate_injury_events, generate_events
from ml.ml_models import train_all_models
from datetime import datetime
import pandas as pd

def setup_database():
    """Initialize and seed database with mock data"""
    print("\n" + "="*60)
    print("🚀 INITIALIZING SPORTS MANAGEMENT SYSTEM")
    print("="*60 + "\n")
    
    # Create app and database
    app = create_app()
    
    with app.app_context():
        print("✅ Database tables created\n")
        
        # Generate mock data
        print("📊 Generating mock athlete data...")
        athletes_df = generate_athlete_data(n=200)
        
        print("📋 Generating injury records...")
        injuries_df = generate_injury_events(athletes_df, n_injuries=60)
        
        print("📅 Generating event records...")
        events_df = generate_events(n_events=30)
        
        # Load athletes into database
        print("\n💾 Loading athletes into database...")
        for idx, row in athletes_df.iterrows():
            athlete = Athlete(
                name=row['name'],
                registration_number=row['registration_number'],
                age=int(row['age']),
                sport=row['sport'],
                height_cm=float(row['height_cm']),
                weight_kg=float(row['weight_kg']),
                performance_score=float(row['performance_score']),
                training_hours_pw=float(row['training_hours_pw']),
                sleep_hours=float(row['sleep_hours'])
            )
            db.session.add(athlete)
        
        db.session.commit()
        print(f"   ✅ {len(athletes_df)} athletes loaded")
        
        # Load injuries into database
        print("💾 Loading injury records into database...")
        for idx, row in injuries_df.iterrows():
            injury = Injury(
                athlete_id=int(row['athlete_id']),
                injury_type=row['injury_type'],
                severity=row['severity'],
                date_occurred=row['date_occurred'],
                recovery_duration_days=int(row['recovery_duration_days']),
                date_recovered=row['date_recovered'],
                notes=row['notes']
            )
            db.session.add(injury)
        
        db.session.commit()
        print(f"   ✅ {len(injuries_df)} injury records loaded")
        
        # Load events into database
        print("💾 Loading events into database...")
        for idx, row in events_df.iterrows():
            event = Event(
                event_name=row['event_name'],
                event_type=row['event_type'],
                date=row['date'],
                location=row['location'],
                description=row['description']
            )
            db.session.add(event)
        
        db.session.commit()
        print(f"   ✅ {len(events_df)} events loaded")
        
        print("\n✨ Database initialization complete!")


def train_models():
    """Train and save ML models"""
    print("\n" + "="*60)
    print("🤖 TRAINING MACHINE LEARNING MODELS")
    print("="*60 + "\n")
    
    # Generate training data
    print("📊 Preparing training data...")
    athletes_df = generate_athlete_data(n=200)
    athletes_df.to_csv('mock_athletes.csv', index=False)
    
    # Train all models
    train_all_models('mock_athletes.csv')


def main():
    """Main setup flow"""
    try:
        # Setup database
        setup_database()
        
        # Train ML models
        train_models()
        
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE!")
        print("="*60)
        print("\n🚀 Next steps:")
        print("   1. Run: python run.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Explore the dashboard and analytics\n")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
