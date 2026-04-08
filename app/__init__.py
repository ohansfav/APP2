"""
Flask Application Factory with Environment-based Configuration
"""
from flask import Flask
from models.database import db
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_app(config=None):
    """Create and configure Flask application with production-ready security"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration - Load from .env or use defaults
    # PRODUCTION SECURITY: All sensitive values should be in .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///sports_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        # Initialize demo data on first run
        initialize_demo_data()
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add custom template filters
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        if isinstance(value, str):
            return value
        return value.strftime(format) if value else ''
    
    return app


def initialize_demo_data():
    """Initialize database with demo data if empty"""
    from models.database import Athlete, Event, Injury, InjuryRiskAssessment, User
    from datetime import timedelta
    import random
    from werkzeug.security import generate_password_hash
    
    # Check if admin user exists, if not create it
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin = User(
            username='admin',
            email='admin@athleteapp.com',
            password=generate_password_hash('admin123'),
            full_name='System Administrator',
            role='admin',
            sport_specialization=None
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created (username: admin, password: admin123)")
    
    # Check if data already exists
    if Athlete.query.first() is not None:
        return  # Data already exists
    
    # Demo athletes - REDUCED TO 4
    demo_athletes = [
        {'name': 'John Okoro', 'sport': 'Football', 'age': 22, 'performance_score': 88},
        {'name': 'Mary Chen', 'sport': 'Basketball', 'age': 21, 'performance_score': 92},
        {'name': 'Ahmed Hassan', 'sport': 'Track & Field', 'age': 20, 'performance_score': 85},
        {'name': 'Sarah Williams', 'sport': 'Tennis', 'age': 23, 'performance_score': 78},
    ]
    
    athletes = []
    for i, athlete_data in enumerate(demo_athletes):
        import uuid
        athlete = Athlete(
            name=athlete_data['name'],
            registration_number=f"ATH-{uuid.uuid4().hex[:8].upper()}",
            age=athlete_data['age'],
            sport=athlete_data['sport'],
            performance_score=athlete_data['performance_score'],
            height_cm=random.randint(160, 195),
            weight_kg=random.randint(60, 95),
            training_hours_pw=random.randint(10, 20),
            sleep_hours=random.randint(6, 9)
        )
        athletes.append(athlete)
        db.session.add(athlete)
    
    db.session.commit()
    
    # Demo events
    demo_events = [
        {'name': 'Football Championship', 'location': 'Main Stadium', 'days_ahead': 3},
        {'name': 'Basketball Tournament', 'location': 'Sports Hall', 'days_ahead': 7},
    ]
    
    for event_data in demo_events:
        event = Event(
            event_name=event_data['name'],
            event_type='Competition',
            date=datetime.utcnow() + timedelta(days=event_data['days_ahead']),
            location=event_data['location'],
            description=f"{event_data['name']} - Annual event"
        )
        db.session.add(event)
    
    db.session.commit()
    
    # Demo injuries
    injury_types = ['Muscle Strain', 'Sprain', 'Knee Injury']
    for i in range(2):
        random_athlete = random.choice(athletes)
        injury = Injury(
            athlete_id=random_athlete.id,
            injury_type=random.choice(injury_types),
            severity=random.choice(['Mild', 'Moderate']),
            date_occurred=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            recovery_duration_days=random.randint(7, 30),
            notes='Demo injury record'
        )
        db.session.add(injury)
    
    # Add injury risk assessments for analytics
    for athlete in athletes:
        risk_score = random.uniform(0.2, 0.8)
        risk_category = 'Low' if risk_score < 0.4 else 'Medium' if risk_score < 0.7 else 'High'
        
        # Determine main risk factor and recommendations based on athlete profile
        if athlete.training_hours_pw > 15:
            main_risk_factor = 'High training load'
            recommendations = 'Reduce weekly training hours or increase recovery time.'
        elif athlete.sleep_hours < 6:
            main_risk_factor = 'Insufficient sleep'
            recommendations = 'Improve sleep hygiene. Aim for 7-9 hours per night.'
        else:
            main_risk_factor = 'Normal risk profile'
            recommendations = 'Continue current training regimen. Maintain good sleep and recovery habits.'
        
        assessment = InjuryRiskAssessment(
            athlete_id=athlete.id,
            training_hours_pw=athlete.training_hours_pw,
            prev_injuries=1 if random.random() > 0.5 else 0,
            sleep_hours=athlete.sleep_hours,
            injury_risk_score=risk_score,
            risk_category=risk_category,
            main_risk_factor=main_risk_factor,
            recommendations=recommendations,
            model_confidence=random.uniform(0.7, 0.95)
        )
        db.session.add(assessment)
    
    db.session.commit()
    
    print("✅ Demo data initialized successfully!")
