"""
Mock Data Generator - Nigerian University Sports Context
Generates synthetic athlete data for initial ML model training
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_athlete_data(n=200):
    """
    Generate synthetic athlete data tailored to Nigerian university context
    """
    np.random.seed(42)
    random.seed(42)
    
    sports = ['Football', 'Basketball', 'Track & Field', 'Volleyball', 'Tennis', 'Badminton', 'Swimming']
    nigerian_names = [
        'Chioma', 'Ola', 'Adeyemi', 'Zainab', 'Tunde', 'Ngozi', 'Ibrahim', 'Fatima',
        'Chukwu', 'Aisha', 'Malik', 'Blessing', 'Ahmed', 'Taiwo', 'Damilare', 'Nneka',
        'Kofi', 'Amina', 'Segun', 'Precious', 'Jamal', 'Zara', 'Emeka', 'Halima'
    ]
    
    data = {
        'athlete_id': range(1, n + 1),
        'name': [f"{random.choice(nigerian_names)} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Obi', 'Adamu', 'Hassan', 'Ali'])}" for _ in range(n)],
        'registration_number': [f"UOD-{2024 + np.random.randint(0, 4)}-{1001 + i}" for i in range(n)],
        'age': np.random.randint(18, 26, size=n),
        'sport': np.random.choice(sports, size=n),
        'height_cm': np.random.uniform(160, 195, size=n),
        'weight_kg': np.random.uniform(55, 95, size=n),
        'training_hours_pw': np.random.uniform(5, 25, size=n),
        'prev_injuries': np.random.randint(0, 4, size=n),
        'performance_score': np.random.uniform(40, 100, size=n),
        'sleep_hours': np.random.uniform(5, 9, size=n)
    }
    
    df = pd.DataFrame(data)
    
    # Logic for Injury Prediction (Target for Random Forest)
    # Risk increases with high training hours and low sleep
    df['injury_risk'] = (
        (df['training_hours_pw'] * 0.6) + 
        (df['prev_injuries'] * 2.0) - 
        (df['sleep_hours'] * 0.5)
    )
    df['injury_occurred'] = (df['injury_risk'] > df['injury_risk'].median()).astype(int)
    
    # Logic for Talent Identification (Target for Logistic Regression)
    # Talent is a factor of performance score relative to age
    df['talent_potential'] = (
        (df['performance_score'] * 0.7) - 
        (df['age'] * 0.3)
    )
    df['is_high_potential'] = (df['talent_potential'] > df['talent_potential'].median()).astype(int)
    
    return df


def generate_injury_events(athletes_df, n_injuries=60):
    """Generate injury event records"""
    injury_types = ['Sprain', 'Strain', 'Fracture', 'Concussion', 'Tendinitis', 'Contusion', 'Dislocation']
    severities = ['mild', 'moderate', 'severe']
    
    injury_data = []
    injured_athletes = np.random.choice(athletes_df['athlete_id'].values, size=n_injuries, replace=True)
    
    for athlete_id in injured_athletes:
        injury_date = datetime.utcnow() - timedelta(days=np.random.randint(1, 365))
        recovery_days = np.random.randint(7, 180)
        
        injury_data.append({
            'athlete_id': athlete_id,
            'injury_type': np.random.choice(injury_types),
            'severity': np.random.choice(severities),
            'date_occurred': injury_date,
            'recovery_duration_days': recovery_days,
            'date_recovered': injury_date + timedelta(days=recovery_days),
            'notes': 'Injury sustained during training/competition'
        })
    
    return pd.DataFrame(injury_data)


def generate_events(n_events=30):
    """Generate event records"""
    event_types = ['competition', 'training', 'tournament', 'league_match']
    nigerians_locations = ['Lagos Sports Complex', 'Abuja Stadium', 'Ibadan Sports Center', 
                          'Port Harcourt Arena', 'Kano Olympic Stadium', 'Benin Arena']
    
    event_data = []
    for i in range(n_events):
        event_date = datetime.utcnow() + timedelta(days=np.random.randint(-30, 90))
        event_data.append({
            'event_name': f"Sports Event #{i+1}",
            'event_type': np.random.choice(event_types),
            'date': event_date,
            'location': np.random.choice(nigerians_locations),
            'description': 'University of Delta Sports Event'
        })
    
    return pd.DataFrame(event_data)


if __name__ == "__main__":
    print("🏅 Generating Mock Data for Intelligent Sports Management System...")
    
    # Generate athlete data
    athletes_df = generate_athlete_data(n=200)
    athletes_df.to_csv('mock_athletes.csv', index=False)
    print(f"✅ Generated {len(athletes_df)} athlete records")
    
    # Generate injury events
    injuries_df = generate_injury_events(athletes_df, n_injuries=60)
    injuries_df.to_csv('mock_injuries.csv', index=False)
    print(f"✅ Generated {len(injuries_df)} injury records")
    
    # Generate events
    events_df = generate_events(n_events=30)
    events_df.to_csv('mock_events.csv', index=False)
    print(f"✅ Generated {len(events_df)} event records")
    
    print("\n✨ Mock data generation complete! Ready for ML model training.")
